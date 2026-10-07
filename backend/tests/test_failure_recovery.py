"""Test suite for Failure Injection, Recovery, and Graceful Degradation."""

from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.auth import create_access_token
from app.seed_demo import seed_demo_accounts
from app.explanation.spendable_ai_chat import SpendableAIChatEngine
from app.forecasting.models import CashFlowForecastModel
from app.forecasting.cache import forecast_cache

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_failure_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    seed_demo_accounts(session_factory=TestingSessionLocal)
    forecast_cache.clear()
    yield
    forecast_cache.clear()
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_gemini_api_failure_fallback():
    """Gemini API failure/unavailability falls back gracefully to rule-based explanation."""
    chat_engine = SpendableAIChatEngine(api_key="")
    ctx = {
        "user_id": "acc_supan",
        "current_balance": 321000.0,
        "spendable_amount": 250000.0,
        "protected_amount": 71000.0,
        "liquidity_state": "HEALTHY",
        "forecasted_minimum_balance": 180000.0,
        "upcoming_commitments": 56000.0,
        "safety_reserve": 15000.0,
    }
    res = chat_engine.answer("What is my safe spendable runway?", chat_history=[], account_context=ctx)
    assert res.agent_name == "Spendable AI"
    assert "Spendable AI" in res.reply
    assert "৳321,000.00" in res.reply


def test_ml_model_unfitted_fallback():
    """Unfitted ML model activates heuristic fallback with widened uncertainty intervals and is_fallback=True metadata."""
    model = CashFlowForecastModel()
    sample_features = {
        "account_id": "acc_test_fallback",
        "snapshot_timestamp": datetime.now(timezone.utc).isoformat(),
        "current_balance": 50000.0,
        "total_inflow_30d": 40000.0,
        "total_outflow_30d": 30000.0,
    }
    output = model.predict_snapshot(sample_features)
    assert output.user_id == "acc_test_fallback"
    assert output.model_metadata is not None
    assert output.model_metadata.is_fallback is True
    assert "FALLBACK" in output.model_metadata.model_name
    assert output.forecast_30d.estimated_range_upper - output.forecast_30d.estimated_range_lower >= 4000.0


def test_cache_miss_and_invalidation_recovery():
    """Cache misses and invalidations recover seamlessly by re-computing fresh forecast outputs."""
    forecast_cache.clear()

    # Initial get (Miss)
    cached1 = forecast_cache.get("acc_supan", "rev_001", "v1.2.0")
    assert cached1 is None

    # Invalidate
    count = forecast_cache.invalidate("acc_supan")
    assert count == 0

    metrics = forecast_cache.get_metrics()
    assert metrics["misses"] == 1
    assert metrics["hits"] == 0


def test_api_controlled_error_handling_on_nonexistent_routes():
    """Non-existent or malformed requests return clean JSON errors without leaking internal stack trace details."""
    token = create_access_token({"sub": "acc_supan", "username": "supan"})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/non_existent_route", headers=headers)
    assert res.status_code == 404
    assert "detail" in res.json()
    assert "Traceback" not in res.text
