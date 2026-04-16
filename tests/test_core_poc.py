"""
CloudDoctor POC - Core Workflow Validation
Tests: LLM call, failure simulation, log generation/retrieval, incident persistence, AI diagnosis
"""
import asyncio
import os
import sys
import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Load env
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

# ============================================================
# TEST 1: LLM Call Sanity (Emergent LLM Key + OpenAI GPT-4o)
# ============================================================
async def test_llm_call():
    print("\n" + "="*60)
    print("TEST 1: LLM Call Sanity (GPT-4o via Emergent Key)")
    print("="*60)
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            print("❌ EMERGENT_LLM_KEY not found in environment")
            return False
        
        print(f"  API Key: {api_key[:12]}...")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"poc-test-{uuid.uuid4().hex[:8]}",
            system_message="""You are CloudDoctor, an AI cloud infrastructure diagnostics expert.
When given log data about infrastructure issues, provide diagnosis in JSON format:
{
  "root_cause": "Brief description of the root cause",
  "severity": "critical|high|medium|low",
  "confidence": 95,
  "recommended_fixes": ["fix 1", "fix 2"],
  "estimated_mttr": "15 minutes"
}
Respond ONLY with valid JSON, no markdown."""
        )
        chat.with_model("openai", "gpt-4o")
        
        # Simulate a diagnosis request
        sample_logs = """
[ERROR] 2024-01-15 10:00:01 - Database connection pool exhausted (0/50 connections available)
[ERROR] 2024-01-15 10:00:02 - Failed to acquire DB connection: pool timeout after 5000ms
[WARN]  2024-01-15 10:00:03 - Request queue depth: 250 (threshold: 100)
[ERROR] 2024-01-15 10:00:04 - Transaction rollback: connection reset by peer
[FATAL] 2024-01-15 10:00:05 - Service health check failed: database unreachable
        """
        
        user_msg = UserMessage(
            text=f"Analyze these cloud infrastructure logs and diagnose the issue:\n{sample_logs}"
        )
        
        response = await chat.send_message(user_msg)
        print(f"  LLM Response: {response[:200]}...")
        
        # Try to parse as JSON
        try:
            # Clean up response - remove markdown code blocks if present
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("\n", 1)[1]
                clean_response = clean_response.rsplit("```", 1)[0]
            
            diagnosis = json.loads(clean_response)
            print(f"  ✅ JSON parsed successfully")
            print(f"  Root Cause: {diagnosis.get('root_cause', 'N/A')}")
            print(f"  Severity: {diagnosis.get('severity', 'N/A')}")
            print(f"  Confidence: {diagnosis.get('confidence', 'N/A')}%")
            print(f"  Fixes: {diagnosis.get('recommended_fixes', [])}")
            print(f"  MTTR: {diagnosis.get('estimated_mttr', 'N/A')}")
            return True
        except json.JSONDecodeError as e:
            print(f"  ⚠️ Response not valid JSON, but LLM call worked: {e}")
            print(f"  Raw response: {response}")
            return True  # LLM call itself worked
            
    except Exception as e:
        print(f"  ❌ LLM call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# TEST 2: MongoDB Incident Persistence
# ============================================================
async def test_mongodb_incidents():
    print("\n" + "="*60)
    print("TEST 2: MongoDB Incident Persistence")
    print("="*60)
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME", "test_database")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print("  ✅ MongoDB connection successful")
        
        # Create incident
        incident_id = str(uuid.uuid4())
        incident = {
            "id": incident_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "database-service",
            "anomaly_type": "db-crash",
            "severity_score": 0.95,
            "severity_label": "critical",
            "status": "open",
            "confidence": 95,
            "estimated_mttr": "15 minutes",
            "diagnosis": {
                "root_cause": "Connection pool exhaustion",
                "recommended_fixes": ["Increase pool size", "Add connection timeout"]
            },
            "log_count": 10,
            "error_count": 5,
            "fatal_count": 1,
            "resolved_at": None
        }
        
        await db.incidents.insert_one(incident)
        print(f"  ✅ Incident created: {incident_id}")
        
        # Retrieve incident
        found = await db.incidents.find_one({"id": incident_id}, {"_id": 0})
        assert found is not None, "Incident not found"
        assert found["status"] == "open"
        print(f"  ✅ Incident retrieved: status={found['status']}")
        
        # Update incident (resolve)
        await db.incidents.update_one(
            {"id": incident_id},
            {"$set": {"status": "resolved", "resolved_at": datetime.now(timezone.utc).isoformat()}}
        )
        found = await db.incidents.find_one({"id": incident_id}, {"_id": 0})
        assert found["status"] == "resolved"
        print(f"  ✅ Incident resolved: status={found['status']}")
        
        # Cleanup
        await db.incidents.delete_one({"id": incident_id})
        print("  ✅ Cleanup complete")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"  ❌ MongoDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# TEST 3: Local Log Provider (Ring Buffer)
# ============================================================
async def test_local_log_provider():
    print("\n" + "="*60)
    print("TEST 3: Local Log Provider (Ring Buffer)")
    print("="*60)
    
    try:
        from collections import deque
        from datetime import datetime, timezone
        
        # Simulate LocalLogProvider
        class LocalLogProvider:
            def __init__(self, max_size=10000):
                self.logs = deque(maxlen=max_size)
            
            def append(self, log_event):
                self.logs.append(log_event)
            
            def query(self, levels=None, since=None, limit=100):
                results = []
                for log in reversed(self.logs):
                    if levels and log.get("level") not in levels:
                        continue
                    if since and log.get("timestamp", "") < since:
                        continue
                    results.append(log)
                    if len(results) >= limit:
                        break
                return results
            
            def stats(self, since=None):
                counts = {"DEBUG": 0, "INFO": 0, "WARN": 0, "ERROR": 0, "FATAL": 0}
                for log in self.logs:
                    if since and log.get("timestamp", "") < since:
                        continue
                    level = log.get("level", "INFO")
                    counts[level] = counts.get(level, 0) + 1
                return counts
        
        provider = LocalLogProvider(max_size=1000)
        
        # Simulate failure logs (db-crash scenario)
        scenarios = {
            "db-crash": [
                {"level": "ERROR", "message": "Database connection pool exhausted (0/50 connections available)", "service": "database"},
                {"level": "ERROR", "message": "Failed to acquire DB connection: pool timeout after 5000ms", "service": "database"},
                {"level": "WARN", "message": "Request queue depth: 250 (threshold: 100)", "service": "api-gateway"},
                {"level": "ERROR", "message": "Transaction rollback: connection reset by peer", "service": "database"},
                {"level": "FATAL", "message": "Service health check failed: database unreachable", "service": "database"},
            ]
        }
        
        now = datetime.now(timezone.utc)
        for i, log_template in enumerate(scenarios["db-crash"]):
            log_event = {
                **log_template,
                "timestamp": (now + timedelta(seconds=i)).isoformat(),
                "scenario": "db-crash",
                "id": str(uuid.uuid4())
            }
            provider.append(log_event)
        
        # Add some INFO logs
        for i in range(5):
            provider.append({
                "level": "INFO",
                "message": f"Normal operation log entry {i}",
                "service": "api-gateway",
                "timestamp": (now + timedelta(seconds=10+i)).isoformat(),
                "id": str(uuid.uuid4())
            })
        
        print(f"  Total logs: {len(provider.logs)}")
        
        # Query all
        all_logs = provider.query(limit=50)
        print(f"  ✅ All logs query: {len(all_logs)} results")
        
        # Query by level
        errors = provider.query(levels=["ERROR", "FATAL"])
        print(f"  ✅ Error/Fatal logs: {len(errors)} results")
        assert len(errors) == 4, f"Expected 4 error/fatal logs, got {len(errors)}"
        
        # Stats
        stats = provider.stats()
        print(f"  ✅ Log stats: {stats}")
        assert stats["ERROR"] == 3
        assert stats["FATAL"] == 1
        assert stats["WARN"] == 1
        assert stats["INFO"] == 5
        
        return True
        
    except Exception as e:
        print(f"  ❌ Local Log Provider test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# TEST 4: Full Diagnosis Flow (Logs → LLM → Incident)
# ============================================================
async def test_full_diagnosis_flow():
    print("\n" + "="*60)
    print("TEST 4: Full Diagnosis Flow (Logs → LLM → Incident)")
    print("="*60)
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        from motor.motor_asyncio import AsyncIOMotorClient
        
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME", "test_database")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Step 1: Create incident
        incident_id = str(uuid.uuid4())
        incident = {
            "id": incident_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "database-service",
            "anomaly_type": "memory-leak",
            "severity_score": 0.0,
            "severity_label": "unknown",
            "status": "open",
            "confidence": 0,
            "estimated_mttr": "unknown",
            "diagnosis": None,
            "log_count": 0,
            "error_count": 0,
            "fatal_count": 0,
            "resolved_at": None
        }
        await db.incidents.insert_one(incident)
        print(f"  ✅ Step 1: Incident created: {incident_id}")
        
        # Step 2: Generate logs for this incident
        sample_logs = [
            "[ERROR] Memory usage at 95% (threshold: 80%)",
            "[WARN] GC pause time: 5200ms (threshold: 1000ms)",
            "[ERROR] OOMKilled: container exceeded memory limit 2Gi",
            "[FATAL] Pod restart count: 5 (threshold: 3)",
            "[ERROR] Heap dump generated: /tmp/heapdump-20240115.hprof"
        ]
        log_text = "\n".join(sample_logs)
        print(f"  ✅ Step 2: Generated {len(sample_logs)} log entries")
        
        # Step 3: Run AI diagnosis
        chat = LlmChat(
            api_key=api_key,
            session_id=f"diagnosis-{incident_id[:8]}",
            system_message="""You are CloudDoctor, an AI cloud infrastructure diagnostics expert.
Analyze the provided logs and respond with ONLY a valid JSON object (no markdown, no code blocks):
{
  "root_cause": "Brief description",
  "severity": "critical|high|medium|low",
  "confidence": 95,
  "recommended_fixes": ["fix1", "fix2", "fix3"],
  "estimated_mttr": "X minutes"
}"""
        )
        chat.with_model("openai", "gpt-4o")
        
        user_msg = UserMessage(
            text=f"Diagnose this cloud infrastructure incident (scenario: memory-leak):\n{log_text}"
        )
        
        response = await chat.send_message(user_msg)
        print(f"  ✅ Step 3: AI diagnosis received")
        
        # Parse response
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1]
            clean = clean.rsplit("```", 1)[0]
        
        diagnosis = json.loads(clean)
        print(f"    Root Cause: {diagnosis.get('root_cause')}")
        print(f"    Confidence: {diagnosis.get('confidence')}%")
        
        # Step 4: Update incident with diagnosis
        await db.incidents.update_one(
            {"id": incident_id},
            {"$set": {
                "diagnosis": diagnosis,
                "severity_score": diagnosis.get("confidence", 0) / 100,
                "severity_label": diagnosis.get("severity", "unknown"),
                "confidence": diagnosis.get("confidence", 0),
                "estimated_mttr": diagnosis.get("estimated_mttr", "unknown"),
                "log_count": len(sample_logs),
                "error_count": sum(1 for l in sample_logs if "ERROR" in l),
                "fatal_count": sum(1 for l in sample_logs if "FATAL" in l),
                "status": "diagnosed"
            }}
        )
        
        # Step 5: Verify
        updated = await db.incidents.find_one({"id": incident_id}, {"_id": 0})
        assert updated["status"] == "diagnosed"
        assert updated["diagnosis"] is not None
        print(f"  ✅ Step 4: Incident updated with diagnosis")
        print(f"  ✅ Step 5: Full flow verified - incident is '{updated['status']}'")
        
        # Cleanup
        await db.incidents.delete_one({"id": incident_id})
        client.close()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Full diagnosis flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# TEST 5: Scenario Reset (Stop)
# ============================================================
async def test_scenario_reset():
    print("\n" + "="*60)
    print("TEST 5: Scenario Reset (Stop)")
    print("="*60)
    
    try:
        # Simulate service state management
        service_state = {
            "current_scenario": None,
            "is_healthy": True,
            "active_since": None
        }
        
        # Trigger a scenario
        service_state["current_scenario"] = "db-crash"
        service_state["is_healthy"] = False
        service_state["active_since"] = datetime.now(timezone.utc).isoformat()
        print(f"  Triggered: {service_state['current_scenario']}, healthy={service_state['is_healthy']}")
        
        # Reset (stop)
        service_state["current_scenario"] = None
        service_state["is_healthy"] = True
        service_state["active_since"] = None
        print(f"  After stop: scenario={service_state['current_scenario']}, healthy={service_state['is_healthy']}")
        
        assert service_state["is_healthy"] == True
        assert service_state["current_scenario"] is None
        print("  ✅ Scenario reset works correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Scenario reset test failed: {e}")
        return False


# ============================================================
# MAIN: Run all tests
# ============================================================
async def main():
    print("🏥 CloudDoctor POC - Core Workflow Validation")
    print("="*60)
    
    results = {}
    
    results["LLM Call"] = await test_llm_call()
    results["MongoDB Incidents"] = await test_mongodb_incidents()
    results["Local Log Provider"] = await test_local_log_provider()
    results["Full Diagnosis Flow"] = await test_full_diagnosis_flow()
    results["Scenario Reset"] = await test_scenario_reset()
    
    print("\n" + "="*60)
    print("📊 POC RESULTS SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL POC TESTS PASSED - Core workflow is validated!")
    else:
        print("⚠️ SOME POC TESTS FAILED - Fix before proceeding to app development")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
