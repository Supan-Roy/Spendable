"""Scenario Simulation Engine Validator.

Validates financial sanity, monotonicity laws, base immutability, and edge-case safety.
"""

from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd

from app.engine.schema import SpendableOutput, LiquidityState
from app.scenario.schema import ScenarioInput, ScenarioResult, ScenarioType, ScenarioValidationMetrics
from app.scenario.simulator import ScenarioSimulator


class ScenarioValidator:
    """Validates financial sanity properties and monotonicity laws across scenarios."""

    def __init__(self, simulator: Optional[ScenarioSimulator] = None):
        self.simulator = simulator or ScenarioSimulator()

    def validate_scenario_sanity(
        self,
        user_id: str,
        snapshot_time: str,
        current_balance: float,
        features: Dict[str, float],
        commitments: List[Any],
        forecast: Optional[Any] = None,
    ) -> ScenarioValidationMetrics:
        """Run standard sanity test battery across all scenario types for a given user snapshot."""
        violations_monotonicity = 0
        violations_negative = 0
        violations_mutation = 0

        # Baseline Spendable
        base_out = self.simulator.calculator.calculate(
            user_id=user_id,
            snapshot_time=snapshot_time,
            current_balance=current_balance,
            features=features,
            commitments=commitments,
            forecast=forecast,
        )
        base_dump_before = base_out.model_dump()

        scenarios_to_test = [
            ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=3000.0),
            ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=current_balance + 50000.0), # Expense > balance
            ScenarioInput(scenario_type=ScenarioType.ADDITIONAL_INCOME, amount=5000.0),
            ScenarioInput(scenario_type=ScenarioType.ADDITIONAL_COMMITMENT, amount=4000.0),
            ScenarioInput(scenario_type=ScenarioType.SPENDING_REDUCTION, percentage=20.0),
            ScenarioInput(scenario_type=ScenarioType.INCOME_DELAY, amount=10000.0),
            ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=0.0), # Zero adjustment
        ]

        total_tested = len(scenarios_to_test)

        for scen_inp in scenarios_to_test:
            res = self.simulator.simulate(
                user_id=user_id,
                snapshot_time=snapshot_time,
                current_balance=current_balance,
                features=features,
                commitments=commitments,
                forecast=forecast,
                scenario_input=scen_inp,
            )

            # Check 1: Non-negative spendable
            if res.scenario_spendable_amount < 0.0 or np.isnan(res.scenario_spendable_amount) or np.isinf(res.scenario_spendable_amount):
                violations_negative += 1

            # Check 2: Monotonicity rules
            if scen_inp.scenario_type == ScenarioType.ONE_TIME_EXPENSE and scen_inp.amount > 0:
                if res.scenario_spendable_amount > res.base_spendable_amount + 1e-3:
                    violations_monotonicity += 1
            elif scen_inp.scenario_type == ScenarioType.ADDITIONAL_INCOME and scen_inp.amount > 0:
                if res.scenario_spendable_amount < res.base_spendable_amount - 1e-3:
                    violations_monotonicity += 1
            elif scen_inp.scenario_type == ScenarioType.ADDITIONAL_COMMITMENT and scen_inp.amount > 0:
                if res.scenario_spendable_amount > res.base_spendable_amount + 1e-3:
                    violations_monotonicity += 1
            elif scen_inp.scenario_type == ScenarioType.SPENDING_REDUCTION and scen_inp.percentage > 0:
                if res.scenario_spendable_amount < res.base_spendable_amount - 1e-3:
                    violations_monotonicity += 1

            # Check 3: Immutability of base state
            base_out_after = self.simulator.calculator.calculate(
                user_id=user_id,
                snapshot_time=snapshot_time,
                current_balance=current_balance,
                features=features,
                commitments=commitments,
                forecast=forecast,
            )
            if base_out_after.model_dump() != base_dump_before:
                violations_mutation += 1

        passed = (violations_monotonicity == 0 and violations_negative == 0 and violations_mutation == 0)

        return ScenarioValidationMetrics(
            total_scenarios_tested=total_tested,
            monotonicity_violations=violations_monotonicity,
            negative_spendable_violations=violations_negative,
            state_mutation_violations=violations_mutation,
            passed_all_sanity_checks=passed,
            summary_notes="Passed all financial sanity properties, zero state mutation, and non-negative spendable bounds." if passed else "Sanity violations detected."
        )
