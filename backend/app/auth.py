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
