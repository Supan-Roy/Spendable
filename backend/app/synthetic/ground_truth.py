"""Ground truth representation for synthetic financial datasets.

Ground truth metadata captures internal generator state, planted recurring rules,
persona allocations, and behavioral phase shifts. Ground truth is maintained
separately from observable raw customer transaction feeds.
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


class UserGroundTruth(BaseModel):
    """Ground truth metadata summary for a single generated synthetic user."""
    account_id: str
    persona: PersonaType
    starting_balance: Decimal
    planted_rules: List[PlantedRuleGroundTruth] = []
    milestones: List[BehaviorMilestoneGroundTruth] = []


class DatasetGroundTruth(BaseModel):
    """Top-level ground truth structure for an entire synthetic dataset run."""
    seed: int
    num_users: int
    generated_at_utc: datetime
    users: Dict[str, UserGroundTruth] = {}
    annotations: Dict[str, ActivityAnnotationGroundTruth] = {}

    model_config = ConfigDict(from_attributes=True)
