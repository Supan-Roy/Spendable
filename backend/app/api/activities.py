from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.activity import FinancialActivityModel
from app.schemas.activity import FinancialActivityCreate, FinancialActivityResponse
from app.domain.enums import TransactionDirection, ActivityType

router = APIRouter(prefix="/activities", tags=["Financial Activities"])


@router.post("", response_model=FinancialActivityResponse, status_code=status.HTTP_201_CREATED)
def record_activity(
    payload: FinancialActivityCreate,
    db: Session = Depends(get_db)
):
    """Ingest and persist a verified observed financial activity event."""
    try:
        activity_obj = FinancialActivityModel(
            account_id=payload.account_id,
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
        return activity_obj
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record financial activity: {str(e)}"
        )


@router.get("", response_model=List[FinancialActivityResponse])
def list_activities(
    account_id: Optional[str] = Query(None, description="Filter by account identifier"),
    direction: Optional[TransactionDirection] = Query(None, description="Filter by INFLOW or OUTFLOW"),
    activity_type: Optional[ActivityType] = Query(None, description="Filter by activity classification"),
    limit: int = Query(50, ge=1, le=500, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    db: Session = Depends(get_db)
):
    """Retrieve observed financial activities ordered by timestamp descending."""
    try:
        query = db.query(FinancialActivityModel)
        if account_id:
            query = query.filter(FinancialActivityModel.account_id == account_id)
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
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query financial activities: {str(e)}"
        )
