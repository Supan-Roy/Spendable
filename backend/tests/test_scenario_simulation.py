"""Unit tests for the Scenario Simulation Engine.

Tests:
- 10 mandatory financial sanity & monotonicity properties
- Non-mutation of base state
- Deterministic outputs and zero-adjustment identity
- Edge case safety (expense > balance, zero income, no NaN/infinity)
"""

import pytest
import numpy as np

from app.engine.schema import SpendableOutput, LiquidityState
from app.engine.calculator import SpendableCalculator
from app.recurring.schema import (
    DetectedCommitment,
    DetectionEvidence,
    DetectionStatus,
    RecurrenceIntervalType,
)
from app.forecasting.schema import ForecastOutput, HorizonForecast
from app.scenario.schema import ScenarioInput, ScenarioResult, ScenarioType
from app.scenario.simulator import ScenarioSimulator
from app.scenario.validators import ScenarioValidator


@pytest.fixture
def sample_base_data():
    features = {
        "current_balance": 50000.0,
        "total_outflow_30d": 30000.0,
        "spending_volatility_30d": 1000.0,
        "total_inflow_30d": 40000.0,
        "inflow_volatility_30d": 500.0,
    }
    forecast = ForecastOutput(
        user_id="test_user",
        snapshot_time="2026-03-01T00:00:00",
        current_balance=50000.0,
        forecast_7d=HorizonForecast(
            horizon_days=7, expected_inflow=10000.0, expected_outflow=5000.0,
            expected_net_cash_flow=5000.0, projected_balance=55000.0,
            minimum_projected_balance=48000.0, liquidity_pressure_flag=False,
            estimated_range_lower=45000.0, estimated_range_upper=55000.0
        ),
        forecast_14d=HorizonForecast(
            horizon_days=14, expected_inflow=20000.0, expected_outflow=15000.0,
            expected_net_cash_flow=5000.0, projected_balance=55000.0,
            minimum_projected_balance=42000.0, liquidity_pressure_flag=False,
            estimated_range_lower=40000.0, estimated_range_upper=58000.0
        ),
        forecast_30d=HorizonForecast(
            horizon_days=30, expected_inflow=40000.0, expected_outflow=30000.0,
            expected_net_cash_flow=10000.0, projected_balance=60000.0,
            minimum_projected_balance=35000.0, liquidity_pressure_flag=False,
            estimated_range_lower=30000.0, estimated_range_upper=65000.0
        ),
        model_version="HIST_GRADIENT_BOOSTING_v1",
        safety_threshold_bdt=15000.0,
    )
    return {
        "user_id": "test_user",
        "snapshot_time": "2026-03-01T00:00:00",
        "current_balance": 50000.0,
        "features": features,
        "commitments": [],
        "forecast": forecast,
    }


def test_1_spending_more_never_increases_spendable(sample_base_data):
    """Sanity Test 1: Spending more should never increase spendable amount."""
    simulator = ScenarioSimulator()
    res_small = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=2000.0)
    )
    res_large = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=10000.0)
    )
    assert res_large.scenario_spendable_amount <= res_small.scenario_spendable_amount
    assert res_small.scenario_spendable_amount <= res_small.base_spendable_amount


def test_2_additional_income_does_not_decrease_spendable(sample_base_data):
    """Sanity Test 2: Additional positive income should not decrease spendable amount."""
    simulator = ScenarioSimulator()
    res_income = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.ADDITIONAL_INCOME, amount=5000.0)
    )
    assert res_income.scenario_spendable_amount >= res_income.base_spendable_amount


def test_3_additional_commitment_does_not_increase_spendable(sample_base_data):
    """Sanity Test 3: Additional commitment should not increase spendable amount."""
    simulator = ScenarioSimulator()
    res_comm = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.ADDITIONAL_COMMITMENT, amount=4000.0)
    )
    assert res_comm.scenario_spendable_amount <= res_comm.base_spendable_amount


def test_4_reducing_spending_does_not_decrease_spendable(sample_base_data):
    """Sanity Test 4: Reducing spending should not decrease spendable amount."""
    simulator = ScenarioSimulator()
    res_cut = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.SPENDING_REDUCTION, percentage=20.0)
    )
    assert res_cut.scenario_spendable_amount >= res_cut.base_spendable_amount


def test_5_one_time_expense_does_not_mutate_base_result(sample_base_data):
    """Sanity Test 5: One-time expense must not mutate the base result."""
    simulator = ScenarioSimulator()
    base_before = simulator.calculator.calculate(
        user_id=sample_base_data["user_id"],
        snapshot_time=sample_base_data["snapshot_time"],
        current_balance=sample_base_data["current_balance"],
        features=sample_base_data["features"],
        commitments=sample_base_data["commitments"],
        forecast=sample_base_data["forecast"],
    ).model_dump()

    _ = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=15000.0)
    )

    base_after = simulator.calculator.calculate(
        user_id=sample_base_data["user_id"],
        snapshot_time=sample_base_data["snapshot_time"],
        current_balance=sample_base_data["current_balance"],
        features=sample_base_data["features"],
        commitments=sample_base_data["commitments"],
        forecast=sample_base_data["forecast"],
    ).model_dump()

    assert base_before == base_after


def test_6_zero_adjustment_reproduces_base_result(sample_base_data):
    """Sanity Test 6: Scenario with zero adjustment should reproduce the base result."""
    simulator = ScenarioSimulator()
    res_zero = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=0.0)
    )
    assert res_zero.scenario_spendable_amount == res_zero.base_spendable_amount
    assert res_zero.spendable_delta == 0.0


def test_7_expense_greater_than_balance_safely_zero_spendable(sample_base_data):
    """Sanity Test 7: Expense greater than balance must remain safe and produce spendable = 0."""
    simulator = ScenarioSimulator()
    res_huge = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=100000.0)
    )
    assert res_huge.scenario_spendable_amount == 0.0
    assert res_huge.scenario_liquidity_state == LiquidityState.PRESSURED


def test_8_liquidity_state_recalculated(sample_base_data):
    """Sanity Test 8: Liquidity state should be recalculated rather than copied from base."""
    simulator = ScenarioSimulator()
    res_huge = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=45000.0)
    )
    assert res_huge.base_liquidity_state == LiquidityState.HEALTHY
    assert res_huge.scenario_liquidity_state == LiquidityState.PRESSURED


def test_9_deterministic_scenario_output(sample_base_data):
    """Sanity Test 9: Scenario result must remain deterministic."""
    simulator = ScenarioSimulator()
    inp = ScenarioInput(scenario_type=ScenarioType.ADDITIONAL_INCOME, amount=7500.0)
    res1 = simulator.simulate(**sample_base_data, scenario_input=inp)
    res2 = simulator.simulate(**sample_base_data, scenario_input=inp)
    assert res1.model_dump() == res2.model_dump()


def test_10_no_nan_or_infinity(sample_base_data):
    """Sanity Test 10: No NaN or infinity for edge cases."""
    simulator = ScenarioSimulator()
    res = simulator.simulate(
        **sample_base_data,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.INCOME_DELAY, amount=999999.0)
    )
    assert not np.isnan(res.scenario_spendable_amount)
    assert not np.isinf(res.scenario_spendable_amount)
    assert res.scenario_spendable_amount >= 0.0
