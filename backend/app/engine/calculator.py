"""Spendable Financial Intelligence Engine Calculator.

Calculates the safe spendable capacity for a user at snapshot time T by integrating:
- Current available balance
- Detected recurring financial commitments
- Multi-horizon cash-flow forecasts
- Adaptive safety reserve buffer

Ensures no double-counting between recurring commitments and forecasted outflows.
Produces structured machine-readable factor objects for downstream Gemini NLP generation.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

from app.engine.schema import (
    SpendableOutput,
    SpendableFactor,
    LiquidityState,
    FactorType,
    FactorImpact,
    CandidateSpendableResult,
)
from app.engine.safety import AdaptiveSafetyReserveCalculator
from app.recurring.schema import DetectedCommitment
from app.forecasting.schema import ForecastOutput


class SpendableCalculator:
    """Core domain engine computing Spendable capacity and explanation factors."""

    def __init__(
        self,
        safety_calculator: Optional[AdaptiveSafetyReserveCalculator] = None,
        default_horizon_days: int = 30,
    ):
        self.safety_calculator = safety_calculator or AdaptiveSafetyReserveCalculator()
        self.default_horizon_days = default_horizon_days

    def calculate(
        self,
        user_id: str,
        snapshot_time: str,
        current_balance: float,
        features: Dict[str, float],
        commitments: List[DetectedCommitment],
        forecast: Optional[ForecastOutput] = None,
        candidate_methodology: str = "CANDIDATE_A",
    ) -> SpendableOutput:
        """Compute Spendable capacity, safety reserve, liquidity state, and structured factors."""
        # 1. Extract commitments due in 30 days
        upcoming_commitments_30d = sum(
            float(getattr(c, "expected_amount", getattr(c, "amount", 0.0)))
            for c in commitments
            if (getattr(c, "direction", "OUTFLOW") in ("OUTFLOW", "DEBIT") and getattr(c, "is_commitment", True))
        )
        
        # 2. Extract forecast metrics
        if forecast:
            forecast_30d = forecast.forecast_30d
            expected_inflow = forecast_30d.expected_inflow
            expected_outflow = forecast_30d.expected_outflow
            forecasted_min_balance = forecast_30d.minimum_projected_balance
            liquidity_pressure_flag = forecast_30d.liquidity_pressure_flag
        else:
            # Fallback when forecast is unavailable
            expected_inflow = features.get("inflow_sum_30d", 0.0)
            expected_outflow = features.get("outflow_sum_30d", 0.0)
            forecasted_min_balance = max(0.0, current_balance + expected_inflow - expected_outflow)
            liquidity_pressure_flag = forecasted_min_balance < 15000.0

        # 3. Calculate Adaptive Safety Reserve
        outflow_sum_30d = float(features.get("total_outflow_30d", features.get("outflow_sum_30d", expected_outflow)))
        outflow_std_30d = float(features.get("spending_volatility_30d", features.get("outflow_std_30d", 0.0)))
        income_sum_30d = float(features.get("total_inflow_30d", features.get("inflow_sum_30d", expected_inflow)))
        income_std_30d = float(features.get("inflow_volatility_30d", features.get("inflow_std_30d", 0.0)))

        safety_details = self.safety_calculator.calculate_reserve(
            current_balance=current_balance,
            outflow_sum_30d=outflow_sum_30d,
            outflow_std_30d=outflow_std_30d,
            income_sum_30d=income_sum_30d,
            income_std_30d=income_std_30d,
            upcoming_commitments=upcoming_commitments_30d,
        )
        safety_reserve = safety_details.total_reserve

        # 4. Evaluate Candidate Spendable Methodologies
        candidate_results = self.evaluate_candidates(
            current_balance=current_balance,
            upcoming_commitments=upcoming_commitments_30d,
            forecasted_min_balance=forecasted_min_balance,
            safety_reserve=safety_reserve,
        )

        selected_res = candidate_results.get(
            candidate_methodology, candidate_results["CANDIDATE_A"]
        )

        spendable_amount = selected_res.spendable_amount
        protected_amount = selected_res.protected_amount

        # 5. Classify Liquidity State
        liquidity_state = self._determine_liquidity_state(
            current_balance=current_balance,
            spendable_amount=spendable_amount,
            forecasted_min_balance=forecasted_min_balance,
            safety_reserve=safety_reserve,
            liquidity_pressure_flag=liquidity_pressure_flag,
        )

        # 6. Generate Machine-Readable Explanation Factors
        factors = self._generate_factors(
            current_balance=current_balance,
            spendable_amount=spendable_amount,
            protected_amount=protected_amount,
            expected_inflow=expected_inflow,
            expected_outflow=expected_outflow,
            upcoming_commitments=upcoming_commitments_30d,
            forecasted_min_balance=forecasted_min_balance,
            safety_reserve=safety_reserve,
            features=features,
            liquidity_state=liquidity_state,
        )

        return SpendableOutput(
            user_id=user_id,
            snapshot_time=snapshot_time,
            current_balance=round(current_balance, 2),
            planning_horizon_days=self.default_horizon_days,
            spendable_amount=round(spendable_amount, 2),
            protected_amount=round(protected_amount, 2),
            expected_inflow=round(expected_inflow, 2),
            expected_outflow=round(expected_outflow, 2),
            upcoming_commitments=round(upcoming_commitments_30d, 2),
            forecasted_minimum_balance=round(forecasted_min_balance, 2),
            safety_reserve=round(safety_reserve, 2),
            safety_reserve_details=safety_details,
            liquidity_state=liquidity_state,
            candidate_formula_used=candidate_methodology,
            factors=factors,
        )

    def evaluate_candidates(
        self,
        current_balance: float,
        upcoming_commitments: float,
        forecasted_min_balance: float,
        safety_reserve: float,
    ) -> Dict[str, CandidateSpendableResult]:
        """Compute Spendable amounts for Candidate A, B, and C formulations."""
        if current_balance <= 0:
            return {
                "CANDIDATE_A": CandidateSpendableResult(
                    candidate_name="CANDIDATE_A",
                    spendable_amount=0.0,
                    protected_amount=0.0,
                    safety_reserve=0.0,
                    liquidity_state=LiquidityState.PRESSURED,
                ),
                "CANDIDATE_B": CandidateSpendableResult(
                    candidate_name="CANDIDATE_B",
                    spendable_amount=0.0,
                    protected_amount=0.0,
                    safety_reserve=0.0,
                    liquidity_state=LiquidityState.PRESSURED,
                ),
                "CANDIDATE_C": CandidateSpendableResult(
                    candidate_name="CANDIDATE_C",
                    spendable_amount=0.0,
                    protected_amount=0.0,
                    safety_reserve=0.0,
                    liquidity_state=LiquidityState.PRESSURED,
                ),
            }

        # Projected Max Drawdown from current balance
        drawdown_30d = max(0.0, current_balance - forecasted_min_balance)

        # Candidate A: Non-Double-Counting Protected Requirement (Recommended)
        # Protected = max(Commitments, Forecasted Drawdown) + Safety Reserve
        protected_a = max(upcoming_commitments, drawdown_30d) + safety_reserve
        spendable_a = max(0.0, current_balance - protected_a)

        # Candidate B: Forecast-Aware Trajectory Buffer
        # Protected = Forecasted Drawdown + Safety Reserve  =>  Spendable = Min Balance - Reserve
        protected_b = drawdown_30d + safety_reserve
        spendable_b = max(0.0, forecasted_min_balance - safety_reserve)

        # Candidate C: Commitment-Aware Direct Cash Buffer
        # Protected = Commitments + Safety Reserve
        protected_c = upcoming_commitments + safety_reserve
        spendable_c = max(0.0, current_balance - protected_c)

        return {
            "CANDIDATE_A": CandidateSpendableResult(
                candidate_name="CANDIDATE_A",
                spendable_amount=round(spendable_a, 2),
                protected_amount=round(protected_a, 2),
                safety_reserve=round(safety_reserve, 2),
                liquidity_state=self._determine_liquidity_state(
                    current_balance, spendable_a, forecasted_min_balance, safety_reserve, False
                ),
            ),
            "CANDIDATE_B": CandidateSpendableResult(
                candidate_name="CANDIDATE_B",
                spendable_amount=round(spendable_b, 2),
                protected_amount=round(protected_b, 2),
                safety_reserve=round(safety_reserve, 2),
                liquidity_state=self._determine_liquidity_state(
                    current_balance, spendable_b, forecasted_min_balance, safety_reserve, False
                ),
            ),
            "CANDIDATE_C": CandidateSpendableResult(
                candidate_name="CANDIDATE_C",
                spendable_amount=round(spendable_c, 2),
                protected_amount=round(protected_c, 2),
                safety_reserve=round(safety_reserve, 2),
                liquidity_state=self._determine_liquidity_state(
                    current_balance, spendable_c, forecasted_min_balance, safety_reserve, False
                ),
            ),
        }

    def _determine_liquidity_state(
        self,
        current_balance: float,
        spendable_amount: float,
        forecasted_min_balance: float,
        safety_reserve: float,
        liquidity_pressure_flag: bool,
    ) -> LiquidityState:
        """Classify liquidity state into HEALTHY, WATCH, or PRESSURED."""
        if current_balance <= 0 or spendable_amount == 0.0 or forecasted_min_balance < safety_reserve or liquidity_pressure_flag:
            return LiquidityState.PRESSURED

        if forecasted_min_balance < safety_reserve * 1.5 or spendable_amount < current_balance * 0.25:
            return LiquidityState.WATCH

        return LiquidityState.HEALTHY

    def _generate_factors(
        self,
        current_balance: float,
        spendable_amount: float,
        protected_amount: float,
        expected_inflow: float,
        expected_outflow: float,
        upcoming_commitments: float,
        forecasted_min_balance: float,
        safety_reserve: float,
        features: Dict[str, float],
        liquidity_state: LiquidityState,
    ) -> List[SpendableFactor]:
        """Produce structured factors for downstream Gemini explanation generation."""
        factors: List[SpendableFactor] = []

        # 1. Upcoming Commitments
        if upcoming_commitments > 0:
            factors.append(
                SpendableFactor(
                    type=FactorType.UPCOMING_COMMITMENT,
                    impact=FactorImpact.NEGATIVE,
                    amount=round(upcoming_commitments, 2),
                    description=f"৳{upcoming_commitments:,.2f} reserved for detected recurring bills and commitments over 30 days.",
                )
            )

        # 2. Expected Inflow
        if expected_inflow > 0:
            factors.append(
                SpendableFactor(
                    type=FactorType.EXPECTED_INFLOW,
                    impact=FactorImpact.POSITIVE,
                    amount=round(expected_inflow, 2),
                    description=f"৳{expected_inflow:,.2f} projected incoming cash flow over next 30 days.",
                )
            )

        # 3. Forecasted Minimum Balance
        if forecasted_min_balance < safety_reserve:
            factors.append(
                SpendableFactor(
                    type=FactorType.FORECAST_MINIMUM,
                    impact=FactorImpact.NEGATIVE,
                    amount=round(forecasted_min_balance, 2),
                    description=f"Forecasted 30-day minimum balance of ৳{forecasted_min_balance:,.2f} drops below safety threshold.",
                )
            )
        else:
            factors.append(
                SpendableFactor(
                    type=FactorType.FORECAST_MINIMUM,
                    impact=FactorImpact.POSITIVE,
                    amount=round(forecasted_min_balance, 2),
                    description=f"Forecasted minimum account balance remains safe at ৳{forecasted_min_balance:,.2f}.",
                )
            )

        # 4. Safety Reserve Buffer
        factors.append(
            SpendableFactor(
                type=FactorType.SAFETY_BUFFER,
                impact=FactorImpact.NEGATIVE,
                amount=round(safety_reserve, 2),
                description=f"৳{safety_reserve:,.2f} allocated to adaptive safety reserve buffer for unexpected expenses.",
            )
        )

        # 5. Spending / Income Volatility
        outflow_std = features.get("outflow_std_30d", 0.0)
        outflow_mean = features.get("outflow_sum_30d", 0.0) / 30.0
        if outflow_mean > 0 and (outflow_std / outflow_mean) > 0.4:
            factors.append(
                SpendableFactor(
                    type=FactorType.SPENDING_VOLATILITY,
                    impact=FactorImpact.NEGATIVE,
                    amount=round(outflow_std, 2),
                    description="High spending volatility detected; safety buffer expanded.",
                )
            )

        # 6. Liquidity State Warning
        if liquidity_state == LiquidityState.PRESSURED:
            factors.append(
                SpendableFactor(
                    type=FactorType.LIQUIDITY_PRESSURE,
                    impact=FactorImpact.NEGATIVE,
                    amount=None,
                    description="Account is in a PRESSURED liquidity state; spendable capacity is restricted.",
                )
            )

        return factors
