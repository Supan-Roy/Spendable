"""Pytest test suite for Spendable Recurring Payment Detector & Offline Evaluator.

Verifies:
- Strong monthly and weekly recurring pattern detection.
- Variable amount recurring commitment detection.
- Filtering of irregular/non-recurring transaction noise.
- Insufficient historical observation cutoff (< 3 occurrences).
- Strict snapshot cutoff non-leakage invariant (t <= T).
- Next expected occurrence date & expected amount calculations.
- Deterministic output across multiple detector runs.
- Ground truth offline evaluation metrics matching & split isolation.
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
        {"account_id": "U1", "counterparty_name": "Apex Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 15000.0, "timestamp_utc": "2026-06-01T10:00:00"},
        {"account_id": "U1", "counterparty_name": "Apex Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 15000.0, "timestamp_utc": "2026-07-01T10:00:00"},
        {"account_id": "U1", "counterparty_name": "Apex Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 15000.0, "timestamp_utc": "2026-08-01T10:00:00"},
        {"account_id": "U1", "counterparty_name": "Apex Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 15000.0, "timestamp_utc": "2026-09-01T10:00:00"},
    ]

    commitments = default_detector.detect(txs, base_snapshot)

    assert len(commitments) == 1
    comm = commitments[0]
    assert comm.user_id == "U1"
    assert comm.counterparty_name == "Apex Landlord"
    assert comm.category == "HOUSING"
    assert comm.expected_amount == 15000.0
    assert comm.recurrence_interval == RecurrenceIntervalType.MONTHLY
    assert comm.detection_status == DetectionStatus.STRONG
    assert comm.next_expected_date in ("2026-10-01", "2026-10-02")
    assert comm.confidence_score >= 0.70


def test_strong_weekly_recurring_pattern(default_detector, base_snapshot):
    """Test detection of regular weekly payments."""
    txs = [
        {"account_id": "U2", "counterparty_name": "Weekly Maid Service", "category": "SERVICES", "activity_type": "MERCHANT_PAYMENT", "amount": 1200.0, "timestamp_utc": "2026-09-01T10:00:00"},
        {"account_id": "U2", "counterparty_name": "Weekly Maid Service", "category": "SERVICES", "activity_type": "MERCHANT_PAYMENT", "amount": 1200.0, "timestamp_utc": "2026-09-08T10:00:00"},
        {"account_id": "U2", "counterparty_name": "Weekly Maid Service", "category": "SERVICES", "activity_type": "MERCHANT_PAYMENT", "amount": 1200.0, "timestamp_utc": "2026-09-15T10:00:00"},
        {"account_id": "U2", "counterparty_name": "Weekly Maid Service", "category": "SERVICES", "activity_type": "MERCHANT_PAYMENT", "amount": 1200.0, "timestamp_utc": "2026-09-22T10:00:00"},
        {"account_id": "U2", "counterparty_name": "Weekly Maid Service", "category": "SERVICES", "activity_type": "MERCHANT_PAYMENT", "amount": 1200.0, "timestamp_utc": "2026-09-29T10:00:00"},
    ]

    commitments = default_detector.detect(txs, base_snapshot)

    assert len(commitments) == 1
    comm = commitments[0]
    assert comm.recurrence_interval == RecurrenceIntervalType.WEEKLY
    assert comm.occurrence_count == 5
    assert comm.detection_status in (DetectionStatus.STRONG, DetectionStatus.MODERATE)


def test_variable_amount_recurring_pattern(default_detector, base_snapshot):
    """Test recurring payment with minor amount variations (e.g. electric utility bill)."""
    txs = [
        {"account_id": "U3", "counterparty_name": "Dhaka Power Electricity", "category": "UTILITIES", "activity_type": "UTILITY_BILL", "amount": 3450.0, "timestamp_utc": "2026-06-05T00:00:00"},
        {"account_id": "U3", "counterparty_name": "Dhaka Power Electricity", "category": "UTILITIES", "activity_type": "UTILITY_BILL", "amount": 3610.0, "timestamp_utc": "2026-07-05T00:00:00"},
        {"account_id": "U3", "counterparty_name": "Dhaka Power Electricity", "category": "UTILITIES", "activity_type": "UTILITY_BILL", "amount": 3390.0, "timestamp_utc": "2026-08-05T00:00:00"},
        {"account_id": "U3", "counterparty_name": "Dhaka Power Electricity", "category": "UTILITIES", "activity_type": "UTILITY_BILL", "amount": 3520.0, "timestamp_utc": "2026-09-05T00:00:00"},
    ]

    commitments = default_detector.detect(txs, base_snapshot)

    assert len(commitments) == 1
    comm = commitments[0]
    assert comm.category == "UTILITIES"
    assert comm.recurrence_interval == RecurrenceIntervalType.MONTHLY
    assert 3300.0 <= comm.expected_amount <= 3700.0
    assert comm.detection_status in (DetectionStatus.STRONG, DetectionStatus.MODERATE)


def test_irregular_non_recurring_pattern(default_detector, base_snapshot):
    """Test that highly irregular random purchases do not get classified as STRONG recurring commitments."""
    txs = [
        {"account_id": "U4", "counterparty_name": "Random Gift Shop", "category": "SHOPPING", "activity_type": "MERCHANT_PAYMENT", "amount": 500.0, "timestamp_utc": "2026-01-10T00:00:00"},
        {"account_id": "U4", "counterparty_name": "Random Gift Shop", "category": "SHOPPING", "activity_type": "MERCHANT_PAYMENT", "amount": 3500.0, "timestamp_utc": "2026-04-22T00:00:00"},
        {"account_id": "U4", "counterparty_name": "Random Gift Shop", "category": "SHOPPING", "activity_type": "MERCHANT_PAYMENT", "amount": 120.0, "timestamp_utc": "2026-05-02T00:00:00"},
    ]

    commitments = default_detector.detect(txs, base_snapshot)

    assert len(commitments) == 0 or commitments[0].detection_status != DetectionStatus.STRONG


def test_insufficient_history(default_detector, base_snapshot):
    """Test candidate with < min_occurrences is excluded from active detection."""
    txs = [
        {"account_id": "U5", "counterparty_name": "New Gym", "category": "FITNESS", "activity_type": "MERCHANT_PAYMENT", "amount": 2500.0, "timestamp_utc": "2026-08-01T00:00:00"},
        {"account_id": "U5", "counterparty_name": "New Gym", "category": "FITNESS", "activity_type": "MERCHANT_PAYMENT", "amount": 2500.0, "timestamp_utc": "2026-09-01T00:00:00"},
    ]

    commitments = default_detector.detect(txs, base_snapshot, include_insufficient=False)
    assert len(commitments) == 0

    all_candidates = default_detector.detect(txs, base_snapshot, include_insufficient=True)
    assert len(all_candidates) == 1
    assert all_candidates[0].detection_status == DetectionStatus.INSUFFICIENT_EVIDENCE


def test_snapshot_cutoff_exclusion(default_detector, base_snapshot):
    """Critical non-leakage invariant: adding future transactions after snapshot T must NOT change output at T."""
    txs_past = [
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 1200.0, "timestamp_utc": "2026-07-01T00:00:00"},
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 1200.0, "timestamp_utc": "2026-08-01T00:00:00"},
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 1200.0, "timestamp_utc": "2026-09-01T00:00:00"},
    ]

    txs_with_future = txs_past + [
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 1200.0, "timestamp_utc": "2026-10-02T00:00:00"},
        {"account_id": "U6", "counterparty_name": "ISP Broadband", "category": "TELECOM", "activity_type": "UTILITY_BILL", "amount": 9999.0, "timestamp_utc": "2026-11-01T00:00:00"},
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
        {"account_id": "U7", "counterparty_name": "Netflix", "category": "ENTERTAINMENT", "activity_type": "MERCHANT_PAYMENT", "amount": 1499.0, "timestamp_utc": "2026-07-10T00:00:00"},
        {"account_id": "U7", "counterparty_name": "Netflix", "category": "ENTERTAINMENT", "activity_type": "MERCHANT_PAYMENT", "amount": 1499.0, "timestamp_utc": "2026-08-10T00:00:00"},
        {"account_id": "U7", "counterparty_name": "Netflix", "category": "ENTERTAINMENT", "activity_type": "MERCHANT_PAYMENT", "amount": 1499.0, "timestamp_utc": "2026-09-10T00:00:00"},
    ]

    res1 = default_detector.detect(txs, base_snapshot)
    res2 = default_detector.detect(txs, base_snapshot)

    assert res1[0].model_dump() == res2[0].model_dump()


def test_evaluator_metrics_and_split_isolation(default_detector, base_snapshot):
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
        {"account_id": "U8", "counterparty_name": "Apartment Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 20000.0, "timestamp_utc": "2026-07-01T00:00:00"},
        {"account_id": "U8", "counterparty_name": "Apartment Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 20000.0, "timestamp_utc": "2026-08-01T00:00:00"},
        {"account_id": "U8", "counterparty_name": "Apartment Landlord", "category": "HOUSING", "activity_type": "UTILITY_BILL", "amount": 20000.0, "timestamp_utc": "2026-09-01T00:00:00"},
    ]

    evaluator = RecurringEvaluator(mock_gt)
    m = evaluator.evaluate_split(default_detector, txs, base_snapshot, "TRAIN")

    assert m.split_name == "TRAIN"
    assert m.total_users == 1
    assert m.true_positives == 1
    assert m.false_positives == 0
    assert m.false_negatives == 0
    assert m.precision == 1.0
    assert m.recall == 1.0
    assert m.f1_score == 1.0
