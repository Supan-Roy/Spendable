"""Unit tests for the Spendable Data Quality Validation and EDA Pipeline."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from app.synthetic.config import GeneratorConfig
from app.synthetic.generator import SyntheticDataGenerator
from app.analysis.validator import DatasetValidator, RuleStatus
from app.analysis.eda import EDAEngine


@pytest.fixture
def sample_dataset():
    """Fixture producing a clean 3-user synthetic dataset."""
    config = GeneratorConfig(seed=42, num_users=3, duration_days=30)
    generator = SyntheticDataGenerator(config)
    activities, ground_truth = generator.generate()
    return activities, ground_truth.model_dump()


def test_validator_schema_and_contract_compliance(sample_dataset):
    """Verify that a valid synthetic dataset passes all schema and contract checks."""
    activities, ground_truth = sample_dataset
    validator = DatasetValidator(activities, ground_truth)
    result = validator.validate()

    assert result.total_records == len(activities)
    assert result.total_users == 3
    assert result.summary_counts[RuleStatus.FAIL] == 0


def test_validator_detects_duplicate_ids(sample_dataset):
    """Verify that validator flags duplicate transaction IDs as FAIL."""
    activities, ground_truth = sample_dataset
    # Inject a duplicate ID intentionally
    corrupted_activities = [dict(a) for a in activities]
    corrupted_activities[1]["id"] = corrupted_activities[0]["id"]

    validator = DatasetValidator(corrupted_activities, ground_truth)
    result = validator.validate()

    assert result.overall_status == RuleStatus.FAIL
    fail_checks = [c for c in result.checks if c.status == RuleStatus.FAIL]
    assert any(c.rule_id == "UNIQUE_TXN_ID" for c in fail_checks)


def test_validator_detects_negative_amounts(sample_dataset):
    """Verify that validator flags non-positive amounts as FAIL."""
    activities, ground_truth = sample_dataset
    corrupted_activities = [dict(a) for a in activities]
    corrupted_activities[0]["amount"] = Decimal("-500.00")

    validator = DatasetValidator(corrupted_activities, ground_truth)
    result = validator.validate()

    assert result.overall_status == RuleStatus.FAIL
    fail_checks = [c for c in result.checks if c.status == RuleStatus.FAIL]
    assert any(c.rule_id == "POSITIVE_AMOUNT" for c in fail_checks)


def test_validator_detects_balance_imbalance(sample_dataset):
    """Verify that validator flags balance reconstruction discrepancies as FAIL."""
    activities, ground_truth = sample_dataset
    corrupted_activities = [dict(a) for a in activities]
    # Corrupt balance_after intentionally
    corrupted_activities[2]["balance_after"] = Decimal("999999.00")

    validator = DatasetValidator(corrupted_activities, ground_truth)
    result = validator.validate()

    assert result.overall_status == RuleStatus.FAIL
    fail_checks = [c for c in result.checks if c.status == RuleStatus.FAIL]
    assert any(c.rule_id == "BALANCE_RECONSTRUCTION" for c in fail_checks)


def test_validator_detects_out_of_order_timestamps(sample_dataset):
    """Verify that validator flags out-of-order timestamps as FAIL."""
    activities, ground_truth = sample_dataset
    corrupted_activities = [dict(a) for a in activities]
    # Swap timestamps of first two transactions for ACC-0001
    u1_indices = [i for i, a in enumerate(corrupted_activities) if a["account_id"] == "ACC-0001"]
    if len(u1_indices) >= 2:
        t0 = corrupted_activities[u1_indices[0]]["timestamp_utc"]
        t1 = corrupted_activities[u1_indices[1]]["timestamp_utc"]
        corrupted_activities[u1_indices[0]]["timestamp_utc"] = t1
        corrupted_activities[u1_indices[1]]["timestamp_utc"] = t0

    validator = DatasetValidator(corrupted_activities, ground_truth)
    result = validator.validate()

    assert result.overall_status == RuleStatus.FAIL
    fail_checks = [c for c in result.checks if c.status == RuleStatus.FAIL]
    assert any(c.rule_id == "CHRONOLOGICAL_ORDER" for c in fail_checks)


def test_validation_result_reproducibility(sample_dataset):
    """Verify validation result structure and determinism."""
    activities, ground_truth = sample_dataset
    val1 = DatasetValidator(activities, ground_truth).validate()
    val2 = DatasetValidator(activities, ground_truth).validate()

    assert val1.overall_status == val2.overall_status
    assert val1.summary_counts == val2.summary_counts
    assert len(val1.checks) == len(val2.checks)


def test_eda_engine_metrics_calculation(sample_dataset):
    """Verify EDA engine correctly computes overview, user metrics, and persona checks."""
    activities, ground_truth = sample_dataset
    eda = EDAEngine(activities, ground_truth)

    overview = eda.get_dataset_overview()
    user_metrics = eda.get_user_level_metrics()
    persona_stats = eda.get_persona_sanity_check()

    assert overview["total_users"] == 3
    assert overview["total_transactions"] == len(activities)
    assert len(user_metrics) == 3
    assert len(persona_stats) > 0
