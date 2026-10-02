"""Adaptive Safety Reserve Calculator.

Computes a dynamic, behavior-aware safety buffer (R_safe) based on:
- Baseline spending velocity
- Spending volatility (coefficient of variation)
- Income volatility and regularity
- Recurring commitment burden ratio

Avoids fixed arbitrary percentage caps or static persona labels.
"""

from typing import Dict, Any, Optional
from app.engine.schema import SafetyReserveDetails


class AdaptiveSafetyReserveCalculator:
    """Calculates adaptive safety reserve tailored to user spending and income patterns."""

    def __init__(
        self,
        min_reserve_bdt: float = 3000.0,
        baseline_days_cover: float = 7.0,
        max_balance_reserve_pct: float = 0.60,
    ):
        self.min_reserve_bdt = min_reserve_bdt
        self.baseline_days_cover = baseline_days_cover
        self.max_balance_reserve_pct = max_balance_reserve_pct

    def calculate_reserve(
        self,
        current_balance: float,
        outflow_sum_30d: float,
        outflow_std_30d: float,
        income_sum_30d: float,
        income_std_30d: float,
        upcoming_commitments: float = 0.0,
    ) -> SafetyReserveDetails:
        """Calculate dynamic safety reserve details from observable user features at T."""
        if current_balance <= 0:
            return SafetyReserveDetails(
                baseline_spending_buffer=0.0,
                spending_volatility_addon=0.0,
                income_volatility_addon=0.0,
                commitment_burden_addon=0.0,
                total_reserve=0.0,
                reserve_ratio_pct=0.0,
            )

        # 1. Baseline spending buffer (cover N days of average daily outflow)
        daily_outflow_avg = max(0.0, outflow_sum_30d / 30.0)
        baseline_buffer = max(
            self.min_reserve_bdt,
            daily_outflow_avg * self.baseline_days_cover,
        )

        # 2. Spending Volatility Addon
        # Coefficient of variation CV = std / mean
        if daily_outflow_avg > 0 and outflow_std_30d > 0:
            spending_cv = outflow_std_30d / (daily_outflow_avg + 1e-5)
            # Add up to 50% of baseline buffer for high spending volatility
            spending_vol_mult = min(1.0, max(0.0, (spending_cv - 0.3) * 0.5))
            spending_volatility_addon = baseline_buffer * spending_vol_mult
        else:
            spending_volatility_addon = 0.0

        # 3. Income Volatility Addon
        daily_income_avg = max(0.0, income_sum_30d / 30.0)
        if daily_income_avg > 0 and income_std_30d > 0:
            income_cv = income_std_30d / (daily_income_avg + 1e-5)
            # Irregular income adds up to 40% cushion
            income_vol_mult = min(0.8, max(0.0, income_cv * 0.4))
            income_volatility_addon = baseline_buffer * income_vol_mult
        elif income_sum_30d == 0:
            # Zero observed income in 30d (high risk)
            income_volatility_addon = baseline_buffer * 0.35
        else:
            income_volatility_addon = 0.0

        # 4. Commitment Burden Addon
        commitment_ratio = upcoming_commitments / (current_balance + 1e-5)
        if commitment_ratio > 0.3:
            commitment_burden_addon = upcoming_commitments * min(0.20, (commitment_ratio - 0.3) * 0.5)
        else:
            commitment_burden_addon = 0.0

        # Total un-capped reserve
        raw_total_reserve = (
            baseline_buffer
            + spending_volatility_addon
            + income_volatility_addon
            + commitment_burden_addon
        )

        # Cap reserve to reasonable fraction of balance to avoid squeezing liquidity
        max_allowed_reserve = max(self.min_reserve_bdt, current_balance * self.max_balance_reserve_pct)
        total_reserve = min(raw_total_reserve, max_allowed_reserve)
        
        # Bounded by current balance
        total_reserve = min(total_reserve, current_balance)

        reserve_ratio_pct = (total_reserve / current_balance) * 100.0 if current_balance > 0 else 0.0

        return SafetyReserveDetails(
            baseline_spending_buffer=round(baseline_buffer, 2),
            spending_volatility_addon=round(spending_volatility_addon, 2),
            income_volatility_addon=round(income_volatility_addon, 2),
            commitment_burden_addon=round(commitment_burden_addon, 2),
            total_reserve=round(total_reserve, 2),
            reserve_ratio_pct=round(reserve_ratio_pct, 2),
        )
