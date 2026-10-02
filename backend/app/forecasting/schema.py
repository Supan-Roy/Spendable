"""Domain schemas for cash-flow forecasting and liquidity trajectory estimation.

Defines data models for horizon forecasts, complete forecast outputs,
model configuration, evaluation metrics, persona breakdowns, and reports.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class ForecastModelType(str, Enum):
    """Supported forecasting model architectures."""
    ROLLING_AVERAGE_BASELINE = "ROLLING_AVERAGE_BASELINE"
    RECURRING_COMMITMENT_BASELINE = "RECURRING_COMMITMENT_BASELINE"
    HIST_GRADIENT_BOOSTING = "HIST_GRADIENT_BOOSTING"
    RANDOM_FOREST = "RANDOM_FOREST"


class HorizonForecast(BaseModel):
    """Projected cash-flow and balance metrics for a single forecast horizon."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    horizon_days: int = Field(..., description="Forecast horizon window in days (7, 14, 30)")
    expected_inflow: float = Field(..., description="Projected cumulative inflow over horizon")
    expected_outflow: float = Field(..., description="Projected cumulative outflow over horizon")
    expected_net_cash_flow: float = Field(..., description="Projected net cash flow (inflow - outflow)")
    projected_balance: float = Field(..., description="Projected account balance at end of horizon")
    minimum_projected_balance: float = Field(..., description="Projected minimum account balance during horizon")
    liquidity_pressure_flag: bool = Field(False, description="True if minimum projected balance drops below safety margin")
    estimated_range_lower: float = Field(..., description="Lower bound prediction interval estimate")
    estimated_range_upper: float = Field(..., description="Upper bound prediction interval estimate")


class DailyTrajectoryPoint(BaseModel):
    """Daily projected balance trajectory point."""
    day_offset: int = Field(..., description="Day offset relative to snapshot time T (1..30)")
    date_str: str = Field(..., description="ISO 8601 date string YYYY-MM-DD")
    projected_balance: float = Field(..., description="Estimated account balance on day d")


class ForecastOutput(BaseModel):
    """Complete structured forecasting output payload for a single snapshot."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str = Field(..., description="Account ID of the user")
    snapshot_time: str = Field(..., description="Point-in-time snapshot timestamp T")
    current_balance: float = Field(..., description="Observed account balance at snapshot time T")
    
    forecast_7d: HorizonForecast = Field(..., description="7-day liquidity forecast")
    forecast_14d: HorizonForecast = Field(..., description="14-day liquidity forecast")
    forecast_30d: HorizonForecast = Field(..., description="30-day liquidity forecast")
    
    daily_trajectory: List[DailyTrajectoryPoint] = Field(default_factory=list, description="30-day daily projected balance trajectory")
    model_version: str = Field(..., description="Identifier of the model used to generate forecast")
    safety_threshold_bdt: float = Field(15000.0, description="Low-balance safety margin threshold in BDT")


class ForecastConfig(BaseModel):
    """Configuration options for cash-flow forecasting pipeline."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    safety_threshold_bdt: float = 15000.0
    cadence_days: int = 14
    max_horizon_days: int = 30
    random_seed: int = 42


class RegressionMetric(BaseModel):
    """Standard regression evaluation metric for a single horizon."""
    horizon_days: int
    mae: float
    rmse: float
    r2_score: float


class LiquidityPressureMetric(BaseModel):
    """Evaluation metric for liquidity pressure detection (low-balance anticipation)."""
    horizon_days: int
    safety_threshold_bdt: float
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1_score: float


class PersonaEvaluationMetric(BaseModel):
    """Forecasting performance breakdown for a specific user persona profile."""
    persona: str
    total_snapshots: int
    mae_30d: float
    rmse_30d: float
    pressure_f1_30d: float


class ModelEvaluationSummary(BaseModel):
    """Evaluation summary for a specific model on a dataset split."""
    model_name: str
    split_name: str
    total_snapshots: int
    metrics_7d: RegressionMetric
    metrics_14d: RegressionMetric
    metrics_30d: RegressionMetric
    pressure_metrics_30d: LiquidityPressureMetric
    persona_breakdown: List[PersonaEvaluationMetric] = []


class ForecastingReport(BaseModel):
    """Comprehensive comparative forecasting evaluation report across models and splits."""
    evaluated_at: str
    config: ForecastConfig
    models_evaluated: List[str]
    summaries: List[ModelEvaluationSummary]
    feature_importances: Dict[str, float] = {}
