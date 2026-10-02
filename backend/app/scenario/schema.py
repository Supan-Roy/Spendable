"""Domain Pydantic schemas for the Scenario Simulation Engine.

Defines schemas for:
- Supported scenario types
- Scenario input parameters & assumptions
- Detailed scenario simulation output payload
- Comparative monotonicity & evaluation metrics
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from app.engine.schema import SpendableOutput, LiquidityState, SpendableFactor


class ScenarioType(str, Enum):
    """Supported hypothetical financial scenario types."""
    ONE_TIME_EXPENSE = "ONE_TIME_EXPENSE"
    ADDITIONAL_INCOME = "ADDITIONAL_INCOME"
    ADDITIONAL_COMMITMENT = "ADDITIONAL_COMMITMENT"
    SPENDING_REDUCTION = "SPENDING_REDUCTION"
    INCOME_DELAY = "INCOME_DELAY"


class ScenarioInput(BaseModel):
    """Input payload defining a hypothetical scenario request."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    scenario_type: ScenarioType = Field(..., description="Type of scenario to simulate")
    amount: float = Field(0.0, description="Associated monetary amount in BDT (for expense, income, commitment, delay)")
    percentage: float = Field(0.0, description="Percentage adjustment [0.0 - 100.0] (for spending reduction)")
    description: Optional[str] = Field(None, description="Human-readable description of hypothetical scenario")
    custom_params: Dict[str, Any] = Field(default_factory=dict, description="Additional custom simulation parameters")


class ScenarioResult(BaseModel):
    """Structured output payload produced by the Scenario Simulation Engine."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str = Field(..., description="Unique account identifier")
    snapshot_time: str = Field(..., description="Point-in-time snapshot timestamp T")
    
    scenario_type: ScenarioType = Field(..., description="Type of scenario simulated")
    scenario_description: str = Field(..., description="Human-readable description of scenario")
    
    base_spendable_amount: float = Field(..., description="Original baseline spendable capacity in BDT")
    scenario_spendable_amount: float = Field(..., description="Recalculated spendable capacity under scenario in BDT")
    spendable_delta: float = Field(..., description="Net change in spendable amount (scenario - base)")
    
    base_current_balance: float = Field(..., description="Original baseline account balance")
    scenario_current_balance: float = Field(..., description="Recalculated current balance under scenario")
    
    base_forecasted_minimum_balance: float = Field(..., description="Original model-predicted 30-day minimum balance")
    scenario_forecasted_minimum_balance: float = Field(..., description="Recalculated 30-day minimum balance under scenario")
    
    base_safety_reserve: float = Field(..., description="Original baseline safety reserve")
    scenario_safety_reserve: float = Field(..., description="Recalculated safety reserve under scenario")
    
    base_liquidity_state: LiquidityState = Field(..., description="Original baseline liquidity state")
    scenario_liquidity_state: LiquidityState = Field(..., description="Recalculated liquidity state under scenario")
    
    assumptions: Dict[str, Any] = Field(default_factory=dict, description="Explicit parameters and state adjustments used")
    factors: List[SpendableFactor] = Field(default_factory=list, description="Machine-readable factor breakdown under scenario")
    
    scenario_spendable_output: SpendableOutput = Field(..., description="Full recalculation output object from Spendable Engine")


class ScenarioValidationMetrics(BaseModel):
    """Evaluation metrics for scenario monotonicity and financial sanity rules."""
    total_scenarios_tested: int
    monotonicity_violations: int
    negative_spendable_violations: int
    state_mutation_violations: int
    passed_all_sanity_checks: bool
    summary_notes: str
