"""Ground truth representation for synthetic financial datasets.

Ground truth metadata captures internal generator state, planted recurring rules,
persona allocations, behavioral phase shifts, user dataset splits, and future evaluation outcomes.
Ground truth is maintained strictly separately from observable raw transaction feeds.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict
from app.domain.enums import ActivityType
from app.synthetic.enums import PersonaType, RecurrenceFrequency, MilestoneType


class PlantedRuleGroundTruth(BaseModel):
    """Metadata describing an intentionally planted recurring financial pattern."""
    rule_id: str
    account_id: str
    activity_type: ActivityType
    category: Optional[str] = None
    counterparty_name: Optional[str] = None
    frequency: RecurrenceFrequency
    target_day: Optional[int] = None  # e.g., day of month (1-28) or day of week (0-6)
    base_amount: Decimal
    amount_variance_pct: float
    expected_occurrences: int = 0


class BehaviorMilestoneGroundTruth(BaseModel):
    """Metadata describing an intentionally introduced behavioral regime change."""
    account_id: str
    milestone_type: MilestoneType
    effective_date: datetime
    description: str
    params: Dict[str, Any] = {}


class ActivityAnnotationGroundTruth(BaseModel):
    """Ground truth mapping annotation for an individual generated transaction."""
    activity_id: str
    account_id: str
    persona: PersonaType
    planted_rule_id: Optional[str] = None
    is_planted_recurring: bool = False
    persona_phase: str = "DEFAULT"


class FutureOutcomeGroundTruth(BaseModel):
    """Ground truth future outcomes evaluated at a historical checkpoint date for model validation."""
    account_id: str
    checkpoint_date: datetime
    observed_balance: Decimal
    future_min_balance_7d: Decimal
    future_min_balance_14d: Decimal
    future_min_balance_30d: Decimal
    future_inflow_sum_7d: Decimal
    future_inflow_sum_14d: Decimal
    future_inflow_sum_30d: Decimal
    future_outflow_sum_7d: Decimal
    future_outflow_sum_14d: Decimal
    future_outflow_sum_30d: Decimal
    liquidity_stress_event_within_30d: bool = False


class UserGroundTruth(BaseModel):
    """Ground truth metadata summary for a single generated synthetic user."""
    account_id: str
    persona: PersonaType
    starting_balance: Decimal
    split_assignment: str  # "TRAIN", "VALIDATION", "TEST"
    planted_rules: List[PlantedRuleGroundTruth] = []
    milestones: List[BehaviorMilestoneGroundTruth] = []


class DatasetGroundTruth(BaseModel):
    """Top-level ground truth structure for an entire synthetic dataset run."""
    seed: int
    num_users: int
    generated_at_utc: datetime
    user_splits: Dict[str, str] = {}  # account_id -> "TRAIN" | "VALIDATION" | "TEST"
    users: Dict[str, UserGroundTruth] = {}
    annotations: Dict[str, ActivityAnnotationGroundTruth] = {}
    future_outcomes: List[FutureOutcomeGroundTruth] = []

    model_config = ConfigDict(from_attributes=True)
