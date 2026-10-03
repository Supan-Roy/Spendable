"""Gemini Explanation Layer & Deterministic Fallback Engine.

Converts structured ExplanationContext into human-readable explanations using the Gemini API.
If Gemini is unavailable or fails, returns a deterministic fallback explanation ensuring zero service disruption.
"""

import hashlib
import json
import os
import time
from typing import Dict, List, Optional, Any

from app.config import settings
from app.engine.schema import SpendableOutput
from app.scenario.schema import ScenarioResult
from app.recommendation.schema import Recommendation
from app.explanation.schema import ExplanationContext, GeminiExplanationResponse
from app.explanation.prompts import SYSTEM_INSTRUCTION, build_explanation_prompt


class ExplanationGenerator:
    """Generates structured explanations via Gemini API with deterministic fallback and smart SHA256 response caching."""

    _cache: Dict[str, tuple[float, GeminiExplanationResponse]] = {}
    _cache_ttl: float = 600.0  # 10 minutes cache window

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "")

        if model_name is not None:
            self.model_name = model_name
        else:
            self.model_name = os.environ.get("GEMINI_MODEL") or getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash-lite")

    def build_context(
        self,
        spendable_output: SpendableOutput,
        recommendations: List[Recommendation],
        scenario_result: Optional[ScenarioResult] = None,
    ) -> ExplanationContext:
        """Construct facts-only ExplanationContext payload."""
        scen_dict = None
        if scenario_result:
            scen_dict = {
                "scenario_type": scenario_result.scenario_type.value,
                "scenario_description": scenario_result.scenario_description,
                "base_spendable_amount": scenario_result.base_spendable_amount,
                "scenario_spendable_amount": scenario_result.scenario_spendable_amount,
                "spendable_delta": scenario_result.spendable_delta,
                "base_liquidity_state": scenario_result.base_liquidity_state.value,
                "scenario_liquidity_state": scenario_result.scenario_liquidity_state.value,
                "assumptions": scenario_result.assumptions,
            }

        return ExplanationContext(
            user_id=spendable_output.user_id,
            snapshot_time=spendable_output.snapshot_time,
            current_balance=spendable_output.current_balance,
            spendable_amount=spendable_output.spendable_amount,
            protected_amount=spendable_output.protected_amount,
            planning_horizon_days=spendable_output.planning_horizon_days,
            expected_inflow=spendable_output.expected_inflow,
            expected_outflow=spendable_output.expected_outflow,
            upcoming_commitments=spendable_output.upcoming_commitments,
            forecasted_minimum_balance=spendable_output.forecasted_minimum_balance,
            safety_reserve=spendable_output.safety_reserve,
            liquidity_state=spendable_output.liquidity_state.value,
            recommendations=recommendations,
            scenario=scen_dict,
        )

    def explain(
        self,
        context: ExplanationContext,
    ) -> GeminiExplanationResponse:
        """Generate human-readable explanation using Gemini API or deterministic fallback."""
        if not self.api_key or self.api_key.strip() == "":
            return self.generate_fallback_explanation(context)

        # Compute deterministic cache key from financial context fields
        cache_payload = f"{context.user_id}:{context.current_balance}:{context.spendable_amount}:{context.protected_amount}:{context.upcoming_commitments}:{context.liquidity_state}:{context.scenario}"
        cache_key = hashlib.sha256(cache_payload.encode()).hexdigest()
        now = time.time()

        if cache_key in ExplanationGenerator._cache:
            cached_time, cached_resp = ExplanationGenerator._cache[cache_key]
            if now - cached_time < ExplanationGenerator._cache_ttl:
                return cached_resp

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            prompt = build_explanation_prompt(context)

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )

            text = response.text or ""
            parsed = json.loads(text)
            
            res = GeminiExplanationResponse(
                summary=str(parsed.get("summary", "")),
                why=[str(x) for x in parsed.get("why", [])],
                key_factors=[str(x) for x in parsed.get("key_factors", [])],
                recommendations=[str(x) for x in parsed.get("recommendations", [])],
                scenario_explanation=parsed.get("scenario_explanation"),
                disclaimer=str(parsed.get("disclaimer", "Based on observed account activity.")),
                is_fallback=False,
            )

            ExplanationGenerator._cache[cache_key] = (now, res)
            return res
        except Exception:
            # On any API error, rate limit, or invalid response JSON -> Fallback
            return self.generate_fallback_explanation(context)

    def generate_fallback_explanation(
        self,
        context: ExplanationContext,
    ) -> GeminiExplanationResponse:
        """Deterministic, reliable fallback explanation generated without API dependency."""
        cur_bal = context.current_balance
        sp_amt = context.spendable_amount
        prot_amt = context.protected_amount
        commitments = context.upcoming_commitments
        min_bal = context.forecasted_minimum_balance
        reserve = context.safety_reserve
        state = context.liquidity_state

        summary = f"You have ৳{sp_amt:,.2f} safely spendable out of your ৳{cur_bal:,.2f} account balance over the next {context.planning_horizon_days} days."

        why = [
            f"Your observed balance is ৳{cur_bal:,.2f}, but ৳{prot_amt:,.2f} is protected for obligations and safety reserves.",
            f"Forecasted minimum account balance trajectory is projected at ৳{min_bal:,.2f}."
        ]

        key_factors = []
        if commitments > 0:
            key_factors.append(f"Detected recurring commitments: ৳{commitments:,.2f}")
        key_factors.append(f"Adaptive safety reserve buffer: ৳{reserve:,.2f}")
        key_factors.append(f"Categorical liquidity state: {state}")

        recs = [f"[{r.priority.value}] {r.title}: {r.message}" for r in context.recommendations]

        scen_expl = None
        if context.scenario:
            sc = context.scenario
            delta = sc.get("spendable_delta", 0.0)
            dir_str = "increase" if delta > 0 else "decrease"
            scen_expl = (
                f"Simulating scenario '{sc.get('scenario_description')}' results in a {dir_str} of "
                f"৳{abs(delta):,.2f} in spendable capacity (from ৳{sc.get('base_spendable_amount'):,.2f} "
                f"to ৳{sc.get('scenario_spendable_amount'):,.2f})."
            )

        disclaimer = (
            "This estimate is strictly derived from observed account transaction history up to the snapshot date. "
            "It does not include external accounts, physical cash, or unobserved obligations."
        )

        return GeminiExplanationResponse(
            summary=summary,
            why=why,
            key_factors=key_factors,
            recommendations=recs,
            scenario_explanation=scen_expl,
            disclaimer=disclaimer,
            is_fallback=True,
        )
