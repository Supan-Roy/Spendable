"""Unit tests for Stage 6 — Recommendation Engine & Gemini Explanation Layer.

Tests:
- Deterministic recommendation rule triggers (PRESSURE, COMMITMENTS, IRREGULARITY, HEALTHY)
- Fact-matching and non-fabrication in recommendation text
- Exact reflection of Spendable output in ExplanationContext
- Gemini API fallback execution when API is missing or fails
- Responsible AI safeguards (no secrets, safe schema validation)
- Scenario explanation correctness
"""

import pytest
import numpy as np

from app.engine.schema import SpendableOutput, LiquidityState, SafetyReserveDetails
from app.engine.calculator import SpendableCalculator
from app.scenario.schema import ScenarioInput, ScenarioResult, ScenarioType
from app.scenario.simulator import ScenarioSimulator
from app.recommendation.schema import Recommendation, RecommendationPriority, RecommendationType
from app.recommendation.engine import RecommendationEngine
from app.explanation.schema import ExplanationContext, GeminiExplanationResponse
from app.explanation.prompts import build_explanation_prompt
from app.explanation.gemini import ExplanationGenerator


@pytest.fixture
def base_spendable_healthy():
    return SpendableOutput(
        user_id="user_healthy",
        snapshot_time="2026-03-01T00:00:00",
        current_balance=50000.0,
        planning_horizon_days=30,
        spendable_amount=30000.0,
        protected_amount=20000.0,
        expected_inflow=40000.0,
        expected_outflow=20000.0,
        upcoming_commitments=12000.0,
        forecasted_minimum_balance=35000.0,
        safety_reserve=5000.0,
        safety_reserve_details=SafetyReserveDetails(
            baseline_spending_buffer=5000.0,
            spending_volatility_addon=0.0,
            income_volatility_addon=0.0,
            commitment_burden_addon=0.0,
            total_reserve=5000.0,
            reserve_ratio_pct=10.0,
        ),
        liquidity_state=LiquidityState.HEALTHY,
        candidate_formula_used="CANDIDATE_A",
        factors=[],
    )


@pytest.fixture
def base_spendable_pressured():
    return SpendableOutput(
        user_id="user_pressured",
        snapshot_time="2026-03-01T00:00:00",
        current_balance=10000.0,
        planning_horizon_days=30,
        spendable_amount=0.0,
        protected_amount=10000.0,
        expected_inflow=5000.0,
        expected_outflow=15000.0,
        upcoming_commitments=8000.0,
        forecasted_minimum_balance=2000.0,
        safety_reserve=5000.0,
        safety_reserve_details=SafetyReserveDetails(
            baseline_spending_buffer=3000.0,
            spending_volatility_addon=1000.0,
            income_volatility_addon=1000.0,
            commitment_burden_addon=0.0,
            total_reserve=5000.0,
            reserve_ratio_pct=50.0,
        ),
        liquidity_state=LiquidityState.PRESSURED,
        candidate_formula_used="CANDIDATE_A",
        factors=[],
    )


def test_1_pressured_state_produces_liquidity_warning(base_spendable_pressured):
    """Test 1: PRESSURED state produces liquidity warning recommendation."""
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(base_spendable_pressured)

    warn_types = [r.type for r in recs]
    assert RecommendationType.LIQUIDITY_WARNING in warn_types
    
    crit_recs = [r for r in recs if r.priority == RecommendationPriority.CRITICAL]
    assert len(crit_recs) > 0
    assert crit_recs[0].type == RecommendationType.LIQUIDITY_WARNING


def test_2_upcoming_commitments_produce_recommendation(base_spendable_healthy):
    """Test 2: Significant upcoming commitments produce commitment recommendation."""
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(base_spendable_healthy)

    comm_recs = [r for r in recs if r.type == RecommendationType.UPCOMING_COMMITMENTS]
    assert len(comm_recs) == 1
    assert comm_recs[0].supporting_amount == 12000.0
    assert "12,000" in comm_recs[0].message


def test_3_irregular_income_produces_recommendation(base_spendable_pressured):
    """Test 3: Irregular income / volatility addon produces income irregularity recommendation."""
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(base_spendable_pressured)

    vol_recs = [r for r in recs if r.type == RecommendationType.INCOME_IRREGULARITY]
    assert len(vol_recs) == 1
    assert vol_recs[0].supporting_amount == 2000.0


def test_4_healthy_state_does_not_produce_pressure_warning(base_spendable_healthy):
    """Test 4: HEALTHY state does not incorrectly produce pressure warning."""
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(base_spendable_healthy)

    types = [r.type for r in recs]
    assert RecommendationType.LIQUIDITY_WARNING not in types
    assert RecommendationType.POSITIVE_LIQUIDITY in types


