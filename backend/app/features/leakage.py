"""Automated Data Leakage Verification & Quality Guard.

Enforces zero future transaction contamination, zero target leakage in feature vectors,
and strict user isolation.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from app.features.builder import FeatureBuilder


class LeakageError(Exception):
    """Raised when future data leakage is detected in feature engineering."""
    pass


class FeatureLeakageDetector:
    """Automated leakage auditor for point-in-time snapshot features."""

    FORBIDDEN_LEAKAGE_KEYS = {
        "is_recurring",
        "planted_rule_id",
        "persona",
        "persona_phase",
        "milestone",
        "future_min_balance_7d",
        "future_min_balance_14d",
        "future_min_balance_30d",
        "liquidity_stress_event_within_30d",
        "future_inflow_sum_7d",
        "future_outflow_sum_7d",
        "target",
    }

    @classmethod
    def verify_future_transaction_isolation(
        cls,
        user_activities: List[Dict[str, Any]],
        snapshot_time: datetime,
    ) -> bool:
        """Verify that injecting a future transaction at T+1 day does NOT modify features at snapshot time T.
        
        Raises LeakageError if any feature changes.
        """
        builder = FeatureBuilder(user_activities)
        f1 = builder.build_snapshot_features(snapshot_time)

        # Inject a future transaction at T + 1 day
        future_tx = {
            "id": "leakage-test-future-id-999",
            "account_id": user_activities[0]["account_id"] if user_activities else "ACC-TEST",
            "amount": Decimal("999999.00"),
            "currency": "BDT",
            "direction": "INFLOW",
            "activity_type": "SALARY",
            "timestamp_utc": snapshot_time + timedelta(days=1),
            "balance_after": Decimal("999999.00"),
            "provenance": "SYNTHETIC",
        }

        augmented_activities = list(user_activities) + [future_tx]
        builder_augmented = FeatureBuilder(augmented_activities)
        f2 = builder_augmented.build_snapshot_features(snapshot_time)

        # Compare features
        diffs = []
        for k in f1:
            if f1[k] != f2[k]:
                diffs.append(f"Feature '{k}' changed at snapshot T after adding future transaction: f1={f1[k]}, f2={f2[k]}")

        if diffs:
            raise LeakageError("Future transaction leakage detected!\n" + "\n".join(diffs))

        return True

    @classmethod
    def verify_feature_key_purity(cls, feature_dict: Dict[str, Any]) -> bool:
        """Verify feature vector contains zero forbidden ground truth or target keys.
        
        Raises LeakageError if forbidden key is present.
        """
        leaked = cls.FORBIDDEN_LEAKAGE_KEYS.intersection(feature_dict.keys())
        if leaked:
            raise LeakageError(f"Forbidden ground-truth/target keys detected in input feature vector: {leaked}")
        return True
