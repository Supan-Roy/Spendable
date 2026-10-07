from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.activity import FinancialActivityModel
from app.schemas.activity import FinancialActivityCreate, FinancialActivityResponse
from app.domain.enums import TransactionDirection, ActivityType

from app.auth import get_current_account
from app.models.account import UserAccount
from app.audit import audit_logger

router = APIRouter(prefix="/activities", tags=["Financial Activities"])


@router.post("", response_model=FinancialActivityResponse, status_code=status.HTTP_201_CREATED)
def record_activity(
    payload: FinancialActivityCreate,
    request: Request,
    current_account: UserAccount = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    """Ingest and persist a verified observed financial activity event."""
    has_auth_header = bool(request.headers.get("Authorization"))
    if has_auth_header and payload.account_id and payload.account_id != current_account.account_id:
        audit_logger.log_event(
            event_type="CROSS_ACCOUNT_RECORD_DENIED",
            account_id=current_account.account_id,
            endpoint="/activities",
            detail=f"Attempted to record activity for target '{payload.account_id}'",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot record financial activity for another account.",
        )
    
    target_account = current_account.account_id if (has_auth_header or not payload.account_id) else payload.account_id
    try:
        activity_obj = FinancialActivityModel(
            account_id=target_account,
            amount=payload.amount,
            currency=payload.currency,
            direction=payload.direction.value if hasattr(payload.direction, "value") else str(payload.direction),
            activity_type=payload.activity_type.value if hasattr(payload.activity_type, "value") else str(payload.activity_type),
            timestamp_utc=payload.timestamp_utc,
            category=payload.category,
            channel=payload.channel,
            counterparty_name=payload.counterparty_name,
            reference_id=payload.reference_id,
            balance_after=payload.balance_after,
            provenance=payload.provenance.value if hasattr(payload.provenance, "value") else str(payload.provenance)
        )
        db.add(activity_obj)
        db.commit()
        db.refresh(activity_obj)
        audit_logger.log_event("FINANCIAL_ACTIVITY_RECORDED", account_id=target_account, endpoint="/activities")
        return activity_obj
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record financial activity: {str(e)}"
        )


@router.get("", response_model=List[FinancialActivityResponse])
def list_activities(
    request: Request,
    account_id: Optional[str] = Query(None, description="Filter by account identifier"),
    direction: Optional[TransactionDirection] = Query(None, description="Filter by INFLOW or OUTFLOW"),
    activity_type: Optional[ActivityType] = Query(None, description="Filter by activity classification"),
    limit: int = Query(50, ge=1, le=500, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    current_account: UserAccount = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    """Retrieve observed financial activities ordered by timestamp descending."""
    has_auth_header = bool(request.headers.get("Authorization"))
    if has_auth_header and account_id and account_id != current_account.account_id:
        audit_logger.log_event(
            event_type="CROSS_ACCOUNT_ACCESS_DENIED",
            account_id=current_account.account_id,
            endpoint="/activities",
            detail=f"Attempted list activities for target '{account_id}'",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cross-account activity retrieval denied.",
        )

    target_account = current_account.account_id if has_auth_header else account_id
    try:
        query = db.query(FinancialActivityModel)
        if target_account:
            query = query.filter(FinancialActivityModel.account_id == target_account)
        if direction:
            dir_val = direction.value if hasattr(direction, "value") else str(direction)
            query = query.filter(FinancialActivityModel.direction == dir_val)
        if activity_type:
            type_val = activity_type.value if hasattr(activity_type, "value") else str(activity_type)
            query = query.filter(FinancialActivityModel.activity_type == type_val)

        activities = (
            query.order_by(FinancialActivityModel.timestamp_utc.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        audit_logger.log_event("FINANCIAL_ACTIVITIES_LISTED", account_id=target_account, endpoint="/activities")
        return activities
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query financial activities: {str(e)}"
        )
