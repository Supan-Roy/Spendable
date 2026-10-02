"""Exporter module for synthetic datasets.

Supports exporting generated financial activities and ground truth metadata to
CSV files, JSON files, user-level TRAIN/VAL/TEST splits, and seeding directly
into PostgreSQL/SQLite databases.
"""

import csv
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
from typing import List, Dict, Any
from app.models.activity import FinancialActivityModel


def _custom_json_serializer(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, "value"):
        return obj.value
    raise TypeError(f"Type {type(obj)} not serializable")


def export_to_csv(activities: List[Dict[str, Any]], filepath: str) -> None:
    """Export raw financial activity records to CSV file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not activities:
        return

    fieldnames = [
        "id",
        "account_id",
        "amount",
        "currency",
        "direction",
        "activity_type",
        "timestamp_utc",
        "category",
        "channel",
        "counterparty_name",
        "reference_id",
        "balance_after",
        "provenance",
    ]

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for act in activities:
            row = {}
            for k in fieldnames:
                val = act.get(k)
                if isinstance(val, datetime):
                    row[k] = val.isoformat()
                elif isinstance(val, Decimal):
                    row[k] = str(val)
                elif hasattr(val, "value"):
                    row[k] = val.value
                else:
                    row[k] = "" if val is None else str(val)
            writer.writerow(row)


def export_to_json(activities: List[Dict[str, Any]], filepath: str) -> None:
    """Export raw financial activity records to JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, mode="w", encoding="utf-8") as f:
        json.dump(activities, f, default=_custom_json_serializer, indent=2)


def export_ground_truth_to_json(ground_truth: Any, filepath: str) -> None:
    """Export dataset ground truth metadata to JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    gt_dict = ground_truth.model_dump() if hasattr(ground_truth, "model_dump") else ground_truth

    with open(path, mode="w", encoding="utf-8") as f:
        json.dump(gt_dict, f, default=_custom_json_serializer, indent=2)


def export_partitioned_dataset(activities: List[Dict[str, Any]], ground_truth: Any, output_dir: str) -> None:
    """Export complete dataset partitioned into user-level train/validation/test splits."""
    base_path = Path(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    user_splits = ground_truth.user_splits if hasattr(ground_truth, "user_splits") else ground_truth.get("user_splits", {})

    train_acts = [a for a in activities if user_splits.get(a["account_id"]) == "TRAIN"]
    val_acts = [a for a in activities if user_splits.get(a["account_id"]) == "VALIDATION"]
    test_acts = [a for a in activities if user_splits.get(a["account_id"]) == "TEST"]

    # Export Full dataset
    full_dir = base_path / "full"
    export_to_csv(activities, str(full_dir / "transactions.csv"))
    export_to_json(activities, str(full_dir / "transactions.json"))

    # Export Train split
    train_dir = base_path / "train"
    export_to_csv(train_acts, str(train_dir / "transactions.csv"))
    export_to_json(train_acts, str(train_dir / "transactions.json"))

    # Export Validation split
    val_dir = base_path / "validation"
    export_to_csv(val_acts, str(val_dir / "transactions.csv"))
    export_to_json(val_acts, str(val_dir / "transactions.json"))

    # Export Test split
    test_dir = base_path / "test"
    export_to_csv(test_acts, str(test_dir / "transactions.csv"))
    export_to_json(test_acts, str(test_dir / "transactions.json"))

    # Export Ground Truth directory
    gt_dir = base_path / "ground_truth"
    export_ground_truth_to_json(ground_truth, str(gt_dir / "ground_truth.json"))

    train_users = [uid for uid, split in user_splits.items() if split == "TRAIN"]
    val_users = [uid for uid, split in user_splits.items() if split == "VALIDATION"]
    test_users = [uid for uid, split in user_splits.items() if split == "TEST"]

    with open(gt_dir / "train_users.json", mode="w", encoding="utf-8") as f:
        json.dump(train_users, f, indent=2)
    with open(gt_dir / "val_users.json", mode="w", encoding="utf-8") as f:
        json.dump(val_users, f, indent=2)
    with open(gt_dir / "test_users.json", mode="w", encoding="utf-8") as f:
        json.dump(test_users, f, indent=2)


def seed_database(activities: List[Dict[str, Any]], session) -> int:
    """Seed synthetic activities into database via SQLAlchemy session.
    
    Returns count of records inserted.
    """
    db_models = []
    for act in activities:
        db_model = FinancialActivityModel(
            id=act["id"],
            account_id=act["account_id"],
            amount=Decimal(str(act["amount"])),
            currency=act["currency"],
            direction=act["direction"],
            activity_type=act["activity_type"],
            timestamp_utc=act["timestamp_utc"],
            category=act.get("category"),
            channel=act.get("channel"),
            counterparty_name=act.get("counterparty_name"),
            reference_id=act.get("reference_id"),
            balance_after=Decimal(str(act["balance_after"])) if act.get("balance_after") is not None else None,
            provenance=act["provenance"],
        )
        db_models.append(db_model)

    session.add_all(db_models)
    session.commit()
    return len(db_models)
