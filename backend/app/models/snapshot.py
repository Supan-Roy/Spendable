import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Integer, DateTime
from sqlalchemy.orm import relationship, foreign
from app.database import Base


class SpendableSnapshot(Base):
    """SQLAlchemy ORM model for storing cached/auditable Spendable calculation outputs."""
    __tablename__ = "spendable_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(64), nullable=False, index=True)
    snapshot_time = Column(String(32), nullable=False, index=True)
    current_balance = Column(Numeric(14, 2), nullable=False)
    spendable_amount = Column(Numeric(14, 2), nullable=False)
    protected_amount = Column(Numeric(14, 2), nullable=False)
    planning_horizon_days = Column(Integer, nullable=False, default=30)
    expected_inflow = Column(Numeric(14, 2), nullable=False, default=0.0)
    expected_outflow = Column(Numeric(14, 2), nullable=False, default=0.0)
    upcoming_commitments = Column(Numeric(14, 2), nullable=False, default=0.0)
    forecasted_minimum_balance = Column(Numeric(14, 2), nullable=False, default=0.0)
    safety_reserve = Column(Numeric(14, 2), nullable=False, default=0.0)
    liquidity_state = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    account = relationship(
        "UserAccount",
        back_populates="snapshots",
        primaryjoin="foreign(SpendableSnapshot.account_id) == UserAccount.account_id",
    )
