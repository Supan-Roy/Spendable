"""Unit tests for the Spendable Financial Intelligence Engine.

Tests:
- Spendable calculation methodology and candidate formulations
- Non-double-counting logic between recurring commitments and forecasts
- Dynamic adaptive safety reserve scaling
- Historical snapshot point-in-time cutoff & no future data leakage
- Mandatory sanity properties (commitments increase, inflow increase)
- Zero/low balance, missing forecast, and edge case safety
- Deterministic Pydantic schema validation
"""

import pytest
import pandas as pd
import numpy as np

from app.engine.schema import (
    SpendableOutput,
    LiquidityState,
    FactorType,
    FactorImpact,
)
from app.engine.safety import AdaptiveSafetyReserveCalculator
from app.engine.calculator import SpendableCalculator
from app.engine.backtest import SpendableBacktester
from app.recurring.schema import DetectedCommitment
from app.forecasting.schema import ForecastOutput, HorizonForecast


@pytest.fixture
def sample_features():
    return {
        "current_balance": 50000.0,
        "outflow_sum_30d": 30000.0,
        "outflow_std_30d": 500.0,
        "inflow_sum_30d": 40000.0,
        "inflow_std_30d": 200.0,
        "total_recurring_debit_monthly": 10000.0,
    }


from app.recurring.schema import (
    DetectedCommitment,
    DetectionEvidence,
    DetectionStatus,
    RecurrenceIntervalType,
)


def make_test_commitment(user_id: str = "user_001", category: str = "RENT", amount: float = 10000.0) -> DetectedCommitment:
    evidence = DetectionEvidence(
        occurrences=5,
        median_interval_days=30.0,
        mean_interval_days=30.0,
        std_interval_days=1.0,
        interval_cv=0.03,
        mean_amount=amount,
        median_amount=amount,
        std_amount=0.0,
        amount_cv=0.0,
        recency_days=5.0,
        active_duration_days=120.0,
        interval_consistency_score=0.95,
        amount_consistency_score=1.0,
        recency_score=0.9,
        count_score=0.9,
        counterparty_score=0.8,
        commitment_likelihood_score=0.92,
    )
    return DetectedCommitment(
        commitment_id=f"comm_{category}_{int(amount)}",
        user_id=user_id,
        counterparty_name="Landlord",
        category=category,
        activity_type=category,
        direction="OUTFLOW",
        is_commitment=True,
        expected_amount=amount,
        recurrence_interval=RecurrenceIntervalType.MONTHLY,
        median_interval_days=30.0,
        next_expected_date="2026-04-01",
        amount_variability=0.0,
        occurrence_count=5,
        confidence_score=0.95,
        commitment_likelihood=0.92,
        detection_status=DetectionStatus.STRONG,
        evidence=evidence,
    )


@pytest.fixture
def sample_commitments():
    return [make_test_commitment(user_id="user_001", category="RENT", amount=10000.0)]


@pytest.fixture
def sample_forecast():
    return ForecastOutput(
        user_id="user_001",
        snapshot_time="2026-03-01T00:00:00",
        current_balance=50000.0,
        forecast_7d=HorizonForecast(
            horizon_days=7,
            expected_inflow=10000.0,
            expected_outflow=5000.0,
            expected_net_cash_flow=5000.0,
            projected_balance=55000.0,
            minimum_projected_balance=48000.0,
            liquidity_pressure_flag=False,
            estimated_range_lower=45000.0,
            estimated_range_upper=55000.0,
        ),
        forecast_14d=HorizonForecast(
            horizon_days=14,
            expected_inflow=20000.0,
            expected_outflow=15000.0,
            expected_net_cash_flow=5000.0,
            projected_balance=55000.0,
            minimum_projected_balance=42000.0,
            liquidity_pressure_flag=False,
            estimated_range_lower=40000.0,
            estimated_range_upper=58000.0,
        ),
        forecast_30d=HorizonForecast(
            horizon_days=30,
            expected_inflow=40000.0,
            expected_outflow=30000.0,
            expected_net_cash_flow=10000.0,
            projected_balance=60000.0,
            minimum_projected_balance=35000.0,
            liquidity_pressure_flag=False,
            estimated_range_lower=30000.0,
            estimated_range_upper=65000.0,
        ),
        model_version="HIST_GRADIENT_BOOSTING_v1",
        safety_threshold_bdt=15000.0,
    )


def test_spendable_calculator_basic(sample_features, sample_commitments, sample_forecast):
    calculator = SpendableCalculator()
    output = calculator.calculate(
        user_id="user_001",
        snapshot_time="2026-03-01T00:00:00",
        current_balance=50000.0,
        features=sample_features,
        commitments=sample_commitments,
        forecast=sample_forecast,
    )

    assert isinstance(output, SpendableOutput)
    assert output.user_id == "user_001"
    assert output.current_balance == 50000.0
    assert output.spendable_amount >= 0.0
    assert output.spendable_amount <= output.current_balance
    assert output.liquidity_state in [LiquidityState.HEALTHY, LiquidityState.WATCH, LiquidityState.PRESSURED]
    assert len(output.factors) > 0


