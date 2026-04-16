from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from models import (
    Incident, IncidentCreate, DiagnosisResult, LogEvent, HealthStatus
)
from log_provider import log_provider
from simulator import simulator, SCENARIOS
from diagnosis import run_diagnosis, check_llm_health

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'clouddoctor')]

# Create the main app
app = FastAPI(title="CloudDoctor API", version="1.0.0")

# Create a router with /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def serialize_doc(doc: dict) -> dict:
    """Serialize MongoDB document, handling ObjectId and datetime."""
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if key == '_id':
            continue
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(v) if isinstance(v, dict) else v for v in value]
        else:
            result[key] = value
    return result


# ========================
# Health Check
# ========================
@api_router.get("/health")
async def health_check():
    """Check all service connections."""
    health = {}

    # MongoDB
    try:
        await client.admin.command('ping')
        health["mongodb"] = {"status": "connected", "message": "MongoDB operational"}
    except Exception as e:
        health["mongodb"] = {"status": "error", "message": str(e)}

    # LLM
    llm_key = os.environ.get("EMERGENT_LLM_KEY")
    if llm_key:
        health["llm"] = {"status": "connected", "message": "GPT-4o via Emergent key configured"}
    else:
        health["llm"] = {"status": "error", "message": "EMERGENT_LLM_KEY not configured"}

    # BetterStack
    bs_source = os.environ.get("BETTERSTACK_SOURCE_TOKEN")
    bs_query = os.environ.get("BETTERSTACK_QUERY_TOKEN")
    if bs_source and bs_query:
        health["betterstack"] = {"status": "connected", "message": "BetterStack tokens configured"}
    elif bs_source or bs_query:
        health["betterstack"] = {"status": "warning", "message": "Partial BetterStack configuration"}
    else:
        health["betterstack"] = {"status": "not_configured", "message": "Using local log provider (BetterStack tokens not set)"}

    # Sample App (simulator)
    health["sample_app"] = {
        "status": "healthy" if simulator.is_healthy else "unhealthy",
        "message": simulator.state["description"],
        "current_scenario": simulator.current_scenario,
    }

    return health


# ========================
# Incident Management
# ========================
@api_router.post("/incidents/trigger")
async def trigger_incident(body: IncidentCreate):
    """Trigger a failure scenario and create an incident."""
    scenario = body.scenario

    if scenario not in SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario: {scenario}. Available: {list(SCENARIOS.keys())}"
        )

    # Trigger the simulator
    sim_state = simulator.trigger(scenario)
    if "error" in sim_state:
        raise HTTPException(status_code=400, detail=sim_state["error"])

    # Get log stats
    stats = log_provider.stats()

    # Create incident in MongoDB
    incident = Incident(
        anomaly_type=scenario,
        service=SCENARIOS[scenario]["service"],
        severity_label="high",
        severity_score=0.8,
        log_count=stats.get("ERROR", 0) + stats.get("WARN", 0) + stats.get("FATAL", 0),
        error_count=stats.get("ERROR", 0),
        fatal_count=stats.get("FATAL", 0),
    )
    incident_dict = incident.model_dump()
    if incident_dict.get('diagnosis'):
        incident_dict['diagnosis'] = incident_dict['diagnosis']
    else:
        incident_dict['diagnosis'] = None

    await db.incidents.insert_one(incident_dict)
    logger.info(f"Incident created: {incident.id} for scenario: {scenario}")

    return serialize_doc(incident_dict)


@api_router.get("/incidents")
async def list_incidents(
    status: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
):
    """List all incidents."""
    query = {}
    if status:
        query["status"] = status

    incidents = await db.incidents.find(query, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return [serialize_doc(inc) for inc in incidents]


@api_router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get a specific incident."""
    incident = await db.incidents.find_one({"id": incident_id}, {"_id": 0})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return serialize_doc(incident)


@api_router.post("/incidents/{incident_id}/diagnose")
async def diagnose_incident(incident_id: str):
    """Run AI diagnosis on an incident."""
    incident = await db.incidents.find_one({"id": incident_id}, {"_id": 0})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Get logs for this incident's scenario
    scenario = incident.get("anomaly_type", "")
    logs = log_provider.query(scenario=scenario, limit=50)

    if not logs:
        # If no scenario-specific logs, get recent error logs
        logs = log_provider.query(levels=["ERROR", "WARN", "FATAL"], limit=30)

    # Format logs for AI
    logs_text = "\n".join(
        f"[{log.get('level', 'INFO')}] {log.get('timestamp', '')} - {log.get('message', '')}"
        for log in logs
    )

    if not logs_text:
        logs_text = f"No logs found for scenario: {scenario}. This is a {scenario} incident."

    # Run diagnosis
    diagnosis = await run_diagnosis(logs_text, scenario, incident_id)

    # Update incident
    log_stats = log_provider.stats()
    await db.incidents.update_one(
        {"id": incident_id},
        {"$set": {
            "diagnosis": diagnosis.model_dump(),
            "status": "diagnosed",
            "severity_score": diagnosis.confidence / 100,
            "severity_label": diagnosis.severity,
            "confidence": diagnosis.confidence,
            "estimated_mttr": diagnosis.estimated_mttr,
            "log_count": sum(log_stats.values()),
            "error_count": log_stats.get("ERROR", 0),
            "fatal_count": log_stats.get("FATAL", 0),
        }}
    )

    updated = await db.incidents.find_one({"id": incident_id}, {"_id": 0})
    return serialize_doc(updated)


@api_router.post("/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: str):
    """Resolve an incident."""
    incident = await db.incidents.find_one({"id": incident_id})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    await db.incidents.update_one(
        {"id": incident_id},
        {"$set": {
            "status": "resolved",
            "resolved_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    updated = await db.incidents.find_one({"id": incident_id}, {"_id": 0})
    return serialize_doc(updated)


# ========================
# Logs
# ========================
@api_router.get("/logs")
async def get_logs(
    levels: Optional[str] = None,  # Comma-separated: "ERROR,WARN"
    since: Optional[str] = None,
    limit: int = Query(default=200, ge=1, le=1000),
    scenario: Optional[str] = None,
):
    """Get logs from the log provider."""
    level_list = levels.split(",") if levels else None
    logs = log_provider.query(
        levels=level_list,
        since=since,
        limit=limit,
        scenario=scenario,
    )
    return {"logs": logs, "count": len(logs)}


@api_router.get("/logs/stats")
async def get_log_stats(since: Optional[str] = None):
    """Get log count statistics by severity."""
    stats = log_provider.stats(since=since)
    total = sum(stats.values())
    return {"stats": stats, "total": total}


# ========================
# Simulator Control
# ========================
@api_router.get("/simulator/state")
async def get_simulator_state():
    """Get current simulator state."""
    return simulator.state


@api_router.post("/simulator/stop")
async def stop_simulator():
    """Stop the current scenario and reset to healthy."""
    state = simulator.stop()
    return state


@api_router.get("/scenarios")
async def list_scenarios():
    """List available failure scenarios."""
    return {
        name: {"description": data["description"], "service": data["service"]}
        for name, data in SCENARIOS.items()
    }


# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    simulator.stop()
    client.close()
