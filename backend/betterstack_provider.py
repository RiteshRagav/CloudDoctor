"""
BetterStack Logtail integration — ingestion + source health.
Dual-write: every log goes to the local ring buffer AND to BetterStack.
Query remains local for sub-second latency; BetterStack is long-term storage.
"""
import asyncio
import os
import logging
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collections import deque
import threading

import httpx

logger = logging.getLogger(__name__)

INGEST_URL = "https://in.logs.betterstack.com"
SOURCES_API = "https://telemetry.betterstack.com/api/v1/sources"


class BetterStackProvider:
    """Sends logs to BetterStack Logtail and checks connectivity."""

    def __init__(self):
        self.source_token: str = ""
        self.query_token: str = ""
        self._buffer: deque = deque(maxlen=500)  # batch buffer
        self._lock = threading.Lock()
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False
        self._last_send_ok: bool = False
        self._last_error: str = ""
        self._total_sent: int = 0
        self._total_failed: int = 0
        self._source_name: str = ""
        self._source_id: str = ""

    def load_tokens(self):
        """Load tokens from environment — call after load_dotenv."""
        self.source_token = os.environ.get("BETTERSTACK_SOURCE_TOKEN", "")
        self.query_token = os.environ.get("BETTERSTACK_QUERY_TOKEN", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.source_token)

    @property
    def has_query_token(self) -> bool:
        return bool(self.query_token)

    def enqueue(self, log_event: dict):
        """Add a log event to the batch buffer."""
        if not self.is_configured:
            return
        # Prepare event for BetterStack
        bs_event = {
            "dt": log_event.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "level": log_event.get("level", "INFO"),
            "message": log_event.get("message", ""),
            "service": log_event.get("service", "unknown"),
            "scenario": log_event.get("scenario"),
            "source": "clouddoctor",
            "id": log_event.get("id", ""),
        }
        with self._lock:
            self._buffer.append(bs_event)

    async def flush(self):
        """Send buffered logs to BetterStack."""
        if not self.is_configured:
            return

        with self._lock:
            if not self._buffer:
                return
            batch = list(self._buffer)
            self._buffer.clear()

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    INGEST_URL,
                    json=batch,
                    headers={
                        "Authorization": f"Bearer {self.source_token}",
                        "Content-Type": "application/json",
                    },
                )
                if resp.status_code in (200, 202):
                    self._last_send_ok = True
                    self._last_error = ""
                    self._total_sent += len(batch)
                else:
                    self._last_send_ok = False
                    self._last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
                    self._total_failed += len(batch)
                    logger.warning(f"BetterStack flush failed: {self._last_error}")
        except Exception as e:
            self._last_send_ok = False
            self._last_error = str(e)
            self._total_failed += len(batch)
            logger.error(f"BetterStack flush error: {e}")

    async def start_background_flush(self, interval: float = 3.0):
        """Start periodic flushing of log buffer."""
        self._running = True
        while self._running:
            await asyncio.sleep(interval)
            try:
                await self.flush()
            except Exception as e:
                logger.error(f"BetterStack background flush error: {e}")

    def stop(self):
        self._running = False

    async def check_health(self) -> Dict[str, Any]:
        """Check BetterStack connectivity."""
        if not self.is_configured:
            return {
                "status": "not_configured",
                "message": "BetterStack Source Token not set — using local logs only",
            }

        try:
            # Test ingestion endpoint with a minimal ping
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.post(
                    INGEST_URL,
                    json={"dt": datetime.now(timezone.utc).isoformat(), "message": "health_check", "level": "DEBUG", "source": "clouddoctor"},
                    headers={
                        "Authorization": f"Bearer {self.source_token}",
                        "Content-Type": "application/json",
                    },
                )

            if resp.status_code in (200, 202):
                # Also try to get source info if query token is available
                source_info = ""
                if self.has_query_token:
                    try:
                        async with httpx.AsyncClient(timeout=8) as client:
                            src_resp = await client.get(
                                SOURCES_API,
                                headers={"Authorization": f"Bearer {self.query_token}"},
                            )
                            if src_resp.status_code == 200:
                                sources = src_resp.json().get("data", [])
                                # Find CloudDoctor source
                                for src in sources:
                                    attrs = src.get("attributes", {})
                                    if "cloud" in attrs.get("name", "").lower() or "doctor" in attrs.get("name", "").lower():
                                        self._source_name = attrs.get("name", "")
                                        self._source_id = src.get("id", "")
                                        break
                                if not self._source_name and sources:
                                    # Use last source
                                    attrs = sources[-1].get("attributes", {})
                                    self._source_name = attrs.get("name", "")
                                    self._source_id = sources[-1].get("id", "")
                                source_info = f" · Source: {self._source_name}" if self._source_name else ""
                    except Exception:
                        pass

                return {
                    "status": "connected",
                    "message": f"BetterStack Logtail operational{source_info} · {self._total_sent} logs sent",
                }
            else:
                return {
                    "status": "error",
                    "message": f"BetterStack ingestion error: HTTP {resp.status_code}",
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"BetterStack connection failed: {str(e)}",
            }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "configured": self.is_configured,
            "total_sent": self._total_sent,
            "total_failed": self._total_failed,
            "last_send_ok": self._last_send_ok,
            "last_error": self._last_error,
            "buffer_size": len(self._buffer),
            "source_name": self._source_name,
            "source_id": self._source_id,
        }


# Singleton
betterstack_provider = BetterStackProvider()
