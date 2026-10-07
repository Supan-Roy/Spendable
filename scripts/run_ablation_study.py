"""CLI script to run the Spendable pipeline innovation ablation study and save results to JSON report."""

import json
from pathlib import Path
import sys

# Ensure backend app is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.analysis.ablation import AblationStudyRunner


def main():
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data"
    output_report_path = root_dir / "reports" / "ablation_study_results.json"

    print(f"Running Spendable Innovation Ablation Study on dataset at {data_dir}...")
    runner = AblationStudyRunner(data_dir=str(data_dir), split_name="TEST")
    report = runner.run()

    report_dict = report.to_dict()

    output_report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    print("\n=== ABLATION STUDY RESULTS SUMMARY ===")
    print(f"Evaluated Snapshots: {report.total_snapshots} (TEST Split)")
    print(f"Report saved to: {output_report_path}\n")

    print(f"{'Variant':<35} | {'Breach Rate':<12} | {'Zero Rate':<10} | {'Mean Spendable':<15} | {'Median Spendable':<18} | {'Avg Buffer':<12}")
    print("-" * 115)

    for vid, vmetric in report.variants.items():
        print(
            f"{vmetric.variant_name:<35} | "
            f"{vmetric.safety_breach_rate:>10.2f}% | "
            f"{vmetric.zero_spendable_rate:>8.2f}% | "
            f"BDT {vmetric.mean_spendable_bdt:>11,.2f} | "
            f"BDT {vmetric.median_spendable_bdt:>14,.2f} | "
            f"BDT {vmetric.avg_unallocated_buffer_bdt:>8,.2f}"
        )

    print("\n=== NON-DOUBLE-COUNTING EXPERIMENT ===")
    ndc = report.non_double_counting_experiment
    print(f"Naive Formulation Mean Spendable: BDT {ndc.naive_mean_spendable_bdt:,.2f} | Breach Rate: {ndc.naive_safety_breach_rate:.2f}% | Zero Rate: {ndc.naive_zero_spendable_rate:.2f}%")
    print(f"Prod Formulation Mean Spendable:  BDT {ndc.prod_mean_spendable_bdt:,.2f} | Breach Rate: {ndc.prod_safety_breach_rate:.2f}% | Zero Rate: {ndc.prod_zero_spendable_rate:.2f}%")
    print(f"Mean Double-Counting Penalty Avoided: BDT {ndc.mean_double_counting_penalty_bdt:,.2f} per snapshot")
    print(f"Conclusion: {ndc.conclusion}\n")


if __name__ == "__main__":
    main()
