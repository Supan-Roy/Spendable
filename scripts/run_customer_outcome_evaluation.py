"""CLI script to run the Spendable Customer Outcome Impact Evaluation and save JSON report."""

import json
from pathlib import Path
import sys

# Ensure backend app is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.analysis.customer_outcome import CustomerOutcomeEvaluator


def main():
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data"
    output_report_path = root_dir / "reports" / "customer_outcome_evaluation_results.json"

    print(f"Running Spendable Customer Outcome Impact Evaluation on dataset at {data_dir}...")
    evaluator = CustomerOutcomeEvaluator(data_dir=str(data_dir), split_name="TEST")
    report = evaluator.run()

    report_dict = report.to_dict()

    output_report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    print("\n=== SPENDABLE CUSTOMER OUTCOME IMPACT EVALUATION ===")
    print(f"Evaluated Snapshots: {report.total_snapshots:,} (TEST Split)")
    print(f"Simulated Purchase Scenarios: {report.total_scenarios_simulated:,}")
    print(f"Report saved to: {output_report_path}\n")

    print(f"{'Metric':<38} | {'Baseline':<10} | {'Spendable':<10} | {'Abs Reduction':<15} | {'Rel Reduction':<15} | {'95% CI':<15}")
    print("-" * 115)

    for mk, m in report.metrics.items():
        ci_str = f"[{m.ci_95_lower:.2f}%, {m.ci_95_upper:.2f}%]"
        print(
            f"{m.metric_name:<38} | "
            f"{m.baseline_value:>8.2f}% | "
            f"{m.spendable_value:>8.2f}% | "
            f"{m.absolute_reduction:>12.2f}% | "
            f"{m.relative_reduction_pct:>13.2f}% | "
            f"{ci_str:>15}"
        )

    print("\n=== PERSONA-LEVEL OUTCOME BREAKDOWN ===")
    print(f"{'Persona':<25} | {'Snapshots':<10} | {'Baseline Fail':<14} | {'Spendable Fail':<14} | {'Abs Reduction':<14} | {'Rel Reduction':<14}")
    print("-" * 105)

    for pk, p in report.persona_breakdown.items():
        print(
            f"{p.persona:<25} | "
            f"{p.total_snapshots:>10} | "
            f"{p.baseline_failure_rate:>12.2f}% | "
            f"{p.spendable_failure_rate:>12.2f}% | "
            f"{p.absolute_failure_reduction:>12.2f}% | "
            f"{p.relative_failure_reduction_pct:>12.2f}%"
        )

    print("\n=== PIPELINE VARIANT PROGRESSION (CUSTOMER OUTCOMES) ===")
    print(f"{'Variant':<35} | {'Liquidity Failure Rate':<25} | {'Overdraft Incident Rate':<25}")
    print("-" * 90)

    for vk, v in report.pipeline_variants.items():
        print(
            f"{v['variant_name']:<35} | "
            f"{v['liquidity_failure_rate']:>23.2f}% | "
            f"{v['overdraft_rate']:>23.2f}%"
        )

    print("\n=== DECISION TIME & INTERACTION STATUS ===")
    dt = report.decision_time_framework
    print(f"Status: {dt.status}")
    print(f"Reason: {dt.reason}")
    print(f"Prohibited Substitutes: {', '.join(dt.prohibited_substitutes)}\n")


if __name__ == "__main__":
    main()
