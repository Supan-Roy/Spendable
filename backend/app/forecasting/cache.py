"""Thread-Safe Revision-Aware ML Forecast Caching Layer for Spendable.

Caches deterministic forecast outputs for unchanged account snapshots using account identity,
transaction data revision hash, and model version. Ensures strict thread safety and cross-account isolation.
"""

from datetime import datetime, timezone
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
import threading

from app.forecasting.schema import ForecastOutput

logger = logging.getLogger("spendable.forecast_cache")


class ThreadSafeForecastCache:
    """Thread-safe, revision-aware in-memory cache for ML forecast outputs."""

    def __init__(self, default_ttl_seconds: float = 300.0):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl_seconds
        
        # Performance metrics
        self.hits = 0
        self.misses = 0
        self.invalidations = 0

    def make_cache_key(self, account_id: str, data_revision: str, model_version: str) -> str:
        """Construct scoped, account-isolated cache key."""
        clean_acc = str(account_id).strip().lower()
        clean_rev = str(data_revision).strip()
        clean_ver = str(model_version).strip()
        return f"forecast:{clean_acc}:{clean_rev}:{clean_ver}"

    def get(self, account_id: str, data_revision: str, model_version: str) -> Optional[ForecastOutput]:
        """Retrieve cached ForecastOutput if hit and valid, else None."""
        key = self.make_cache_key(account_id, data_revision, model_version)
        now_ts = datetime.now(timezone.utc).timestamp()

        with self._lock:
            entry = self._cache.get(key)
            if entry:
                if now_ts - entry["created_at"] <= self.default_ttl:
                    self.hits += 1
                    logger.debug(f"[CACHE HIT] key={key}")
                    return entry["forecast_output"]
                else:
                    # Expired entry
                    self._cache.pop(key, None)

            self.misses += 1
            logger.debug(f"[CACHE MISS] key={key}")
            return None

    def set(self, account_id: str, data_revision: str, model_version: str, forecast: ForecastOutput) -> None:
        """Store ForecastOutput in thread-safe cache."""
        key = self.make_cache_key(account_id, data_revision, model_version)
        now_ts = datetime.now(timezone.utc).timestamp()

        with self._lock:
            self._cache[key] = {
                "created_at": now_ts,
                "account_id": str(account_id).strip().lower(),
                "data_revision": str(data_revision).strip(),
                "model_version": str(model_version).strip(),
                "forecast_output": forecast,
            }
            logger.debug(f"[CACHE SET] key={key}")

    def invalidate(self, account_id: Optional[str] = None) -> int:
        """Invalidate cache entries for a specific account or all accounts."""
        count = 0
        with self._lock:
            if account_id:
                clean_acc = str(account_id).strip().lower()
                keys_to_remove = [k for k, v in self._cache.items() if v.get("account_id") == clean_acc]
                for k in keys_to_remove:
                    self._cache.pop(k, None)
                    count += 1
            else:
                count = len(self._cache)
                self._cache.clear()

            self.invalidations += count
            logger.info(f"[CACHE INVALIDATE] account_id={account_id or 'ALL'} removed={count} entries")
        return count

    def get_metrics(self) -> Dict[str, Any]:
        """Retrieve cache efficiency metrics."""
        with self._lock:
            total_queries = self.hits + self.misses
            hit_ratio = (self.hits / total_queries) if total_queries > 0 else 0.0
            return {
                "hits": self.hits,
                "misses": self.misses,
                "total_queries": total_queries,
                "hit_ratio": round(hit_ratio, 4),
                "active_entries": len(self._cache),
                "invalidations": self.invalidations,
            }

    def clear(self) -> None:
        """Clear cache state and reset metrics (for test teardowns)."""
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0
            self.invalidations = 0


# Global singleton forecast cache instance
forecast_cache = ThreadSafeForecastCache()
