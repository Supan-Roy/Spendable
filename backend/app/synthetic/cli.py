"""Command Line Interface for Spendable Synthetic Data Generator.

Usage:
    python -m app.synthetic.cli --seed 42 --users 500 --days 365 --output-dir ./data
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
    export_partitioned_dataset,
    seed_database,
)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Spendable Synthetic Financial Data Generator")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible generation (default: 42)")
    parser.add_argument("--users", type=int, default=500, help="Number of synthetic users to generate (default: 500)")
    parser.add_argument("--days", type=int, default=365, help="Historical duration in days (default: 365)")
    parser.add_argument("--start-date", type=str, default="2026-01-01", help="Start date YYYY-MM-DD (default: 2026-01-01)")
    parser.add_argument("--currency", type=str, default="BDT", help="ISO 3-letter currency code (default: BDT)")
    parser.add_argument("--output-dir", type=str, default="./data", help="Output directory path (default: ./data)")
    parser.add_argument("--train-split", type=float, default=0.70, help="Proportion of users in TRAIN split (default: 0.70)")
    parser.add_argument("--val-split", type=float, default=0.15, help="Proportion of users in VALIDATION split (default: 0.15)")
    parser.add_argument("--test-split", type=float, default=0.15, help="Proportion of users in TEST split (default: 0.15)")
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
        train_split=args.train_split,
        val_split=args.val_split,
        test_split=args.test_split,
    )

    print(f"==================================================")
    print(f" Spendable Large-Scale Synthetic Generator")
    print(f" Seed: {config.seed}")
    print(f" Users: {config.num_users} (Train: {int(config.num_users * config.train_split)}, Val: {int(config.num_users * config.val_split)}, Test: {config.num_users - int(config.num_users * config.train_split) - int(config.num_users * config.val_split)})")
    print(f" Duration: {config.duration_days} days (Start: {config.start_date.date()})")
    print(f" Currency: {config.currency}")
    print(f"==================================================")

    generator = SyntheticDataGenerator(config)
    print("Generating large-scale synthetic financial activity dataset...")
    activities, ground_truth = generator.generate()

    out_dir = Path(args.output_dir)
    print(f"Exporting partitioned datasets to {out_dir.resolve()}...")
    export_partitioned_dataset(activities, ground_truth, str(out_dir))

    # Also maintain top-level files for direct compatibility
    export_to_csv(activities, str(out_dir / "transactions.csv"))
    export_to_json(activities, str(out_dir / "transactions.json"))
    export_ground_truth_to_json(ground_truth, str(out_dir / "ground_truth.json"))

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
    print(f"Train Users: {len([u for u in ground_truth.users.values() if u.split_assignment == 'TRAIN'])}")
    print(f"Val Users: {len([u for u in ground_truth.users.values() if u.split_assignment == 'VALIDATION'])}")
    print(f"Test Users: {len([u for u in ground_truth.users.values() if u.split_assignment == 'TEST'])}")
    print(f"Planted Recurring Rules: {sum(len(u.planted_rules) for u in ground_truth.users.values())}")
    print(f"Future Outcome Checkpoints: {len(ground_truth.future_outcomes)}")


if __name__ == "__main__":
    main()
