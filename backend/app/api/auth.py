"""Authentication & Account Management API Endpoints for Spendable."""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import UserAccount
from app.auth import hash_password, verify_password, create_access_token, get_current_account

router = APIRouter(prefix="/auth", tags=["Authentication & User Accounts"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    account_id: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    is_demo_account: bool = False


class UserAccountResponse(BaseModel):
    account_id: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    currency: str = "BDT"
    current_balance: float
    is_demo_account: bool = False


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new normal user account."""
    clean_username = payload.username.strip().lower()
    if not clean_username or not payload.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    existing = db.query(UserAccount).filter(UserAccount.username == clean_username).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Username '{clean_username}' is already taken")

    # Generate unique account ID
    acc_id = f"usr_{clean_username}"
    disp_name = payload.display_name or clean_username.title()

    user_obj = UserAccount(
        account_id=acc_id,
        username=clean_username,
        password_hash=hash_password(payload.password),
        display_name=disp_name,
        currency="BDT",
        current_balance=0.0,
        is_demo_account=False,
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    token = create_access_token({"sub": user_obj.account_id, "username": user_obj.username})

    return AuthTokenResponse(
        access_token=token,
        account_id=user_obj.account_id,
        username=user_obj.username,
        display_name=user_obj.display_name,
        is_demo_account=False,
    )


@router.post("/login", response_model=AuthTokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with username and password."""
    clean_username = payload.username.strip().lower()
    user = db.query(UserAccount).filter(UserAccount.username == clean_username).first()

    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.account_id, "username": user.username})

    return AuthTokenResponse(
        access_token=token,
        account_id=user.account_id,
        username=user.username,
        display_name=user.display_name,
        is_demo_account=user.is_demo_account,
    )


@router.post("/demo-login/{account_identifier}", response_model=AuthTokenResponse)
def demo_login(account_identifier: str, db: Session = Depends(get_db)):
    """Authenticate cleanly as one of the 5 permanent hackathon demo accounts."""
    ident = account_identifier.strip().lower()

    # Match by username (e.g. supan) or account_id (e.g. acc_supan)
    user = (
        db.query(UserAccount)
        .filter(
            (UserAccount.username == ident)
            | (UserAccount.account_id == ident)
            | (UserAccount.account_id == f"acc_{ident}")
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Demo account '{account_identifier}' not found. Please run seed script.",
        )

    token = create_access_token({"sub": user.account_id, "username": user.username})

    return AuthTokenResponse(
        access_token=token,
        account_id=user.account_id,
        username=user.username,
        display_name=user.display_name,
        is_demo_account=user.is_demo_account,
    )


@router.get("/demo-accounts", response_model=List[UserAccountResponse])
def get_demo_accounts(db: Session = Depends(get_db)):
    """Retrieve list of permanent seeded demo accounts."""
    demos = (
        db.query(UserAccount)
        .filter(UserAccount.is_demo_account == True)
        .order_by(UserAccount.account_id.asc())
        .all()
    )
    return [
        UserAccountResponse(
            account_id=d.account_id,
            username=d.username,
            display_name=d.display_name,
            currency=d.currency,
            current_balance=float(d.current_balance),
            is_demo_account=True,
        )
        for d in demos
    ]


@router.get("/me", response_model=UserAccountResponse)
def get_current_user_profile(account: UserAccount = Depends(get_current_account)):
    """Return authenticated account metadata."""
    return UserAccountResponse(
        account_id=account.account_id,
        username=account.username,
        display_name=account.display_name,
        currency=account.currency,
        current_balance=float(account.current_balance),
        is_demo_account=account.is_demo_account,
    )


@router.post("/inject-sample-data")
def inject_sample_data(
    account: UserAccount = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    """Programmatically generate 1-year realistic sample transaction history for the authenticated user."""
    from app.auth import seed_sample_data_for_user
    res = seed_sample_data_for_user(account.account_id, db)
    return res


@router.delete("/delete-account", status_code=status.HTTP_200_OK)
def delete_user_account(
    account: UserAccount = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    """Permanently delete user-created account and all associated database records with no trace."""
    if account.is_demo_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permanent demo accounts cannot be deleted.",
        )

    from app.models.activity import FinancialActivityModel
    from app.models.snapshot import SpendableSnapshot

    acc_id = account.account_id
    uname = account.username

    # 1. Permanently delete all financial activity records
    db.query(FinancialActivityModel).filter(FinancialActivityModel.account_id == acc_id).delete(synchronize_session=False)

    # 2. Permanently delete all spendable snapshot records
    db.query(SpendableSnapshot).filter(SpendableSnapshot.account_id == acc_id).delete(synchronize_session=False)

    # 3. Permanently delete the user account profile record itself
    db.delete(account)
    db.commit()

    return {
        "status": "success",
        "detail": f"Account '{uname}' and all associated database entries have been permanently removed with no trace.",
    }

