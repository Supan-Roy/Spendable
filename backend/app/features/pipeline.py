"""Snapshot Dataset Pipeline & Feature Matrix Exporter.

Builds point-in-time snapshot feature matrices across user histories, attaches
offline ground-truth targets, and exports partitioned TRAIN/VALIDATION/TEST feature datasets.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

from app.features.builder import FeatureBuilder
from app.features.leakage import FeatureLeakageDetector, LeakageError
from app.features.schema import FEATURE_CATALOG


class FeaturePipeline:
    """Pipeline for generating snapshot-based feature matrices and targets."""

    def __init__(self, dataset_dir: str, cadence_days: int = 14):
        """Initialize pipeline with dataset directory and snapshot cadence in days.
        
        Args:
            dataset_dir: Directory containing raw transactions and ground truth.
            cadence_days: Time interval in days between snapshot checkpoints (default: 14 days).
        """
        self.dataset_dir = Path(dataset_dir)
        self.cadence_days = cadence_days
        self.raw_activities, self.ground_truth = self._load_data()

    def _load_data(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        raw_activities: List[Dict[str, Any]] = []
        ground_truth: Dict[str, Any] = {}

        # Look for transactions.json or transactions.csv
        full_json = self.dataset_dir / "transactions.json"
        full_csv = self.dataset_dir / "transactions.csv"
        gt_json = self.dataset_dir / "ground_truth.json"

        if not gt_json.exists() and (self.dataset_dir / "ground_truth" / "ground_truth.json").exists():
            gt_json = self.dataset_dir / "ground_truth" / "ground_truth.json"

        if full_json.exists():
            with open(full_json, mode="r", encoding="utf-8") as f:
                raw_activities = json.load(f)
        elif full_csv.exists():
            import csv
            with open(full_csv, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_activities.append(dict(row))
        else:
            raise FileNotFoundError(f"No transactions found in {self.dataset_dir}")

        if gt_json.exists():
            with open(gt_json, mode="r", encoding="utf-8") as f:
                ground_truth = json.load(f)

        return raw_activities, ground_truth

    def _find_targets_at_checkpoint(
        self,
        account_id: str,
        snapshot_time: datetime,
        user_acts_sorted: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Compute offline evaluation targets from future transactions occurring AFTER snapshot_time."""
        st_utc = FeatureBuilder._parse_timestamp(snapshot_time)
        fut_7d = [a for a in user_acts_sorted if st_utc < FeatureBuilder._parse_timestamp(a["timestamp_utc"]) <= st_utc + timedelta(days=7)]
        fut_14d = [a for a in user_acts_sorted if st_utc < FeatureBuilder._parse_timestamp(a["timestamp_utc"]) <= st_utc + timedelta(days=14)]
        fut_30d = [a for a in user_acts_sorted if st_utc < FeatureBuilder._parse_timestamp(a["timestamp_utc"]) <= st_utc + timedelta(days=30)]

        past_acts = [a for a in user_acts_sorted if FeatureBuilder._parse_timestamp(a["timestamp_utc"]) <= st_utc]
        obs_bal = float(Decimal(str(past_acts[-1]["balance_after"]))) if past_acts else 0.0

        b7 = [float(Decimal(str(a["balance_after"]))) for a in fut_7d] if fut_7d else [obs_bal]
        b14 = [float(Decimal(str(a["balance_after"]))) for a in fut_14d] if fut_14d else [obs_bal]
        b30 = [float(Decimal(str(a["balance_after"]))) for a in fut_30d] if fut_30d else [obs_bal]

        min_b30 = float(min(b30))
        shortfall_30d = 1 if min_b30 < 1000.0 else 0

        in30 = sum(float(Decimal(str(a["amount"]))) for a in fut_30d if str(a["direction"]).replace("TransactionDirection.", "") == "INFLOW")
        out30 = sum(float(Decimal(str(a["amount"]))) for a in fut_30d if str(a["direction"]).replace("TransactionDirection.", "") == "OUTFLOW")

        return {
            "target_future_min_balance_7d": round(float(min(b7)), 2),
            "target_future_min_balance_14d": round(float(min(b14)), 2),
            "target_future_min_balance_30d": round(min_b30, 2),
            "target_liquidity_shortfall_30d": shortfall_30d,
            "target_future_net_cash_flow_30d": round(in30 - out30, 2),
        }

    def generate_snapshot_dataset(self) -> pd.DataFrame:
        """Generate point-in-time feature matrix for all users across historical checkpoints."""
        user_acts: Dict[str, List[Dict[str, Any]]] = {}
        for a in self.raw_activities:
            uid = a["account_id"]
            user_acts.setdefault(uid, []).append(a)

        user_splits = self.ground_truth.get("user_splits", {})
        gt_users = self.ground_truth.get("users", {})

        records = []

        for uid, acts in user_acts.items():
            acts_sorted = sorted(acts, key=lambda x: FeatureBuilder._parse_timestamp(x["timestamp_utc"]))
            if not acts_sorted:
                continue

            builder = FeatureBuilder(acts_sorted)
            start_ts = FeatureBuilder._parse_timestamp(acts_sorted[0]["timestamp_utc"])
            end_ts = FeatureBuilder._parse_timestamp(acts_sorted[-1]["timestamp_utc"])

            # First snapshot after 30 days of initial transaction history
            current_chk = start_ts + timedelta(days=30)
            
            # Stop snapshots 30 days before simulation end to allow full 30-day future target evaluation
            max_chk = end_ts - timedelta(days=30)

            while current_chk <= max_chk:
                features = builder.build_snapshot_features(current_chk)
                FeatureLeakageDetector.verify_feature_key_purity(features)

                targets = self._find_targets_at_checkpoint(uid, current_chk, acts_sorted)

                rec = dict(features)
                rec.update(targets)

                # Attach metadata
                rec["split_assignment"] = user_splits.get(uid, "TRAIN")
                user_gt = gt_users.get(uid, {})
                rec["persona"] = str(user_gt.get("persona", "UNKNOWN"))

                records.append(rec)
                current_chk += timedelta(days=self.cadence_days)

        df = pd.DataFrame(records)
        return df

    def export_feature_datasets(self, output_dir: str) -> Dict[str, int]:
        """Export partitioned train/validation/test feature datasets to output directory.
        
        Returns dictionary of row counts per split.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        df_full = self.generate_snapshot_dataset()
        if df_full.empty:
            return {"total": 0, "train": 0, "validation": 0, "test": 0}

        df_train = df_full[df_full["split_assignment"] == "TRAIN"].copy()
        df_val = df_full[df_full["split_assignment"] == "VALIDATION"].copy()
        df_test = df_full[df_full["split_assignment"] == "TEST"].copy()

        # Save CSV files
        df_full.to_csv(out_path / "features_full.csv", index=False)
        df_train.to_csv(out_path / "features_train.csv", index=False)
        df_val.to_csv(out_path / "features_validation.csv", index=False)
        df_test.to_csv(out_path / "features_test.csv", index=False)

        # Save JSON metadata summary
        summary = {
            "total_snapshots": len(df_full),
            "train_snapshots": len(df_train),
            "val_snapshots": len(df_val),
            "test_snapshots": len(df_test),
            "total_users": df_full["account_id"].nunique(),
            "train_users": df_train["account_id"].nunique(),
            "val_users": df_val["account_id"].nunique(),
            "test_users": df_test["account_id"].nunique(),
            "feature_columns": [c for c in df_full.columns if not c.startswith("target_") and c not in ("account_id", "snapshot_time", "split_assignment", "persona")],
            "target_columns": [c for c in df_full.columns if c.startswith("target_")],
        }

        with open(out_path / "feature_summary.json", mode="w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return {
            "total": len(df_full),
            "train": len(df_train),
            "validation": len(df_val),
            "test": len(df_test),
        }
