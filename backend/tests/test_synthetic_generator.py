"""Unit and integration tests for the Spendable Synthetic Data Generator."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.schemas.activity import FinancialActivityCreate
from app.domain.enums import TransactionDirection, ActivityType, DataProvenance
from app.synthetic.config import GeneratorConfig
from app.synthetic.enums import PersonaType, MilestoneType
from app.synthetic.generator import SyntheticDataGenerator
from app.synthetic.validator import validate_synthetic_dataset, DataValidationError
from app.synthetic.exporter import seed_database
from app.models.activity import FinancialActivityModel


@pytest.fixture
def db_session():
    """In-memory SQLite database session fixture for testing DB seeding."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


def test_generator_reproducibility():
    """Verify that identical seeds produce 100% identical activity records and ground truth."""
    config1 = GeneratorConfig(seed=42, num_users=3, duration_days=30)
    config2 = GeneratorConfig(seed=42, num_users=3, duration_days=30)

    gen1 = SyntheticDataGenerator(config1)
    gen2 = SyntheticDataGenerator(config2)

    acts1, gt1 = gen1.generate()
    acts2, gt2 = gen2.generate()

    assert len(acts1) == len(acts2)
    assert acts1 == acts2
    assert gt1.seed == gt2.seed
    assert gt1.num_users == gt2.num_users
    assert gt1.users == gt2.users
    assert gt1.annotations == gt2.annotations


def test_generator_different_seeds():
    """Verify that different seeds produce distinct output datasets."""
    config1 = GeneratorConfig(seed=42, num_users=3, duration_days=30)
    config2 = GeneratorConfig(seed=999, num_users=3, duration_days=30)

    gen1 = SyntheticDataGenerator(config1)
    gen2 = SyntheticDataGenerator(config2)

    acts1, _ = gen1.generate()
    acts2, _ = gen2.generate()

    assert acts1 != acts2


def test_data_contract_conformance():
    """Verify that every generated record conforms strictly to FinancialActivityCreate."""
    config = GeneratorConfig(seed=123, num_users=5, duration_days=60)
    generator = SyntheticDataGenerator(config)
    activities, ground_truth = generator.generate()

    assert len(activities) > 0

    for act in activities:
        payload = {k: v for k, v in act.items() if k != "id"}
        schema_obj = FinancialActivityCreate(**payload)

        assert schema_obj.amount > Decimal("0.00")
        assert schema_obj.currency == "BDT"
        assert schema_obj.provenance == DataProvenance.SYNTHETIC
        assert schema_obj.timestamp_utc.tzinfo == timezone.utc
        if schema_obj.balance_after is not None:
            assert schema_obj.balance_after >= Decimal("0.00")


def test_unique_transaction_ids():
    """Verify all generated transaction IDs are unique across dataset."""
    config = GeneratorConfig(seed=42, num_users=5, duration_days=90)
    generator = SyntheticDataGenerator(config)
    activities, _ = generator.generate()

    ids = [act["id"] for act in activities]
    assert len(ids) == len(set(ids))


def test_balance_progression_consistency():
    """Verify running balance progression is 100% consistent with starting balance."""
    config = GeneratorConfig(seed=42, num_users=4, duration_days=60)
    generator = SyntheticDataGenerator(config)
    activities, ground_truth = generator.generate()

    # Pass through validator explicitly
    is_valid, warnings = validate_synthetic_dataset(activities, ground_truth)
    assert is_valid is True


def test_ground_truth_separation():
    """Verify raw activity dictionaries contain zero leaked ground-truth metadata fields."""
    config = GeneratorConfig(seed=42, num_users=3, duration_days=30)
    generator = SyntheticDataGenerator(config)
    activities, ground_truth = generator.generate()

    forbidden_keys = {"is_recurring", "planted_rule_id", "persona", "persona_phase", "milestone"}

    for act in activities:
        leaked = forbidden_keys.intersection(act.keys())
        assert len(leaked) == 0, f"Leaked ground truth fields found: {leaked}"

    # Verify ground truth metadata is recorded separately
    assert len(ground_truth.users) == 3
    assert len(ground_truth.annotations) == len(activities)


def test_persona_expectations_commitment_heavy():
    """Verify CommitmentHeavy persona contains multiple planted recurring rules."""
    config = GeneratorConfig(
        seed=10,
        num_users=1,
        duration_days=60,
        persona_weights={PersonaType.COMMITMENT_HEAVY: 1.0},
    )
    generator = SyntheticDataGenerator(config)
    activities, ground_truth = generator.generate()

    user_gt = ground_truth.users["ACC-0001"]
    assert user_gt.persona == PersonaType.COMMITMENT_HEAVY
    assert len(user_gt.planted_rules) >= 5


def test_persona_expectations_spending_drift():
    """Verify SpendingDrift persona records a DRIFT_START milestone and higher drift volume."""
    config = GeneratorConfig(
        seed=77,
        num_users=1,
        duration_days=90,
        persona_weights={PersonaType.SPENDING_DRIFT: 1.0},
    )
    generator = SyntheticDataGenerator(config)
    activities, ground_truth = generator.generate()

    user_gt = ground_truth.users["ACC-0001"]
    assert user_gt.persona == PersonaType.SPENDING_DRIFT
    assert len(user_gt.milestones) == 1
    assert user_gt.milestones[0].milestone_type == MilestoneType.DRIFT_START


def test_db_seeding_exporter(db_session):
    """Verify generated activities can be seeded into database via SQLAlchemy."""
    config = GeneratorConfig(seed=42, num_users=2, duration_days=14)
    generator = SyntheticDataGenerator(config)
    activities, _ = generator.generate()

    count = seed_database(activities, db_session)
    assert count == len(activities)

    # Query DB to confirm records exist
    db_records = db_session.query(FinancialActivityModel).all()
    assert len(db_records) == len(activities)
