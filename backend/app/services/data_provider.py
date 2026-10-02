"""Data Provider abstraction layer for Spendable.

Isolates data access so that synthetic prototype data can later be seamlessly
replaced by live production banking/wallet integrations (e.g. Upay, bKash, MFS providers).
"""

from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

from app.recurring.detector import RecurringDetector
from app.recurring.schema import DetectedCommitment
from app.forecasting.models import CashFlowForecastModel
from app.forecasting.schema import ForecastOutput


class BaseDataProvider(ABC):
    """Abstract Base Class for Spendable data providers."""

    @abstractmethod
    def get_snapshot_data(
        self, user_id: Optional[str] = None, snapshot_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve point-in-time snapshot features, commitments, and forecast for a user."""
        pass

    @abstractmethod
    def get_recent_activities(
        self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieve recent transaction activity records."""
        pass


class SyntheticDataProvider(BaseDataProvider):
    """Synthetic data provider leveraging prepared offline datasets and model pipelines."""

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path("data")
        self._test_df: Optional[pd.DataFrame] = None
        self._train_df: Optional[pd.DataFrame] = None
        self._transactions_df: Optional[pd.DataFrame] = None
        
        self.forecast_model = CashFlowForecastModel()
        self.recurring_detector = RecurringDetector()
        
        self._initialize()

    def _initialize(self):
        """Lazy load feature datasets and train forecasting model on startup."""
        feat_dir = self.data_dir / "features"
        if not feat_dir.exists():
            feat_dir = self.data_dir

        test_path = feat_dir / "features_test.csv"
        train_path = feat_dir / "features_train.csv"

        if test_path.exists():
            self._test_df = pd.read_csv(test_path)
        if train_path.exists():
            self._train_df = pd.read_csv(train_path)
            # Fit model on training split
            self.forecast_model.fit(self._train_df)

        tx_path = self.data_dir / "transactions.csv"
        if tx_path.exists():
            self._transactions_df = pd.read_csv(tx_path)

    def get_snapshot_data(
        self, user_id: Optional[str] = None, snapshot_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve snapshot data for a specified user or default demo user."""
        df = self._test_df if self._test_df is not None else self._train_df
        if df is None or len(df) == 0:
            raise ValueError("No snapshot dataset available in data provider.")

        # Find matching row or fallback to first row
        row_match = None
        if user_id:
            user_col = "account_id" if "account_id" in df.columns else "user_id"
            matches = df[df[user_col] == user_id]
            if len(matches) > 0:
                row_match = matches.iloc[0].to_dict()

        if row_match is None:
            row_match = df.iloc[0].to_dict()

        matched_user_id = str(row_match.get("account_id", row_match.get("user_id", "ACC-DEMO-001")))
        matched_snapshot_time = str(row_match.get("snapshot_time", "2026-03-01T00:00:00"))
        current_balance = float(row_match.get("current_balance", 0.0))

        # Predict forecast trajectory using trained model
        forecast: Optional[ForecastOutput] = None
        if self.forecast_model.is_fitted:
            forecast = self.forecast_model.predict_snapshot(row_match)

        # Detect recurring commitments from transactions if available
        commitments: List[DetectedCommitment] = []
        if self._transactions_df is not None:
            tx_col = "account_id" if "account_id" in self._transactions_df.columns else "user_id"
            user_txs = self._transactions_df[self._transactions_df[tx_col] == matched_user_id]
            if len(user_txs) > 0:
                commitments = self.recurring_detector.detect(
                    user_txs.to_dict(orient="records"), matched_snapshot_time
                )

        return {
            "user_id": matched_user_id,
            "snapshot_time": matched_snapshot_time,
            "current_balance": current_balance,
            "features": row_match,
            "commitments": commitments,
            "forecast": forecast,
        }

    def get_recent_activities(
        self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieve observed transactions with pagination."""
        if self._transactions_df is None or len(self._transactions_df) == 0:
            return {"total_count": 0, "limit": limit, "offset": offset, "activities": []}

        df = self._transactions_df
        if user_id:
            user_col = "account_id" if "account_id" in df.columns else "user_id"
            df = df[df[user_col] == user_id]

        total_count = len(df)
        paged_df = df.iloc[offset : offset + limit]

        activities = []
        for idx, row in paged_df.iterrows():
            activities.append({
                "transaction_id": str(row.get("transaction_id", f"tx_{idx}")),
                "account_id": str(row.get("account_id", row.get("user_id", "ACC-DEMO-001"))),
                "timestamp_utc": str(row.get("timestamp_utc", row.get("timestamp", ""))),
                "amount": float(row.get("amount", 0.0)),
                "direction": str(row.get("direction", "OUTFLOW")),
                "category": str(row.get("category", "GENERAL")),
                "counterparty_name": str(row.get("counterparty_name", "Merchant")) if pd.notna(row.get("counterparty_name")) else None,
                "balance_after": float(row.get("balance_after")) if pd.notna(row.get("balance_after")) else None,
            })

        return {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "activities": activities,
        }
