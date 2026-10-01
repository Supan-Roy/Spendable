"""Exporter module for synthetic datasets.

Supports exporting generated financial activities and ground truth metadata to
CSV files, JSON files, and seeding directly into PostgreSQL/SQLite databases.
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
