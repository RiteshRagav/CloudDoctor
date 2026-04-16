from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class LogEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    level: str = "INFO"
    message: str = ""
    service: str = "unknown"
    scenario: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class IncidentCreate(BaseModel):
    scenario: str


class DiagnosisResult(BaseModel):
    root_cause: str = ""
    severity: str = "unknown"
    confidence: int = 0
    recommended_fixes: List[str] = []
    estimated_mttr: str = "unknown"


class Incident(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    service: str = "sample-app"
    anomaly_type: str = ""
    severity_score: float = 0.0
    severity_label: str = "unknown"
    status: str = "open"  # open, diagnosed, resolved
    confidence: int = 0
    estimated_mttr: str = "unknown"
    diagnosis: Optional[DiagnosisResult] = None
    log_count: int = 0
    error_count: int = 0
    fatal_count: int = 0
    resolved_at: Optional[str] = None


class HealthStatus(BaseModel):
    betterstack: Dict[str, Any] = {"status": "not_configured", "message": "No tokens configured"}
    mongodb: Dict[str, Any] = {"status": "unknown", "message": ""}
    llm: Dict[str, Any] = {"status": "unknown", "message": ""}
    sample_app: Dict[str, Any] = {"status": "unknown", "message": ""}
