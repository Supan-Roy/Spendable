"""Scenario Simulation Engine Simulator.

Performs deterministic hypothetical financial state transformations and re-runs
the Spendable Engine without mutating the original base state or introducing future leakage.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
import numpy as np

from app.engine.calculator import SpendableCalculator
from app.engine.schema import SpendableOutput, SpendableFactor, LiquidityState
from app.recurring.schema import (
    DetectedCommitment,
    DetectionEvidence,
    DetectionStatus,
    RecurrenceIntervalType,
)
from app.forecasting.schema import ForecastOutput, HorizonForecast
from app.scenario.schema import ScenarioInput, ScenarioResult, ScenarioType


class ScenarioSimulator:
    """Core domain simulator executing hypothetical financial scenario transformations."""

    def __init__(self, calculator: Optional[SpendableCalculator] = None):
        self.calculator = calculator or SpendableCalculator()

    def simulate(
        self,
        user_id: str,
        snapshot_time: str,
        current_balance: float,
        features: Dict[str, float],
        commitments: List[DetectedCommitment],
        forecast: Optional[ForecastOutput] = None,
        scenario_input: Optional[ScenarioInput] = None,
    ) -> ScenarioResult:
        """Simulate a hypothetical scenario while preserving base state immutability."""
        # 1. Compute Base Spendable State (authoritative baseline)
        base_output = self.calculator.calculate(
            user_id=user_id,
            snapshot_time=snapshot_time,
            current_balance=current_balance,
            features=features,
            commitments=commitments,
            forecast=forecast,
        )

        if scenario_input is None:
            # Zero scenario / default baseline
            return ScenarioResult(
                user_id=user_id,
                snapshot_time=snapshot_time,
                scenario_type=ScenarioType.ONE_TIME_EXPENSE,
                scenario_description="Baseline (No Scenario Adjustment)",
                base_spendable_amount=base_output.spendable_amount,
                scenario_spendable_amount=base_output.spendable_amount,
                spendable_delta=0.0,
                base_current_balance=base_output.current_balance,
                scenario_current_balance=base_output.current_balance,
                base_forecasted_minimum_balance=base_output.forecasted_minimum_balance,
                scenario_forecasted_minimum_balance=base_output.forecasted_minimum_balance,
                base_safety_reserve=base_output.safety_reserve,
                scenario_safety_reserve=base_output.safety_reserve,
                base_liquidity_state=base_output.liquidity_state,
                scenario_liquidity_state=base_output.liquidity_state,
                assumptions={"adjustment": "NONE"},
                factors=base_output.factors,
                scenario_spendable_output=base_output,
            )

        # 2. Deep-copy inputs to guarantee zero mutation of base state
        scenario_features = deepcopy(features)
        scenario_commitments = deepcopy(commitments)
        scenario_forecast = deepcopy(forecast) if forecast else None

        scen_type = scenario_input.scenario_type
        amount = max(0.0, float(scenario_input.amount))
        percentage = max(0.0, min(100.0, float(scenario_input.percentage)))

        scenario_balance = float(current_balance)
        assumptions: Dict[str, Any] = {
            "scenario_type": scen_type.value,
            "input_amount": amount,
            "input_percentage": percentage,
        }

        # 3. Apply Scenario Transformations
        if scen_type == ScenarioType.ONE_TIME_EXPENSE:
            scenario_balance = max(0.0, current_balance - amount)
            scenario_features["current_balance"] = scenario_balance
            
            if scenario_forecast:
                scen_30d = scenario_forecast.forecast_30d
                scen_30d.minimum_projected_balance = max(
                    0.0, scen_30d.minimum_projected_balance - amount
                )
                scen_30d.projected_balance = max(0.0, scen_30d.projected_balance - amount)
            assumptions["description"] = f"One-time expense of ৳{amount:,.2f} deducted today."

        elif scen_type == ScenarioType.ADDITIONAL_INCOME:
            scenario_balance = current_balance + amount
            scenario_features["current_balance"] = scenario_balance
            
            if scenario_forecast:
                scen_30d = scenario_forecast.forecast_30d
                scen_30d.expected_inflow += amount
                scen_30d.minimum_projected_balance += amount
                scen_30d.projected_balance += amount
            assumptions["description"] = f"Additional income of ৳{amount:,.2f} received today."

        elif scen_type == ScenarioType.ADDITIONAL_COMMITMENT:
            # Add hypothetical recurring commitment
            hypo_evidence = DetectionEvidence(
                occurrences=1, median_interval_days=30.0, mean_interval_days=30.0,
                std_interval_days=0.0, interval_cv=0.0, mean_amount=amount,
                median_amount=amount, std_amount=0.0, amount_cv=0.0, recency_days=0.0,
                active_duration_days=30.0, interval_consistency_score=1.0,
                amount_consistency_score=1.0, recency_score=1.0, count_score=1.0,
                counterparty_score=1.0, commitment_likelihood_score=1.0
            )
            scenario_commitments.append(
                DetectedCommitment(
                    commitment_id=f"hypo_comm_{int(amount)}",
                    user_id=user_id,
                    counterparty_name="Hypothetical Commitment",
                    category="ADDITIONAL_OBLIGATION",
                    activity_type="COMMITMENT",
                    direction="OUTFLOW",
                    is_commitment=True,
                    expected_amount=amount,
                    recurrence_interval=RecurrenceIntervalType.MONTHLY,
                    median_interval_days=30.0,
                    next_expected_date=snapshot_time,
                    amount_variability=0.0,
                    occurrence_count=1,
                    confidence_score=1.0,
                    commitment_likelihood=1.0,
                    detection_status=DetectionStatus.STRONG,
                    evidence=hypo_evidence,
                )
            )
            assumptions["description"] = f"Additional recurring commitment of ৳{amount:,.2f} added."

        elif scen_type == ScenarioType.SPENDING_REDUCTION:
            ratio = percentage / 100.0
            outflow_30d = float(scenario_features.get("total_outflow_30d", base_output.expected_outflow))
            savings_30d = outflow_30d * ratio
            
            scenario_features["total_outflow_30d"] = max(0.0, outflow_30d - savings_30d)
            if scenario_forecast:
                scen_30d = scenario_forecast.forecast_30d
                scen_30d.expected_outflow = max(0.0, scen_30d.expected_outflow - savings_30d)
                scen_30d.minimum_projected_balance += savings_30d
                scen_30d.projected_balance += savings_30d
            assumptions["description"] = f"Discretionary spending reduced by {percentage:.1f}% (saving ৳{savings_30d:,.2f})."

        elif scen_type == ScenarioType.INCOME_DELAY:
            delayed_amount = min(base_output.expected_inflow, amount)
            if scenario_forecast:
                scen_30d = scenario_forecast.forecast_30d
                scen_30d.expected_inflow = max(0.0, scen_30d.expected_inflow - delayed_amount)
                scen_30d.minimum_projected_balance = max(
                    0.0, scen_30d.minimum_projected_balance - delayed_amount
                )
                scen_30d.projected_balance = max(0.0, scen_30d.projected_balance - delayed_amount)
            scenario_features["total_inflow_30d"] = max(0.0, float(scenario_features.get("total_inflow_30d", 0.0)) - delayed_amount)
            assumptions["description"] = f"Expected income of ৳{delayed_amount:,.2f} delayed beyond planning horizon."

        # 4. Re-run Spendable Engine on Derived Scenario State
        scenario_output = self.calculator.calculate(
            user_id=user_id,
            snapshot_time=snapshot_time,
            current_balance=scenario_balance,
            features=scenario_features,
            commitments=scenario_commitments,
            forecast=scenario_forecast,
        )

        spendable_delta = round(scenario_output.spendable_amount - base_output.spendable_amount, 2)
        desc = scenario_input.description or assumptions.get("description", f"Simulated {scen_type.value}")

        return ScenarioResult(
            user_id=user_id,
            snapshot_time=snapshot_time,
            scenario_type=scen_type,
            scenario_description=desc,
            base_spendable_amount=base_output.spendable_amount,
            scenario_spendable_amount=scenario_output.spendable_amount,
            spendable_delta=spendable_delta,
            base_current_balance=base_output.current_balance,
            scenario_current_balance=scenario_output.current_balance,
            base_forecasted_minimum_balance=base_output.forecasted_minimum_balance,
            scenario_forecasted_minimum_balance=scenario_output.forecasted_minimum_balance,
            base_safety_reserve=base_output.safety_reserve,
            scenario_safety_reserve=scenario_output.safety_reserve,
            base_liquidity_state=base_output.liquidity_state,
            scenario_liquidity_state=scenario_output.liquidity_state,
            assumptions=assumptions,
            factors=scenario_output.factors,
            scenario_spendable_output=scenario_output,
        )
