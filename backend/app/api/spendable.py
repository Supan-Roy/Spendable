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


from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.auth import get_current_account
from app.models.account import UserAccount
from app.audit import audit_logger
from app.rate_limiter import RateLimiter

ai_chat_limiter = RateLimiter(max_requests=30, window_seconds=60, name="ai_chat")
ai_explain_limiter = RateLimiter(max_requests=30, window_seconds=60, name="ai_explain")


def _verify_account_isolation(
    requested_uid: Optional[str],
    current_account: UserAccount,
    endpoint_name: str,
    request: Request,
) -> str:
    """Verify that user_id requested matches authenticated account_id when Auth header present."""
    has_auth_header = bool(request.headers.get("Authorization"))
    if has_auth_header and requested_uid and requested_uid != current_account.account_id:
        audit_logger.log_event(
            event_type="CROSS_ACCOUNT_ACCESS_DENIED",
            account_id=current_account.account_id,
            endpoint=endpoint_name,
            detail=f"Attempted access to account '{requested_uid}'",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cross-account financial data access denied.",
        )
    return current_account.account_id if (has_auth_header or not requested_uid) else requested_uid


@router.get("/overview", response_model=SpendableOverviewResponse)
@router.get("/spendable/overview", response_model=SpendableOverviewResponse)
def get_overview(
    request: Request,
    user_id: Optional[str] = Query(None, description="Account identifier"),
    snapshot_time: Optional[str] = Query(None, description="Snapshot timestamp T"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Return main Spendable dashboard overview state."""
    target_uid = _verify_account_isolation(user_id, current_account, "/overview", request)
    try:
        audit_logger.log_event("FINANCIAL_SNAPSHOT_ACCESSED", account_id=target_uid, endpoint="/overview")
        return service.get_overview(user_id=target_uid, snapshot_time=snapshot_time)
    except HTTPException:
        raise
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
    request: Request,
    user_id: Optional[str] = Query(None, description="Account identifier"),
    snapshot_time: Optional[str] = Query(None, description="Snapshot timestamp T"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Return multi-horizon forecasts and 30-day daily projected balance trajectory."""
    target_uid = _verify_account_isolation(user_id, current_account, "/forecast", request)
    try:
        audit_logger.log_event("FINANCIAL_SNAPSHOT_ACCESSED", account_id=target_uid, endpoint="/forecast")
        return service.get_forecast(user_id=target_uid, snapshot_time=snapshot_time)
    except HTTPException:
        raise
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
    request: Request,
    user_id: Optional[str] = Query(None, description="Account identifier"),
    limit: int = Query(50, ge=1, le=500, description="Pagination page limit"),
    offset: int = Query(0, ge=0, description="Pagination page offset"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Return recent observed transaction activity records with pagination."""
    target_uid = _verify_account_isolation(user_id, current_account, "/activity", request)
    try:
        audit_logger.log_event("FINANCIAL_SNAPSHOT_ACCESSED", account_id=target_uid, endpoint="/activity")
        return service.get_activities(user_id=target_uid, limit=limit, offset=offset)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve activity records: {str(e)}"
        )


@router.get("/recommendations", response_model=SpendableRecommendationsResponse)
@router.get("/spendable/recommendations", response_model=SpendableRecommendationsResponse)
def get_recommendations(
    request: Request,
    user_id: Optional[str] = Query(None, description="Account identifier"),
    snapshot_time: Optional[str] = Query(None, description="Snapshot timestamp T"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Return deterministic recommendations and Gemini explanation (or fallback)."""
    target_uid = _verify_account_isolation(user_id, current_account, "/recommendations", request)
    try:
        audit_logger.log_event("FINANCIAL_SNAPSHOT_ACCESSED", account_id=target_uid, endpoint="/recommendations")
        return service.get_recommendations(user_id=target_uid, snapshot_time=snapshot_time)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/simulate", response_model=ScenarioResult)
@router.post("/spendable/simulate", response_model=ScenarioResult)
def simulate_scenario(
    payload: ScenarioInput,
    request: Request,
    user_id: Optional[str] = Query(None, description="Account identifier"),
    snapshot_time: Optional[str] = Query(None, description="Snapshot timestamp T"),
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Simulate a hypothetical scenario ('what-if') without mutating base state."""
    target_uid = _verify_account_isolation(user_id, current_account, "/simulate", request)
    try:
        audit_logger.log_event("SCENARIO_SIMULATION_EXECUTED", account_id=target_uid, endpoint="/simulate")
        return service.simulate_scenario(
            scenario_input=payload, user_id=target_uid, snapshot_time=snapshot_time
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to execute scenario simulation: {str(e)}"
        )


@router.post("/explain", response_model=GeminiExplanationResponse, dependencies=[Depends(ai_explain_limiter)])
@router.post("/spendable/explain", response_model=GeminiExplanationResponse, dependencies=[Depends(ai_explain_limiter)])
def explain_context(
    request: Request,
    payload: Optional[ExplainRequest] = None,
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
):
    """Generate Gemini explanation (or fallback) from Spendable context."""
    req_uid = payload.user_id if payload else None
    target_uid = _verify_account_isolation(req_uid, current_account, "/explain", request)
    try:
        audit_logger.log_event("EXPLANATION_GENERATED", account_id=target_uid, endpoint="/explain")
        stime = payload.snapshot_time if payload else None
        inc_scen = payload.include_scenario if payload else False
        return service.explain(user_id=target_uid, snapshot_time=stime, include_scenario=inc_scen)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )


from app.schemas.spendable import ChatRequest, ChatResponse
from app.explanation.spendable_ai_chat import SpendableAIChatEngine

_chat_engine_instance: Optional[SpendableAIChatEngine] = None

def get_chat_engine() -> SpendableAIChatEngine:
    global _chat_engine_instance
    if _chat_engine_instance is None:
        _chat_engine_instance = SpendableAIChatEngine()
    return _chat_engine_instance


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(ai_chat_limiter)])
@router.post("/spendable/chat", response_model=ChatResponse, dependencies=[Depends(ai_chat_limiter)])
def chat_spendable_ai(
    payload: ChatRequest,
    current_account: UserAccount = Depends(get_current_account),
    service: SpendableService = Depends(get_spendable_service),
    chat_engine: SpendableAIChatEngine = Depends(get_chat_engine),
):
    """Chat with Spendable AI Assistant using real user account context and Gemini SDK."""
    uid = current_account.account_id
    try:
        audit_logger.log_event("AI_CHAT_REQUESTED", account_id=uid, endpoint="/chat")
        account_context = chat_engine.build_account_context(
            service=service,
            user_id=uid,
            scenario_result=payload.scenario_result,
        )
        return chat_engine.answer(
            user_message=payload.message,
            chat_history=payload.chat_history or [],
            account_context=account_context,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Spendable AI chat error: {str(e)}"
        )

