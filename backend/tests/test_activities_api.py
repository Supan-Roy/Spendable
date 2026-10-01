from datetime import datetime, timezone
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models.activity import FinancialActivityModel  # Ensures model is registered with Base.metadata

# Setup shared in-memory SQLite engine using StaticPool for testing
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override database dependency BEFORE instantiating TestClient
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_record_financial_activity_api():
    """Test POST /api/v1/activities endpoint records an activity successfully."""
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "account_id": "usr_test_1001",
        "amount": "1500.75",
        "currency": "BDT",
        "direction": "OUTFLOW",
        "activity_type": "MERCHANT_PAYMENT",
        "timestamp_utc": now_iso,
        "category": "GROCERIES",
        "counterparty_name": "Superstore Market",
        "provenance": "SYNTHETIC"
    }

    response = client.post("/api/v1/activities", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["account_id"] == "usr_test_1001"
    assert data["amount"] == "1500.75"
    assert data["currency"] == "BDT"
    assert data["direction"] == "OUTFLOW"
    assert data["activity_type"] == "MERCHANT_PAYMENT"
    assert "id" in data
    assert "created_at" in data


def test_list_financial_activities_api():
    """Test GET /api/v1/activities endpoint retrieves and filters activities."""
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Ingest 2 activities for different accounts
    act1 = {
        "account_id": "usr_alpha",
        "amount": "5000.00",
        "currency": "BDT",
        "direction": "INFLOW",
        "activity_type": "SALARY",
        "timestamp_utc": now_iso
    }
    act2 = {
        "account_id": "usr_beta",
        "amount": "200.00",
        "currency": "BDT",
        "direction": "OUTFLOW",
        "activity_type": "MOBILE_RECHARGE",
        "timestamp_utc": now_iso
    }
    r1 = client.post("/api/v1/activities", json=act1)
    assert r1.status_code == 201, r1.text
    r2 = client.post("/api/v1/activities", json=act2)
    assert r2.status_code == 201, r2.text

    # Fetch all
    res_all = client.get("/api/v1/activities")
    assert res_all.status_code == 200, res_all.text
    assert len(res_all.json()) == 2

    # Filter by account_id
    res_alpha = client.get("/api/v1/activities?account_id=usr_alpha")
    assert res_alpha.status_code == 200, res_alpha.text
    assert len(res_alpha.json()) == 1
    assert res_alpha.json()[0]["account_id"] == "usr_alpha"
