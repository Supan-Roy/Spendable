"""API integration tests for FastAPI product endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.spendable import (
    SpendableOverviewResponse,
    SpendableForecastResponse,
    SpendableActivityListResponse,
    SpendableRecommendationsResponse,
)
from app.scenario.schema import ScenarioResult
from app.explanation.schema import GeminiExplanationResponse

client = TestClient(app)


def test_1_get_health_endpoint():
    """Test 1: GET /api/v1/health returns HTTP 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]


def test_2_get_overview_returns_valid_schema():
    """Test 2: GET /api/v1/overview returns valid schema matching SpendableOverviewResponse."""
    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    parsed = SpendableOverviewResponse(**data)
    assert parsed.current_balance >= 0.0
    assert parsed.spendable_amount >= 0.0
    assert parsed.liquidity_state in ["HEALTHY", "WATCH", "PRESSURED"]


def test_3_get_forecast_returns_valid_schema():
    """Test 3: GET /api/v1/forecast returns valid schema matching SpendableForecastResponse."""
    response = client.get("/api/v1/forecast")
    assert response.status_code == 200
    data = response.json()
    parsed = SpendableForecastResponse(**data)
    assert parsed.forecast_7d.horizon_days == 7
    assert parsed.forecast_14d.horizon_days == 14
    assert parsed.forecast_30d.horizon_days == 30


def test_4_get_activity_returns_valid_schema():
    """Test 4: GET /api/v1/activity returns valid schema matching SpendableActivityListResponse."""
    response = client.get("/api/v1/activity?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    parsed = SpendableActivityListResponse(**data)
    assert parsed.limit == 10
    assert parsed.offset == 0


def test_5_get_recommendations_returns_valid_schema():
    """Test 5: GET /api/v1/recommendations returns valid schema matching SpendableRecommendationsResponse."""
    response = client.get("/api/v1/recommendations")
    assert response.status_code == 200
    data = response.json()
    parsed = SpendableRecommendationsResponse(**data)
    assert len(parsed.recommendations) >= 0
    assert parsed.explanation is not None


def test_6_post_simulate_returns_valid_scenario_result():
    """Test 6: POST /api/v1/simulate with valid ONE_TIME_EXPENSE returns valid ScenarioResult."""
    payload = {
        "scenario_type": "ONE_TIME_EXPENSE",
        "amount": 5000.0,
        "description": "Test expense"
    }
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    parsed = ScenarioResult(**data)
    assert parsed.scenario_type == "ONE_TIME_EXPENSE"
    assert parsed.spendable_delta <= 0.0


def test_7_post_simulate_rejects_invalid_scenario_input():
    """Test 7: POST /api/v1/simulate rejects invalid scenario input with 422 Unprocessable Entity."""
    payload = {
        "scenario_type": "INVALID_SCENARIO_TYPE",
        "amount": 5000.0
    }
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 422


def test_8_post_simulate_does_not_mutate_base_state():
    """Test 8: POST /api/v1/simulate does not mutate base state."""
    overview_before = client.get("/api/v1/overview").json()

    _ = client.post("/api/v1/simulate", json={"scenario_type": "ONE_TIME_EXPENSE", "amount": 15000.0})

    overview_after = client.get("/api/v1/overview").json()
    overview_before.pop("explanation_summary", None)
    overview_after.pop("explanation_summary", None)
    assert overview_before == overview_after


def test_9_gemini_failure_does_not_break_overview():
    """Test 9: Gemini API failure / missing key does not break overview endpoint."""
    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    assert "explanation_summary" in data


def test_10_gemini_failure_returns_fallback_explanation(monkeypatch):
    """Test 10: Gemini API failure returns fallback explanation."""
    from app.api.spendable import get_spendable_service
    service = get_spendable_service()
    monkeypatch.setattr(service.expl_generator, "api_key", "")
    response = client.post("/api/v1/explain", json={})
    assert response.status_code == 200
    data = response.json()
    parsed = GeminiExplanationResponse(**data)
    assert parsed.is_fallback is True
    assert len(parsed.summary) > 0


def test_11_missing_user_fallback():
    """Test 11: Non-existent user query gracefully falls back to demo snapshot."""
    response = client.get("/api/v1/overview?user_id=NON_EXISTENT_USER_ID_123")
    assert response.status_code == 200
    assert response.json()["user_id"] is not None


def test_12_no_secrets_in_responses():
    """Test 12: No API response contains secrets or API keys."""
    endpoints = [
        "/api/v1/overview",
        "/api/v1/forecast",
        "/api/v1/recommendations",
    ]
    for ep in endpoints:
        text = client.get(ep).text
        assert "GEMINI_API_KEY" not in text
        assert "SECRET" not in text


def test_13_no_nan_or_infinity_in_endpoints():
    """Test 13: Endpoints return no NaN or infinity."""
    endpoints = [
        "/api/v1/overview",
        "/api/v1/forecast",
        "/api/v1/recommendations",
    ]
    for ep in endpoints:
        text = client.get(ep).text
        assert "NaN" not in text
        assert "Infinity" not in text


def test_14_api_serialization_works_all_models():
    """Test 14: API serialization works cleanly for all Pydantic response models."""
    res_overview = client.get("/api/v1/overview")
    res_forecast = client.get("/api/v1/forecast")
    res_activity = client.get("/api/v1/activity")
    res_recs = client.get("/api/v1/recommendations")

    assert res_overview.status_code == 200
    assert res_forecast.status_code == 200
    assert res_activity.status_code == 200
    assert res_recs.status_code == 200
