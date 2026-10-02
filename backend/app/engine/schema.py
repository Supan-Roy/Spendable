"""Domain Pydantic schemas for the Spendable Financial Intelligence Engine.

Defines schemas for:
- Liquidity state classifications
- Machine-readable explanation factor objects
- Adaptive safety reserve breakdown
- Complete Spendable output payload
- Comparative methodology backtest results
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class LiquidityState(str, Enum):
    """Categorical classification of user liquidity state."""
    HEALTHY = "HEALTHY"
    WATCH = "WATCH"
    PRESSURED = "PRESSURED"


class FactorType(str, Enum):
    """Structured taxonomy of factors influencing Spendable capacity."""
    UPCOMING_COMMITMENT = "UPCOMING_COMMITMENT"
    EXPECTED_INFLOW = "EXPECTED_INFLOW"
    EXPECTED_OUTFLOW = "EXPECTED_OUTFLOW"
    SAFETY_BUFFER = "SAFETY_BUFFER"
    FORECAST_MINIMUM = "FORECAST_MINIMUM"
    SPENDING_VOLATILITY = "SPENDING_VOLATILITY"
    INCOME_VOLATILITY = "INCOME_VOLATILITY"
    LIQUIDITY_PRESSURE = "LIQUIDITY_PRESSURE"
    LOW_BALANCE_WARNING = "LOW_BALANCE_WARNING"
    RUNWAY_MARGIN = "RUNWAY_MARGIN"


class FactorImpact(str, Enum):
    """Directional impact of a factor on Spendable amount."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class SpendableFactor(BaseModel):
    """Machine-readable factor object for downstream Gemini NLP processing."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: FactorType = Field(..., description="Taxonomy type of the financial factor")
    impact: FactorImpact = Field(..., description="Impact on spendable amount (POSITIVE/NEGATIVE/NEUTRAL)")
    amount: Optional[float] = Field(None, description="Associated monetary amount in BDT, if applicable")
    description: str = Field(..., description="Structured, deterministic explanation text")


class SafetyReserveDetails(BaseModel):
    """Detailed breakdown of adaptive safety reserve computation components."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    baseline_spending_buffer: float = Field(..., description="Base liquidity buffer derived from spending rate")
    spending_volatility_addon: float = Field(..., description="Additional buffer derived from spending variability")
    income_volatility_addon: float = Field(..., description="Buffer addon for irregular or unpredictable income")
    commitment_burden_addon: float = Field(..., description="Buffer addon for heavy upcoming commitment obligations")
    total_reserve: float = Field(..., description="Final computed adaptive safety reserve amount")
    reserve_ratio_pct: float = Field(..., description="Safety reserve as percentage of current balance")


class SpendableOutput(BaseModel):
    """Structured output payload produced by the Spendable Financial Intelligence Engine."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str = Field(..., description="Unique user identifier")
    snapshot_time: str = Field(..., description="Snapshot timestamp T")
    current_balance: float = Field(..., description="Observed liquid balance at snapshot time T")
    planning_horizon_days: int = Field(30, description="Planning horizon window in days (7, 14, 30)")
    
    spendable_amount: float = Field(..., description="Safely spendable capacity in BDT")
    protected_amount: float = Field(..., description="Total liquidity protected for commitments, trajectory dips, and reserve")
    
    expected_inflow: float = Field(..., description="Projected cumulative inflow over horizon")
    expected_outflow: float = Field(..., description="Projected cumulative outflow over horizon")
    upcoming_commitments: float = Field(..., description="Total detected recurring commitment obligations in horizon")
    forecasted_minimum_balance: float = Field(..., description="Model-predicted minimum account balance over horizon")
    
    safety_reserve: float = Field(..., description="Adaptive safety buffer amount in BDT")
    safety_reserve_details: SafetyReserveDetails = Field(..., description="Detailed components of safety reserve calculation")
    
    liquidity_state: LiquidityState = Field(..., description="Categorical liquidity state (HEALTHY, WATCH, PRESSURED)")
    candidate_formula_used: str = Field(..., description="Identifier of formula used to compute Spendable capacity")
    
    factors: List[SpendableFactor] = Field(default_factory=list, description="Structured factors for downstream Gemini NLP generation")


class CandidateSpendableResult(BaseModel):
    """Comparative Spendable result for a single candidate formula."""
    candidate_name: str
    spendable_amount: float
    protected_amount: float
    safety_reserve: float
    liquidity_state: LiquidityState


class SnapshotEvaluationRow(BaseModel):
    """Single historical snapshot backtest evaluation metrics row."""
    user_id: str
    snapshot_time: str
    persona: str
    current_balance: float
    actual_30d_min_balance: float
    actual_30d_net_cash_flow: float
    
    candidate_a_spendable: float
    candidate_b_spendable: float
    candidate_c_spendable: float
    
    candidate_a_breached: bool
    candidate_b_breached: bool
    candidate_c_breached: bool


class CandidateBacktestMetrics(BaseModel):
    """Aggregated backtest safety and performance metrics for a candidate formula."""
    candidate_name: str
    total_snapshots: int
    mean_spendable_bdt: float
    median_spendable_bdt: float
    safety_breach_rate: float = Field(..., description="Percentage of snapshots where actual minimum balance dropped below reserve after spending spendable")
    zero_spendable_rate: float = Field(..., description="Percentage of snapshots resulting in zero spendable recommendation")
    avg_unallocated_buffer_bdt: float = Field(..., description="Mean remaining balance margin above safety reserve")


class EngineBacktestReport(BaseModel):
    """Comprehensive backtesting report evaluating all Spendable candidate formulas."""
    split_name: str
    total_users: int
    total_snapshots: int
    candidate_metrics: Dict[str, CandidateBacktestMetrics]
    selected_methodology: str
    summary_notes: str
