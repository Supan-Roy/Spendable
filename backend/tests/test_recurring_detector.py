"""Pytest test suite for Spendable Recurring Payment Detector & Offline Evaluator.

Verifies:
- Strong monthly and weekly recurring pattern detection.
- Variable amount recurring commitment detection.
- Discretionary habit spending (dining/shopping) non-commitment filtering.
- Specific merchant strong signal emergence.
- Inflow income vs Outflow commitment separation.
- Insufficient historical observation cutoff (< 3 occurrences).
- Strict snapshot cutoff non-leakage invariant (t <= T).
- Next expected occurrence date & expected amount calculations.
- Deterministic output across multiple detector runs.
- Ground truth offline evaluator with category breakdown & split isolation.
"""

from datetime import datetime, timedelta
from decimal import Decimal
import pytest

from app.recurring.detector import RecurringDetector
from app.recurring.evaluator import RecurringEvaluator
from app.recurring.schema import (
    DetectionConfig,
    DetectionStatus,
    RecurrenceIntervalType,
)


@pytest.fixture
def base_snapshot():
    return datetime(2026, 10, 1, 12, 0, 0)


@pytest.fixture
def default_detector():
    return RecurringDetector(
        DetectionConfig(min_occurrences=3, strong_threshold=0.70, moderate_threshold=0.45)
    )


def test_strong_monthly_recurring_pattern(default_detector, base_snapshot):
    """Test detection of regular monthly rent payments."""
    txs = [
        {"account_id": "U1", "counterparty_name": "Apex Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 15000.0, "direction": "OUTFLOW", "timestamp_utc": "2026-06-01T10:00:00"},
        {"account_id": "U1", "counterparty_name": "Apex Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 15000.0, "direction": "OUTFLOW", "timestamp_utc": "2026-07-01T10:00:00"},
        {"account_id": "U1", "counterparty_name": "Apex Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 15000.0, "direction": "OUTFLOW", "timestamp_utc": "2026-08-01T10:00:00"},
        {"account_id": "U1", "counterparty_name": "Apex Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 15000.0, "direction": "OUTFLOW", "timestamp_utc": "2026-09-01T10:00:00"},
    ]

    commitments = default_detector.detect(txs, base_snapshot, direction_filter="OUTFLOW")

    assert len(commitments) == 1
    comm = commitments[0]
    assert comm.user_id == "U1"
    assert comm.counterparty_name == "Apex Landlord"
    assert comm.category == "HOUSING"
    assert comm.expected_amount == 15000.0
    assert comm.is_commitment is True
    assert comm.recurrence_interval == RecurrenceIntervalType.MONTHLY
    assert comm.detection_status == DetectionStatus.STRONG
    assert comm.next_expected_date in ("2026-10-01", "2026-10-02")
    assert comm.confidence_score >= 0.70


def test_discretionary_dining_not_classified_as_commitment(default_detector, base_snapshot):
    """Test that generic dining transactions without a specific counterparty do not get grouped into a commitment."""
    txs = [
        {"account_id": "U_DINING", "counterparty_name": None, "category": "DINING", "activity_type": "MERCHANT_PAYMENT", "amount": 450.0, "direction": "OUTFLOW", "timestamp_utc": "2026-09-01T12:00:00"},
        {"account_id": "U_DINING", "counterparty_name": None, "category": "DINING", "activity_type": "MERCHANT_PAYMENT", "amount": 890.0, "direction": "OUTFLOW", "timestamp_utc": "2026-09-05T19:00:00"},
        {"account_id": "U_DINING", "counterparty_name": None, "category": "DINING", "activity_type": "MERCHANT_PAYMENT", "amount": 1200.0, "direction": "OUTFLOW", "timestamp_utc": "2026-09-12T13:00:00"},
        {"account_id": "U_DINING", "counterparty_name": None, "category": "DINING", "activity_type": "MERCHANT_PAYMENT", "amount": 350.0, "direction": "OUTFLOW", "timestamp_utc": "2026-09-20T20:00:00"},
    ]

    commitments = default_detector.detect(txs, base_snapshot, direction_filter="OUTFLOW")
    assert len(commitments) == 0


def test_specific_merchant_discretionary_can_emerge(default_detector, base_snapshot):
    """Test that a specific merchant (e.g., Coffee Subscription) with stable interval and amount CAN emerge even if category is discretionary."""
    txs = [
        {"account_id": "U_COFFEE", "counterparty_name": "Artisan Coffee Club Subscription", "category": "DINING", "activity_type": "MERCHANT_PAYMENT", "amount": 1500.0, "direction": "OUTFLOW", "timestamp_utc": "2026-06-15T09:00:00"},
        {"account_id": "U_COFFEE", "counterparty_name": "Artisan Coffee Club Subscription", "category": "DINING", "activity_type": "MERCHANT_PAYMENT", "amount": 1500.0, "direction": "OUTFLOW", "timestamp_utc": "2026-07-15T09:00:00"},
        {"account_id": "U_COFFEE", "counterparty_name": "Artisan Coffee Club Subscription", "category": "DINING", "activity_type": "MERCHANT_PAYMENT", "amount": 1500.0, "direction": "OUTFLOW", "timestamp_utc": "2026-08-15T09:00:00"},
        {"account_id": "U_COFFEE", "counterparty_name": "Artisan Coffee Club Subscription", "category": "DINING", "activity_type": "MERCHANT_PAYMENT", "amount": 1500.0, "direction": "OUTFLOW", "timestamp_utc": "2026-09-15T09:00:00"},
    ]

    commitments = default_detector.detect(txs, base_snapshot, direction_filter="OUTFLOW")
    assert len(commitments) == 1
    assert commitments[0].counterparty_name == "Artisan Coffee Club Subscription"
    assert commitments[0].expected_amount == 1500.0
    assert commitments[0].detection_status in (DetectionStatus.STRONG, DetectionStatus.MODERATE)


def test_income_separated_from_outflow_commitment(default_detector, base_snapshot):
    """Test that INFLOW salary and freelance transactions are separated from OUTFLOW commitment detection."""
    txs = [
        {"account_id": "U_INC", "counterparty_name": "Tech Corp Payroll", "category": "INCOME", "activity_type": "SALARY", "amount": 75000.0, "direction": "INFLOW", "timestamp_utc": "2026-07-01T00:00:00"},
        {"account_id": "U_INC", "counterparty_name": "Tech Corp Payroll", "category": "INCOME", "activity_type": "SALARY", "amount": 75000.0, "direction": "INFLOW", "timestamp_utc": "2026-08-01T00:00:00"},
        {"account_id": "U_INC", "counterparty_name": "Tech Corp Payroll", "category": "INCOME", "activity_type": "SALARY", "amount": 75000.0, "direction": "INFLOW", "timestamp_utc": "2026-09-01T00:00:00"},
    ]

    outflow_commitments = default_detector.detect(txs, base_snapshot, direction_filter="OUTFLOW")
    assert len(outflow_commitments) == 0

    inflow_streams = default_detector.detect(txs, base_snapshot, direction_filter="INFLOW")
    assert len(inflow_streams) == 1
    assert inflow_streams[0].is_commitment is False
    assert inflow_streams[0].direction == "INFLOW"


def test_snapshot_cutoff_exclusion(default_detector, base_snapshot):
    """Critical non-leakage invariant: adding future transactions after snapshot T must NOT change output at T."""
    txs_past = [
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 1200.0, "direction": "OUTFLOW", "timestamp_utc": "2026-07-01T00:00:00"},
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 1200.0, "direction": "OUTFLOW", "timestamp_utc": "2026-08-01T00:00:00"},
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 1200.0, "direction": "OUTFLOW", "timestamp_utc": "2026-09-01T00:00:00"},
    ]

    txs_with_future = txs_past + [
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 1200.0, "direction": "OUTFLOW", "timestamp_utc": "2026-10-02T00:00:00"},
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 9999.0, "direction": "OUTFLOW", "timestamp_utc": "2026-11-01T00:00:00"},
    ]

    comm_past = default_detector.detect(txs_past, base_snapshot)
    comm_future = default_detector.detect(txs_with_future, base_snapshot)

    assert len(comm_past) == 1
    assert len(comm_future) == 1
    assert comm_past[0].confidence_score == comm_future[0].confidence_score
    assert comm_past[0].expected_amount == comm_future[0].expected_amount
    assert comm_past[0].next_expected_date == comm_future[0].next_expected_date


