from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.health import router as health_router
from app.api.activities import router as activities_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Spendable - AI-powered personal financial liquidity intelligence platform.",
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(activities_router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint presenting system identity and API status."""
    return {
        "project": "Spendable",
        "tagline": "Know what you can safely spend.",
        "platform": "Personal Liquidity Intelligence Engine",
        "status": "initialization_foundation",
        "documentation": "/docs",
        "health_check": "/api/v1/health"
    }
