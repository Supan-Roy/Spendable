"""Spendable Provider-Neutral Transaction Ingestion Architecture Module."""

from app.ingestion.schema import CanonicalTransaction, IngestionResult
from app.ingestion.base import BaseIngestionAdapter
from app.ingestion.csv_adapter import CSVTransactionAdapter

__all__ = [
    "CanonicalTransaction",
    "IngestionResult",
    "BaseIngestionAdapter",
    "CSVTransactionAdapter",
]