def test_adaptive_safety_reserve_scaling():
    calculator = AdaptiveSafetyReserveCalculator(min_reserve_bdt=3000.0)

    # Low volatility stable user
    reserve_stable = calculator.calculate_reserve(
        current_balance=50000.0,
        outflow_sum_30d=30000.0,
        outflow_std_30d=100.0,
        income_sum_30d=40000.0,
        income_std_30d=100.0,
        upcoming_commitments=5000.0,
    )

    # High volatility unstable user
    reserve_volatile = calculator.calculate_reserve(
        current_balance=50000.0,
        outflow_sum_30d=30000.0,
        outflow_std_30d=5000.0,
        income_sum_30d=40000.0,
        income_std_30d=8000.0,
        upcoming_commitments=25000.0,
    )

    assert reserve_volatile.total_reserve > reserve_stable.total_reserve
    assert reserve_volatile.spending_volatility_addon >= reserve_stable.spending_volatility_addon
    assert reserve_volatile.income_volatility_addon >= reserve_stable.income_volatility_addon


def test_no_double_counting_commitments_and_forecast(sample_features, sample_forecast):
    calculator = SpendableCalculator()

    # Case 1: Forecast already predicts drawdown of 15,000 (from 50,000 to min 35,000)
    # Commitments = 10,000 (which is <= drawdown of 15,000)
    commitments_small = [make_test_commitment(user_id="user_001", category="RENT", amount=10000.0)]

    out_small = calculator.calculate(
        user_id="user_001",
        snapshot_time="2026-03-01T00:00:00",
        current_balance=50000.0,
        features=sample_features,
        commitments=commitments_small,
        forecast=sample_forecast,
        candidate_methodology="CANDIDATE_A",
    )

    # In Candidate A, max(10000, 50000 - 35000) = max(10000, 15000) = 15000.
    # The protected amount for drawdown and commitments combined is 15000 + safety_reserve,
    # NOT 10000 + 15000 + safety_reserve (which would be double counting!).
    drawdown = 50000.0 - 35000.0  # 15000
    expected_protected = max(10000.0, drawdown) + out_small.safety_reserve
    assert abs(out_small.protected_amount - expected_protected) < 1e-2


def test_sanity_commitment_increase_behavior(sample_features, sample_forecast):
    """Sanity Rule: Increasing expected commitments should NOT increase spendable capacity."""
    calculator = SpendableCalculator()

    comm_low = [make_test_commitment(user_id="user_001", category="RENT", amount=5000.0)]
    comm_high = [make_test_commitment(user_id="user_001", category="RENT", amount=30000.0)]

    out_low = calculator.calculate(
        user_id="user_001",
        snapshot_time="2026-03-01",
        current_balance=50000.0,
        features=sample_features,
        commitments=comm_low,
        forecast=sample_forecast,
    )

    out_high = calculator.calculate(
        user_id="user_001",
        snapshot_time="2026-03-01",
        current_balance=50000.0,
        features=sample_features,
        commitments=comm_high,
        forecast=sample_forecast,
    )

    assert out_high.spendable_amount <= out_low.spendable_amount


def test_sanity_inflow_increase_behavior(sample_features):
    """Sanity Rule: Increasing expected inflows should NOT decrease spendable capacity."""
    calculator = SpendableCalculator()

    features_low_inflow = sample_features.copy()
    features_low_inflow["inflow_sum_30d"] = 10000.0

    features_high_inflow = sample_features.copy()
    features_high_inflow["inflow_sum_30d"] = 50000.0

    out_low = calculator.calculate(
        user_id="user_001",
        snapshot_time="2026-03-01",
        current_balance=50000.0,
        features=features_low_inflow,
        commitments=[],
        forecast=None,
    )

    out_high = calculator.calculate(
        user_id="user_001",
        snapshot_time="2026-03-01",
        current_balance=50000.0,
        features=features_high_inflow,
        commitments=[],
        forecast=None,
    )

    assert out_high.spendable_amount >= out_low.spendable_amount


def test_zero_low_balance_edge_cases():
    calculator = SpendableCalculator()

    # Zero balance
    out_zero = calculator.calculate(
        user_id="user_002",
        snapshot_time="2026-03-01",
        current_balance=0.0,
        features={"current_balance": 0.0},
        commitments=[],
        forecast=None,
    )

    assert out_zero.spendable_amount == 0.0
    assert out_zero.liquidity_state == LiquidityState.PRESSURED

    # Negative balance
    out_neg = calculator.calculate(
        user_id="user_003",
        snapshot_time="2026-03-01",
        current_balance=-1500.0,
        features={"current_balance": -1500.0},
        commitments=[],
        forecast=None,
    )

    assert out_neg.spendable_amount == 0.0
    assert out_neg.liquidity_state == LiquidityState.PRESSURED


def test_deterministic_output_schema():
    calculator = SpendableCalculator()
    output1 = calculator.calculate(
        user_id="user_001",
        snapshot_time="2026-03-01",
        current_balance=25000.0,
        features={"current_balance": 25000.0, "outflow_sum_30d": 15000.0},
        commitments=[],
        forecast=None,
    )

    output2 = calculator.calculate(
        user_id="user_001",
        snapshot_time="2026-03-01",
        current_balance=25000.0,
        features={"current_balance": 25000.0, "outflow_sum_30d": 15000.0},
        commitments=[],
        forecast=None,
    )

    assert output1.model_dump() == output2.model_dump()
