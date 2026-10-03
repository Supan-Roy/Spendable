"""Ground-truth offline evaluator for recurring payment and commitment detection.

Matches observable detected commitments against hidden planted recurring rules
to compute unbiased Precision, Recall, F1, True Positive, False Positive, and False Negative metrics
across user-level TRAIN, VALIDATION, and TEST dataset splits and financial categories.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple, Any
import numpy as np

from app.recurring.detector import RecurringDetector
from app.recurring.schema import (
    CategoryEvaluationMetric,
    DetectionConfig,
    DetectionStatus,
    DetectedCommitment,
    SingleEvaluationMetric,
    EvaluationReport,
)


class RecurringEvaluator:
    """Evaluates detector performance against hidden synthetic ground truth."""

    def __init__(self, ground_truth_data: Dict[str, Any]):
        """Initialize evaluator with dataset ground truth payload."""
        self.ground_truth_data = ground_truth_data
        self.users_gt = ground_truth_data.get("users", {})
        self.user_splits = self._extract_user_splits()

    def _extract_user_splits(self) -> Dict[str, str]:
        """Extract mapping of account_id -> split_name (TRAIN / VALIDATION / TEST)."""
        splits: Dict[str, str] = {}
        for account_id, udata in self.users_gt.items():
            split = udata.get("split_assignment") or udata.get("split") or "TRAIN"
            splits[account_id] = str(split).upper()
        return splits

    def evaluate_split(
        self,
        detector: RecurringDetector,
        transactions: List[Dict[str, Any]],
        snapshot_time: datetime,
        split_name: str,
        direction_filter: str = "OUTFLOW",
    ) -> SingleEvaluationMetric:
        """Evaluate recurring detector on a specific dataset split at snapshot time T.

        Args:
            detector: RecurringDetector instance.
            transactions: Full raw transactions list.
            snapshot_time: Point-in-time snapshot date/time T.
            split_name: Name of split ('TRAIN', 'VALIDATION', or 'TEST').
            direction_filter: 'OUTFLOW' for commitments, 'INFLOW' for income, or 'ALL'.
        """
        split_name_upper = split_name.upper()

        # Identify users belonging to target split
        target_users = {
            uid for uid, sname in self.user_splits.items()
            if sname == split_name_upper
        }

        # Filter transactions for split users
        split_txs = [
            tx for tx in transactions
            if str(tx.get("account_id") or tx.get("user_id")) in target_users
        ]

        # Run detector for target direction
        detected_commitments = detector.detect(
            transactions=split_txs,
            snapshot_time=snapshot_time,
            include_insufficient=False,
            direction_filter=direction_filter,
        )

        # Collect relevant ground truth rules for split users
        gt_rules: List[Dict[str, Any]] = []
        for uid in target_users:
            udata = self.users_gt.get(uid, {})
            rules = udata.get("planted_rules", [])
            for r in rules:
                cat = str(r.get("category") or "").upper()
                act = str(r.get("activity_type") or "").upper()
                is_income_rule = (cat == "INCOME" or act == "SALARY")

                if direction_filter == "OUTFLOW" and not is_income_rule:
                    gt_rules.append(r)
                elif direction_filter == "INFLOW" and is_income_rule:
                    gt_rules.append(r)
                elif direction_filter == "ALL":
                    gt_rules.append(r)

        # Perform bipartite matching
        tp, fp, fn, matched_gt_ids = self._evaluate_matches(
            detected_commitments=detected_commitments,
            gt_rules=gt_rules,
        )

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        strong_count = sum(1 for c in detected_commitments if c.detection_status == DetectionStatus.STRONG)
        moderate_count = sum(1 for c in detected_commitments if c.detection_status == DetectionStatus.MODERATE)

        # Category breakdown evaluation
        category_metrics = self._evaluate_by_category(
            detected_commitments=detected_commitments,
            gt_rules=gt_rules,
        )

        return SingleEvaluationMetric(
            split_name=split_name_upper,
            direction_filter=direction_filter,
            total_users=len(target_users),
            ground_truth_rules_count=len(gt_rules),
            detected_commitments_count=len(detected_commitments),
            strong_commitments_count=strong_count,
            moderate_commitments_count=moderate_count,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            precision=round(prec, 4),
            recall=round(rec, 4),
            f1_score=round(f1, 4),
            category_breakdown=category_metrics,
        )

    def evaluate_all_splits(
        self,
        detector: RecurringDetector,
        transactions: List[Dict[str, Any]],
        snapshot_time: datetime,
        direction_filter: str = "OUTFLOW",
    ) -> EvaluationReport:
        """Run complete offline evaluation report across TRAIN, VALIDATION, and TEST splits."""
        train_m = self.evaluate_split(detector, transactions, snapshot_time, "TRAIN", direction_filter)
        val_m = self.evaluate_split(detector, transactions, snapshot_time, "VALIDATION", direction_filter)
        test_m = self.evaluate_split(detector, transactions, snapshot_time, "TEST", direction_filter)

        snapshot_str = snapshot_time.strftime("%Y-%m-%d %H:%M:%S")

        return EvaluationReport(
            snapshot_time=snapshot_str,
            config=detector.config,
            train_metrics=train_m,
            validation_metrics=val_m,
            test_metrics=test_m,
        )

    def _evaluate_matches(
        self,
        detected_commitments: List[DetectedCommitment],
        gt_rules: List[Dict[str, Any]],
    ) -> Tuple[int, int, int, Set[str]]:
        """Match detected commitments to ground truth rules.

        Returns (TP, FP, FN, matched_gt_rule_ids).
        """
        matched_gt_ids: Set[str] = set()
        matched_det_ids: Set[str] = set()

        for det in detected_commitments:
            det_user = det.user_id
            det_amount = det.expected_amount
            det_interval = det.recurrence_interval.value
            det_cp = (det.counterparty_name or "").lower()
            det_cat = (det.category or "").lower()

            best_match_rule: Optional[Dict[str, Any]] = None
            best_match_score = 0.0

            for rule in gt_rules:
                rule_id = rule["rule_id"]
                if rule_id in matched_gt_ids:
                    continue

                rule_user = str(rule["account_id"])
                if det_user != rule_user:
                    continue

                rule_amount = float(rule["base_amount"])
                rule_interval = str(rule.get("frequency", "MONTHLY")).upper()
                rule_cp = str(rule.get("counterparty_name") or "").lower()
                rule_cat = str(rule.get("category") or "").lower()
                rule_act = str(rule.get("activity_type") or "").lower()

                # 1. Identity match score
                cp_match = False
                if det_cp and rule_cp:
                    if det_cp != rule_cp:
                        continue
                    cp_match = True
                
                cat_match = (det_cat == rule_cat)

                if not (cp_match or cat_match):
                    continue

                # 2. Amount similarity match
                rel_diff = abs(det_amount - rule_amount) / max(rule_amount, 1.0)
                if rel_diff > 0.05:
                    continue

                # 3. Frequency compatibility
                freq_match = (det_interval == rule_interval)
                if not freq_match:
                    continue

                # Match confidence score
                match_score = (1.0 - rel_diff) * (1.5 if cp_match else 1.0) * (1.2 if freq_match else 0.8)

                if match_score > best_match_score:
                    best_match_score = match_score
                    best_match_rule = rule

            if best_match_rule is not None:
                matched_gt_ids.add(best_match_rule["rule_id"])
                matched_det_ids.add(det.commitment_id)

        tp = len(matched_det_ids)
        fp = len(detected_commitments) - tp
        fn = len(gt_rules) - len(matched_gt_ids)

        return tp, fp, fn, matched_gt_ids

    def _evaluate_by_category(
        self,
        detected_commitments: List[DetectedCommitment],
        gt_rules: List[Dict[str, Any]],
    ) -> List[CategoryEvaluationMetric]:
        """Compute category-level evaluation metrics breakdown."""
        categories = set(c.category.upper() for c in detected_commitments)
        categories.update(str(r.get("category") or r.get("activity_type") or "OTHER").upper() for r in gt_rules)

        metrics: List[CategoryEvaluationMetric] = []

        for cat in sorted(categories):
            cat_dets = [c for c in detected_commitments if c.category.upper() == cat]
            cat_rules = [r for r in gt_rules if str(r.get("category") or r.get("activity_type") or "OTHER").upper() == cat]

            if not cat_dets and not cat_rules:
                continue

            tp, fp, fn, _ = self._evaluate_matches(cat_dets, cat_rules)
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0

            metrics.append(
                CategoryEvaluationMetric(
                    category=cat,
                    ground_truth_count=len(cat_rules),
                    detected_count=len(cat_dets),
                    true_positives=tp,
                    false_positives=fp,
                    false_negatives=fn,
                    precision=round(prec, 4),
                    recall=round(rec, 4),
                )
            )

        return metrics
