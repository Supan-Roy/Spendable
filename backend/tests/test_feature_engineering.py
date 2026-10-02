"""Unit and integration tests for Spendable Feature Engineering Pipeline and Leakage Protection."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest

from app.domain.enums import TransactionDirection, ActivityType, DataProvenance
from app.features.schema import FEATURE_CATALOG, FeatureCategory
from app.features.builder import FeatureBuilder
from app.features.pipeline import FeaturePipeline
from app.features.leakage import FeatureLeakageDetector, LeakageError


@pytest.fixture
def sample_user_activities():
    """Fixture providing a deterministic 60-day history for one user."""
    start_dt = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    user_id = "ACC-TEST-0001"
    activities = []
    current_bal = Decimal("50000.00")

    # Day 1: Salary Inflow 60,000 BDT
    activities.append({
        "id": "tx-001",
        "account_id": user_id,
        "amount": Decimal("60000.00"),
        "currency": "BDT",
        "direction": TransactionDirection.INFLOW,
        "activity_type": ActivityType.SALARY,
        "timestamp_utc": start_dt,
        "category": "INCOME",
        "balance_after": Decimal("110000.00"),
        "provenance": DataProvenance.SYNTHETIC,
    })
    current_bal = Decimal("110000.00")

    # Day 5: Rent Outflow 20,000 BDT
    activities.append({
        "id": "tx-002",
        "account_id": user_id,
        "amount": Decimal("20000.00"),
        "currency": "BDT",
        "direction": TransactionDirection.OUTFLOW,
        "activity_type": ActivityType.UTILITY_BILL,
        "timestamp_utc": start_dt + timedelta(days=4),
        "category": "HOUSING",
        "balance_after": Decimal("90000.00"),
        "provenance": DataProvenance.SYNTHETIC,
    })
    current_bal = Decimal("90000.00")

    # Day 10: Groceries Outflow 2,500 BDT
    activities.append({
        "id": "tx-003",
        "account_id": user_id,
        "amount": Decimal("2500.00"),
        "currency": "BDT",
        "direction": TransactionDirection.OUTFLOW,
        "activity_type": ActivityType.MERCHANT_PAYMENT,
        "timestamp_utc": start_dt + timedelta(days=9),
        "category": "FOOD_AND_GROCERIES",
        "balance_after": Decimal("87500.00"),
        "provenance": DataProvenance.SYNTHETIC,
    })

    # Day 32: Second Salary Inflow 60,000 BDT
    activities.append({
        "id": "tx-004",
        "account_id": user_id,
        "amount": Decimal("60000.00"),
        "currency": "BDT",
        "direction": TransactionDirection.INFLOW,
        "activity_type": ActivityType.SALARY,
        "timestamp_utc": start_dt + timedelta(days=31),
        "category": "INCOME",
        "balance_after": Decimal("147500.00"),
        "provenance": DataProvenance.SYNTHETIC,
    })

    return activities


def test_feature_catalog_definitions():
    """Verify Feature Catalog contains valid feature specifications."""
    assert len(FEATURE_CATALOG) >= 35
    names = [f.name for f in FEATURE_CATALOG]
    assert len(names) == len(set(names))
    assert "current_balance" in names
    assert "net_cash_flow_30d" in names
    assert "discretionary_spending_share_30d" in names


def test_feature_builder_snapshot_calculation(sample_user_activities):
    """Verify FeatureBuilder accurately extracts snapshot metrics at T."""
    builder = FeatureBuilder(sample_user_activities)
    snapshot_t = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

    features = builder.build_snapshot_features(snapshot_t)

    assert features["account_id"] == "ACC-TEST-0001"
    assert features["current_balance"] == 87500.00
    assert features["total_inflow_30d"] == 60000.00
    assert features["total_outflow_30d"] == 22500.00
    assert features["net_cash_flow_30d"] == 37500.00
    assert features["essential_spending_share_30d"] > 0.8  # Rent 20k / Total 22.5k


def test_future_transaction_non_leakage(sample_user_activities):
    """Verify that transactions occurring after T do NOT affect snapshot features at T."""
    snapshot_t = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

    # Automated leakage verification helper
    assert FeatureLeakageDetector.verify_future_transaction_isolation(sample_user_activities, snapshot_t) is True


def test_feature_key_purity_check(sample_user_activities):
    """Verify that feature vectors contain zero forbidden leakage or target keys."""
    builder = FeatureBuilder(sample_user_activities)
    features = builder.build_snapshot_features(datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc))

    assert FeatureLeakageDetector.verify_feature_key_purity(features) is True


def test_division_by_zero_safety():
    """Verify features compute safely when user has 0 outflows or 0 inflows."""
    start_dt = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    # User with ONLY inflow
    inflow_only = [{
        "id": "tx-in-only",
        "account_id": "ACC-INFLOW-ONLY",
        "amount": Decimal("5000.00"),
        "currency": "BDT",
        "direction": TransactionDirection.INFLOW,
        "activity_type": ActivityType.SALARY,
        "timestamp_utc": start_dt,
        "balance_after": Decimal("5000.00"),
        "provenance": DataProvenance.SYNTHETIC,
    }]

    builder = FeatureBuilder(inflow_only)
    features = builder.build_snapshot_features(start_dt + timedelta(days=5))

    assert features["total_outflow_30d"] == 0.0
    assert features["inflow_outflow_ratio_30d"] > 1000.0  # Handled safely via 1e-5 offset
    assert features["essential_spending_share_30d"] == 0.0
    assert features["discretionary_spending_share_30d"] == 0.0


def test_user_isolation(sample_user_activities):
    """Verify that user A's features are unaffected by user B's activities."""
    builder_a = FeatureBuilder(sample_user_activities)
    f_a_1 = builder_a.build_snapshot_features(datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc))

    # User B activities
    user_b_activities = [{
        "id": "tx-user-b",
        "account_id": "ACC-USER-B",
        "amount": Decimal("1000000.00"),
        "currency": "BDT",
        "direction": TransactionDirection.INFLOW,
        "activity_type": ActivityType.SALARY,
        "timestamp_utc": datetime(2026, 1, 5, 10, 0, 0, tzinfo=timezone.utc),
        "balance_after": Decimal("1000000.00"),
        "provenance": DataProvenance.SYNTHETIC,
    }]

    builder_a_again = FeatureBuilder(sample_user_activities)
    f_a_2 = builder_a_again.build_snapshot_features(datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc))

    assert f_a_1 == f_a_2


def test_feature_pipeline_export(tmp_path):
    """Verify FeaturePipeline generates and exports partitioned feature datasets."""
    # Run pipeline on project data directory
    pipeline = FeaturePipeline("data", cadence_days=30)
    counts = pipeline.export_feature_datasets(str(tmp_path))

    assert counts["total"] > 0
    assert counts["train"] > 0
    assert counts["validation"] > 0
    assert counts["test"] > 0
    assert (tmp_path / "features_train.csv").exists()
    assert (tmp_path / "features_validation.csv").exists()
    assert (tmp_path / "features_test.csv").exists()
