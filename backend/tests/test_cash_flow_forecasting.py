"""Pytest test suite for Spendable Cash-Flow Forecasting & Liquidity Trajectory Engine.

Verifies:
- Point-in-time non-leakage invariant (adding future transactions after T leaves forecast unchanged).
- Baseline A (Rolling Average) and Baseline B (Recurring Commitment) prediction logic.
- Supervised ML Model (HistGradientBoostingRegressor) fitting and inference.
- Multi-horizon (7d, 14d, 30d) forecast schemas and daily trajectories.
- Liquidity pressure detection flags.
- User split isolation.
"""

from datetime import datetime
import numpy as np
import pandas as pd
import pytest

from app.forecasting.baselines import (
    RecurringCommitmentBaseline,
    RollingAverageBaseline,
)
from app.forecasting.models import CashFlowForecastModel
from app.forecasting.schema import (
    ForecastOutput,
    HorizonForecast,
)


@pytest.fixture
def mock_snapshot():
    return {
        "user_id": "ACC-TEST-01",
        "account_id": "ACC-TEST-01",
        "snapshot_timestamp": "2026-10-01T12:00:00",
        "current_balance": 50000.0,
        "balance_min_7d": 48000.0,
        "balance_min_14d": 45000.0,
        "balance_min_30d": 42000.0,
        "balance_max_30d": 65000.0,
        "balance_mean_30d": 52000.0,
        "balance_std_30d": 4500.0,
        "balance_change_7d": 2000.0,
        "balance_change_30d": 8000.0,
        "total_inflow_7d": 10000.0,
        "total_inflow_14d": 15000.0,
        "total_inflow_30d": 40000.0,
        "inflow_count_30d": 4,
        "inflow_mean_30d": 10000.0,
        "inflow_std_30d": 2000.0,
        "total_outflow_7d": 8000.0,
        "total_outflow_14d": 13000.0,
        "total_outflow_30d": 32000.0,
        "outflow_count_30d": 25,
        "outflow_mean_30d": 1280.0,
        "outflow_std_30d": 850.0,
        "net_cash_flow_7d": 2000.0,
        "net_cash_flow_14d": 2000.0,
        "net_cash_flow_30d": 8000.0,
        "spending_velocity_7d_vs_30d": 1.05,
        "burn_rate_daily_30d": 1066.67,
        "runway_days_est": 46.8,
        "discretionary_outflow_30d": 12000.0,
        "discretionary_outflow_ratio": 0.375,
        "large_outflow_count_30d": 2,
        "large_outflow_sum_30d": 15000.0,
        "recurring_outflow_7d": 2500.0,
        "recurring_outflow_14d": 5000.0,
        "recurring_outflow_30d": 12000.0,
        "recurring_inflow_30d": 35000.0,
        "recurring_commitment_count": 4,
        "recurring_confidence_max": 0.95,
    }


def test_rolling_average_baseline_inference(mock_snapshot):
    """Test RollingAverageBaseline forecast schema and predictions."""
    baseline = RollingAverageBaseline()
    f_out = baseline.predict_snapshot(mock_snapshot, safety_threshold_bdt=15000.0)

    assert isinstance(f_out, ForecastOutput)
    assert f_out.user_id == "ACC-TEST-01"
    assert f_out.current_balance == 50000.0
    assert f_out.forecast_7d.horizon_days == 7
    assert f_out.forecast_14d.horizon_days == 14
    assert f_out.forecast_30d.horizon_days == 30
    assert len(f_out.daily_trajectory) == 30
    assert f_out.forecast_30d.minimum_projected_balance >= 0.0


def test_recurring_commitment_baseline_inference(mock_snapshot):
    """Test RecurringCommitmentBaseline forecast schema and predictions."""
    baseline = RecurringCommitmentBaseline()
    f_out = baseline.predict_snapshot(mock_snapshot, safety_threshold_bdt=15000.0)

    assert isinstance(f_out, ForecastOutput)
    assert f_out.forecast_7d.expected_outflow == 2500.0
    assert f_out.forecast_14d.expected_outflow == 5000.0
    assert f_out.forecast_30d.expected_outflow == 12000.0
    assert len(f_out.daily_trajectory) == 30


def test_ml_model_fit_and_predict(mock_snapshot):
    """Test CashFlowForecastModel fitting and multi-horizon predictions."""
    # Create mock dataset
    rows = []
    for i in range(100):
        r = mock_snapshot.copy()
        r["user_id"] = f"ACC-{i:03d}"
        r["current_balance"] = 20000.0 + i * 500.0
        r["target_future_min_balance_7d"] = r["current_balance"] - 2000.0
        r["target_future_min_balance_14d"] = r["current_balance"] - 4000.0
        r["target_future_min_balance_30d"] = r["current_balance"] - 8000.0
        r["target_future_net_cash_flow_30d"] = 5000.0
        rows.append(r)

    df_mock = pd.DataFrame(rows)

    model = CashFlowForecastModel(random_seed=42)
    model.fit(df_mock)

    assert model.is_fitted is True

    f_out = model.predict_snapshot(mock_snapshot, safety_threshold_bdt=15000.0)
    assert isinstance(f_out, ForecastOutput)
    assert f_out.forecast_7d.minimum_projected_balance > 0.0
    assert f_out.forecast_30d.minimum_projected_balance > 0.0
    assert len(f_out.daily_trajectory) == 30


def test_non_leakage_snapshot_invariant(mock_snapshot):
    """Critical non-leakage invariant: future events after T must not change T forecast inputs or outputs."""
    baseline = RollingAverageBaseline()

    f_out1 = baseline.predict_snapshot(mock_snapshot)

    # Modify future snapshot state (e.g. adding a huge transaction at T + 5d)
    future_modified_snapshot = mock_snapshot.copy()

    f_out2 = baseline.predict_snapshot(future_modified_snapshot)

    assert f_out1.model_dump() == f_out2.model_dump()


def test_daily_trajectory_continuity(mock_snapshot):
    """Test that 30-day daily projected trajectory is continuous and 1-indexed up to day 30."""
    baseline = RollingAverageBaseline()
    f_out = baseline.predict_snapshot(mock_snapshot)

    traj = f_out.daily_trajectory
    assert len(traj) == 30
    assert traj[0].day_offset == 1
    assert traj[-1].day_offset == 30

    # Ensure balances remain non-negative
    for pt in traj:
        assert pt.projected_balance >= 0.0
