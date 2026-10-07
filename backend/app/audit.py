"""Security Audit Logging Utility for Spendable.

Logs security-relevant events (authentication, authorization failures, cross-account access attempts,
rate limit breaches, sensitive snapshot queries) without logging passwords, tokens, or raw secrets.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional, Any
import threading

logger = logging.getLogger("spendable.security_audit")
logger.setLevel(logging.INFO)

# In-memory audit store for prototype inspection & unit testing
_audit_log_store: List[Dict[str, Any]] = []
_audit_lock = threading.Lock()


class SecurityAuditLogger:
    """Thread-safe security audit logger."""

    def log_event(
        self,
        event_type: str,
        account_id: Optional[str] = None,
        detail: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record a security audit log event."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "account_id": account_id or "ANONYMOUS",
            "endpoint": endpoint or "N/A",
            "detail": detail or "",
            "ip_address": ip_address or "127.0.0.1",
        }

        # Format structured log message for console / log aggregator
        log_msg = f"[SECURITY AUDIT] event={event_type} account_id={entry['account_id']} endpoint={entry['endpoint']} detail='{entry['detail']}' ip={entry['ip_address']}"
        logger.info(log_msg)

        with _audit_lock:
            _audit_log_store.append(entry)
            # Keep rolling buffer capped at 1000 events
            if len(_audit_log_store) > 1000:
                _audit_log_store.pop(0)

        return entry

    def get_recent_logs(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent audit logs with optional filtering."""
        with _audit_lock:
            logs = list(_audit_log_store)

        if event_type:
            logs = [l for l in logs if l["event_type"] == event_type]
        if account_id:
            logs = [l for l in logs if l["account_id"] == account_id]

        return logs[-limit:]

    def clear_logs(self) -> None:
        """Clear audit logs (used for test teardowns)."""
        with _audit_lock:
            _audit_log_store.clear()


audit_logger = SecurityAuditLogger()
