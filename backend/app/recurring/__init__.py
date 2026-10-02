"""Spendable Recurring Payment & Financial Commitment Detection Module.

Exports:
- RecurringDetector: Baseline deterministic recurring commitment detector.
- RecurringEvaluator: Offline ground-truth evaluator.
- DetectionConfig: Detector hyperparameter and weight configuration.
- DetectedCommitment: Domain schema for detected recurring commitment.
- DetectionEvidence: Observable metrics and sub-score evidence payload.
- DetectionStatus: Categorical status (STRONG, MODERATE, INSUFFICIENT_EVIDENCE).
- RecurrenceIntervalType: Recurrence periodicity enum (WEEKLY, MONTHLY, etc.).
- EvaluationReport: Comprehensive evaluation report schema across dataset splits.
"""

from app.recurring.schema import (
    DetectionConfig,
    DetectionEvidence,
    DetectionStatus,
    DetectedCommitment,
    RecurrenceIntervalType,
    SingleEvaluationMetric,
    EvaluationReport,
)
from app.recurring.detector import RecurringDetector
from app.recurring.evaluator import RecurringEvaluator

__all__ = [
    "DetectionConfig",
    "DetectionEvidence",
    "DetectionStatus",
    "DetectedCommitment",
    "RecurrenceIntervalType",
    "SingleEvaluationMetric",
    "EvaluationReport",
    "RecurringDetector",
    "RecurringEvaluator",
]
