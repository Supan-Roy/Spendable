"""Automated tests for Spendable AI/ML Validation Upgrade."""

from pathlib import Path
import pytest

from app.analysis.ml_validation import (
    MLValidationRunner,
    MLValidationReport,
    PressureClassifierAudit,
)


def test_ml_validation_execution():
    """Verify MLValidationRunner executes cleanly and produces valid baseline, ablation, and robustness metrics."""
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    runner = MLValidationRunner(data_dir=str(data_dir), split_name="TEST")
    report = runner.run()

    assert isinstance(report, MLValidationReport)
    assert report.total_snapshots == 1649
    assert report.split_name == "TEST"

    # 1. Verify baseline comparison
    assert "ROLLING_AVERAGE_BASELINE" in report.baseline_comparison
    assert "RECURRING_COMMITMENT_BASELINE" in report.baseline_comparison
    assert "HIST_GRADIENT_BOOSTING" in report.baseline_comparison

    ml_metrics = report.baseline_comparison["HIST_GRADIENT_BOOSTING"]
    assert len(ml_metrics) == 3  # 7d, 14d, 30d
    for m in ml_metrics:
        assert m.mae > 0.0
        assert m.r2_score > 0.90

    # 2. Verify feature importance & group ablation
    assert len(report.top_feature_importances) > 0
    assert "BALANCE_HISTORY" in report.feature_group_ablation
    assert "RECURRING_COMMITMENTS" in report.feature_group_ablation

    for g_name, ab in report.feature_group_ablation.items():
        assert ab.remaining_features_count < 38
        assert ab.r2_30d > 0.90

    # 3. Verify robustness scenarios
    assert "DEFAULT_OFFICIAL_TEST" in report.robustness_scenarios
    assert "COMBINED_EXTREME_NOISE" in report.robustness_scenarios

    default_rob = report.robustness_scenarios["DEFAULT_OFFICIAL_TEST"]
    extreme_rob = report.robustness_scenarios["COMBINED_EXTREME_NOISE"]

    # Verify graceful degradation under extreme noise
    assert extreme_rob.mae_30d >= default_rob.mae_30d
    assert extreme_rob.r2_30d <= default_rob.r2_30d

    # 4. Verify Pressure Classifier Audit
    audit = report.pressure_classifier_audit
    assert isinstance(audit, PressureClassifierAudit)
    assert audit.total_snapshots == 1649
    assert audit.safety_threshold_bdt == 15000.0
    assert audit.true_positives + audit.false_positives + audit.false_negatives + audit.true_negatives == 1649

    # 5. Verify persona breakdown
    assert len(report.persona_breakdown) >= 5
    assert "TIGHT_LIQUIDITY" in report.persona_breakdown
    assert report.persona_breakdown["TIGHT_LIQUIDITY"].pressure_f1_30d > 0.60

    # Test serialization to dictionary
    rep_dict = report.to_dict()
    assert rep_dict["split_name"] == "TEST"
    assert "baseline_comparison" in rep_dict
    assert "pressure_classifier_audit" in rep_dict
