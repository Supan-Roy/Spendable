"""Abstract Base Transaction Ingestion Adapter Interface."""

from abc import ABC, abstractmethod
import hashlib
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.ingestion.schema import IngestionResult, CanonicalTransaction


class BaseIngestionAdapter(ABC):
    """Abstract Base Class for provider-neutral transaction ingestion adapters."""

    def __init__(self, adapter_name: str):
        self.adapter_name = adapter_name

    @abstractmethod
    def ingest_records(
        self, raw_data: Any, target_account_id: str, db: Session
    ) -> IngestionResult:
        """Parse, validate, deduplicate, and persist transaction records."""
        pass

    @staticmethod
    def generate_idempotency_hash(
        account_id: str,
        reference_id: Optional[str],
        amount: float,
        timestamp_str: str,
        direction_str: str,
    ) -> str:
        """Generate SHA-256 idempotency hash for transaction deduplication."""
        raw_key = f"{account_id}:{reference_id or 'NO_REF'}:{amount:.2f}:{timestamp_str}:{direction_str.upper()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
