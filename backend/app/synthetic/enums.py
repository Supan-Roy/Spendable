"""Synthetic data generation enums."""
from enum import Enum


class PersonaType(str, Enum):
    """Behavioral profile types for synthetic financial user generation."""
    STABLE = "STABLE"
    TIGHT_LIQUIDITY = "TIGHT_LIQUIDITY"
    IRREGULAR_INCOME = "IRREGULAR_INCOME"
    COMMITMENT_HEAVY = "COMMITMENT_HEAVY"
    SPENDING_DRIFT = "SPENDING_DRIFT"
    FINANCIAL_PRESSURE = "FINANCIAL_PRESSURE"


class RecurrenceFrequency(str, Enum):
    """Temporal frequency for planted recurring financial events."""
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"


class MilestoneType(str, Enum):
    """Behavioral shift milestone types for ground-truth tracking."""
    DRIFT_START = "DRIFT_START"
    PRESSURE_START = "PRESSURE_START"
    INCOME_DISRUPTION = "INCOME_DISRUPTION"
