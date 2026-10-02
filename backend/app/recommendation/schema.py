"""Domain Pydantic schemas for the Deterministic Recommendation Engine.

Defines schemas for:
- Recommendation priorities (CRITICAL, WARNING, INFO)
- Recommendation taxonomy types
- Structured recommendation objects
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class RecommendationPriority(str, Enum):
    """Presentation ordering priority level for recommendations."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class RecommendationType(str, Enum):
    """Taxonomy of deterministic recommendation types."""
    LIQUIDITY_WARNING = "LIQUIDITY_WARNING"
    UPCOMING_COMMITMENTS = "UPCOMING_COMMITMENTS"
    SPENDING_CAUTION = "SPENDING_CAUTION"
    INCOME_IRREGULARITY = "INCOME_IRREGULARITY"
    FORECAST_PRESSURE = "FORECAST_PRESSURE"
    POSITIVE_LIQUIDITY = "POSITIVE_LIQUIDITY"
    SCENARIO_INSIGHT = "SCENARIO_INSIGHT"


class Recommendation(BaseModel):
    """Structured deterministic recommendation item."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: RecommendationType = Field(..., description="Taxonomy type of the recommendation")
    priority: RecommendationPriority = Field(..., description="Presentation priority (CRITICAL, WARNING, INFO)")
    title: str = Field(..., description="Short concise recommendation title")
    message: str = Field(..., description="Actionable recommendation message")
    supporting_amount: Optional[float] = Field(None, description="Associated monetary amount in BDT, if applicable")
    supporting_metric: Optional[str] = Field(None, description="Associated metric identifier or label")
    reason: str = Field(..., description="Deterministic factual condition that triggered the recommendation")
    action: Optional[str] = Field(None, description="Suggested non-consequential user guidance action")
