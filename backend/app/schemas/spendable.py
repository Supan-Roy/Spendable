"""API response Pydantic schemas for Spendable product integration."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from app.engine.schema import LiquidityState, SpendableFactor
from app.recommendation.schema import Recommendation
from app.forecasting.schema import HorizonForecast, DailyTrajectoryPoint
from app.explanation.schema import GeminiExplanationResponse


class SpendableOverviewResponse(BaseModel):
    """API response model for GET /api/v1/overview dashboard endpoint."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str = Field(..., description="Account identifier")
    snapshot_time: str = Field(..., description="Point-in-time snapshot timestamp T")
    current_balance: float = Field(..., description="Observed liquid account balance in BDT")
    spendable_amount: float = Field(..., description="Safely spendable capacity in BDT")
    protected_amount: float = Field(..., description="Total liquidity protected for obligations and safety reserve")
    planning_horizon_days: int = Field(30, description="Planning horizon window in days")
    
    liquidity_state: LiquidityState = Field(..., description="Categorical liquidity state (HEALTHY, WATCH, PRESSURED)")
    expected_inflow: float = Field(..., description="Projected cumulative incoming cash flow over 30 days")
    expected_outflow: float = Field(..., description="Projected cumulative outgoing cash flow over 30 days")
    upcoming_commitments: float = Field(..., description="Sum of detected recurring financial commitments")
    forecasted_minimum_balance: float = Field(..., description="Model-predicted minimum account balance over horizon")
    safety_reserve: float = Field(..., description="Adaptive safety reserve buffer in BDT")
    
    recommendations: List[Recommendation] = Field(default_factory=list, description="Prioritized deterministic recommendations")
    factors: List[SpendableFactor] = Field(default_factory=list, description="Machine-readable factor breakdown")
    explanation_summary: Optional[str] = Field(None, description="Human-readable explanation summary")


class SpendableForecastResponse(BaseModel):
    """API response model for GET /api/v1/forecast multi-horizon endpoint."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str = Field(..., description="Account identifier")
    snapshot_time: str = Field(..., description="Point-in-time snapshot timestamp T")
    current_balance: float = Field(..., description="Observed liquid account balance in BDT")
    
    forecast_7d: HorizonForecast = Field(..., description="7-day cash flow & balance trajectory forecast")
    forecast_14d: HorizonForecast = Field(..., description="14-day cash flow & balance trajectory forecast")
    forecast_30d: HorizonForecast = Field(..., description="30-day cash flow & balance trajectory forecast")
    
    daily_trajectory: List[DailyTrajectoryPoint] = Field(default_factory=list, description="Daily projected balance points")
    safety_threshold_bdt: float = Field(15000.0, description="Low-balance safety threshold")


class SpendableActivityItem(BaseModel):
    """API response model for an individual transaction activity."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    transaction_id: str = Field(..., description="Unique transaction identifier")
    account_id: str = Field(..., description="Account identifier")
    timestamp_utc: str = Field(..., description="ISO 8601 transaction timestamp")
    amount: float = Field(..., description="Transaction amount in BDT")
    direction: str = Field(..., description="Transaction direction (INFLOW or OUTFLOW)")
    category: str = Field(..., description="Financial activity category")
    counterparty_name: Optional[str] = Field(None, description="Counterparty or merchant name")
    balance_after: Optional[float] = Field(None, description="Account balance following transaction")


class SpendableActivityListResponse(BaseModel):
    """API response model for GET /api/v1/activity transaction list endpoint."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    total_count: int = Field(..., description="Total activity record count")
    limit: int = Field(..., description="Pagination page limit")
    offset: int = Field(..., description="Pagination page offset")
    activities: List[SpendableActivityItem] = Field(default_factory=list, description="List of activity records")


class SpendableRecommendationsResponse(BaseModel):
    """API response model for GET /api/v1/recommendations endpoint."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str = Field(..., description="Account identifier")
    snapshot_time: str = Field(..., description="Point-in-time snapshot timestamp T")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Prioritized deterministic recommendations")
    explanation: GeminiExplanationResponse = Field(..., description="Human-readable explanation object (or deterministic fallback)")


class ExplainRequest(BaseModel):
    """Payload model for POST /api/v1/explain endpoint."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: Optional[str] = Field(None, description="Account identifier")
    snapshot_time: Optional[str] = Field(None, description="Snapshot timestamp")
    include_scenario: bool = Field(False, description="Whether to include current scenario result in explanation")
