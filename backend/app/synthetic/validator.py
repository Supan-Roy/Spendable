"""Validation engine for synthetic datasets.

Verifies strict adherence to data contract invariants, timestamp ordering,
balance progression, uniqueness, and ground truth separation.
"""

from decimal import Decimal
from typing import List, Dict, Any, Tuple
from app.schemas.activity import FinancialActivityCreate
from app.domain.enums import TransactionDirection
from app.synthetic.ground_truth import DatasetGroundTruth


class DataValidationError(Exception):
    """Exception raised when generated synthetic data violates domain invariants."""
    pass


def validate_synthetic_dataset(
    activities: List[Dict[str, Any]],
    ground_truth: DatasetGroundTruth,
) -> Tuple[bool, List[str]]:
    """Validate generated synthetic activities and ground truth consistency.
    
    Raises:
        DataValidationError: If any validation rule fails.
        
    Returns:
        Tuple of (is_valid, list_of_warning_messages).
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not activities:
        raise DataValidationError("Generated dataset contains 0 activities")

    # 1. Check Unique Activity IDs
    seen_ids = set()
    for idx, act in enumerate(activities):
        act_id = act.get("id")
        if not act_id:
            errors.append(f"Activity at index {idx} missing 'id'")
        elif act_id in seen_ids:
            errors.append(f"Duplicate activity ID detected: {act_id}")
        else:
            seen_ids.add(act_id)

    # 2. Check Data Contract Conformance (FinancialActivityCreate)
    for idx, act in enumerate(activities):
        try:
            # Prepare payload for Pydantic validation (excluding extra 'id' field if present)
            payload = {k: v for k, v in act.items() if k != "id"}
            FinancialActivityCreate(**payload)
        except Exception as e:
            errors.append(f"Activity at index {idx} failed FinancialActivityCreate schema: {e}")

    # 3. Check Ground Truth Separation Invariant
    forbidden_ground_truth_keys = {"is_recurring", "planted_rule_id", "persona", "persona_phase", "milestone"}
    for idx, act in enumerate(activities):
        leaked_keys = forbidden_ground_truth_keys.intersection(act.keys())
        if leaked_keys:
            errors.append(f"Activity at index {idx} leaks ground-truth fields: {leaked_keys}")

    # 4. Check Per-User Temporal Ordering & Balance Progression
    activities_by_user: Dict[str, List[Dict[str, Any]]] = {}
    for act in activities:
        user_id = act["account_id"]
        activities_by_user.setdefault(user_id, []).append(act)

    for user_id, user_acts in activities_by_user.items():
        user_gt = ground_truth.users.get(user_id)
        if not user_gt:
            errors.append(f"User {user_id} found in activities but missing in ground truth metadata")
            continue

        prev_timestamp = None
        current_balance = user_gt.starting_balance

        for idx, act in enumerate(user_acts):
            ts = act["timestamp_utc"]
            act_id = act.get("id", f"idx_{idx}")

            # Timestamp non-decreasing check
            if prev_timestamp and ts < prev_timestamp:
                errors.append(f"User {user_id} activity {act_id} timestamp {ts} is out of order (prev: {prev_timestamp})")
            prev_timestamp = ts

            # Amount invariant
            amt = Decimal(str(act["amount"]))
            if amt <= Decimal("0.00"):
                errors.append(f"User {user_id} activity {act_id} amount {amt} must be strictly positive")

            # Balance progression check
            direction = act["direction"]
            if direction == TransactionDirection.INFLOW:
                expected_balance = (current_balance + amt).quantize(Decimal("0.01"))
            elif direction == TransactionDirection.OUTFLOW:
                expected_balance = (current_balance - amt).quantize(Decimal("0.01"))
            else:
                errors.append(f"User {user_id} activity {act_id} has invalid direction: {direction}")
                continue

            balance_after = act.get("balance_after")
            if balance_after is not None:
                dec_balance_after = Decimal(str(balance_after)).quantize(Decimal("0.01"))
                if dec_balance_after != expected_balance:
                    errors.append(
                        f"User {user_id} activity {act_id} balance progression mismatch: "
                        f"expected {expected_balance}, recorded {dec_balance_after} (prev: {current_balance}, amt: {amt}, dir: {direction})"
                    )
                if dec_balance_after < Decimal("0.00"):
                    errors.append(f"User {user_id} activity {act_id} balance_after {dec_balance_after} is negative")

            current_balance = expected_balance

    if errors:
        raise DataValidationError(f"Synthetic dataset validation failed with {len(errors)} error(s):\n" + "\n".join(errors[:10]))

    return True, warnings
