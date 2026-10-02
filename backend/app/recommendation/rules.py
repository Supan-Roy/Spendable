"""Deterministic Recommendation Rules Engine.

Evaluates objective financial conditions on SpendableOutput and ScenarioResult.
Uses actual numbers from base engine outputs without generating fake data or arbitrary advice.
"""

from typing import Dict, List, Optional, Any
from app.engine.schema import SpendableOutput, LiquidityState
from app.scenario.schema import ScenarioResult
from app.recommendation.schema import (
    Recommendation,
    RecommendationPriority,
    RecommendationType,
)


class RecommendationRulesEvaluator:
    """Evaluates deterministic recommendation rules against financial outputs."""

    def evaluate(
        self,
        spendable_output: SpendableOutput,
        scenario_result: Optional[ScenarioResult] = None,
    ) -> List[Recommendation]:
        """Run all deterministic rules and return prioritized recommendations."""
        recommendations: List[Recommendation] = []

        cur_bal = spendable_output.current_balance
        sp_amt = spendable_output.spendable_amount
        commitments = spendable_output.upcoming_commitments
        min_bal = spendable_output.forecasted_minimum_balance
        reserve = spendable_output.safety_reserve
        state = spendable_output.liquidity_state

        # Rule 1: LIQUIDITY_WARNING (Trigger: PRESSURED state)
        if state == LiquidityState.PRESSURED:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.LIQUIDITY_WARNING,
                    priority=RecommendationPriority.CRITICAL,
                    title="Liquidity Under Pressure",
                    message="Your projected balance may come under pressure within the next 30 days.",
                    supporting_amount=round(min_bal, 2),
                    supporting_metric="forecasted_minimum_balance",
                    reason=f"Account is in a PRESSURED state with projected minimum balance of ৳{min_bal:,.2f} relative to ৳{reserve:,.2f} safety reserve.",
                    action="Review upcoming expenses and avoid non-essential spending.",
                )
            )

        # Rule 2: UPCOMING_COMMITMENTS (Trigger: Material recurring obligations)
        if commitments > 0 and cur_bal > 0:
            commit_ratio = commitments / cur_bal
            if commit_ratio >= 0.15 or commitments >= 5000.0:
                recommendations.append(
                    Recommendation(
                        type=RecommendationType.UPCOMING_COMMITMENTS,
                        priority=RecommendationPriority.WARNING if commit_ratio >= 0.30 else RecommendationPriority.INFO,
                        title="Upcoming Recurring Commitments",
                        message=f"You have ৳{commitments:,.2f} in detected recurring commitments over the next 30 days.",
                        supporting_amount=round(commitments, 2),
                        supporting_metric="upcoming_commitments",
                        reason=f"Detected ৳{commitments:,.2f} in recurring obligations representing {commit_ratio*100:.1f}% of current balance.",
                        action="Ensure account has sufficient funds to cover scheduled bills.",
                    )
                )

        # Rule 3: SPENDING_CAUTION (Trigger: Small spendable capacity relative to balance)
        if sp_amt < 0.25 * cur_bal and cur_bal > 0 and state != LiquidityState.PRESSURED:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.SPENDING_CAUTION,
                    priority=RecommendationPriority.WARNING,
                    title="Limited Spendable Capacity",
                    message=f"Your estimated spendable amount is restricted to ৳{sp_amt:,.2f} ({sp_amt/cur_bal*100:.1f}% of balance).",
                    supporting_amount=round(sp_amt, 2),
                    supporting_metric="spendable_amount",
                    reason=f"High proportion of balance is protected for upcoming commitments and safety reserve.",
                    action="Pace discretionary purchases carefully until next expected income.",
                )
            )

        # Rule 4: INCOME_IRREGULARITY (Trigger: High income/spending volatility addon)
        details = spendable_output.safety_reserve_details
        if details.income_volatility_addon > 0 or details.spending_volatility_addon > 0:
            vol_addon = details.income_volatility_addon + details.spending_volatility_addon
            recommendations.append(
                Recommendation(
                    type=RecommendationType.INCOME_IRREGULARITY,
                    priority=RecommendationPriority.INFO,
                    title="Adaptive Volatility Buffer Active",
                    message="Your recent cash flow has shown variability, so your safety buffer has been expanded.",
                    supporting_amount=round(vol_addon, 2),
                    supporting_metric="volatility_addon",
                    reason=f"Safety reserve includes an additional ৳{vol_addon:,.2f} buffer due to cash flow volatility.",
                    action="Maintain liquidity buffer to cushion against income fluctuations.",
                )
            )

        # Rule 5: FORECAST_PRESSURE (Trigger: Min balance approaching safety reserve)
        if reserve <= min_bal < reserve * 1.5 and state != LiquidityState.PRESSURED:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.FORECAST_PRESSURE,
                    priority=RecommendationPriority.WARNING,
                    title="Forecasted Balance Near Safety Threshold",
                    message=f"Your forecasted minimum balance of ৳{min_bal:,.2f} is close to your ৳{reserve:,.2f} safety buffer.",
                    supporting_amount=round(min_bal, 2),
                    supporting_metric="forecasted_minimum_balance",
                    reason="Projected balance trajectory dips near safety threshold during planning horizon.",
                    action="Monitor daily spending trends closely.",
                )
            )

        # Rule 6: POSITIVE_LIQUIDITY (Trigger: HEALTHY state & high spendable capacity)
        if state == LiquidityState.HEALTHY and sp_amt >= 0.50 * cur_bal and cur_bal > 0:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.POSITIVE_LIQUIDITY,
                    priority=RecommendationPriority.INFO,
                    title="Healthy Liquidity Position",
                    message=f"You have ৳{sp_amt:,.2f} in safe spendable capacity available.",
                    supporting_amount=round(sp_amt, 2),
                    supporting_metric="spendable_amount",
                    reason=f"Forecasted trajectories remain strong with spendable capacity representing {sp_amt/cur_bal*100:.1f}% of current balance.",
                    action="Liquidity position is healthy for planned goals.",
                )
            )

        # Rule 7: SCENARIO_INSIGHT (Trigger: ScenarioResult present)
        if scenario_result:
            delta = scenario_result.spendable_delta
            direction_str = "increase" if delta > 0 else "reduce"
            recommendations.append(
                Recommendation(
                    type=RecommendationType.SCENARIO_INSIGHT,
                    priority=RecommendationPriority.WARNING if delta < 0 else RecommendationPriority.INFO,
                    title="Scenario Impact Insight",
                    message=f"Simulating '{scenario_result.scenario_description}' would {direction_str} your spendable amount by ৳{abs(delta):,.2f}.",
                    supporting_amount=round(delta, 2),
                    supporting_metric="spendable_delta",
                    reason=f"Hypothetical state change from ৳{scenario_result.base_spendable_amount:,.2f} to ৳{scenario_result.scenario_spendable_amount:,.2f}.",
                    action=f"State changes from {scenario_result.base_liquidity_state.value} to {scenario_result.scenario_liquidity_state.value}.",
                )
            )

        return recommendations
