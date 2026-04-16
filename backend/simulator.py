import asyncio
import random
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List
from models import LogEvent
from log_provider import log_provider
import uuid

logger = logging.getLogger(__name__)

# Available failure scenarios
SCENARIOS = {
    "db-crash": {
        "service": "database-service",
        "description": "Simulates DB connection pool exhaustion",
        "logs": [
            {"level": "WARN", "message": "Database connection pool utilization at 85%"},
            {"level": "ERROR", "message": "Database connection pool exhausted (0/{max_conn} connections available)"},
            {"level": "ERROR", "message": "Failed to acquire DB connection: pool timeout after {timeout}ms"},
            {"level": "WARN", "message": "Request queue depth: {queue_depth} (threshold: 100)"},
            {"level": "ERROR", "message": "Transaction rollback: connection reset by peer"},
            {"level": "FATAL", "message": "Service health check failed: database unreachable"},
            {"level": "ERROR", "message": "Circuit breaker OPEN for database-service after {failures} consecutive failures"},
            {"level": "WARN", "message": "Retry attempt {attempt}/3 for database connection"},
        ],
    },
    "memory-leak": {
        "service": "compute-service",
        "description": "Simulates OOMKilled pod (memory overflow)",
        "logs": [
            {"level": "WARN", "message": "Memory usage at {mem_pct}% (threshold: 80%)"},
            {"level": "WARN", "message": "GC pause time: {gc_ms}ms (threshold: 1000ms)"},
            {"level": "ERROR", "message": "Memory allocation failed: requested {alloc_mb}MB, available {avail_mb}MB"},
            {"level": "ERROR", "message": "OOMKilled: container exceeded memory limit {limit}"},
            {"level": "FATAL", "message": "Pod restart count: {restarts} (threshold: 3)"},
            {"level": "ERROR", "message": "Heap dump generated: /tmp/heapdump-{timestamp}.hprof"},
            {"level": "WARN", "message": "Memory fragmentation detected: {frag_pct}% fragmented"},
        ],
    },
    "high-latency": {
        "service": "api-gateway",
        "description": "Simulates SLA breach (latency > 3000ms)",
        "logs": [
            {"level": "WARN", "message": "Response time: {latency}ms (SLA: 500ms)"},
            {"level": "WARN", "message": "Upstream service response time degraded: {upstream_ms}ms"},
            {"level": "ERROR", "message": "SLA breach: P99 latency {p99}ms exceeds threshold 3000ms"},
            {"level": "WARN", "message": "Connection pool saturation: {pool_pct}% utilized"},
            {"level": "ERROR", "message": "Request timeout after {timeout}ms for /api/data endpoint"},
            {"level": "WARN", "message": "Load balancer health check degraded: response time {lb_ms}ms"},
            {"level": "ERROR", "message": "Circuit breaker HALF-OPEN: testing downstream availability"},
        ],
    },
    "crash": {
        "service": "worker-service",
        "description": "Simulates NullPointerException + pod restart",
        "logs": [
            {"level": "ERROR", "message": "NullPointerException in WorkerThread-{thread_id}: cannot invoke method on null reference"},
            {"level": "FATAL", "message": "Unhandled exception caught by global error handler"},
            {"level": "ERROR", "message": "Stack trace: com.app.worker.ProcessTask.execute(ProcessTask.java:{line})"},
            {"level": "WARN", "message": "Graceful shutdown initiated, draining {pending} pending tasks"},
            {"level": "ERROR", "message": "Pod CrashLoopBackOff detected, restart count: {restarts}"},
            {"level": "FATAL", "message": "Container terminated with exit code 137 (SIGKILL)"},
            {"level": "INFO", "message": "Pod restarting... attempt {attempt}/5"},
        ],
    },
}


