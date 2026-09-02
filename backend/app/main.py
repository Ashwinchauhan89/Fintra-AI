"""
Fintra-AI Backend & Prediction Service Entry Point.
FastAPI Application providing REST APIs for Financial Intelligence and ML Models.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.core.config import settings
from backend.app.api.v1.endpoints import health, predictions

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=(
        "Production-ready REST API for Fintra-AI. Provides predictive financial intelligence, "
        "fraud detection, real-time spending anomaly detection, optimal budget allocations, "
        "and goal forecasting."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configure Cross-Origin Resource Sharing (CORS) for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["System Health"])
app.include_router(predictions.router, prefix=settings.API_V1_STR, tags=["ML Predictions & Intelligence"])


@app.get("/", include_in_schema=False)
def root():
    """Redirect root path to interactive Swagger documentation."""
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")
