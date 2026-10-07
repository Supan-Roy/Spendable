"""CLI script to run the Spendable AI/ML Validation Upgrade and save JSON report."""

import json
from pathlib import Path
import sys

# Ensure backend app is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.analysis.ml_validation import MLValidationRunner


def main():
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data"
    output_report_path = root_dir / "reports" / "ml_validation_report.json"

    print(f"Running Spendable AI/ML Validation Upgrade on dataset at {data_dir}...")
    runner = MLValidationRunner(data_dir=str(data_dir), split_name="TEST")
    report = runner.run()

    report_dict = report.to_dict()

    output_report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    print("\n=== SPENDABLE AI/ML VALIDATION SUMMARY REPORT ===")
    print(f"Evaluated Snapshots: {report.total_snapshots:,} ({report.split_name} Split)")
    print(f"Report saved to: {output_report_path}\n")

    print("--- 1. MULTI-HORIZON BASELINE COMPARISON ---")
    print(f"{'Model Name':<32} | {'Horizon':<8} | {'MAE (BDT)':<12} | {'RMSE (BDT)':<12} | {'R² Score':<10} | {'30d Pressure F1':<15}")
    print("-" * 105)

    for m_name, metrics_list in report.baseline_comparison.items():
        for m in metrics_list:
            f1_str = f"{m.f1_score_30d * 100.0:.2f}%" if m.f1_score_30d is not None else "N/A"
            print(
                f"{m.model_name:<32} | "
                f"{m.horizon_days:>5}d  | "
                f"BDT {m.mae:>8,.2f} | "
                f"BDT {m.rmse:>8,.2f} | "
                f"{m.r2_score:>8.4f} | "
                f"{f1_str:>14}"
            )

    print("\n--- 2. TOP INDIVIDUAL FEATURE IMPORTANCES (Validation Split) ---")
    for feat, imp in list(report.top_feature_importances.items())[:8]:
        print(f"  • {feat:<32}: {imp:.5f}")

    print("\n--- CONTROLLED FEATURE-GROUP ABLATION (TEST Split) ---")
    print(f"{'Removed Feature Group':<26} | {'Rem. Features':<13} | {'30d MAE':<12} | {'30d R²':<10} | {'MAE Delta':<12} | {'30d F1':<10}")
    print("-" * 100)

    for g_name, ab in report.feature_group_ablation.items():
        delta_str = f"+BDT {ab.mae_delta_bdt:,.2f}" if ab.mae_delta_bdt >= 0 else f"-BDT {abs(ab.mae_delta_bdt):,.2f}"
        print(
            f"{ab.removed_group:<26} | "
            f"{ab.remaining_features_count:>13} | "
            f"BDT {ab.mae_30d:>8,.2f} | "
            f"{ab.r2_30d:>8.4f} | "
            f"{delta_str:>12} | "
            f"{ab.pressure_f1_30d * 100.0:>8.2f}%"
        )

    print("\n--- 3. SYNTHETIC BEHAVIOR NOISE PERTURBATION ROBUSTNESS ---")
    print(f"{'Robustness Scenario':<28} | {'30d MAE':<12} | {'30d RMSE':<12} | {'30d R²':<10} | {'30d F1':<10}")
    print("-" * 85)

    for s_name, rob in report.robustness_scenarios.items():
        print(
            f"{rob.scenario_name:<28} | "
            f"BDT {rob.mae_30d:>8,.2f} | "
            f"BDT {rob.rmse_30d:>8,.2f} | "
            f"{rob.r2_30d:>8.4f} | "
            f"{rob.pressure_f1_30d * 100.0:>8.2f}%"
        )

    print("\n--- 4. LIQUIDITY PRESSURE CLASSIFIER AUDIT (F1 = 86.75%) ---")
    audit = report.pressure_classifier_audit
    print(f"Target Threshold: BDT {audit.safety_threshold_bdt:,.2f}")
    print(f"Ground Truth: {audit.ground_truth_definition}")
    print(f"Predicted:    {audit.predicted_definition}")
    print(f"Confusion Matrix: TP={audit.true_positives}, FP={audit.false_positives}, FN={audit.false_negatives}, TN={audit.true_negatives}")
    print(f"Precision: {audit.precision * 100.0:.2f}% | Recall: {audit.recall * 100.0:.2f}% | F1 Score: {audit.f1_score * 100.0:.2f}%")
    print(f"Reproducible: {audit.is_reproducible}")

    print("\n--- 5. PERSONA-LEVEL FORECASTING PERFORMANCE ---")
    print(f"{'Persona':<25} | {'Snapshots':<10} | {'30d MAE (BDT)':<15} | {'30d RMSE (BDT)':<15} | {'30d Pressure F1':<15}")
    print("-" * 90)

    for p_name, p in report.persona_breakdown.items():
        print(
            f"{p.persona:<25} | "
            f"{p.sample_count:>10} | "
            f"BDT {p.mae_30d:>11,.2f} | "
            f"BDT {p.rmse_30d:>11,.2f} | "
            f"{p.pressure_f1_30d * 100.0:>14.2f}%"
        )

    print()


if __name__ == "__main__":
    main()
