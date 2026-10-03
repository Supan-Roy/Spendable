import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.health import router as health_router
from app.api.activities import router as activities_router
from app.api.spendable import router as spendable_router
from app.api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Automatic startup initialization (Alembic check & demo seed on boot)."""
    try:
        from app.seed_demo import seed_demo_accounts
        seed_demo_accounts()
    except Exception as e:
        print(f"[Startup] Demo seed notice: {e}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Spendable - AI-powered personal financial liquidity intelligence platform.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(activities_router, prefix="/api/v1")
app.include_router(spendable_router, prefix="/api/v1")


# Locate static frontend build directory if present (e.g., in Docker container or after pnpm build)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend", "dist"))

if not os.path.exists(FRONTEND_DIST):
    FRONTEND_DIST = os.path.abspath("frontend/dist")

if os.path.exists(FRONTEND_DIST) and os.path.isdir(FRONTEND_DIST):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Exclude API endpoints and OpenAPI docs from SPA fallback
        if full_path.startswith("api/") or full_path.startswith("api") or full_path in ("docs", "redoc", "openapi.json"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API endpoint not found")
        requested_file = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(requested_file):
            return FileResponse(requested_file)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
else:
    @app.get("/")
    def root():
        """Root endpoint presenting system identity and API status when frontend is not built."""
        return {
            "project": "Spendable",
            "tagline": "Know what you can safely spend.",
            "platform": "Personal Liquidity Intelligence Engine",
            "status": "initialization_foundation",
            "documentation": "/docs",
            "health_check": "/api/v1/health"
        }

