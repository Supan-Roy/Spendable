"""Command Line Interface for Recurring Commitment Detection & Offline Ground-Truth Evaluation.

Usage:
    python -m app.recurring.cli --dataset-dir data/ --snapshot-date 2026-10-01 --direction OUTFLOW
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

from app.recurring.detector import RecurringDetector
from app.recurring.evaluator import RecurringEvaluator
from app.recurring.schema import DetectionConfig


def load_dataset(dataset_dir: Path):
    """Load transactions and ground truth from dataset directory."""
    tx_path = dataset_dir / "transactions.json"
    gt_path = dataset_dir / "ground_truth.json"

    if not tx_path.exists() and (dataset_dir / "transactions.csv").exists():
        tx_path = dataset_dir / "transactions.csv"

    if not tx_path.exists():
        raise FileNotFoundError(f"No transactions found in {dataset_dir}")

    if tx_path.suffix == ".json":
        with open(tx_path, "r", encoding="utf-8") as f:
            transactions = json.load(f)
    else:
        import csv
        transactions = []
        with open(tx_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                transactions.append(dict(row))

    gt_data = {}
    if gt_path.exists():
        with open(gt_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)

    return transactions, gt_data


def main():
    parser = argparse.ArgumentParser(description="Spendable Recurring Payment Detector CLI")
    parser.add_argument("--dataset-dir", type=str, default="data/", help="Path to data directory containing transactions and ground_truth")
    parser.add_argument("--snapshot-date", type=str, default="2026-10-01", help="Snapshot cutoff date (YYYY-MM-DD)")
    parser.add_argument("--direction", type=str, default="OUTFLOW", choices=["OUTFLOW", "INFLOW", "ALL"], help="Filter direction: OUTFLOW (commitments), INFLOW (income), or ALL")
    parser.add_argument("--strong-threshold", type=float, default=0.70, help="Strong confidence threshold")
    parser.add_argument("--moderate-threshold", type=float, default=0.45, help="Moderate confidence threshold")
    parser.add_argument("--output-json", type=str, default="reports/recurring_evaluation.json", help="Path to save evaluation report JSON")

    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    snapshot_time = datetime.fromisoformat(args.snapshot_date)

    print(f"==================================================")
    print(f"SPENDABLE RECURRING COMMITMENT DETECTION & EVALUATION")
    print(f"Dataset Directory: {dataset_dir}")
    print(f"Snapshot Cutoff T: {snapshot_time.strftime('%Y-%m-%d')}")
    print(f"Direction Target : {args.direction} ('OUTFLOW' = Financial Commitments)")
    print(f"Config: Strong Threshold={args.strong_threshold}, Moderate Threshold={args.moderate_threshold}")
    print(f"==================================================\n")

    transactions, gt_data = load_dataset(dataset_dir)
    print(f"Loaded {len(transactions):,} total historical transactions.")

    config = DetectionConfig(
        strong_threshold=args.strong_threshold,
        moderate_threshold=args.moderate_threshold,
    )
    detector = RecurringDetector(config=config)

    if not gt_data:
        print("No ground_truth.json found. Running single user detection demo...")
        commitments = detector.detect(transactions, snapshot_time, direction_filter=args.direction)
        print(f"Detected {len(commitments)} commitments at snapshot T.")
        return

    evaluator = RecurringEvaluator(gt_data)
    report = evaluator.evaluate_all_splits(detector, transactions, snapshot_time, direction_filter=args.direction)

    # Print summary tables
    print("\n--- RECURRING COMMITMENT EVALUATION SUMMARY ---")
    print(f"{'Split':<12} | {'Users':<6} | {'GT Rules':<9} | {'Detected':<9} | {'TP':<5} | {'FP':<5} | {'FN':<5} | {'Precision':<10} | {'Recall':<10} | {'F1 Score':<10}")
    print("-" * 105)

    for m in [report.train_metrics, report.validation_metrics, report.test_metrics]:
        print(f"{m.split_name:<12} | {m.total_users:<6} | {m.ground_truth_rules_count:<9} | {m.detected_commitments_count:<9} | {m.true_positives:<5} | {m.false_positives:<5} | {m.false_negatives:<5} | {m.precision:<10.4f} | {m.recall:<10.4f} | {m.f1_score:<10.4f}")

    print("-" * 105)

    # Print TRAIN category-level breakdown table
    print("\n--- TRAIN CATEGORY-LEVEL EVALUATION BREAKDOWN ---")
    print(f"{'Category':<22} | {'GT Count':<8} | {'Detected':<8} | {'TP':<5} | {'FP':<5} | {'FN':<5} | {'Precision':<10} | {'Recall':<10}")
    print("-" * 90)
    for c_m in report.train_metrics.category_breakdown:
        print(f"{c_m.category:<22} | {c_m.ground_truth_count:<8} | {c_m.detected_count:<8} | {c_m.true_positives:<5} | {c_m.false_positives:<5} | {c_m.false_negatives:<5} | {c_m.precision:<10.4f} | {c_m.recall:<10.4f}")
    print("-" * 90)

    # Save output report JSON
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    print(f"\nEvaluation report successfully saved to: {output_path}")


if __name__ == "__main__":
    main()