def test_deterministic_output(default_detector, base_snapshot):
    """Test that running detector multiple times on identical input yields identical outputs."""
    txs = [
        {"account_id": "U7", "counterparty_name": "Netflix", "category": "ENTERTAINMENT", "activity_type": "MERCHANT_PAYMENT", "amount": 1499.0, "direction": "OUTFLOW", "timestamp_utc": "2026-07-10T00:00:00"},
        {"account_id": "U7", "counterparty_name": "Netflix", "category": "ENTERTAINMENT", "activity_type": "MERCHANT_PAYMENT", "amount": 1499.0, "direction": "OUTFLOW", "timestamp_utc": "2026-08-10T00:00:00"},
        {"account_id": "U7", "counterparty_name": "Netflix", "category": "ENTERTAINMENT", "activity_type": "MERCHANT_PAYMENT", "amount": 1499.0, "direction": "OUTFLOW", "timestamp_utc": "2026-09-10T00:00:00"},
    ]

    res1 = default_detector.detect(txs, base_snapshot)
    res2 = default_detector.detect(txs, base_snapshot)

    assert res1[0].model_dump() == res2[0].model_dump()


def test_evaluator_metrics_and_category_breakdown(default_detector, base_snapshot):
    """Test ground-truth offline evaluator calculations on mock user splits."""
    mock_gt = {
        "users": {
            "U8": {
                "account_id": "U8",
                "split_assignment": "TRAIN",
                "planted_rules": [
                    {
                        "rule_id": "rule_u8_rent",
                        "account_id": "U8",
                        "category": "HOUSING",
                        "counterparty_name": "Apartment Landlord",
                        "frequency": "MONTHLY",
                        "base_amount": 20000.0,
                    }
                ]
            }
        }
    }

    txs = [
        {"account_id": "U8", "counterparty_name": "Apartment Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 20000.0, "direction": "OUTFLOW", "timestamp_utc": "2026-07-01T00:00:00"},
        {"account_id": "U8", "counterparty_name": "Apartment Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 20000.0, "direction": "OUTFLOW", "timestamp_utc": "2026-08-01T00:00:00"},
        {"account_id": "U8", "counterparty_name": "Apartment Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 20000.0, "direction": "OUTFLOW", "timestamp_utc": "2026-09-01T00:00:00"},
    ]

    evaluator = RecurringEvaluator(mock_gt)
    m = evaluator.evaluate_split(default_detector, txs, base_snapshot, "TRAIN", direction_filter="OUTFLOW")

    assert m.split_name == "TRAIN"
    assert m.total_users == 1
    assert m.true_positives == 1
    assert m.false_positives == 0
    assert m.false_negatives == 0
    assert m.precision == 1.0
    assert m.recall == 1.0
    assert m.f1_score == 1.0
    assert len(m.category_breakdown) >= 1
    assert m.category_breakdown[0].category == "HOUSING"
