"""Canonical Normalized Transaction Schema & Ingestion Result Models."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from app.domain.enums import TransactionDirection, ActivityType, DataProvenance


class CanonicalTransaction(BaseModel):
    """Normalized, provider-neutral financial transaction payload."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    transaction_id: str = Field(..., description="Unique canonical transaction identifier")
    account_id: str = Field(..., description="Target account identifier")
    amount: float = Field(..., gt=0.0, description="Transaction monetary amount in BDT")
    currency: str = Field("BDT", description="Currency ISO code")
    direction: TransactionDirection = Field(..., description="INFLOW or OUTFLOW")
    activity_type: ActivityType = Field(ActivityType.MERCHANT_PAYMENT, description="Activity classification")
    timestamp_utc: datetime = Field(..., description="Transaction execution timestamp UTC")
    category: str = Field("MISCELLANEOUS", description="Category tag")
    channel: str = Field("DIGITAL", description="Payment channel tag (POS, MFS_UPAY, BANK_BEFTN)")
    counterparty_name: str = Field("Unknown Counterparty", description="Counterparty entity name")
    reference_id: Optional[str] = Field(None, description="External provider transaction reference ID")
    balance_after: Optional[float] = Field(None, description="Observed account balance after transaction execution")
    provenance: DataProvenance = Field(DataProvenance.SYNTHETIC, description="Provenance source classification")


class IngestionResult(BaseModel):
    """Structured result returned by transaction ingestion adapters."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    adapter_name: str = Field(..., description="Name of the ingestion adapter used")
    account_id: str = Field(..., description="Target user account identifier")
    total_records: int = Field(0, description="Total input records processed")
    records_ingested: int = Field(0, description="Successfully normalized and persisted records")
    duplicates_skipped: int = Field(0, description="Identified duplicate records skipped by idempotency hash")
    invalid_records: int = Field(0, description="Malformed records rejected during validation")
    errors: List[str] = Field(default_factory=list, description="Validation or ingestion error messages")
    ingested_transactions: List[CanonicalTransaction] = Field(default_factory=list, description="List of normalized ingested transactions")
