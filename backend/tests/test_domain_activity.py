from datetime import datetime, timezone
from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.domain.enums import TransactionDirection, ActivityType, DataProvenance
from app.schemas.activity import FinancialActivityCreate, FinancialActivityResponse


def test_valid_financial_activity_schema():
    """Test creating a valid financial activity schema instance."""
    now_utc = datetime.now(timezone.utc)
    payload = FinancialActivityCreate(
        account_id="acc_usr_99182",
        amount=Decimal("2500.00"),
        currency="bdt",  # lowercase should normalize to BDT uppercase
        direction=TransactionDirection.OUTFLOW,
        activity_type=ActivityType.UTILITY_BILL,
        timestamp_utc=now_utc,
        category="UTILITIES",
        channel="MFS_APP",
        counterparty_name="Dhaka Electric Supply",
        reference_id="DESCO_881920",
        balance_after=Decimal("15900.50"),
        provenance=DataProvenance.SYNTHETIC
    )

    assert payload.account_id == "acc_usr_99182"
    assert payload.amount == Decimal("2500.00")
    assert payload.currency == "BDT"  # Normalized
    assert payload.direction == TransactionDirection.OUTFLOW
    assert payload.activity_type == ActivityType.UTILITY_BILL
    assert payload.timestamp_utc == now_utc
    assert payload.balance_after == Decimal("15900.50")


def test_invalid_negative_amount_rejected():
    """Test that zero or negative amounts are strictly rejected by validation."""
    now_utc = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        FinancialActivityCreate(
            account_id="acc_123",
            amount=Decimal("-100.00"),
            currency="BDT",
            direction=TransactionDirection.OUTFLOW,
            activity_type=ActivityType.OTHER,
            timestamp_utc=now_utc
        )

    with pytest.raises(ValidationError):
        FinancialActivityCreate(
            account_id="acc_123",
            amount=Decimal("0.00"),
            currency="BDT",
            direction=TransactionDirection.OUTFLOW,
            activity_type=ActivityType.OTHER,
            timestamp_utc=now_utc
        )


def test_invalid_currency_code_rejected():
    """Test that non-standard currency codes are rejected."""
    now_utc = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        FinancialActivityCreate(
            account_id="acc_123",
            amount=Decimal("500.00"),
            currency="INVALID_CURRENCY",
            direction=TransactionDirection.INFLOW,
            activity_type=ActivityType.CASH_IN,
            timestamp_utc=now_utc
        )


def test_monetary_decimal_precision():
    """Test that monetary amounts are strictly rounded to 2 decimal places without float loss."""
    now_utc = datetime.now(timezone.utc)
    payload = FinancialActivityCreate(
        account_id="acc_123",
        amount=Decimal("123.4567"),  # Should round to 123.46
        currency="BDT",
        direction=TransactionDirection.INFLOW,
        activity_type=ActivityType.SALARY,
        timestamp_utc=now_utc
    )
    assert payload.amount == Decimal("123.46")


def test_naive_timestamp_normalized_to_utc():
    """Test that naive datetimes are automatically assumed and converted to UTC."""
    naive_dt = datetime(2026, 10, 2, 14, 30, 0)
    payload = FinancialActivityCreate(
        account_id="acc_123",
        amount=Decimal("50.00"),
        currency="BDT",
        direction=TransactionDirection.OUTFLOW,
        activity_type=ActivityType.MOBILE_RECHARGE,
        timestamp_utc=naive_dt
    )
    assert payload.timestamp_utc.tzinfo == timezone.utc
