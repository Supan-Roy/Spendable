"""Command Line Interface for Spendable Synthetic Data Generator.

Usage:
    python -m app.synthetic.cli --seed 42 --users 10 --days 180 --output-dir ./data
"""

import argparse
from datetime import datetime, timezone
import sys
from pathlib import Path

from app.synthetic.config import GeneratorConfig
from app.synthetic.generator import SyntheticDataGenerator
from app.synthetic.exporter import (
    export_to_csv,
    export_to_json,
    export_ground_truth_to_json,
    seed_database,
)


def main():
    parser = argparse.ArgumentParser(description="Spendable Synthetic Financial Data Generator")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible generation (default: 42)")
    parser.add_argument("--users", type=int, default=10, help="Number of synthetic users to generate (default: 10)")
    parser.add_argument("--days", type=int, default=180, help="Historical duration in days (default: 180)")
    parser.add_argument("--start-date", type=str, default="2026-01-01", help="Start date YYYY-MM-DD (default: 2026-01-01)")
    parser.add_argument("--currency", type=str, default="BDT", help="ISO 3-letter currency code (default: BDT)")
    parser.add_argument("--output-dir", type=str, default="./synthetic_output", help="Output directory path (default: ./synthetic_output)")
    parser.add_argument("--seed-db", action="store_true", help="Seed generated data into application database")

    args = parser.parse_args()

    try:
        dt = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"Error: Invalid start date format '{args.start_date}'. Must be YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)

    config = GeneratorConfig(
        seed=args.seed,
        num_users=args.users,
        duration_days=args.days,
        start_date=dt,
        currency=args.currency,
    )

    print(f"==================================================")
    print(f" Spendable Synthetic Data Generator")
    print(f" Seed: {config.seed}")
    print(f" Users: {config.num_users}")
    print(f" Duration: {config.duration_days} days (Start: {config.start_date.date()})")
    print(f" Currency: {config.currency}")
    print(f"==================================================")

    generator = SyntheticDataGenerator(config)
    print("Generating synthetic financial activity dataset...")
    activities, ground_truth = generator.generate()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "transactions.csv"
    json_path = out_dir / "transactions.json"
    gt_path = out_dir / "ground_truth.json"

    print(f"Exporting raw transactions to {csv_path}...")
    export_to_csv(activities, str(csv_path))

    print(f"Exporting raw transactions to {json_path}...")
    export_to_json(activities, str(json_path))

    print(f"Exporting ground truth metadata to {gt_path}...")
    export_ground_truth_to_json(ground_truth, str(gt_path))

    if args.seed_db:
        print("Seeding database...")
        try:
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                count = seed_database(activities, db)
                print(f"Successfully seeded {count} records into database.")
            finally:
                db.close()
        except Exception as e:
            print(f"Warning: Database seeding failed: {e}", file=sys.stderr)

    print("\nGeneration completed successfully!")
    print(f"Total Transactions Generated: {len(activities)}")
    print(f"Synthetic Users: {len(ground_truth.users)}")


if __name__ == "__main__":
    main()
