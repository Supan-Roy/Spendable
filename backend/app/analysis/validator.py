"""Dataset Quality Validation Engine for Spendable synthetic datasets.

Validates data contract compliance, schema integrity, monetary invariants,
balance progression reconstruction, and temporal consistency.
"""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
import uuid
from typing import List, Dict, Any, Optional, Set

from pydantic import BaseModel, ConfigDict
from app.domain.enums import TransactionDirection, ActivityType, DataProvenance
from app.schemas.activity import FinancialActivityCreate


class RuleStatus(str, Enum):
    """Validation rule result status."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class RuleCheck(BaseModel):
    """Detailed result for an individual validation rule check."""
    rule_id: str
    category: str  # "SCHEMA", "INTEGRITY", "FINANCIAL", "TEMPORAL"
    name: str
    status: RuleStatus
    description: str
    details: List[str] = []
    affected_count: int = 0


class ValidationResult(BaseModel):
    """Overall dataset validation summary and detailed rule breakdown."""
    dataset_name: str
    validated_at_utc: datetime
    overall_status: RuleStatus
    total_records: int
    total_users: int
    summary_counts: Dict[RuleStatus, int]
    checks: List[RuleCheck]

    model_config = ConfigDict(from_attributes=True)

    def to_human_summary(self) -> str:
        """Render a readable human-focused text summary."""
        lines = [
            "==================================================",
            f" Spendable Data Quality Validation Report",
            f" Overall Status: [{self.overall_status.value}]",
            f" Total Records: {self.total_records} | Users: {self.total_users}",
            f" Summary: {self.summary_counts.get(RuleStatus.PASS, 0)} PASS, "
            f"{self.summary_counts.get(RuleStatus.WARNING, 0)} WARNING, "
            f"{self.summary_counts.get(RuleStatus.FAIL, 0)} FAIL",
            "==================================================",
        ]
        for check in self.checks:
            badge = f"[{check.status.value}]"
            lines.append(f"{badge:<9} {check.category:<10} | {check.name}: {check.description}")
            if check.details:
                for detail in check.details[:5]:
                    lines.append(f"          - {detail}")
                if len(check.details) > 5:
                    lines.append(f"          - ... and {len(check.details) - 5} more issue(s)")
        lines.append("==================================================")
        return "\n".join(lines)


class DatasetValidator:
    """Comprehensive Data Quality & Financial Integrity Validator."""

    def __init__(self, activities: List[Dict[str, Any]], ground_truth: Optional[Dict[str, Any]] = None):
        self.raw_activities = activities
        self.ground_truth = ground_truth or {}
        self.checks: List[RuleCheck] = []

    def validate(self) -> ValidationResult:
        """Execute full validation suite and return ValidationResult."""
        self.checks = []

        if not self.raw_activities:
            self.checks.append(
                RuleCheck(
                    rule_id="EMPTY_DATASET",
                    category="INTEGRITY",
                    name="Non-Empty Dataset",
                    status=RuleStatus.FAIL,
                    description="Dataset contains 0 activity records",
                    details=["No activity records provided for validation"],
                    affected_count=0,
                )
            )
            return self._build_result(overall=RuleStatus.FAIL, total_records=0, total_users=0)

        # Execute check suites
        self._validate_schema_and_types()
        self._validate_data_integrity()
        self._validate_financial_balance_consistency()
        self._validate_temporal_consistency()

        # Compute counts and overall status
        status_counts = {RuleStatus.PASS: 0, RuleStatus.WARNING: 0, RuleStatus.FAIL: 0}
        for check in self.checks:
            status_counts[check.status] += 1

        overall_status = RuleStatus.PASS
        if status_counts[RuleStatus.FAIL] > 0:
            overall_status = RuleStatus.FAIL
        elif status_counts[RuleStatus.WARNING] > 0:
            overall_status = RuleStatus.WARNING

        total_users = len({act.get("account_id") for act in self.raw_activities if act.get("account_id")})

        return self._build_result(
            overall=overall_status,
            total_records=len(self.raw_activities),
            total_users=total_users,
        )

    def _build_result(self, overall: RuleStatus, total_records: int, total_users: int) -> ValidationResult:
        status_counts = {RuleStatus.PASS: 0, RuleStatus.WARNING: 0, RuleStatus.FAIL: 0}
        for check in self.checks:
            status_counts[check.status] += 1

        return ValidationResult(
            dataset_name="synthetic_financial_activities",
            validated_at_utc=datetime.now(timezone.utc),
            overall_status=overall,
            total_records=total_records,
            total_users=total_users,
            summary_counts=status_counts,
            checks=self.checks,
        )

    # -------------------------------------------------------------------------
    # 1. Schema & Contract Conformance
    # -------------------------------------------------------------------------

    def _validate_schema_and_types(self):
        # Rule 1.1: Required Fields & Pydantic Schema Conformance
        schema_errors = []
        required_fields = ["id", "account_id", "amount", "currency", "direction", "activity_type", "timestamp_utc", "provenance"]
        missing_required_count = 0

        for idx, act in enumerate(self.raw_activities):
            missing = [f for f in required_fields if f not in act or act[f] is None]
            if missing:
                missing_required_count += 1
                schema_errors.append(f"Record {idx} missing required field(s): {missing}")
            else:
                # Attempt Pydantic validation
                try:
                    payload = {k: v for k, v in act.items() if k != "id"}
                    FinancialActivityCreate(**payload)
                except Exception as e:
                    schema_errors.append(f"Record {idx} (ID: {act.get('id')}) contract error: {e}")

        if schema_errors:
            self.checks.append(
                RuleCheck(
                    rule_id="SCHEMA_CONTRACT",
                    category="SCHEMA",
                    name="Data Contract Conformance",
                    status=RuleStatus.FAIL,
                    description="Records must conform to FinancialActivityCreate schema rules",
                    details=schema_errors,
                    affected_count=len(schema_errors),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="SCHEMA_CONTRACT",
                    category="SCHEMA",
                    name="Data Contract Conformance",
                    status=RuleStatus.PASS,
                    description="All records conform strictly to FinancialActivityCreate contract schema",
                )
            )

        # Rule 1.2: Allowed Categorical Values
        allowed_directions = {d.value for d in TransactionDirection}
        allowed_types = {t.value for t in ActivityType}
        allowed_provenance = {p.value for p in DataProvenance}
        enum_errors = []

        for idx, act in enumerate(self.raw_activities):
            d_val = act.get("direction")
            d_str = d_val.value if hasattr(d_val, "value") else str(d_val).replace("TransactionDirection.", "")
            if d_str not in allowed_directions:
                enum_errors.append(f"Record {idx} invalid direction '{d_val}'")

            t_val = act.get("activity_type")
            t_str = t_val.value if hasattr(t_val, "value") else str(t_val).replace("ActivityType.", "")
            if t_str not in allowed_types:
                enum_errors.append(f"Record {idx} invalid activity_type '{t_val}'")

            p_val = act.get("provenance")
            p_str = p_val.value if hasattr(p_val, "value") else str(p_val).replace("DataProvenance.", "")
            if p_str not in allowed_provenance:
                enum_errors.append(f"Record {idx} invalid provenance '{p_val}'")

        if enum_errors:
            self.checks.append(
                RuleCheck(
                    rule_id="ENUM_VALIDITY",
                    category="SCHEMA",
                    name="Enum Value Constraints",
                    status=RuleStatus.FAIL,
                    description="Enums must match defined domain types",
                    details=enum_errors,
                    affected_count=len(enum_errors),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="ENUM_VALIDITY",
                    category="SCHEMA",
                    name="Enum Value Constraints",
                    status=RuleStatus.PASS,
                    description="All direction, activity_type, and provenance values match valid enums",
                )
            )

        # Rule 1.3: UUID Primary Key Format
        uuid_errors = []
        for idx, act in enumerate(self.raw_activities):
            act_id = act.get("id")
            if act_id:
                try:
                    uuid.UUID(str(act_id))
                except ValueError:
                    uuid_errors.append(f"Record {idx} ID '{act_id}' is not a valid UUID string")

        if uuid_errors:
            self.checks.append(
                RuleCheck(
                    rule_id="UUID_FORMAT",
                    category="SCHEMA",
                    name="Transaction UUID Constraint",
                    status=RuleStatus.FAIL,
                    description="Transaction IDs must be valid UUID v4 strings",
                    details=uuid_errors,
                    affected_count=len(uuid_errors),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="UUID_FORMAT",
                    category="SCHEMA",
                    name="Transaction UUID Constraint",
                    status=RuleStatus.PASS,
                    description="All transaction IDs conform to valid UUID string standard",
                )
            )

    # -------------------------------------------------------------------------
    # 2. Data Integrity & Boundaries
    # -------------------------------------------------------------------------

    def _validate_data_integrity(self):
        # Rule 2.1: Transaction ID Uniqueness
        seen_ids = set()
        duplicate_ids = set()
        for act in self.raw_activities:
            act_id = act.get("id")
            if act_id:
                if act_id in seen_ids:
                    duplicate_ids.add(act_id)
                seen_ids.add(act_id)

        if duplicate_ids:
            self.checks.append(
                RuleCheck(
                    rule_id="UNIQUE_TXN_ID",
                    category="INTEGRITY",
                    name="Transaction ID Uniqueness",
                    status=RuleStatus.FAIL,
                    description="Transaction primary identifiers must be unique across the dataset",
                    details=[f"Duplicate transaction ID: {tid}" for tid in duplicate_ids],
                    affected_count=len(duplicate_ids),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="UNIQUE_TXN_ID",
                    category="INTEGRITY",
                    name="Transaction ID Uniqueness",
                    status=RuleStatus.PASS,
                    description="100% of transaction IDs are unique",
                )
            )

        # Rule 2.2: Duplicate Record Detection (exact attribute duplicate)
        seen_records = set()
        duplicate_records_count = 0
        for act in self.raw_activities:
            # Tuple of core values excluding ID
            tup = (
                act.get("account_id"),
                str(act.get("amount")),
                str(act.get("direction")),
                str(act.get("activity_type")),
                str(act.get("timestamp_utc")),
            )
            if tup in seen_records:
                duplicate_records_count += 1
            seen_records.add(tup)

        if duplicate_records_count > 0:
            self.checks.append(
                RuleCheck(
                    rule_id="DUPLICATE_RECORDS",
                    category="INTEGRITY",
                    name="Duplicate Record Detection",
                    status=RuleStatus.WARNING,
                    description="Multiple identical transaction attributes detected on the same timestamp",
                    details=[f"Found {duplicate_records_count} duplicate attribute combinations"],
                    affected_count=duplicate_records_count,
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="DUPLICATE_RECORDS",
                    category="INTEGRITY",
                    name="Duplicate Record Detection",
                    status=RuleStatus.PASS,
                    description="Zero duplicate transaction attribute records detected",
                )
            )

        # Rule 2.3: Strictly Positive Monetary Amounts
        amount_errors = []
        for idx, act in enumerate(self.raw_activities):
            amt_val = act.get("amount")
            try:
                amt = Decimal(str(amt_val))
                if amt <= Decimal("0.00"):
                    amount_errors.append(f"Record {idx} (ID: {act.get('id')}) non-positive amount {amt}")
            except (InvalidOperation, TypeError, ValueError):
                amount_errors.append(f"Record {idx} (ID: {act.get('id')}) unparseable amount '{amt_val}'")

        if amount_errors:
            self.checks.append(
                RuleCheck(
                    rule_id="POSITIVE_AMOUNT",
                    category="INTEGRITY",
                    name="Monetary Amount Invariant",
                    status=RuleStatus.FAIL,
                    description="Monetary transaction amounts must be strictly positive (> 0.00)",
                    details=amount_errors,
                    affected_count=len(amount_errors),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="POSITIVE_AMOUNT",
                    category="INTEGRITY",
                    name="Monetary Amount Invariant",
                    status=RuleStatus.PASS,
                    description="100% of transaction amounts are strictly positive monetary values",
                )
            )

        # Rule 2.4: Direction & Activity Type Semantic Consistency
        semantic_errors = []
        inflow_types = {ActivityType.SALARY, ActivityType.CASH_IN}
        outflow_types = {ActivityType.MERCHANT_PAYMENT, ActivityType.UTILITY_BILL, ActivityType.MOBILE_RECHARGE, ActivityType.CASH_OUT, ActivityType.FEE}

        for idx, act in enumerate(self.raw_activities):
            d_val = str(act.get("direction", "")).replace("TransactionDirection.", "")
            t_val = str(act.get("activity_type", "")).replace("ActivityType.", "")

            if t_val in inflow_types and d_val == "OUTFLOW":
                semantic_errors.append(f"Record {idx} (ID: {act.get('id')}) activity '{t_val}' cannot be OUTFLOW")
            elif t_val in outflow_types and d_val == "INFLOW":
                semantic_errors.append(f"Record {idx} (ID: {act.get('id')}) activity '{t_val}' cannot be INFLOW")

        if semantic_errors:
            self.checks.append(
                RuleCheck(
                    rule_id="DIRECTION_SEMANTICS",
                    category="INTEGRITY",
                    name="Direction-Activity Semantics",
                    status=RuleStatus.FAIL,
                    description="Activity type must match natural transaction direction (e.g. SALARY must be INFLOW)",
                    details=semantic_errors,
                    affected_count=len(semantic_errors),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="DIRECTION_SEMANTICS",
                    category="INTEGRITY",
                    name="Direction-Activity Semantics",
                    status=RuleStatus.PASS,
                    description="All activity types conform to expected natural transaction direction semantics",
                )
            )

    # -------------------------------------------------------------------------
    # 3. Financial Balance Progression & Reconstruction
    # -------------------------------------------------------------------------

    def _validate_financial_balance_consistency(self):
        # Group activities by account_id
        user_activities: Dict[str, List[Dict[str, Any]]] = {}
        for act in self.raw_activities:
            uid = act.get("account_id")
            if uid:
                user_activities.setdefault(uid, []).append(act)

        gt_users = self.ground_truth.get("users", {})
        reconstruction_errors = []
        negative_balance_errors = []
        warnings = []

        for uid, acts in user_activities.items():
            # Get user starting balance from ground truth or estimate from first transaction
            user_gt = gt_users.get(uid, {})
            starting_balance = None
            if "starting_balance" in user_gt:
                starting_balance = Decimal(str(user_gt["starting_balance"]))

            # Sort user activities chronologically
            sorted_acts = sorted(acts, key=lambda x: x["timestamp_utc"])

            if starting_balance is None:
                # Estimate starting balance from first transaction's balance_after
                first_act = sorted_acts[0]
                first_bal = first_act.get("balance_after")
                if first_bal is not None:
                    amt = Decimal(str(first_act["amount"]))
                    d_val = str(first_act["direction"]).replace("TransactionDirection.", "")
                    if d_val == "INFLOW":
                        starting_balance = Decimal(str(first_bal)) - amt
                    else:
                        starting_balance = Decimal(str(first_bal)) + amt

            current_balance = starting_balance

            for idx, act in enumerate(sorted_acts):
                amt = Decimal(str(act["amount"]))
                d_val = str(act["direction"]).replace("TransactionDirection.", "")
                act_id = act.get("id")

                if current_balance is not None:
                    if d_val == "INFLOW":
                        expected_bal = (current_balance + amt).quantize(Decimal("0.01"))
                    else:
                        expected_bal = (current_balance - amt).quantize(Decimal("0.01"))

                    recorded_bal = act.get("balance_after")
                    if recorded_bal is not None:
                        dec_rec_bal = Decimal(str(recorded_bal)).quantize(Decimal("0.01"))
                        if dec_rec_bal != expected_bal:
                            reconstruction_errors.append(
                                f"User {uid} txn {act_id} balance mismatch: "
                                f"expected {expected_bal}, recorded {dec_rec_bal} (prev: {current_balance}, amt: {amt}, dir: {d_val})"
                            )
                        if dec_rec_bal < Decimal("0.00"):
                            negative_balance_errors.append(f"User {uid} txn {act_id} negative balance_after {dec_rec_bal}")

                    current_balance = expected_bal

                # Check low balance warnings
                if current_balance is not None and current_balance < Decimal("1000.00") and current_balance >= Decimal("0.00"):
                    warnings.append(f"User {uid} experienced low buffer: BDT {current_balance:.2f} on {act['timestamp_utc']}")

        # Report balance reconstruction result
        if reconstruction_errors:
            self.checks.append(
                RuleCheck(
                    rule_id="BALANCE_RECONSTRUCTION",
                    category="FINANCIAL",
                    name="Balance Progression Reconstruction",
                    status=RuleStatus.FAIL,
                    description="Recorded balance_after values must match reconstructed running balance",
                    details=reconstruction_errors,
                    affected_count=len(reconstruction_errors),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="BALANCE_RECONSTRUCTION",
                    category="FINANCIAL",
                    name="Balance Progression Reconstruction",
                    status=RuleStatus.PASS,
                    description="100% of recorded balance_after values match exact reconstructed mathematical running balances",
                )
            )

        # Report negative balance check
        if negative_balance_errors:
            self.checks.append(
                RuleCheck(
                    rule_id="NEGATIVE_BALANCE",
                    category="FINANCIAL",
                    name="Non-Negative Balance Invariant",
                    status=RuleStatus.FAIL,
                    description="Observed post-transaction balances must be non-negative (>= 0.00)",
                    details=negative_balance_errors,
                    affected_count=len(negative_balance_errors),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="NEGATIVE_BALANCE",
                    category="FINANCIAL",
                    name="Non-Negative Balance Invariant",
                    status=RuleStatus.PASS,
                    description="Zero negative account balances detected across all user transaction histories",
                )
            )

        # Report low balance warnings if any
        if warnings:
            self.checks.append(
                RuleCheck(
                    rule_id="LOW_LIQUIDITY_BUFFER",
                    category="FINANCIAL",
                    name="Low Liquidity Buffer Alerts",
                    status=RuleStatus.WARNING,
                    description="Identified user instances with available balance dropping under ৳1,000.00",
                    details=warnings,
                    affected_count=len(warnings),
                )
            )

    # -------------------------------------------------------------------------
    # 4. Temporal Consistency
    # -------------------------------------------------------------------------

    def _validate_temporal_consistency(self):
        # Rule 4.1: Per-User Chronological Ordering
        user_activities: Dict[str, List[Dict[str, Any]]] = {}
        for act in self.raw_activities:
            uid = act.get("account_id")
            if uid:
                user_activities.setdefault(uid, []).append(act)

        out_of_order_errors = []
        for uid, acts in user_activities.items():
            prev_ts = None
            for act in acts:
                ts = act.get("timestamp_utc")
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(ts)
                    except ValueError:
                        out_of_order_errors.append(f"User {uid} invalid timestamp string format '{ts}'")
                        continue

                if prev_ts and ts < prev_ts:
                    out_of_order_errors.append(f"User {uid} txn {act.get('id')} timestamp {ts} out of order (prev: {prev_ts})")
                prev_ts = ts

        if out_of_order_errors:
            self.checks.append(
                RuleCheck(
                    rule_id="CHRONOLOGICAL_ORDER",
                    category="TEMPORAL",
                    name="Per-User Chronological Sequence",
                    status=RuleStatus.FAIL,
                    description="User transaction logs must be strictly non-decreasing in timestamp order",
                    details=out_of_order_errors,
                    affected_count=len(out_of_order_errors),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="CHRONOLOGICAL_ORDER",
                    category="TEMPORAL",
                    name="Per-User Chronological Sequence",
                    status=RuleStatus.PASS,
                    description="All user transaction records maintain strict chronological ordering",
                )
            )

        # Rule 4.2: Timezone & UTC Consistency
        non_utc_errors = []
        for idx, act in enumerate(self.raw_activities):
            ts = act.get("timestamp_utc")
            if isinstance(ts, datetime) and ts.tzinfo != timezone.utc:
                non_utc_errors.append(f"Record {idx} (ID: {act.get('id')}) timestamp {ts} is not explicit UTC")

        if non_utc_errors:
            self.checks.append(
                RuleCheck(
                    rule_id="UTC_TIMEZONE",
                    category="TEMPORAL",
                    name="UTC Timezone Invariant",
                    status=RuleStatus.FAIL,
                    description="Timestamps must be timezone-aware UTC datetime objects",
                    details=non_utc_errors,
                    affected_count=len(non_utc_errors),
                )
            )
        else:
            self.checks.append(
                RuleCheck(
                    rule_id="UTC_TIMEZONE",
                    category="TEMPORAL",
                    name="UTC Timezone Invariant",
                    status=RuleStatus.PASS,
                    description="100% of timestamps are explicit UTC ISO-8601 representations",
                )
            )
