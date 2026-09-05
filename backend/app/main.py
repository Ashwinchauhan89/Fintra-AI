"""
Fintra-AI Backend & Prediction Service Entry Point.
FastAPI Application providing REST APIs for Financial Intelligence and ML Models.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from backend.app.core.config import settings
from backend.app.core.security import RateLimitExceeded
from backend.app.api.v1.endpoints import auth, health, predictions

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


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Inject standard security headers into all outgoing HTTP responses."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom JSON response for rate limit violations with RateLimit headers."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
        headers=exc.headers,
    )


# Mount API Routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["System Health"])
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Authentication & Security"])
app.include_router(predictions.router, prefix=settings.API_V1_STR, tags=["ML Predictions & Intelligence"])


@app.get("/", include_in_schema=False)
def root():
    """Redirect root path to interactive Swagger documentation."""
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")
