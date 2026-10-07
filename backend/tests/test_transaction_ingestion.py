"""Test suite for Transaction Ingestion Architecture & CSV Adapter."""

import io
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models.account import UserAccount
from app.models.activity import FinancialActivityModel
from app.seed_demo import seed_demo_accounts
from app.ingestion.csv_adapter import CSVTransactionAdapter
from app.ingestion.schema import IngestionResult, CanonicalTransaction

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


@pytest.fixture(autouse=True)
def setup_ingestion_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    seed_demo_accounts(session_factory=TestingSessionLocal)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_csv_ingestion_success():
    """Valid CSV file correctly normalizes and ingests transaction records."""
    db = TestingSessionLocal()
    adapter = CSVTransactionAdapter()

    csv_data = """amount,direction,category,timestamp_utc,counterparty_name,reference_id
5000.00,INFLOW,SALARY,2026-10-01T10:00:00Z,Tech Corp,ref_test_001
1200.50,OUTFLOW,UTILITIES,2026-10-02T14:30:00Z,Electric Co,ref_test_002
"""
    res = adapter.ingest_records(csv_data, target_account_id="acc_supan", db=db)
    assert res.records_ingested == 2
    assert res.duplicates_skipped == 0
    assert len(res.errors) == 0

    # Verify persisted in database
    acts = db.query(FinancialActivityModel).filter_by(account_id="acc_supan", reference_id="ref_test_001").all()
    assert len(acts) == 1
    assert acts[0].amount == 5000.00
    assert acts[0].direction == "INFLOW"
    db.close()


def test_csv_ingestion_idempotency_deduplication():
    """Duplicate reference IDs are skipped automatically without double-counting."""
    db = TestingSessionLocal()
    adapter = CSVTransactionAdapter()

    csv_data = """amount,direction,category,timestamp_utc,counterparty_name,reference_id
3000.00,INFLOW,FREELANCE,2026-10-05T10:00:00Z,Client A,ref_dup_999
"""
    # First ingestion
    res1 = adapter.ingest_records(csv_data, target_account_id="acc_supan", db=db)
    assert res1.records_ingested == 1

    # Second ingestion with identical duplicate reference ID
    res2 = adapter.ingest_records(csv_data, target_account_id="acc_supan", db=db)
    assert res2.records_ingested == 0
    assert res2.duplicates_skipped == 1
    db.close()


def test_csv_ingestion_malformed_records_rejected():
    """Malformed records (negative amounts, invalid direction) are flagged with detailed errors."""
    db = TestingSessionLocal()
    adapter = CSVTransactionAdapter()

    csv_data = """amount,direction,category,timestamp_utc
-500.00,OUTFLOW,GROCERIES,2026-10-01T10:00:00Z
1500.00,INVALID_DIR,GROCERIES,2026-10-01T10:00:00Z
2000.00,INFLOW,SALARY,2026-10-01T10:00:00Z
"""
    res = adapter.ingest_records(csv_data, target_account_id="acc_supan", db=db)
    assert res.records_ingested == 1
    assert res.invalid_records == 2
    assert len(res.errors) == 2
    db.close()


def test_csv_ingestion_nonexistent_account():
    """Ingestion fails gracefully if target account does not exist."""
    db = TestingSessionLocal()
    adapter = CSVTransactionAdapter()

    csv_data = "amount,direction\n1000.00,INFLOW"
    res = adapter.ingest_records(csv_data, target_account_id="nonexistent_account_123", db=db)
    assert res.records_ingested == 0
    assert "does not exist" in res.errors[0]
    db.close()
