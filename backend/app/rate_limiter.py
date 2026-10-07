"""In-Memory Rate Limiting Dependency for Spendable FastAPI Endpoints.

Provides sliding-window rate limiting per IP / user identifier for auth and high-cost AI endpoints.
Returns HTTP 429 Too Many Requests when rate limits are exceeded.
"""

from datetime import datetime, timezone
from typing import Dict, List, Tuple
import threading
from fastapi import Request, HTTPException, status

from app.audit import audit_logger

_rate_limit_store: Dict[str, List[float]] = {}
_rate_limit_lock = threading.Lock()
_rate_limiting_enabled: bool = True


def set_rate_limiting_enabled(enabled: bool) -> None:
    """Enable or disable rate limiting globally (useful for testing)."""
    global _rate_limiting_enabled
    _rate_limiting_enabled = enabled


def clear_rate_limits() -> None:
    """Reset rate limiting store (useful for test teardown)."""
    with _rate_limit_lock:
        _rate_limit_store.clear()


class RateLimiter:
    """FastAPI Rate Limiting Dependency."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60, name: str = "default"):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.name = name

    def __call__(self, request: Request) -> None:
        if not _rate_limiting_enabled:
            return

        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"{self.name}:{client_ip}"
        now = datetime.now(timezone.utc).timestamp()
        cutoff = now - self.window_seconds

        with _rate_limit_lock:
            timestamps = _rate_limit_store.get(key, [])
            # Filter timestamps outside window
            valid_timestamps = [t for t in timestamps if t > cutoff]

            if len(valid_timestamps) >= self.max_requests:
                audit_logger.log_event(
                    event_type="RATE_LIMIT_EXCEEDED",
                    detail=f"Rate limit exceeded on endpoint {request.url.path} ({len(valid_timestamps)}/{self.max_requests} in {self.window_seconds}s)",
                    ip_address=client_ip,
                    endpoint=request.url.path,
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for endpoint '{self.name}'. Maximum {self.max_requests} requests per {self.window_seconds} seconds.",
                    headers={"Retry-After": str(self.window_seconds)},
                )

            valid_timestamps.append(now)
            _rate_limit_store[key] = valid_timestamps
