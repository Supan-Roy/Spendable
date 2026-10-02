"""Recurring payment and financial commitment detector.

Identifies repeated financial commitments (e.g., rent, utility bills, subscriptions, salary)
using point-in-time observable transaction history up to snapshot cutoff T.
No ground truth labels or future transaction data are used.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from app.recurring.schema import (
    DetectionConfig,
    DetectionEvidence,
    DetectionStatus,
    DetectedCommitment,
    RecurrenceIntervalType,
)

# Standard recurring financial commitment categories (high prior confidence)
CORE_COMMITMENT_CATEGORIES = {
    "HOUSING", "UTILITIES", "TELECOM", "DEBT_PAYMENT", "SOFTWARE",
    "FITNESS", "FAMILY_SUPPORT", "INCOME", "SALARY", "RENT",
    "INSURANCE", "EDUCATION", "SUBSCRIPTION", "UTILITY_BILL"
}


class RecurringDetector:
    """Deterministic, point-in-time baseline recurring payment detector."""

    def __init__(self, config: Optional[DetectionConfig] = None):
        """Initialize detector with configurable thresholds and weights."""
        self.config = config or DetectionConfig()

    def detect(
        self,
        transactions: List[Dict[str, Any]],
        snapshot_time: datetime,
        include_insufficient: bool = False,
    ) -> List[DetectedCommitment]:
        """Detect recurring financial commitments observable at snapshot time T.

        Args:
            transactions: Raw transaction list from transaction feed.
            snapshot_time: Point-in-time cutoff date/time T.
            include_insufficient: If True, include INSUFFICIENT_EVIDENCE candidates in result.

        Returns:
            List of DetectedCommitment objects sorted by confidence score descending.
        """
        snapshot_dt = self._parse_datetime(snapshot_time)

        # Filter strictly to transactions occurring at or before snapshot_time T
        filtered_txs = [
            tx for tx in transactions
            if self._extract_tx_datetime(tx) <= snapshot_dt
        ]

        if not filtered_txs:
            return []

        # Group transactions by candidate key
        grouped_candidates = self._group_transactions(filtered_txs)

        detected_commitments: List[DetectedCommitment] = []

        for group_key, tx_list in grouped_candidates.items():
            commitment = self._evaluate_candidate_group(
                group_key=group_key,
                tx_list=tx_list,
                snapshot_time=snapshot_dt,
            )

            if commitment is None:
                continue

            if (
                commitment.detection_status != DetectionStatus.INSUFFICIENT_EVIDENCE
                or include_insufficient
            ):
                detected_commitments.append(commitment)

        # Sort commitments by confidence score descending
        detected_commitments.sort(key=lambda c: c.confidence_score, reverse=True)
        return detected_commitments

    def _group_transactions(
        self, transactions: List[Dict[str, Any]]
    ) -> Dict[Tuple[str, str, str, str, str], List[Dict[str, Any]]]:
        """Group transactions by user and counterparty/category identity.

        Returns map of key -> transaction list.
        Key tuple format: (user_id, group_type, key_name, category, direction)
        """
        grouped: Dict[Tuple[str, str, str, str, str], List[Dict[str, Any]]] = {}

        for tx in transactions:
            user_id = str(tx.get("account_id") or tx.get("user_id") or "")
            counterparty = str(tx.get("counterparty_name") or "").strip()
            category = str(tx.get("category") or tx.get("activity_type") or "OTHER").strip().upper()
            direction = str(tx.get("direction") or "OUTFLOW").strip().upper()

            # Determine whether counterparty is informative
            has_counterparty = bool(
                counterparty
                and counterparty.lower() not in ("none", "n/a", "unknown", "null", "", "none/specified")
            )

            if has_counterparty:
                group_key = (user_id, "COUNTERPARTY", counterparty, category, direction)
            else:
                group_key = (user_id, "CATEGORY", category, category, direction)

            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(tx)

        return grouped

    def _evaluate_candidate_group(
        self,
        group_key: Tuple[str, str, str, str, str],
        tx_list: List[Dict[str, Any]],
        snapshot_time: datetime,
    ) -> Optional[DetectedCommitment]:
        """Evaluate a single transaction candidate group for recurrence patterns."""
        user_id, group_type, key_name, category, direction = group_key

        if not tx_list:
            return None

        # Sort transactions chronologically
        tx_sorted = sorted(tx_list, key=self._extract_tx_datetime)
        n_occurrences = len(tx_sorted)

        # Extract timestamps and monetary amounts
        timestamps = [self._extract_tx_datetime(t) for t in tx_sorted]
        amounts = [abs(float(t.get("amount", 0.0))) for t in tx_sorted]

        # 1. Interval Regularity Analysis
        if n_occurrences >= 2:
            intervals = [
                (timestamps[i] - timestamps[i - 1]).total_seconds() / 86400.0
                for i in range(1, n_occurrences)
            ]
            median_interval = float(np.median(intervals))
            mean_interval = float(np.mean(intervals))
            std_interval = float(np.std(intervals)) if len(intervals) >= 2 else 0.0
            interval_cv = (std_interval / mean_interval) if mean_interval > 0 else 0.0
        else:
            intervals = []
            median_interval = 30.0
            mean_interval = 30.0
            std_interval = 0.0
            interval_cv = 1.0

        # Classify recurrence interval pattern
        interval_type, target_days = self._classify_interval_type(median_interval)

        # Interval sub-score calculation
        if n_occurrences < 2:
            interval_consistency_score = 0.0
        elif interval_type == RecurrenceIntervalType.IRREGULAR:
            # Irregular interval penalty: low interval score
            cv_score = max(0.0, 1.0 - interval_cv * 1.5)
            interval_consistency_score = min(0.3, max(0.0, 0.3 * cv_score))
        else:
            rel_dev = abs(median_interval - target_days) / target_days if target_days > 0 else 0.5
            cv_score = max(0.0, 1.0 - interval_cv * 1.2)
            dev_score = max(0.0, 1.0 - rel_dev * 2.0)
            interval_consistency_score = min(1.0, max(0.0, 0.65 * cv_score + 0.35 * dev_score))

        # 2. Amount Consistency Analysis
        mean_amount = float(np.mean(amounts))
        median_amount = float(np.median(amounts))
        std_amount = float(np.std(amounts)) if n_occurrences >= 2 else 0.0
        amount_cv = (std_amount / mean_amount) if mean_amount > 0 else 0.0

        amount_consistency_score = min(1.0, max(0.0, 1.0 - amount_cv * 1.5))

        # 3. Recency & Active Duration Analysis
        last_tx_time = timestamps[-1]
        first_tx_time = timestamps[0]

        recency_days = max(0.0, (snapshot_time - last_tx_time).total_seconds() / 86400.0)
        active_duration_days = max(0.0, (last_tx_time - first_tx_time).total_seconds() / 86400.0)

        expected_window = max(median_interval * 1.6, 30.0)
        recency_score = min(1.0, max(0.0, 1.0 - (recency_days / expected_window)))

        # 4. Occurrence Count Score
        count_score = min(1.0, n_occurrences / 8.0)

        # 5. Category Domain Prior Adjustment
        category_boost = 1.0
        if category in CORE_COMMITMENT_CATEGORIES:
            category_boost = 1.1

        # Composite Confidence Score calculation
        raw_score = (
            self.config.weight_interval * interval_consistency_score
            + self.config.weight_amount * amount_consistency_score
            + self.config.weight_count * count_score
            + self.config.weight_recency * recency_score
        )
        confidence_score = round(min(1.0, max(0.0, raw_score * category_boost)), 4)

        # 6. Determine Categorical Status
        if n_occurrences < self.config.min_occurrences:
            status = DetectionStatus.INSUFFICIENT_EVIDENCE
        elif confidence_score >= self.config.strong_threshold:
            status = DetectionStatus.STRONG
        elif confidence_score >= self.config.moderate_threshold:
            status = DetectionStatus.MODERATE
        else:
            status = DetectionStatus.INSUFFICIENT_EVIDENCE

        # 7. Next Expected Date Calculation
        next_expected_dt = last_tx_time + timedelta(days=median_interval)
        while next_expected_dt < snapshot_time:
            next_expected_dt += timedelta(days=median_interval)
        next_expected_date_str = next_expected_dt.strftime("%Y-%m-%d")

        # 8. Deterministic Identifier
        counterparty_name = key_name if group_type == "COUNTERPARTY" else None
        primary_activity_type = str(tx_sorted[-1].get("activity_type") or category).upper()

        hash_str = f"{user_id}:{counterparty_name or 'NONE'}:{category}:{interval_type.value}"
        commitment_id = f"comm_{hashlib.md5(hash_str.encode('utf-8')).hexdigest()[:12]}"

        evidence = DetectionEvidence(
            occurrences=n_occurrences,
            median_interval_days=round(median_interval, 2),
            mean_interval_days=round(mean_interval, 2),
            std_interval_days=round(std_interval, 2),
            interval_cv=round(interval_cv, 4),
            mean_amount=round(mean_amount, 2),
            median_amount=round(median_amount, 2),
            std_amount=round(std_amount, 2),
            amount_cv=round(amount_cv, 4),
            recency_days=round(recency_days, 2),
            active_duration_days=round(active_duration_days, 2),
            interval_consistency_score=round(interval_consistency_score, 4),
            amount_consistency_score=round(amount_consistency_score, 4),
            recency_score=round(recency_score, 4),
            count_score=round(count_score, 4),
        )

        return DetectedCommitment(
            commitment_id=commitment_id,
            user_id=user_id,
            counterparty_name=counterparty_name,
            category=category,
            activity_type=primary_activity_type,
            direction=direction,
            expected_amount=round(median_amount, 2),
            recurrence_interval=interval_type,
            median_interval_days=round(median_interval, 2),
            next_expected_date=next_expected_date_str,
            amount_variability=round(std_amount, 2),
            occurrence_count=n_occurrences,
            confidence_score=confidence_score,
            detection_status=status,
            evidence=evidence,
        )

    def _classify_interval_type(
        self, median_interval: float
    ) -> Tuple[RecurrenceIntervalType, float]:
        """Classify interval into standard frequency band and return target days."""
        if 5.0 <= median_interval <= 9.0:
            return RecurrenceIntervalType.WEEKLY, 7.0
        elif 12.0 <= median_interval <= 17.0:
            return RecurrenceIntervalType.BIWEEKLY, 14.0
        elif 25.0 <= median_interval <= 35.0:
            return RecurrenceIntervalType.MONTHLY, 30.0
        elif 80.0 <= median_interval <= 105.0:
            return RecurrenceIntervalType.QUARTERLY, 90.0
        elif 340.0 <= median_interval <= 380.0:
            return RecurrenceIntervalType.ANNUAL, 365.0
        else:
            return RecurrenceIntervalType.IRREGULAR, max(median_interval, 1.0)

    def _extract_tx_datetime(self, tx: Dict[str, Any]) -> datetime:
        """Extract datetime object from transaction record."""
        val = tx.get("timestamp_utc") or tx.get("timestamp")
        return self._parse_datetime(val)

    def _parse_datetime(self, val: Any) -> datetime:
        """Parse datetime object or ISO string cleanly into UTC/naive datetime."""
        if isinstance(val, datetime):
            dt = val
        else:
            dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))

        return dt.replace(tzinfo=None)
