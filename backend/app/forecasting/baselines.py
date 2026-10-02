"""Baseline forecasting models for cash-flow and liquidity prediction.

Provides deterministic reference baselines:
1. Rolling Average Baseline (historical net cash-flow rate extrapolation).
2. Recurring Commitment Baseline (point-in-time detected commitment projection).
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np

from app.forecasting.schema import (
    DailyTrajectoryPoint,
    ForecastModelType,
    ForecastOutput,
    HorizonForecast,
)


class RollingAverageBaseline:
    """Baseline model extrapolating rolling 30-day net cash flow rates."""

    def __init__(self, model_name: str = "ROLLING_AVERAGE_BASELINE"):
        self.model_name = model_name

    def predict_snapshot(
        self,
        snapshot_features: Dict[str, Any],
        safety_threshold_bdt: float = 15000.0,
    ) -> ForecastOutput:
        """Predict liquidity trajectory for a single snapshot using 30-day net cash flow rate."""
        user_id = str(snapshot_features.get("account_id") or snapshot_features.get("user_id") or "")
        snap_time_str = str(snapshot_features.get("snapshot_timestamp") or snapshot_features.get("snapshot_time") or "")
        current_balance = float(snapshot_features.get("current_balance", 0.0))
        net_cash_flow_30d = float(snapshot_features.get("net_cash_flow_30d", 0.0))
        total_inflow_30d = float(snapshot_features.get("total_inflow_30d", 0.0))
        total_outflow_30d = float(snapshot_features.get("total_outflow_30d", 0.0))

        daily_rate = net_cash_flow_30d / 30.0
        daily_inflow_rate = total_inflow_30d / 30.0
        daily_outflow_rate = total_outflow_30d / 30.0

        forecasts: Dict[int, HorizonForecast] = {}
        for H in (7, 14, 30):
            exp_inflow = round(daily_inflow_rate * H, 2)
            exp_outflow = round(daily_outflow_rate * H, 2)
            exp_net = round(daily_rate * H, 2)
            proj_bal = round(max(0.0, current_balance + exp_net), 2)
            min_bal = round(max(0.0, min(current_balance, proj_bal)), 2)
            
            # Simple standard deviation estimate for prediction interval
            std_est = abs(exp_net) * 0.25 + 1000.0

            forecasts[H] = HorizonForecast(
                horizon_days=H,
                expected_inflow=exp_inflow,
                expected_outflow=exp_outflow,
                expected_net_cash_flow=exp_net,
                projected_balance=proj_bal,
                minimum_projected_balance=min_bal,
                liquidity_pressure_flag=(min_bal < safety_threshold_bdt),
                estimated_range_lower=round(max(0.0, min_bal - std_est), 2),
                estimated_range_upper=round(min_bal + std_est, 2),
            )

        # Generate 30-day daily trajectory
        trajectory: List[DailyTrajectoryPoint] = []
        snap_dt = self._parse_datetime(snap_time_str) if snap_time_str else datetime.now()
        for d in range(1, 31):
            d_bal = max(0.0, current_balance + daily_rate * d)
            d_date = (snap_dt + timedelta(days=d)).strftime("%Y-%m-%d")
            trajectory.append(
                DailyTrajectoryPoint(
                    day_offset=d,
                    date_str=d_date,
                    projected_balance=round(d_bal, 2),
                )
            )

        return ForecastOutput(
            user_id=user_id,
            snapshot_time=snap_time_str,
            current_balance=round(current_balance, 2),
            forecast_7d=forecasts[7],
            forecast_14d=forecasts[14],
            forecast_30d=forecasts[30],
            daily_trajectory=trajectory,
            model_version=self.model_name,
            safety_threshold_bdt=safety_threshold_bdt,
        )

    def _parse_datetime(self, val: str) -> datetime:
        try:
            return datetime.fromisoformat(str(val).replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return datetime.now()


class RecurringCommitmentBaseline:
    """Baseline model projecting detected point-in-time recurring commitments."""

    def __init__(self, model_name: str = "RECURRING_COMMITMENT_BASELINE"):
        self.model_name = model_name

    def predict_snapshot(
        self,
        snapshot_features: Dict[str, Any],
        safety_threshold_bdt: float = 15000.0,
    ) -> ForecastOutput:
        """Predict liquidity trajectory by subtracting upcoming detected recurring commitments."""
        user_id = str(snapshot_features.get("account_id") or snapshot_features.get("user_id") or "")
        snap_time_str = str(snapshot_features.get("snapshot_timestamp") or snapshot_features.get("snapshot_time") or "")
        current_balance = float(snapshot_features.get("current_balance", 0.0))

        # Extract detected commitment feature aggregates
        rec_out_7d = float(snapshot_features.get("recurring_outflow_7d", 0.0))
        rec_out_14d = float(snapshot_features.get("recurring_outflow_14d", 0.0))
        rec_out_30d = float(snapshot_features.get("recurring_outflow_30d", 0.0))
        rec_in_30d = float(snapshot_features.get("recurring_inflow_30d", 0.0))

        outflows = {7: rec_out_7d, 14: rec_out_14d, 30: rec_out_30d}
        inflows = {7: round(rec_in_30d * (7.0 / 30.0), 2), 14: round(rec_in_30d * (14.0 / 30.0), 2), 30: rec_in_30d}

        forecasts: Dict[int, HorizonForecast] = {}
        for H in (7, 14, 30):
            exp_out = outflows[H]
            exp_in = inflows[H]
            exp_net = round(exp_in - exp_out, 2)
            proj_bal = round(max(0.0, current_balance + exp_net), 2)
            min_bal = round(max(0.0, current_balance - exp_out), 2)
            
            std_est = abs(exp_out) * 0.2 + 800.0

            forecasts[H] = HorizonForecast(
                horizon_days=H,
                expected_inflow=exp_in,
                expected_outflow=exp_out,
                expected_net_cash_flow=exp_net,
                projected_balance=proj_bal,
                minimum_projected_balance=min_bal,
                liquidity_pressure_flag=(min_bal < safety_threshold_bdt),
                estimated_range_lower=round(max(0.0, min_bal - std_est), 2),
                estimated_range_upper=round(min_bal + std_est, 2),
            )

        trajectory: List[DailyTrajectoryPoint] = []
        snap_dt = self._parse_datetime(snap_time_str) if snap_time_str else datetime.now()
        for d in range(1, 31):
            daily_out = rec_out_30d * (d / 30.0)
            daily_in = rec_in_30d * (d / 30.0)
            d_bal = max(0.0, current_balance + daily_in - daily_out)
            d_date = (snap_dt + timedelta(days=d)).strftime("%Y-%m-%d")
            trajectory.append(
                DailyTrajectoryPoint(
                    day_offset=d,
                    date_str=d_date,
                    projected_balance=round(d_bal, 2),
                )
            )

        return ForecastOutput(
            user_id=user_id,
            snapshot_time=snap_time_str,
            current_balance=round(current_balance, 2),
            forecast_7d=forecasts[7],
            forecast_14d=forecasts[14],
            forecast_30d=forecasts[30],
            daily_trajectory=trajectory,
            model_version=self.model_name,
            safety_threshold_bdt=safety_threshold_bdt,
        )

    def _parse_datetime(self, val: str) -> datetime:
        try:
            return datetime.fromisoformat(str(val).replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return datetime.now()
