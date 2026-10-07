"""Automated tests for Spendable Pipeline Innovation Ablation Study."""

from pathlib import Path
import pytest

from app.analysis.ablation import AblationStudyRunner, AblationStudyReport


def test_ablation_study_execution():
    """Verify that AblationStudyRunner executes cleanly on evaluation datasets and produces valid report metrics."""
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    runner = AblationStudyRunner(data_dir=str(data_dir), split_name="TEST")
    report = runner.run()

    assert isinstance(report, AblationStudyReport)
    assert report.total_snapshots == 1649
    assert report.split_name == "TEST"

    # Verify all 5 variants are present
    assert "VARIANT_A" in report.variants
    assert "VARIANT_B" in report.variants
    assert "VARIANT_C" in report.variants
    assert "VARIANT_D" in report.variants
    assert "VARIANT_E" in report.variants

    var_a = report.variants["VARIANT_A"]
    var_b = report.variants["VARIANT_B"]
    var_c = report.variants["VARIANT_C"]
    var_d = report.variants["VARIANT_D"]
    var_e = report.variants["VARIANT_E"]

    # Verify Variant A (Balance Only) has highest mean spendable and high safety breach rate
    assert var_a.mean_spendable_bdt > var_b.mean_spendable_bdt
    assert var_a.safety_breach_rate > 50.0

    # Verify Variant B (Balance + Commitments) lowers safety breach rate relative to Variant A
    assert var_b.safety_breach_rate < var_a.safety_breach_rate

    # Verify Variant E produces 100% identical financial output to Variant D
    assert var_e.financial_identical_to_variant_d is True
    assert var_e.mean_spendable_bdt == var_d.mean_spendable_bdt
    assert var_e.median_spendable_bdt == var_d.median_spendable_bdt
    assert var_e.safety_breach_rate == var_d.safety_breach_rate
    assert var_e.zero_spendable_rate == var_d.zero_spendable_rate

    # Verify Non-Double-Counting experiment
    ndc = report.non_double_counting_experiment
    assert ndc.total_snapshots == 1649
    assert ndc.mean_double_counting_penalty_bdt > 0.0
    assert ndc.prod_mean_spendable_bdt >= ndc.naive_mean_spendable_bdt

    # Test serialization to dict
    rep_dict = report.to_dict()
    assert rep_dict["split_name"] == "TEST"
    assert len(rep_dict["variants"]) == 5
