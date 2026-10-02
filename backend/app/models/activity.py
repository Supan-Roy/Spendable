import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship, foreign
from app.database import Base
from app.domain.enums import TransactionDirection, ActivityType, DataProvenance


class FinancialActivityModel(Base):
    """SQLAlchemy ORM model for persisting observed financial activities."""
    __tablename__ = "financial_activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(64), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="BDT")
    direction = Column(SQLEnum(TransactionDirection, native_enum=False, length=32), nullable=False)
    activity_type = Column(SQLEnum(ActivityType, native_enum=False, length=64), nullable=False)
    timestamp_utc = Column(DateTime(timezone=True), nullable=False, index=True)

    category = Column(String(64), nullable=True)
    channel = Column(String(32), nullable=True)
    counterparty_name = Column(String(128), nullable=True)
    reference_id = Column(String(128), nullable=True)
    balance_after = Column(Numeric(14, 2), nullable=True)
    provenance = Column(SQLEnum(DataProvenance, native_enum=False, length=32), nullable=False, default=DataProvenance.SYNTHETIC)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    account = relationship(
        "UserAccount",
        back_populates="activities",
        primaryjoin="foreign(FinancialActivityModel.account_id) == UserAccount.account_id",
    )
