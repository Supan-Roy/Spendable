from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.domain.enums import TransactionDirection, ActivityType, DataProvenance


class FinancialActivityBase(BaseModel):
    """Base schema containing core financial activity attributes."""
    account_id: str = Field(..., min_length=1, max_length=64, description="Identifier of the observed account/wallet")
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Monetary transaction amount (must be strictly positive)")
    currency: str = Field(default="BDT", min_length=3, max_length=3, description="ISO-4217 3-letter currency code")
    direction: TransactionDirection = Field(..., description="INFLOW or OUTFLOW direction relative to the account")
    activity_type: ActivityType = Field(..., description="Categorical activity classification")
    timestamp_utc: datetime = Field(..., description="Exact UTC execution timestamp")
    
    category: Optional[str] = Field(default=None, max_length=64, description="Optional domain category")
    channel: Optional[str] = Field(default=None, max_length=32, description="Optional channel e.g. APP, AGENT, ATM")
    counterparty_name: Optional[str] = Field(default=None, max_length=128, description="Optional merchant/payee/source name")
    reference_id: Optional[str] = Field(default=None, max_length=128, description="Optional external transaction reference ID")
    balance_after: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"), description="Directly observed post-transaction balance")
    provenance: DataProvenance = Field(default=DataProvenance.SYNTHETIC, description="Data origin provenance")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if len(v_upper) != 3 or not v_upper.isalpha():
            raise ValueError("Currency must be a valid 3-letter alphabetic ISO code")
        return v_upper

    @field_validator("amount", "balance_after", mode="before")
    @classmethod
    def round_monetary_decimal(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is None:
            return None
        dec_v = Decimal(str(v))
        return dec_v.quantize(Decimal("0.01"))

    @field_validator("timestamp_utc")
    @classmethod
    def ensure_utc_timestamp(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class FinancialActivityCreate(FinancialActivityBase):
    """Schema for ingesting/creating a new observed financial activity."""
    pass


class FinancialActivityResponse(FinancialActivityBase):
    """Schema for returning a recorded financial activity."""
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
