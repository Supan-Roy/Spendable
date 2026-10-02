"""JWT Authentication & Password Security Utilities for Spendable.

Handles password hashing/verification, JWT token creation/decoding, and FastAPI authentication dependencies.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.account import UserAccount

import bcrypt

security_bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hash plaintext password using bcrypt."""
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    if not hashed_password:
        return False
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token containing claims."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_account(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db),
) -> UserAccount:
    """Dependency for resolving authenticated UserAccount from JWT Bearer header.
    
    If no token is provided, falls back to the default Supan demo account.
    """
    if credentials and credentials.credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            account_id = payload.get("sub") or payload.get("account_id")
            if account_id:
                account = db.query(UserAccount).filter(UserAccount.account_id == account_id).first()
                if account:
                    return account
        except Exception:
            pass

    # Default fallback to Supan demo account on first visit / unauthenticated public demo request
    try:
        default_account = db.query(UserAccount).filter(UserAccount.account_id == "acc_supan").first()
        if not default_account:
            default_account = db.query(UserAccount).filter(UserAccount.is_demo_account == True).first()
        if default_account:
            return default_account
    except Exception:
        pass

    # Hard fallback if database not yet seeded or table uninitialized in test fixtures
    return UserAccount(account_id="acc_supan", display_name="Supan Roy (Default Demo)", is_demo_account=True)


def seed_sample_data_for_user(account_id: str, db: Session) -> dict:
    """Generate realistic 1-year historical sample transaction activity for a user account."""
    from app.models.activity import FinancialActivityModel
    from app.domain.enums import TransactionDirection, ActivityType, DataProvenance

    user = db.query(UserAccount).filter(UserAccount.account_id == account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")

    existing_count = db.query(FinancialActivityModel).filter(FinancialActivityModel.account_id == user.account_id).count()
    if existing_count > 0:
        return {
            "status": "success",
            "message": "User already has transaction history",
            "activities_inserted": 0,
            "current_balance": float(user.current_balance),
        }

    bal = 15000.0
    activities = []
    ref_seq = 1000

    for year, month in [
        (2025, 3), (2025, 4), (2025, 5), (2025, 6),
        (2025, 7), (2025, 8), (2025, 9), (2025, 10),
        (2025, 11), (2025, 12), (2026, 1), (2026, 2)
    ]:
        m_dt = datetime(year, month, 1, 10, 0, tzinfo=timezone.utc)

        # 1. Salary Inflow on 1st: ৳85,000
        bal += 85000.0
        ref_seq += 1
        activities.append(FinancialActivityModel(
            account_id=user.account_id,
            amount=85000.0,
            currency="BDT",
            direction=TransactionDirection.INFLOW,
            activity_type=ActivityType.SALARY,
            timestamp_utc=m_dt,
            category="SALARY",
            channel="BANK_TRANSFER",
            counterparty_name="Tech Innovations Ltd",
            reference_id=f"ref_sample_{user.account_id}_{ref_seq}",
            balance_after=round(bal, 2),
            provenance=DataProvenance.SYNTHETIC,
        ))

        # 2. Housing Payment on 5th: ৳22,000
        bal -= 22000.0
        ref_seq += 1
        activities.append(FinancialActivityModel(
            account_id=user.account_id,
            amount=22000.0,
            currency="BDT",
            direction=TransactionDirection.OUTFLOW,
            activity_type=ActivityType.UTILITY_PAYMENT,
            timestamp_utc=m_dt.replace(day=5),
            category="HOUSING",
            channel="BANK_TRANSFER",
            counterparty_name="Green City Apartments",
            reference_id=f"ref_sample_{user.account_id}_{ref_seq}",
            balance_after=round(bal, 2),
            provenance=DataProvenance.SYNTHETIC,
        ))

        # 3. Groceries on 8th: ৳3,500
        bal -= 3500.0
        ref_seq += 1
        activities.append(FinancialActivityModel(
            account_id=user.account_id,
            amount=3500.0,
            currency="BDT",
            direction=TransactionDirection.OUTFLOW,
            activity_type=ActivityType.MERCHANT_PAYMENT,
            timestamp_utc=m_dt.replace(day=8),
            category="FOOD_AND_GROCERIES",
            channel="POS",
            counterparty_name="Unimart Superstore",
            reference_id=f"ref_sample_{user.account_id}_{ref_seq}",
            balance_after=round(bal, 2),
            provenance=DataProvenance.SYNTHETIC,
        ))

        # 4. Utility Bill on 10th: ৳3,200
        bal -= 3200.0
        ref_seq += 1
        activities.append(FinancialActivityModel(
            account_id=user.account_id,
            amount=3200.0,
            currency="BDT",
            direction=TransactionDirection.OUTFLOW,
            activity_type=ActivityType.UTILITY_PAYMENT,
            timestamp_utc=m_dt.replace(day=10),
            category="UTILITIES",
            channel="BILL_PAY",
            counterparty_name="DESCO Electricity",
            reference_id=f"ref_sample_{user.account_id}_{ref_seq}",
            balance_after=round(bal, 2),
            provenance=DataProvenance.SYNTHETIC,
        ))

        # 5. Mobile Recharge on 12th: ৳600
        bal -= 600.0
        ref_seq += 1
        activities.append(FinancialActivityModel(
            account_id=user.account_id,
            amount=600.0,
            currency="BDT",
            direction=TransactionDirection.OUTFLOW,
            activity_type=ActivityType.MOBILE_RECHARGE,
            timestamp_utc=m_dt.replace(day=12),
            category="MOBILE_RECHARGE",
            channel="APP",
            counterparty_name="Grameenphone Ltd",
            reference_id=f"ref_sample_{user.account_id}_{ref_seq}",
            balance_after=round(bal, 2),
            provenance=DataProvenance.SYNTHETIC,
        ))

        # 6. Groceries 2nd round on 22nd: ৳3,800
        bal -= 3800.0
        ref_seq += 1
        activities.append(FinancialActivityModel(
            account_id=user.account_id,
            amount=3800.0,
            currency="BDT",
            direction=TransactionDirection.OUTFLOW,
            activity_type=ActivityType.MERCHANT_PAYMENT,
            timestamp_utc=m_dt.replace(day=22),
            category="FOOD_AND_GROCERIES",
            channel="POS",
            counterparty_name="Agora Supermarket",
            reference_id=f"ref_sample_{user.account_id}_{ref_seq}",
            balance_after=round(bal, 2),
            provenance=DataProvenance.SYNTHETIC,
        ))

        # 7. Dining on 25th: ৳1,800
        bal -= 1800.0
        ref_seq += 1
        activities.append(FinancialActivityModel(
            account_id=user.account_id,
            amount=1800.0,
            currency="BDT",
            direction=TransactionDirection.OUTFLOW,
            activity_type=ActivityType.MERCHANT_PAYMENT,
            timestamp_utc=m_dt.replace(day=25),
            category="FOOD_AND_DINING",
            channel="POS",
            counterparty_name="Star Kabab & Restaurant",
            reference_id=f"ref_sample_{user.account_id}_{ref_seq}",
            balance_after=round(bal, 2),
            provenance=DataProvenance.SYNTHETIC,
        ))

    db.add_all(activities)
    user.current_balance = round(bal, 2)
    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": "Sample transaction data injected successfully.",
        "activities_inserted": len(activities),
        "current_balance": float(user.current_balance),
    }
