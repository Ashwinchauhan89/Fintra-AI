"""
Health Check and System Diagnostics Endpoint.
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter()


@router.get("/health", summary="System Health & Diagnostic Status")
def get_health():
    """
    Returns server operational status, environment, and available ML subsystems.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "subsystems": {
            "category_classification": "available",
            "anomaly_detection": "available",
            "fraud_scoring": "available",
            "budget_recommendation": "available",
            "financial_health": "available",
            "goal_timeline": "available",
            "investment_allocation": "available",
        },
    }
