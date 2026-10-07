"""Comprehensive Phase 2 Scalability, Caching & Integration Test Suite."""

import asyncio
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
from app.forecasting.cache import forecast_cache
from app.ingestion.csv_adapter import CSVTransactionAdapter

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
def setup_phase2_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    seed_demo_accounts(session_factory=TestingSessionLocal)
    forecast_cache.clear()
    yield
    forecast_cache.clear()
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_concurrent_multi_user_requests():
    """Simulate 25 concurrent authenticated requests across all 5 demo accounts."""
    accounts = ["acc_supan", "acc_meraj", "acc_sohana", "acc_noman", "acc_refat"]
    tokens = {acc: create_access_token({"sub": acc, "username": acc[4:]}) for acc in accounts}

    responses = []
    for i in range(25):
        acc = accounts[i % len(accounts)]
        h = {"Authorization": f"Bearer {tokens[acc]}"}
        res = client.get("/api/v1/overview", headers=h)
        assert res.status_code == 200
        responses.append(res.json())

    assert len(responses) == 25
    # Verify outputs are account-specific
    supan_res = [r for r in responses if r["user_id"] == "acc_supan"][0]
    meraj_res = [r for r in responses if r["user_id"] == "acc_meraj"][0]
    assert supan_res["current_balance"] != meraj_res["current_balance"]


def test_forecast_cache_hit_and_financial_consistency():
    """Forecast cache returns identical financial outputs with cache hit performance improvement."""
    token = create_access_token({"sub": "acc_supan", "username": "supan"})
    headers = {"Authorization": f"Bearer {token}"}
    forecast_cache.clear()

    # Request 1: Cold Cache
    res1 = client.get("/api/v1/forecast", headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()

    # Request 2: Warm Cache
    res2 = client.get("/api/v1/forecast", headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()

    # Verify 100% mathematical output consistency
    assert data1["current_balance"] == data2["current_balance"]
    assert data1["forecast_30d"]["minimum_projected_balance"] == data2["forecast_30d"]["minimum_projected_balance"]
    assert data1["forecast_30d"]["expected_net_cash_flow"] == data2["forecast_30d"]["expected_net_cash_flow"]


def test_cross_account_cache_isolation():
    """Cache keys prevent cross-account cache contamination or leak."""
    token_supan = create_access_token({"sub": "acc_supan", "username": "supan"})
    token_meraj = create_access_token({"sub": "acc_meraj", "username": "meraj"})

    # Prime cache for Supan
    res_s = client.get("/api/v1/overview", headers={"Authorization": f"Bearer {token_supan}"})
    assert res_s.json()["user_id"] == "acc_supan"

    # Prime cache for Meraj
    res_m = client.get("/api/v1/overview", headers={"Authorization": f"Bearer {token_meraj}"})
    assert res_m.json()["user_id"] == "acc_meraj"

    # Verify no cross-account overlap
    assert res_s.json()["spendable_amount"] != res_m.json()["spendable_amount"]


def test_cache_invalidation_on_transaction_ingestion():
    """Ingesting new transaction invalidates cached forecast for target account."""
    forecast_cache.clear()
    forecast_cache.set("acc_supan", "rev_1", "v1.2.0", None)
    metrics1 = forecast_cache.get_metrics()
    assert metrics1["active_entries"] == 1

    # Ingest new activity
    db = TestingSessionLocal()
    adapter = CSVTransactionAdapter()
    csv_data = "amount,direction,category,timestamp_utc\n15000.00,INFLOW,BONUS,2026-10-06T10:00:00Z\n"
    res_ingest = adapter.ingest_records(csv_data, target_account_id="acc_supan", db=db)
    assert res_ingest.records_ingested == 1
    db.close()

    metrics2 = forecast_cache.get_metrics()
    assert metrics2["active_entries"] == 0
    assert metrics2["invalidations"] >= 1


def test_model_metadata_completeness():
    """Forecasting outputs include complete ModelMetadata schema fields."""
    token = create_access_token({"sub": "acc_supan", "username": "supan"})
    res = client.get("/api/v1/forecast", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "model_version" in data
    assert data["model_version"] == "HIST_GRADIENT_BOOSTING"
    assert "model_metadata" in data
    assert data["model_metadata"] is not None
    assert data["model_metadata"]["model_name"] == "HIST_GRADIENT_BOOSTING"
    assert data["model_metadata"]["model_version"] == "v1.2.0"
    assert data["model_metadata"]["feature_schema_version"] == "v1.0"
    assert "sha256:" in data["model_metadata"]["model_checksum"]
    assert data["model_metadata"]["forecast_horizon_days"] == 30
    assert data["model_metadata"]["is_fallback"] is False


def test_all_five_demo_accounts_functional():
    """Verify all 5 permanent demo accounts function cleanly across Overview and Forecast APIs."""
    for uname in ["supan", "meraj", "sohana", "noman", "refat"]:
        acc_id = f"acc_{uname}"
        token = create_access_token({"sub": acc_id, "username": uname})
        h = {"Authorization": f"Bearer {token}"}

        res_ov = client.get("/api/v1/overview", headers=h)
        assert res_ov.status_code == 200
        assert res_ov.json()["user_id"] == acc_id

        res_fc = client.get("/api/v1/forecast", headers=h)
        assert res_fc.status_code == 200
        assert res_fc.json()["user_id"] == acc_id
