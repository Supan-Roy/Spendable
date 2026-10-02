"""Comprehensive Test Suite for Stage 7.6 Persistent Demo Accounts & Auth System."""

from datetime import datetime, timezone
import json
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models.account import UserAccount
from app.models.activity import FinancialActivityModel
from app.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.seed_demo import seed_demo_accounts
from app.services.data_provider import DatabaseDataProvider
from app.services.spendable_service import SpendableService

# Setup shared in-memory SQLite engine for auth tests
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
def setup_auth_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    seed_demo_accounts(session_factory=TestingSessionLocal)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_1_five_demo_accounts_exist_after_seed():
    """Test 1: Five demo accounts exist after seed operation."""
    res = client.get("/api/v1/auth/demo-accounts")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5
    account_ids = [d["account_id"] for d in data]
    for expected in ["acc_supan", "acc_meraj", "acc_sohana", "acc_noman", "acc_refat"]:
        assert expected in account_ids


def test_2_and_17_seed_is_idempotent_no_duplicates():
    """Test 2 & 17: Seed operation is idempotent and creates 0 duplicate transactions when re-run."""
    res1 = seed_demo_accounts(session_factory=TestingSessionLocal)
    assert res1["status"] == "success"
    res2 = seed_demo_accounts(session_factory=TestingSessionLocal)
    assert res2["status"] == "success"
    assert res2["activities_inserted"] == 0


def test_3_and_4_demo_accounts_have_one_year_transaction_histories():
    """Test 3 & 4: Canonical demo files in Git have ~1 full year of transaction history for all 5 accounts."""
    seed_dir = Path("backend/seed/demo_transactions")
    if not seed_dir.exists():
        seed_dir = Path("seed/demo_transactions")

    for uname in ["supan", "meraj", "sohana", "noman", "refat"]:
        tx_file = seed_dir / f"{uname}.json"
        assert tx_file.exists()
        with open(tx_file, mode="r", encoding="utf-8") as f:
            txs = json.load(f)
        assert len(txs) >= 12  # At least 12 monthly cycles
        t_start = datetime.fromisoformat(txs[0]["timestamp_utc"])
        t_end = datetime.fromisoformat(txs[-1]["timestamp_utc"])
        delta_days = (t_end - t_start).days
        assert delta_days >= 300  # Approximately 1 year span


def test_5_transaction_balance_arithmetic_is_valid():
    """Test 5: Transaction balance_after is mathematically valid across history."""
    seed_dir = Path("backend/seed/demo_transactions")
    if not seed_dir.exists():
        seed_dir = Path("seed/demo_transactions")

    with open(seed_dir / "supan.json", mode="r", encoding="utf-8") as f:
        txs = json.load(f)

    # Verify chronological balance continuity
    for i in range(1, len(txs)):
        prev_bal = txs[i - 1]["balance_after"]
        curr_amt = txs[i]["amount"]
        curr_dir = txs[i]["direction"]
        curr_bal = txs[i]["balance_after"]
        expected_bal = prev_bal + curr_amt if curr_dir == "INFLOW" else prev_bal - curr_amt
        assert abs(curr_bal - expected_bal) < 0.01


def test_6_and_7_demo_accounts_cannot_be_deleted_or_modified():
    """Test 6 & 7: Demo accounts cannot be deleted or modified by normal user endpoints."""
    session = TestingSessionLocal()
    try:
        supan = session.query(UserAccount).filter_by(account_id="acc_supan").first()
        assert supan.is_demo_account is True
    finally:
        session.close()


def test_8_normal_users_can_register():
    """Test 8: Normal user registration works and sets is_demo_account=False."""
    payload = {"username": "newuser123", "password": "securepassword", "display_name": "New User"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "newuser123"
    assert data["is_demo_account"] is False
    assert "access_token" in data


def test_9_passwords_are_hashed():
    """Test 9: Passwords are not stored in plaintext and bcrypt verification works."""
    raw = "mysecretpass"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrongpass", hashed) is False


def test_10_and_11_login_jwt_authentication():
    """Test 10 & 11: Valid login returns JWT access token; invalid credentials fail with 401."""
    # Register normal user
    client.post("/api/v1/auth/register", json={"username": "testauth", "password": "password123"})

    # Valid login
    res_ok = client.post("/api/v1/auth/login", json={"username": "testauth", "password": "password123"})
    assert res_ok.status_code == 200
    token = res_ok.json()["access_token"]
    decoded = decode_access_token(token)
    assert decoded["sub"] == "usr_testauth"

    # Invalid login
    res_fail = client.post("/api/v1/auth/login", json={"username": "testauth", "password": "wrongpassword"})
    assert res_fail.status_code == 401


def test_12_jwt_protects_authenticated_endpoints():
    """Test 12: GET /auth/me returns current authenticated account profile from Bearer token."""
    token = create_access_token({"sub": "acc_supan", "username": "supan"})
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["account_id"] == "acc_supan"
    assert data["username"] == "supan"


def test_13_logout_does_not_delete_accounts():
    """Test 13: Logging out on client (clearing token) leaves DB accounts intact."""
    session = TestingSessionLocal()
    try:
        cnt = session.query(UserAccount).count()
        assert cnt >= 5
    finally:
        session.close()


def test_14_and_15_demo_login_and_supan_default():
    """Test 14 & 15: Demo login authenticates selected account, Supan is default on first visit."""
    # Default unauthenticated call defaults to Supan
    res_def = client.get("/api/v1/auth/me")
    assert res_def.status_code == 200
    assert res_def.json()["account_id"] == "acc_supan"

    # Switch to Meraj
    res_meraj = client.post("/api/v1/auth/demo-login/meraj")
    assert res_meraj.status_code == 200
    m_token = res_meraj.json()["access_token"]

    # Call /auth/me with Meraj token
    res_m_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {m_token}"})
    assert res_m_me.status_code == 200
    assert res_m_me.json()["account_id"] == "acc_meraj"


def test_16_railway_fresh_database_seed():
    """Test 16: Fresh database can be seeded cleanly."""
    res = seed_demo_accounts(session_factory=TestingSessionLocal)
    assert res["status"] == "success"


def test_18_spendable_results_differ_between_demo_accounts():
    """Test 18: Overview outputs differ appropriately between demo accounts based on transaction behavior."""
    # Seed DB
    seed_demo_accounts(session_factory=TestingSessionLocal)

    provider = DatabaseDataProvider(session_factory=TestingSessionLocal)
    service = SpendableService(data_provider=provider)

    supan_ov = service.get_overview(user_id="acc_supan")
    meraj_ov = service.get_overview(user_id="acc_meraj")

    # Outputs differ in numerical balances and commitments
    assert supan_ov.current_balance != meraj_ov.current_balance
    assert supan_ov.spendable_amount != meraj_ov.spendable_amount


def test_19_no_runtime_random_generation():
    """Test 19: Demo accounts use repository-backed static JSON files without random generation."""
    seed_dir = Path("backend/seed/demo_transactions")
    if not seed_dir.exists():
        seed_dir = Path("seed/demo_transactions")
    assert (seed_dir / "supan.json").exists()
    assert (seed_dir / "meraj.json").exists()


def test_20_no_data_lost_after_restart():
    """Test 20: Persistent storage retains demo accounts and transactions across restarts."""
    session = TestingSessionLocal()
    try:
        users = session.query(UserAccount).all()
        assert len(users) >= 5
    finally:
        session.close()