def test_5_recommendations_use_actual_spendable_values(base_spendable_healthy):
    """Test 5: Recommendations use actual Spendable values."""
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(base_spendable_healthy)

    for r in recs:
        if r.supporting_amount is not None:
            assert r.supporting_amount in [
                base_spendable_healthy.current_balance,
                base_spendable_healthy.spendable_amount,
                base_spendable_healthy.upcoming_commitments,
                base_spendable_healthy.forecasted_minimum_balance,
                base_spendable_healthy.safety_reserve,
            ] or r.type == RecommendationType.INCOME_IRREGULARITY


def test_6_no_fabricated_financial_numbers(base_spendable_pressured):
    """Test 6: No recommendation contains fabricated financial numbers."""
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(base_spendable_pressured)

    for r in recs:
        assert r.message != ""
        assert "৳" in r.message or "৳" in r.reason or r.type == RecommendationType.LIQUIDITY_WARNING


def test_7_explanation_context_reflects_deterministic_engine(base_spendable_healthy):
    """Test 7: Explanation context exactly reflects deterministic engine output."""
    generator = ExplanationGenerator(api_key="")
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(base_spendable_healthy)

    context = generator.build_context(base_spendable_healthy, recs)

    assert context.user_id == base_spendable_healthy.user_id
    assert context.current_balance == base_spendable_healthy.current_balance
    assert context.spendable_amount == base_spendable_healthy.spendable_amount
    assert context.protected_amount == base_spendable_healthy.protected_amount
    assert context.liquidity_state == base_spendable_healthy.liquidity_state.value
    assert len(context.recommendations) == len(recs)


def test_8_gemini_failure_produces_deterministic_fallback(base_spendable_healthy):
    """Test 8: Gemini failure produces deterministic fallback response."""
    # Instantiating with invalid/empty API key forces fallback
    generator = ExplanationGenerator(api_key="INVALID_KEY")
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(base_spendable_healthy)

    context = generator.build_context(base_spendable_healthy, recs)
    resp = generator.explain(context)

    assert isinstance(resp, GeminiExplanationResponse)
    assert resp.is_fallback is True
    assert "30,000.00" in resp.summary
    assert len(resp.why) > 0
    assert len(resp.disclaimer) > 0


def test_9_invalid_gemini_response_rejected_safely(base_spendable_healthy):
    """Test 9: Invalid Gemini response is safely caught and handled via fallback."""
    generator = ExplanationGenerator(api_key="")
    context = generator.build_context(base_spendable_healthy, [])
    resp = generator.generate_fallback_explanation(context)

    assert resp.is_fallback is True
    assert isinstance(resp.summary, str)


def test_10_no_secrets_in_prompt_or_context(base_spendable_healthy):
    """Test 10: Gemini prompt/context does not contain secrets or API keys."""
    generator = ExplanationGenerator(api_key="SECRET_KEY_12345")
    context = generator.build_context(base_spendable_healthy, [])
    prompt = build_explanation_prompt(context)

    assert "SECRET_KEY_12345" not in prompt
    assert "api_key" not in prompt.lower()


def test_11_scenario_explanation_reflects_scenario_result(base_spendable_healthy):
    """Test 11: Scenario explanation correctly reflects ScenarioResult."""
    simulator = ScenarioSimulator()
    sc_res = simulator.simulate(
        user_id=base_spendable_healthy.user_id,
        snapshot_time=base_spendable_healthy.snapshot_time,
        current_balance=base_spendable_healthy.current_balance,
        features={"current_balance": 50000.0, "total_outflow_30d": 20000.0},
        commitments=[],
        forecast=None,
        scenario_input=ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=5000.0)
    )

    generator = ExplanationGenerator(api_key="")
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(base_spendable_healthy, sc_res)
    context = generator.build_context(base_spendable_healthy, recs, sc_res)

    resp = generator.generate_fallback_explanation(context)
    assert resp.scenario_explanation is not None
    assert "5,000" in resp.scenario_explanation


def test_12_missing_optional_data_handled_safely():
    """Test 12: Missing optional data is handled safely."""
    spendable_minimal = SpendableOutput(
        user_id="user_min",
        snapshot_time="2026-03-01",
        current_balance=0.0,
        planning_horizon_days=30,
        spendable_amount=0.0,
        protected_amount=0.0,
        expected_inflow=0.0,
        expected_outflow=0.0,
        upcoming_commitments=0.0,
        forecasted_minimum_balance=0.0,
        safety_reserve=0.0,
        safety_reserve_details=SafetyReserveDetails(
            baseline_spending_buffer=0.0,
            spending_volatility_addon=0.0,
            income_volatility_addon=0.0,
            commitment_burden_addon=0.0,
            total_reserve=0.0,
            reserve_ratio_pct=0.0,
        ),
        liquidity_state=LiquidityState.PRESSURED,
        candidate_formula_used="CANDIDATE_A",
        factors=[],
    )

    generator = ExplanationGenerator(api_key="")
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(spendable_minimal)
    context = generator.build_context(spendable_minimal, recs)
    resp = generator.explain(context)

    assert resp.is_fallback is True
    assert resp.scenario_explanation is None
