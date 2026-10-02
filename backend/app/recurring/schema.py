"""Domain schemas for recurring payment and financial commitment detection.

Defines data models for detected recurring commitments, detection evidence,
scoring parameters, detection statuses, and evaluation results.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class DetectionStatus(str, Enum):
    """Categorical confidence status of a detected commitment."""
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RecurrenceIntervalType(str, Enum):
    """Standard recognized financial recurrence intervals."""
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"
    IRREGULAR = "IRREGULAR"


class DetectionEvidence(BaseModel):
    """Structured observable evidence supporting a detected commitment."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    occurrences: int = Field(..., description="Total historical occurrence count up to snapshot time")
    median_interval_days: float = Field(..., description="Median days between consecutive occurrences")
    mean_interval_days: float = Field(..., description="Mean days between consecutive occurrences")
    std_interval_days: float = Field(..., description="Standard deviation of interval days")
    interval_cv: float = Field(..., description="Coefficient of variation for occurrence intervals")
    
    mean_amount: float = Field(..., description="Mean historical payment amount")
    median_amount: float = Field(..., description="Median historical payment amount")
    std_amount: float = Field(..., description="Standard deviation of historical payment amounts")
    amount_cv: float = Field(..., description="Coefficient of variation for payment amounts")
    
    recency_days: float = Field(..., description="Days between snapshot time T and most recent transaction")
    active_duration_days: float = Field(..., description="Span in days between first and last occurrence")
    
    interval_consistency_score: float = Field(..., description="Sub-score [0,1] for interval regularity")
    amount_consistency_score: float = Field(..., description="Sub-score [0,1] for amount predictability")
    recency_score: float = Field(..., description="Sub-score [0,1] for transaction recency")
    count_score: float = Field(..., description="Sub-score [0,1] for observation frequency")
    counterparty_score: float = Field(..., description="Sub-score [0,1] for counterparty specificity")
    commitment_likelihood_score: float = Field(..., description="Overall commitment-likeness score [0,1]")


class DetectedCommitment(BaseModel):
    """Structured representation of a detected recurring financial commitment or income stream."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    commitment_id: str = Field(..., description="Unique deterministic identifier for this commitment")
    user_id: str = Field(..., description="Account ID of the user")
    counterparty_name: Optional[str] = Field(None, description="Observable merchant or counterparty name")
    category: str = Field(..., description="Financial category or activity type")
    activity_type: str = Field(..., description="Primary transaction activity type")
    direction: str = Field(..., description="Transaction direction: OUTFLOW or INFLOW")
    is_commitment: bool = Field(True, description="True for OUTFLOW obligations, False for INFLOW income")
    
    expected_amount: float = Field(..., description="Estimated expected transaction amount")
    recurrence_interval: RecurrenceIntervalType = Field(..., description="Detected recurrence periodicity")
    median_interval_days: float = Field(..., description="Median interval in days between occurrences")
    next_expected_date: str = Field(..., description="ISO 8601 string of next expected occurrence date")
    amount_variability: float = Field(..., description="Standard deviation of transaction amounts")
    occurrence_count: int = Field(..., description="Total historical observation count at snapshot time")
    
    confidence_score: float = Field(..., description="Normalized confidence score in range [0.0, 1.0]")
    commitment_likelihood: float = Field(..., description="Commitment-likeness score in range [0.0, 1.0]")
    detection_status: DetectionStatus = Field(..., description="Confidence classification status")
    
    evidence: DetectionEvidence = Field(..., description="Detailed structured sub-scores and metrics")


class DetectionConfig(BaseModel):
    """Configuration thresholds and weights for the recurring commitment detector."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    min_occurrences: int = 3
    strong_threshold: float = 0.70
    moderate_threshold: float = 0.45
    
    # Sub-score component weights
    weight_interval: float = 0.35
    weight_amount: float = 0.30
    weight_count: float = 0.20
    weight_recency: float = 0.15


class CategoryEvaluationMetric(BaseModel):
    """Evaluation summary for a specific financial category."""
    category: str
    ground_truth_count: int
    detected_count: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float


class SingleEvaluationMetric(BaseModel):
    """Evaluation summary for a specific split or dataset segment."""
    split_name: str
    direction_filter: str
    total_users: int
    ground_truth_rules_count: int
    detected_commitments_count: int
    strong_commitments_count: int
    moderate_commitments_count: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    category_breakdown: List[CategoryEvaluationMetric] = []


class EvaluationReport(BaseModel):
    """Overall evaluation report across dataset splits."""
    snapshot_time: str
    config: DetectionConfig
    train_metrics: SingleEvaluationMetric
    validation_metrics: SingleEvaluationMetric
    test_metrics: SingleEvaluationMetric
