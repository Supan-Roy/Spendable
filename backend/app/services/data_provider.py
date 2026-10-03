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
        matched_snapshot_time = str(row_match.get("snapshot_time", "2026-10-03T00:00:00"))
        current_balance = float(row_match.get("current_balance", 0.0))

        # Predict forecast trajectory using trained model or heuristic fallback
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


class DatabaseDataProvider(BaseDataProvider):
    """Database-backed data provider retrieving application state from SQLAlchemy tables."""

    def __init__(self, session_factory=None):
        from app.database import SessionLocal
        self.session_factory = session_factory or SessionLocal
        self.forecast_model = CashFlowForecastModel()
        self.recurring_detector = RecurringDetector()
        self._synthetic_fallback: Optional[SyntheticDataProvider] = None

        # Pre-fit forecast model on offline training data if available
        feat_path = Path("data/features/features_train.csv")
        if not feat_path.exists():
            feat_path = Path("data/features_train.csv")
        if feat_path.exists():
            try:
                train_df = pd.read_csv(feat_path)
                self.forecast_model.fit(train_df)
            except Exception:
                pass

    def _get_fallback(self) -> SyntheticDataProvider:
        if self._synthetic_fallback is None:
            self._synthetic_fallback = SyntheticDataProvider()
        return self._synthetic_fallback

    def get_snapshot_data(
        self, user_id: Optional[str] = None, snapshot_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve snapshot data from database tables."""
        from app.models.account import UserAccount
        from app.models.activity import FinancialActivityModel
        from app.features.builder import FeatureBuilder

        session = self.session_factory()
        try:
            query = session.query(UserAccount)
            if user_id:
                clean_uid = str(user_id).strip().lower()
                account = (
                    query.filter(
                        (UserAccount.account_id == user_id)
                        | (UserAccount.username == clean_uid)
                        | (UserAccount.account_id == f"acc_{clean_uid}")
                        | (UserAccount.account_id == f"usr_{clean_uid}")
                    ).first()
                )
            else:
                account = query.filter(UserAccount.account_id == "acc_supan").first() or query.first()

            if not account:
                # Fallback to synthetic if database has no accounts
                return self._get_fallback().get_snapshot_data(user_id, snapshot_time)

            account_id = account.account_id
            current_balance = float(account.current_balance)

            # Query all financial activities for account ordered by timestamp
            db_acts = (
                session.query(FinancialActivityModel)
                .filter(FinancialActivityModel.account_id == account_id)
                .order_by(FinancialActivityModel.timestamp_utc.asc())
                .all()
            )

            if not db_acts:
                from datetime import datetime, timezone
                now_dt = datetime.now(timezone.utc)
                now_iso = now_dt.isoformat()
                
                builder = FeatureBuilder([])
                empty_feats = builder._build_empty_feature_dict(now_dt)
                empty_feats["account_id"] = account_id
                empty_feats["current_balance"] = current_balance
                
                empty_forecast = self.forecast_model.predict_snapshot(empty_feats)
                return {
                    "user_id": account_id,
                    "snapshot_time": now_iso,
                    "current_balance": current_balance,
                    "features": empty_feats,
                    "commitments": [],
                    "forecast": empty_forecast,
                }

            act_dicts = []
            for a in db_acts:
                act_dicts.append({
                    "transaction_id": str(a.id),
                    "account_id": str(a.account_id),
                    "amount": float(a.amount),
                    "currency": str(a.currency),
                    "direction": a.direction.value if hasattr(a.direction, "value") else str(a.direction),
                    "activity_type": a.activity_type.value if hasattr(a.activity_type, "value") else str(a.activity_type),
                    "timestamp_utc": a.timestamp_utc.isoformat() if hasattr(a.timestamp_utc, "isoformat") else str(a.timestamp_utc),
                    "category": a.category,
                    "channel": a.channel,
                    "counterparty_name": a.counterparty_name,
                    "reference_id": a.reference_id,
                    "balance_after": float(a.balance_after) if a.balance_after is not None else None,
                    "provenance": a.provenance.value if hasattr(a.provenance, "value") else str(a.provenance),
                })

            if snapshot_time:
                snap_dt = FeatureBuilder._parse_timestamp(snapshot_time)
            else:
                snap_dt = FeatureBuilder._parse_timestamp(act_dicts[-1]["timestamp_utc"])

            builder = FeatureBuilder(act_dicts)
            features = builder.build_snapshot_features(snap_dt)
            features["current_balance"] = current_balance

            commitments = self.recurring_detector.detect(act_dicts, snap_dt.isoformat())
            forecast = self.forecast_model.predict_snapshot(features)

            return {
                "user_id": account_id,
                "snapshot_time": snap_dt.isoformat(),
                "current_balance": current_balance,
                "features": features,
                "commitments": commitments,
                "forecast": forecast,
            }
        finally:
            session.close()

    def get_recent_activities(
        self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieve observed activities from database tables."""
        from app.models.activity import FinancialActivityModel

        session = self.session_factory()
        try:
            query = session.query(FinancialActivityModel)
            if user_id:
                clean_uid = str(user_id).strip().lower()
                from app.models.account import UserAccount
                user = (
                    session.query(UserAccount)
                    .filter(
                        (UserAccount.account_id == user_id)
                        | (UserAccount.username == clean_uid)
                        | (UserAccount.account_id == f"acc_{clean_uid}")
                        | (UserAccount.account_id == f"usr_{clean_uid}")
                    )
                    .first()
                )
                target_acc_id = user.account_id if user else user_id
                query = query.filter(FinancialActivityModel.account_id == target_acc_id)

            total_count = query.count()
            if total_count == 0:
                return {
                    "total_count": 0,
                    "limit": limit,
                    "offset": offset,
                    "activities": [],
                }

            db_acts = (
                query.order_by(FinancialActivityModel.timestamp_utc.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            activities = []
            for a in db_acts:
                activities.append({
                    "transaction_id": str(a.id),
                    "account_id": str(a.account_id),
                    "timestamp_utc": a.timestamp_utc.isoformat() if hasattr(a.timestamp_utc, "isoformat") else str(a.timestamp_utc),
                    "amount": float(a.amount),
                    "direction": a.direction.value if hasattr(a.direction, "value") else str(a.direction),
                    "category": str(a.category or "GENERAL"),
                    "counterparty_name": a.counterparty_name,
                    "balance_after": float(a.balance_after) if a.balance_after is not None else None,
                })

            return {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "activities": activities,
            }
        finally:
            session.close()


def get_data_provider() -> BaseDataProvider:
    """Factory function for selecting active data provider based on settings."""
    from app.config import settings
    provider_type = getattr(settings, "DATA_PROVIDER", "database").lower()
    if provider_type == "synthetic":
        return SyntheticDataProvider()
    return DatabaseDataProvider()
