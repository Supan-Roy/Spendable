"""FastAPI Product Integration API router for Spendable.

Exposes product-oriented endpoints:
- GET /api/v1/overview
- GET /api/v1/forecast
- GET /api/v1/activity
- GET /api/v1/recommendations
- POST /api/v1/simulate
- POST /api/v1/explain

Route handlers are thin orchestration callers delegating business logic to SpendableService.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.services.spendable_service import SpendableService
from app.schemas.spendable import (
    SpendableOverviewResponse,
    SpendableForecastResponse,
    SpendableActivityListResponse,
    SpendableRecommendationsResponse,
    ExplainRequest,
)
from app.scenario.schema import ScenarioInput, ScenarioResult
from app.explanation.schema import GeminiExplanationResponse

router = APIRouter(tags=["Spendable Product Intelligence"])

# Singleton service instance dependency
_spendable_service_instance: Optional[SpendableService] = None


def get_spendable_service() -> SpendableService:
    """Dependency provider for SpendableService."""
    global _spendable_service_instance
    if _spendable_service_instance is None:
        _spendable_service_instance = SpendableService()
    return _spendable_service_instance


from app.auth import get_current_account
from app.models.account import UserAccount


@router.get("/overview", response_model=SpendableOverviewResponse)
@router.get("/spendable/overview", response_model=SpendableOverviewResponse)
def get_overview(
    user_id: Optional[str] = Query(None, description="Account identifier"),
    snapshot_time: Optional[str] = Query(None, description="Snapshot timestamp T"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Return main Spendable dashboard overview state."""
    try:
        target_uid = user_id or current_account.account_id
        return service.get_overview(user_id=target_uid, snapshot_time=snapshot_time)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate spendable overview: {str(e)}"
        )


@router.get("/forecast", response_model=SpendableForecastResponse)
@router.get("/spendable/forecast", response_model=SpendableForecastResponse)
def get_forecast(
    user_id: Optional[str] = Query(None, description="Account identifier"),
    snapshot_time: Optional[str] = Query(None, description="Snapshot timestamp T"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Return multi-horizon forecasts and 30-day daily projected balance trajectory."""
    try:
        target_uid = user_id or current_account.account_id
        return service.get_forecast(user_id=target_uid, snapshot_time=snapshot_time)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate cash-flow forecast: {str(e)}"
        )


@router.get("/activity", response_model=SpendableActivityListResponse)
@router.get("/spendable/activity", response_model=SpendableActivityListResponse)
def get_activity(
    user_id: Optional[str] = Query(None, description="Account identifier"),
    limit: int = Query(50, ge=1, le=500, description="Pagination page limit"),
    offset: int = Query(0, ge=0, description="Pagination page offset"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Return recent observed transaction activity records with pagination."""
    try:
        target_uid = user_id or current_account.account_id
        return service.get_activities(user_id=target_uid, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve activity records: {str(e)}"
        )


@router.get("/recommendations", response_model=SpendableRecommendationsResponse)
@router.get("/spendable/recommendations", response_model=SpendableRecommendationsResponse)
def get_recommendations(
    user_id: Optional[str] = Query(None, description="Account identifier"),
    snapshot_time: Optional[str] = Query(None, description="Snapshot timestamp T"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Return deterministic recommendations and Gemini explanation (or fallback)."""
    try:
        target_uid = user_id or current_account.account_id
        return service.get_recommendations(user_id=target_uid, snapshot_time=snapshot_time)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/simulate", response_model=ScenarioResult)
@router.post("/spendable/simulate", response_model=ScenarioResult)
def simulate_scenario(
    payload: ScenarioInput,
    user_id: Optional[str] = Query(None, description="Account identifier"),
    snapshot_time: Optional[str] = Query(None, description="Snapshot timestamp T"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Simulate a hypothetical scenario ('what-if') without mutating base state."""
    try:
        target_uid = user_id or current_account.account_id
        return service.simulate_scenario(
            scenario_input=payload, user_id=target_uid, snapshot_time=snapshot_time
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to execute scenario simulation: {str(e)}"
        )


@router.post("/explain", response_model=GeminiExplanationResponse)
@router.post("/spendable/explain", response_model=GeminiExplanationResponse)
def explain_context(
    payload: Optional[ExplainRequest] = None,
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Generate Gemini explanation (or fallback) from Spendable context."""
    try:
        uid = payload.user_id if (payload and payload.user_id) else current_account.account_id
        stime = payload.snapshot_time if payload else None
        inc_scen = payload.include_scenario if payload else False
        return service.explain(user_id=uid, snapshot_time=stime, include_scenario=inc_scen)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )
