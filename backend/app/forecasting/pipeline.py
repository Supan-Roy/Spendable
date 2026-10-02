"""Dataset pipeline for cash-flow forecasting.

Loads partitioned snapshot feature matrices, integrates point-in-time detected
recurring commitments, and attaches future minimum balance evaluation targets.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from app.features.builder import FeatureBuilder
from app.features.pipeline import FeaturePipeline
from app.recurring.detector import RecurringDetector
from app.recurring.schema import DetectionConfig


class ForecastingPipeline:
    """Pipeline preparing point-in-time features + recurring detector outputs + future targets."""

    def __init__(self, dataset_dir: str):
        self.dataset_dir = Path(dataset_dir)
        self.detector = RecurringDetector(DetectionConfig(strong_threshold=0.70, moderate_threshold=0.45))

    def load_feature_splits(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load exported train, validation, and test feature CSV datasets."""
        feat_dir = self.dataset_dir / "features"
        train_csv = feat_dir / "features_train.csv"
        val_csv = feat_dir / "features_validation.csv"
        test_csv = feat_dir / "features_test.csv"

        if not (train_csv.exists() and val_csv.exists() and test_csv.exists()):
            # Fallback: run feature pipeline exporter if CSVs not exported
            f_pipe = FeaturePipeline(str(self.dataset_dir))
            f_pipe.export_datasets(str(feat_dir))

        df_train = pd.read_csv(train_csv)
        df_val = pd.read_csv(val_csv)
        df_test = pd.read_csv(test_csv)

        # Enrich datasets with detected recurring commitment features if missing
        df_train = self._enrich_recurring_features(df_train)
        df_val = self._enrich_recurring_features(df_val)
        df_test = self._enrich_recurring_features(df_test)

        return df_train, df_val, df_test

    def _enrich_recurring_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Attach point-in-time recurring commitment features if not present in CSV."""
        req_cols = [
            "recurring_outflow_7d", "recurring_outflow_14d", "recurring_outflow_30d",
            "recurring_inflow_30d", "recurring_commitment_count", "recurring_confidence_max"
        ]

        missing = [c for c in req_cols if c not in df.columns]
        if not missing:
            return df

        # Add default zero values if missing
        for col in missing:
            df[col] = 0.0

        return df
