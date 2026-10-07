"""Automated tests for Spendable Customer Outcome Impact Evaluation."""

from pathlib import Path
import pytest

from app.analysis.customer_outcome import (
    CustomerOutcomeEvaluator,
    CustomerOutcomeReport,
    CustomerDecisionInteractionFramework,
)


def test_customer_outcome_evaluation_execution():
    """Verify CustomerOutcomeEvaluator runs on TEST dataset and computes accurate customer outcome metrics."""
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    evaluator = CustomerOutcomeEvaluator(data_dir=str(data_dir), split_name="TEST", n_bootstrap_samples=100)
    report = evaluator.run()

    assert isinstance(report, CustomerOutcomeReport)
    assert report.total_snapshots == 1649
    assert report.total_scenarios_simulated > 10000

    # Check metrics present
    assert "liquidity_failure_rate" in report.metrics
    assert "overspending_incident_rate" in report.metrics
    assert "missed_payment_rate" in report.metrics

    m_fail = report.metrics["liquidity_failure_rate"]
    assert m_fail.baseline_value > m_fail.spendable_value
    assert m_fail.absolute_reduction > 10.0
    assert m_fail.relative_reduction_pct > 70.0

    m_over = report.metrics["overspending_incident_rate"]
    assert m_over.baseline_value > m_over.spendable_value
    assert m_over.spendable_value < 2.0

    m_miss = report.metrics["missed_payment_rate"]
    assert m_miss.baseline_value > m_miss.spendable_value
    assert m_miss.relative_reduction_pct > 80.0

    # Verify persona breakdowns
    assert len(report.persona_breakdown) >= 5
    for p_name, p_metric in report.persona_breakdown.items():
        assert p_metric.baseline_failure_rate >= p_metric.spendable_failure_rate

    # Verify variant progression
    assert "VARIANT_A" in report.pipeline_variants
    assert "VARIANT_E" in report.pipeline_variants
    assert (
        report.pipeline_variants["VARIANT_E"]["liquidity_failure_rate"]
        == report.pipeline_variants["VARIANT_D"]["liquidity_failure_rate"]
    )

    # Verify decision time framework is marked NOT_YET_MEASURED
    assert report.decision_time_framework.status == "NOT_YET_MEASURED"

    # Test dictionary serialization
    rep_dict = report.to_dict()
    assert rep_dict["split_name"] == "TEST"
    assert "metrics" in rep_dict
    assert "persona_breakdown" in rep_dict
