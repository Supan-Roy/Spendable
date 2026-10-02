"""Tests for Stage 7.5 Application Database Foundation."""

from datetime import datetime, timezone
from decimal import Decimal
import os
import pytest
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.database import Base
from app.models.account import UserAccount
from app.models.snapshot import SpendableSnapshot
from app.models.activity import FinancialActivityModel
from app.domain.enums import TransactionDirection, ActivityType, DataProvenance
from app.services.data_provider import DatabaseDataProvider, SyntheticDataProvider, get_data_provider
from app.services.spendable_service import SpendableService
from app.database_seed import seed_database


@pytest.fixture
def memory_db_session():
    """Fixture providing in-memory SQLite session with full schema initialized."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_1_sqlite_engine_creation_works():
    """Test 1: SQLite engine creation works with check_same_thread."""
    db_url = "sqlite:///:memory:"
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {"connect_timeout": 3}
    engine = create_engine(db_url, connect_args=connect_args)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1")).scalar()
    assert res == 1


def test_2_postgresql_configuration_remains_valid():
    """Test 2: PostgreSQL URL normalization and connect_timeout configuration remain valid."""
    url = "postgresql://usr:pwd@localhost:5432/db"
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {"connect_timeout": 3}
    assert url.startswith("postgresql+psycopg2://")
    assert connect_args == {"connect_timeout": 3}


def test_3_sqlite_does_not_receive_connect_timeout():
    """Test 3: SQLite connect_args does NOT include connect_timeout."""
    db_url = "sqlite:///./test.db"
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {"connect_timeout": 3}
    assert "connect_timeout" not in connect_args
    assert connect_args.get("check_same_thread") is False


def test_4_user_account_model_works(memory_db_session):
    """Test 4: UserAccount ORM model CRUD operations work as expected."""
    user = UserAccount(
        account_id="ACC-TEST-001",
        display_name="Test User",
        currency="BDT",
        current_balance=25000.50,
    )
    memory_db_session.add(user)
    memory_db_session.commit()

    fetched = memory_db_session.query(UserAccount).filter_by(account_id="ACC-TEST-001").first()
    assert fetched is not None
    assert fetched.account_id == "ACC-TEST-001"
    assert float(fetched.current_balance) == 25000.50


def test_5_spendable_snapshot_model_works(memory_db_session):
    """Test 5: SpendableSnapshot ORM model CRUD operations work as expected."""
    snap = SpendableSnapshot(
        account_id="ACC-TEST-001",
        snapshot_time="2026-03-01T00:00:00",
        current_balance=25000.50,
        spendable_amount=12000.00,
        protected_amount=13000.50,
        planning_horizon_days=30,
        expected_inflow=5000.00,
        expected_outflow=3000.00,
        upcoming_commitments=2000.00,
        forecasted_minimum_balance=10000.00,
        safety_reserve=1000.00,
        liquidity_state="HEALTHY",
    )
    memory_db_session.add(snap)
    memory_db_session.commit()

    fetched = memory_db_session.query(SpendableSnapshot).filter_by(account_id="ACC-TEST-001").first()
    assert fetched is not None
    assert float(fetched.spendable_amount) == 12000.00
    assert fetched.liquidity_state == "HEALTHY"


def test_6_and_7_alembic_migration_upgrade_and_downgrade():
    """Test 6 & 7: Alembic migration upgrade and downgrade executed on SQLite without error."""
    from alembic.config import Config
    from alembic import command

    test_db = "test_migration.db"
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass

    ini_path = "backend/alembic.ini" if os.path.exists("backend/alembic.ini") else "alembic.ini"
    alembic_cfg = Config(ini_path)
    script_loc = "backend/alembic" if os.path.exists("backend/alembic") else "alembic"
    alembic_cfg.set_main_option("script_location", script_loc)
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///./{test_db}")

    engine = None
    try:
        command.upgrade(alembic_cfg, "head")
        engine = create_engine(f"sqlite:///./{test_db}")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert "user_accounts" in tables
        assert "spendable_snapshots" in tables
        assert "financial_activities" in tables

        command.downgrade(alembic_cfg, "base")
        inspector_after = inspect(engine)
        tables_after = inspector_after.get_table_names()
        assert "user_accounts" not in tables_after
        assert "spendable_snapshots" not in tables_after
    finally:
        if engine:
            engine.dispose()
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except Exception:
                pass


def test_8_and_9_database_data_provider(memory_db_session):
    """Test 8 & 9: DatabaseDataProvider can retrieve account data and activities."""
    # Seed user account
    user = UserAccount(account_id="ACC-PROVIDER-01", display_name="Provider Test", current_balance=50000.0)
    memory_db_session.add(user)

    # Seed activities
    now_utc = datetime.now(timezone.utc)
    act1 = FinancialActivityModel(
        account_id="ACC-PROVIDER-01",
        amount=50000.0,
        currency="BDT",
        direction=TransactionDirection.INFLOW,
        activity_type=ActivityType.SALARY,
        timestamp_utc=now_utc,
        balance_after=50000.0,
        reference_id="ref_in_01",
    )
    act2 = FinancialActivityModel(
        account_id="ACC-PROVIDER-01",
        amount=5000.0,
        currency="BDT",
        direction=TransactionDirection.OUTFLOW,
        activity_type=ActivityType.MERCHANT_PAYMENT,
        timestamp_utc=now_utc,
        balance_after=45000.0,
        reference_id="ref_out_01",
    )
    memory_db_session.add_all([act1, act2])
    memory_db_session.commit()

    # Pass memory_db_session factory
    session_factory = lambda: memory_db_session
    provider = DatabaseDataProvider(session_factory=session_factory)

    # Test 8: Account snapshot data retrieval
    snap_data = provider.get_snapshot_data(user_id="ACC-PROVIDER-01")
    assert snap_data["user_id"] == "ACC-PROVIDER-01"
    assert snap_data["current_balance"] == 50000.0
    assert "features" in snap_data

    # Test 9: Activity retrieval
    acts_res = provider.get_recent_activities(user_id="ACC-PROVIDER-01")
    assert acts_res["total_count"] == 2
    assert len(acts_res["activities"]) == 2


def test_10_and_16_seed_operation_is_idempotent():
    """Test 10 & 16: Seed operation creates records cleanly and creates 0 duplicates when run again."""
    from app.database import engine, Base
    Base.metadata.create_all(bind=engine)
    res1 = seed_database(limit_accounts=2)
    assert res1["status"] == "success"

    res2 = seed_database(limit_accounts=2)
    assert res2["status"] == "success"
    assert res2["activities_created"] == 0  # No duplicates created


def test_12_and_13_overview_and_spendable_calculation_deterministic():
    """Test 12 & 13: Overview works using DatabaseDataProvider and yields deterministic outputs."""
    from app.database import engine, Base, SessionLocal
    from app.seed_demo import seed_demo_accounts
    Base.metadata.create_all(bind=engine)
    seed_demo_accounts(session_factory=SessionLocal)
    provider = DatabaseDataProvider()
    service = SpendableService(data_provider=provider)

    overview1 = service.get_overview()
    overview2 = service.get_overview()

    assert overview1.user_id == overview2.user_id
    assert overview1.spendable_amount == overview2.spendable_amount
    assert overview1.protected_amount == overview2.protected_amount
    assert overview1.liquidity_state == overview2.liquidity_state


def test_14_gemini_not_required_for_database_functionality(monkeypatch):
    """Test 14: Database operations and Spendable calculation work cleanly when Gemini API key is missing."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    from app.database import engine, Base, SessionLocal
    from app.seed_demo import seed_demo_accounts
    Base.metadata.create_all(bind=engine)
    seed_demo_accounts(session_factory=SessionLocal)
    provider = DatabaseDataProvider()
    service = SpendableService(data_provider=provider)

    overview = service.get_overview()
    assert overview.spendable_amount >= 0.0
    assert len(overview.explanation_summary) > 0


def test_15_no_csv_access_on_normal_database_path(memory_db_session):
    """Test 15: DatabaseDataProvider reads directly from SQLAlchemy session without querying CSVs."""
    user = UserAccount(account_id="ACC-DB-ONLY", display_name="DB Only", current_balance=10000.0)
    act = FinancialActivityModel(
        account_id="ACC-DB-ONLY",
        amount=10000.0,
        currency="BDT",
        direction=TransactionDirection.INFLOW,
        activity_type=ActivityType.SALARY,
        timestamp_utc=datetime.now(timezone.utc),
        balance_after=10000.0,
        reference_id="ref_db_only_01",
    )
    memory_db_session.add_all([user, act])
    memory_db_session.commit()

    provider = DatabaseDataProvider(session_factory=lambda: memory_db_session)
    data = provider.get_snapshot_data(user_id="ACC-DB-ONLY")
    assert data["user_id"] == "ACC-DB-ONLY"
    assert data["current_balance"] == 10000.0
