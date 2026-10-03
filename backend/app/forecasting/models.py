"""Supervised machine learning cash-flow forecasting model.

Uses HistGradientBoostingRegressor to predict multi-horizon future minimum balances,
expected cash flows, liquidity pressure, and 30-day daily projected trajectories.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from app.forecasting.schema import (
    DailyTrajectoryPoint,
    ForecastModelType,
    ForecastOutput,
    HorizonForecast,
)

# Feature columns used for supervised model training and inference
FEATURE_COLS = [
    "current_balance",
    "balance_min_7d",
    "balance_min_14d",
    "balance_min_30d",
    "balance_max_30d",
    "balance_mean_30d",
    "balance_std_30d",
    "balance_change_7d",
    "balance_change_30d",
    "total_inflow_7d",
    "total_inflow_14d",
    "total_inflow_30d",
    "inflow_count_30d",
    "inflow_mean_30d",
    "inflow_std_30d",
    "total_outflow_7d",
    "total_outflow_14d",
    "total_outflow_30d",
    "outflow_count_30d",
    "outflow_mean_30d",
    "outflow_std_30d",
    "net_cash_flow_7d",
    "net_cash_flow_14d",
    "net_cash_flow_30d",
    "spending_velocity_7d_vs_30d",
    "burn_rate_daily_30d",
    "runway_days_est",
    "discretionary_outflow_30d",
    "discretionary_outflow_ratio",
    "large_outflow_count_30d",
    "large_outflow_sum_30d",
    "recurring_outflow_7d",
    "recurring_outflow_14d",
    "recurring_outflow_30d",
    "recurring_inflow_30d",
    "recurring_commitment_count",
    "recurring_confidence_max",
]


class CashFlowForecastModel:
    """Multi-horizon machine learning model for short-term liquidity forecasting."""

    def __init__(self, random_seed: int = 42, model_name: str = "HIST_GRADIENT_BOOSTING"):
        self.random_seed = random_seed
        self.model_name = model_name
        self.is_fitted = False
        self.feature_cols = FEATURE_COLS

        # Regression estimators per horizon for minimum balance
        self.models_min_bal: Dict[int, HistGradientBoostingRegressor] = {
            7: HistGradientBoostingRegressor(random_state=random_seed, max_iter=150, min_samples_leaf=20),
            14: HistGradientBoostingRegressor(random_state=random_seed, max_iter=150, min_samples_leaf=20),
            30: HistGradientBoostingRegressor(random_state=random_seed, max_iter=150, min_samples_leaf=20),
        }

        # Regression estimators per horizon for net cash flow
        self.models_net_flow: Dict[int, HistGradientBoostingRegressor] = {
            7: HistGradientBoostingRegressor(random_state=random_seed, max_iter=100, min_samples_leaf=20),
            14: HistGradientBoostingRegressor(random_state=random_seed, max_iter=100, min_samples_leaf=20),
            30: HistGradientBoostingRegressor(random_state=random_seed, max_iter=100, min_samples_leaf=20),
        }

        # Residual std for prediction intervals
        self.residual_std: Dict[int, float] = {7: 1500.0, 14: 2500.0, 30: 4000.0}

    def fit(self, df_train: pd.DataFrame) -> "CashFlowForecastModel":
        """Fit model estimators on training feature dataset."""
        # Clean feature columns presence
        valid_cols = [c for c in self.feature_cols if c in df_train.columns]
        self.feature_cols = valid_cols

        X_train = df_train[self.feature_cols].fillna(0.0).values

        for H in (7, 14, 30):
            target_min_col = f"target_future_min_balance_{H}d"
            if target_min_col in df_train.columns:
                y_min = df_train[target_min_col].fillna(0.0).values
                self.models_min_bal[H].fit(X_train, y_min)
                preds_min = self.models_min_bal[H].predict(X_train)
                self.residual_std[H] = float(np.std(y_min - preds_min))

            target_net_col = f"target_future_net_cash_flow_{H}d"
            if target_net_col in df_train.columns:
                y_net = df_train[target_net_col].fillna(0.0).values
                self.models_net_flow[H].fit(X_train, y_net)
            else:
                # Fallback: target derived from balance change
                if f"target_future_min_balance_{H}d" in df_train.columns:
                    y_net = (df_train[f"target_future_min_balance_{H}d"] - df_train["current_balance"]).fillna(0.0).values
                    self.models_net_flow[H].fit(X_train, y_net)

        self.is_fitted = True
        return self

    def predict_snapshot(
        self,
        snapshot_features: Dict[str, Any],
        safety_threshold_bdt: float = 15000.0,
    ) -> ForecastOutput:
        """Generate structured liquidity forecast for a single snapshot."""
        user_id = str(snapshot_features.get("account_id") or snapshot_features.get("user_id") or "")
        snap_time_str = str(snapshot_features.get("snapshot_timestamp") or snapshot_features.get("snapshot_time") or "")
        current_balance = float(snapshot_features.get("current_balance", 0.0))

        if not self.is_fitted:
            # Fallback heuristic prediction if not fitted yet
            return self._heuristic_fallback(snapshot_features, safety_threshold_bdt)

        # Prepare feature vector
        x_vec = []
        for col in self.feature_cols:
            x_vec.append(float(snapshot_features.get(col, 0.0)))

        X = np.array([x_vec])

        exp_inflow_feat = float(snapshot_features.get("total_inflow_30d") or snapshot_features.get("sum_inflow_30d") or snapshot_features.get("inflow_sum_30d") or 0.0)
        exp_outflow_feat = float(snapshot_features.get("total_outflow_30d") or snapshot_features.get("sum_outflow_30d") or snapshot_features.get("outflow_sum_30d") or 0.0)

        forecasts: Dict[int, HorizonForecast] = {}
        for H in (7, 14, 30):
            pred_min_bal = float(self.models_min_bal[H].predict(X)[0])
            pred_net_flow = float(self.models_net_flow[H].predict(X)[0])

            # Bound predictions logically
            min_bal = round(max(0.0, pred_min_bal), 2)
            proj_bal = round(max(0.0, current_balance + pred_net_flow), 2)

            exp_inflow = round(max(0.0, exp_inflow_feat * (H / 30.0)), 2)
            exp_outflow = round(max(0.0, exp_outflow_feat * (H / 30.0)), 2) if exp_outflow_feat > 0 else round(max(0.0, exp_inflow - pred_net_flow), 2)


            r_std = self.residual_std.get(H, 2000.0)
            lower_bound = round(max(0.0, min_bal - 1.645 * r_std), 2)
            upper_bound = round(min_bal + 1.645 * r_std, 2)

            forecasts[H] = HorizonForecast(
                horizon_days=H,
                expected_inflow=exp_inflow,
                expected_outflow=exp_outflow,
                expected_net_cash_flow=round(pred_net_flow, 2),
                projected_balance=proj_bal,
                minimum_projected_balance=min_bal,
                liquidity_pressure_flag=(min_bal < safety_threshold_bdt),
                estimated_range_lower=lower_bound,
                estimated_range_upper=upper_bound,
            )

        # Build 30-day daily projected trajectory with realistic cash flow dynamics
        trajectory: List[DailyTrajectoryPoint] = []
        snap_dt = self._parse_datetime(snap_time_str) if snap_time_str else datetime.now()

        b7 = forecasts[7].projected_balance
        b14 = forecasts[14].projected_balance
        b30 = forecasts[30].projected_balance

        # Calculate estimated daily scale for natural cash flow waves
        inflow_scale = exp_inflow_feat if exp_inflow_feat > 0 else 15000.0
        outflow_scale = exp_outflow_feat if exp_outflow_feat > 0 else 10000.0

        for d in range(1, 31):
            if d <= 7:
                alpha = d / 7.0
                base_bal = current_balance + alpha * (b7 - current_balance)
            elif d <= 14:
                alpha = (d - 7) / 7.0
                base_bal = b7 + alpha * (b14 - b7)
            else:
                alpha = (d - 14) / 16.0
                base_bal = b14 + alpha * (b30 - b14)

            # Intra-month cash flow dynamics (payday spikes on 1st/15th, bill dips on 5th/25th, weekend outlays)
            cal_day = (snap_dt + timedelta(days=d)).day
            import math
            micro_wave = math.sin(2.0 * math.pi * d / 7.0) * (outflow_scale * 0.03)

            event_offset = 0.0
            if cal_day in (1, 15):
                event_offset += inflow_scale * 0.08
            elif cal_day in (5, 25):
                event_offset -= outflow_scale * 0.07

            d_bal = max(0.0, base_bal + micro_wave + event_offset)
            d_date = (snap_dt + timedelta(days=d)).strftime("%Y-%m-%d")
            d_buffer = round(safety_threshold_bdt * (0.65 + 0.35 * (d / 30.0)) + (outflow_scale * 0.04 if cal_day in (5, 25) else 0.0), 2)
            trajectory.append(
                DailyTrajectoryPoint(
                    day_offset=d,
                    date_str=d_date,
                    projected_balance=round(d_bal, 2),
                    required_buffer=d_buffer,
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

    def _heuristic_fallback(
        self, snapshot_features: Dict[str, Any], safety_threshold_bdt: float
    ) -> ForecastOutput:
        user_id = str(snapshot_features.get("account_id") or snapshot_features.get("user_id") or "")
        snap_time_str = str(snapshot_features.get("snapshot_timestamp") or snapshot_features.get("snapshot_time") or "")
        current_balance = float(snapshot_features.get("current_balance", 0.0))

        tot_inflow = float(
            snapshot_features.get("total_inflow_30d")
            or snapshot_features.get("sum_inflow_30d")
            or snapshot_features.get("inflow_sum_30d")
            or 0.0
        )
        tot_outflow = float(
            snapshot_features.get("total_outflow_30d")
            or snapshot_features.get("sum_outflow_30d")
            or snapshot_features.get("outflow_sum_30d")
            or 0.0
        )

        net_30d = float(snapshot_features.get("net_cash_flow_30d", tot_inflow - tot_outflow))
        daily_rate = net_30d / 30.0

        forecasts = {}
        for H in (7, 14, 30):
            exp_net = round(daily_rate * H, 2)
            exp_in = round(tot_inflow * (H / 30.0), 2) if tot_inflow > 0 else round(max(0.0, exp_net), 2)
            exp_out = round(tot_outflow * (H / 30.0), 2) if tot_outflow > 0 else round(max(0.0, -exp_net), 2)
            min_b = round(max(0.0, current_balance + min(0.0, exp_net)), 2)
            proj_b = round(max(0.0, current_balance + exp_net), 2)
            forecasts[H] = HorizonForecast(
                horizon_days=H,
                expected_inflow=exp_in,
                expected_outflow=exp_out,
                expected_net_cash_flow=exp_net,
                projected_balance=proj_b,
                minimum_projected_balance=min_b,
                liquidity_pressure_flag=(min_b < safety_threshold_bdt),
                estimated_range_lower=round(max(0.0, min_b - 2000.0), 2),
                estimated_range_upper=round(min_b + 2000.0, 2),
            )

        trajectory = []
        snap_dt = self._parse_datetime(snap_time_str)
        import math
        for d in range(1, 31):
            base_b = current_balance + daily_rate * d
            cal_day = (snap_dt + timedelta(days=d)).day
            wave = math.sin(2.0 * math.pi * d / 7.0) * (tot_outflow * 0.03 if tot_outflow > 0 else 300.0)
            event = 0.0
            if cal_day in (1, 15):
                event += (tot_inflow * 0.08 if tot_inflow > 0 else 1000.0)
            elif cal_day in (5, 25):
                event -= (tot_outflow * 0.07 if tot_outflow > 0 else 800.0)

            d_bal = max(0.0, base_b + wave + event)
            d_date = (snap_dt + timedelta(days=d)).strftime("%Y-%m-%d")
            d_buffer = round(safety_threshold_bdt * (0.65 + 0.35 * (d / 30.0)) + (tot_outflow * 0.04 if cal_day in (5, 25) else 0.0), 2)
            trajectory.append(
                DailyTrajectoryPoint(
                    day_offset=d,
                    date_str=d_date,
                    projected_balance=round(d_bal, 2),
                    required_buffer=d_buffer,
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
            model_version=f"{self.model_name}_UNFITTED_FALLBACK",
            safety_threshold_bdt=safety_threshold_bdt,
        )

    def _parse_datetime(self, val: str) -> datetime:
        try:
            return datetime.fromisoformat(str(val).replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return datetime.now()
