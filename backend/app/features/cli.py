"""Command Line Interface for Spendable Feature Engineering Pipeline.

Usage:
    python -m app.features.cli --data-dir ./data --output-dir ./data/features --cadence 14
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

from app.features.pipeline import FeaturePipeline


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Spendable Feature Engineering Pipeline")
    parser.add_argument("--data-dir", type=str, default="./data", help="Directory containing raw synthetic data and ground truth (default: ./data)")
    parser.add_argument("--output-dir", type=str, default="./data/features", help="Output directory for generated feature matrices (default: ./data/features)")
    parser.add_argument("--cadence", type=int, default=14, help="Snapshot interval cadence in days (default: 14)")

    args = parser.parse_args()

    data_path = Path(args.data_dir)
    out_path = Path(args.output_dir)

    print("==================================================")
    print(" Spendable Feature Engineering Pipeline")
    print(f" Source Data Directory: {data_path.resolve()}")
    print(f" Target Output Directory: {out_path.resolve()}")
    print(f" Snapshot Cadence: Every {args.cadence} days")
    print("==================================================")

    try:
        pipeline = FeaturePipeline(str(data_path), cadence_days=args.cadence)
        print("Building point-in-time snapshot feature matrices and targets...")
        counts = pipeline.export_feature_datasets(str(out_path))

        print("\nFeature Dataset Generation Complete!")
        print(f" Total Snapshots Generated: {counts['total']}")
        print(f" Train Snapshots: {counts['train']} (350 users)")
        print(f" Validation Snapshots: {counts['validation']} (75 users)")
        print(f" Test Snapshots: {counts['test']} (75 users)")
        print(f" Features Output File: {out_path / 'features_train.csv'}")
    except Exception as e:
        print(f"Error running feature pipeline: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