def _fill_template(msg: str) -> str:
    """Fill log message templates with realistic random values."""
    replacements = {
        "{max_conn}": str(random.choice([50, 100, 200])),
        "{timeout}": str(random.randint(3000, 10000)),
        "{queue_depth}": str(random.randint(150, 500)),
        "{failures}": str(random.randint(3, 10)),
        "{attempt}": str(random.randint(1, 3)),
        "{mem_pct}": str(random.randint(85, 99)),
        "{gc_ms}": str(random.randint(2000, 8000)),
        "{alloc_mb}": str(random.randint(256, 1024)),
        "{avail_mb}": str(random.randint(10, 64)),
        "{limit}": random.choice(["2Gi", "4Gi", "8Gi"]),
        "{restarts}": str(random.randint(3, 8)),
        "{timestamp}": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "{frag_pct}": str(random.randint(40, 85)),
        "{latency}": str(random.randint(3000, 15000)),
        "{upstream_ms}": str(random.randint(2000, 8000)),
        "{p99}": str(random.randint(3500, 12000)),
        "{pool_pct}": str(random.randint(80, 99)),
        "{lb_ms}": str(random.randint(1500, 5000)),
        "{thread_id}": str(random.randint(1, 16)),
        "{line}": str(random.randint(42, 387)),
        "{pending}": str(random.randint(10, 200)),
    }
    for key, val in replacements.items():
        msg = msg.replace(key, val)
    return msg


class FailureSimulator:
    """Manages simulated failure scenarios and background log emission."""

    def __init__(self):
        self.current_scenario: Optional[str] = None
        self.is_healthy: bool = True
        self.active_since: Optional[str] = None
        self._task: Optional[asyncio.Task] = None
        self._running: bool = False

    @property
    def state(self) -> Dict:
        return {
            "current_scenario": self.current_scenario,
            "is_healthy": self.is_healthy,
            "active_since": self.active_since,
            "description": SCENARIOS.get(self.current_scenario, {}).get("description", "System healthy") if self.current_scenario else "All systems operational",
        }

    def trigger(self, scenario: str) -> Dict:
        if scenario not in SCENARIOS:
            return {"error": f"Unknown scenario: {scenario}", "available": list(SCENARIOS.keys())}

        # Stop any existing scenario
        self.stop()

        self.current_scenario = scenario
        self.is_healthy = False
        self.active_since = datetime.now(timezone.utc).isoformat()

        # Emit initial burst of logs
        scenario_data = SCENARIOS[scenario]
        for log_template in scenario_data["logs"]:
            log_event = LogEvent(
                level=log_template["level"],
                message=_fill_template(log_template["message"]),
                service=scenario_data["service"],
                scenario=scenario,
            )
            log_provider.append(log_event)

        # Start background log emission
        self._running = True
        self._task = asyncio.create_task(self._emit_logs_background(scenario))

        logger.info(f"Triggered scenario: {scenario}")
        return self.state

    def stop(self) -> Dict:
        """Reset to healthy state."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None

        prev_scenario = self.current_scenario
        self.current_scenario = None
        self.is_healthy = True
        self.active_since = None

        # Emit recovery logs
        if prev_scenario:
            recovery_logs = [
                LogEvent(level="INFO", message=f"Scenario '{prev_scenario}' stopped. System recovering.", service="system", scenario=prev_scenario),
                LogEvent(level="INFO", message="All health checks passing. System operational.", service="system"),
            ]
            for log in recovery_logs:
                log_provider.append(log)

        logger.info(f"Stopped scenario: {prev_scenario}")
        return self.state

    async def _emit_logs_background(self, scenario: str):
        """Emit logs periodically while scenario is active."""
        scenario_data = SCENARIOS.get(scenario)
        if not scenario_data:
            return

        try:
            while self._running:
                await asyncio.sleep(random.uniform(2, 5))
                if not self._running:
                    break

                # Pick random log from scenario
                log_template = random.choice(scenario_data["logs"])
                log_event = LogEvent(
                    level=log_template["level"],
                    message=_fill_template(log_template["message"]),
                    service=scenario_data["service"],
                    scenario=scenario,
                )
                log_provider.append(log_event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Background log emission error: {e}")


# Singleton
simulator = FailureSimulator()
