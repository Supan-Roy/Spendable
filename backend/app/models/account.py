import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.orm import relationship, foreign
from app.database import Base


class UserAccount(Base):
    """SQLAlchemy ORM model for Spendable user account profiles."""
    __tablename__ = "user_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(64), unique=True, nullable=False, index=True)
    display_name = Column(String(128), nullable=True)
    currency = Column(String(3), nullable=False, default="BDT")
    current_balance = Column(Numeric(14, 2), nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    activities = relationship(
        "FinancialActivityModel",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin="UserAccount.account_id == foreign(FinancialActivityModel.account_id)",
    )
    snapshots = relationship(
        "SpendableSnapshot",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin="UserAccount.account_id == foreign(SpendableSnapshot.account_id)",
    )
