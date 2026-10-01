from datetime import datetime, timezone
from fastapi import APIRouter
from app.config import settings
from app.database import check_db_connection

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def get_health():
    """Health check endpoint to verify backend operational state and database readiness."""
    db_health = check_db_connection()
    
    return {
        "status": "healthy" if db_health["connected"] else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_health,
        "services": {
            "api": "online",
            "database_readiness": "ready" if db_health["connected"] else "unreachable_or_not_started",
            "ai_integration": "planned"
        }
    }
