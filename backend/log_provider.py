from collections import deque
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict
from models import LogEvent
import threading
import logging

logger = logging.getLogger(__name__)


class LocalLogProvider:
    """In-memory ring buffer log provider with thread safety."""

    def __init__(self, max_size: int = 10000):
        self.logs: deque = deque(maxlen=max_size)
        self._lock = threading.Lock()

    def append(self, log_event: LogEvent):
        with self._lock:
            self.logs.append(log_event.model_dump())

    def query(
        self,
        levels: Optional[List[str]] = None,
        since: Optional[str] = None,
        limit: int = 200,
        scenario: Optional[str] = None,
    ) -> List[dict]:
        with self._lock:
            results = []
            for log in reversed(self.logs):
                if levels and log.get("level") not in levels:
                    continue
                if since and log.get("timestamp", "") < since:
                    continue
                if scenario and log.get("scenario") != scenario:
                    continue
                results.append(log)
                if len(results) >= limit:
                    break
            return results

    def stats(self, since: Optional[str] = None) -> Dict[str, int]:
        with self._lock:
            counts = {"DEBUG": 0, "INFO": 0, "WARN": 0, "ERROR": 0, "FATAL": 0}
            for log in self.logs:
                if since and log.get("timestamp", "") < since:
                    continue
                level = log.get("level", "INFO")
                if level in counts:
                    counts[level] += 1
            return counts

    def clear(self):
        with self._lock:
            self.logs.clear()

    def count(self) -> int:
        with self._lock:
            return len(self.logs)


# Singleton instance
log_provider = LocalLogProvider(max_size=10000)
