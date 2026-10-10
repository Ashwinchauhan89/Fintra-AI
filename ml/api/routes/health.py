"""
Health & Diagnostic Routes for Fintra-AI ML REST Microservice.
"""

from datetime import datetime
import os
from fastapi import APIRouter
from api.schemas import HealthResponse

router = APIRouter(tags=["Health & Monitoring"])

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")


@router.get("/health", response_model=HealthResponse)
@router.get("/api/v1/health", response_model=HealthResponse)
def get_system_health():
    """
    Health check returning server status and availability of all 15 ML models.
    """
    model_checks = {
        "expense_category_classifier": os.path.exists(os.path.join(MODEL_DIR, "best_model.pkl")),
        "savings_growth_model": os.path.exists(os.path.join(MODEL_DIR, "goals_best_model.pkl")),
        "fraud_risk_pipeline": os.path.exists(os.path.join(MODEL_DIR, "anomaly_fraud_pipeline.pkl")),
        "spending_anomaly_detector": os.path.exists(os.path.join(MODEL_DIR, "anomaly_isolation_forest.pkl")),
        "investment_recommender": os.path.exists(os.path.join(MODEL_DIR, "investment_metadata.json")),
        "goal_timeline_predictor": os.path.exists(os.path.join(MODEL_DIR, "goals_best_model.pkl")),
        "loan_underwriting_engine": os.path.exists(os.path.join(MODEL_DIR, "loan_best_model.pkl")),
        "credit_score_estimator": os.path.exists(os.path.join(MODEL_DIR, "credit_score_pipeline.pkl")),
        "subscription_detector": os.path.exists(os.path.join(MODEL_DIR, "subscription_metadata.json")),
        "ocr_receipt_scanner": os.path.exists(os.path.join(MODEL_DIR, "ocr_metadata.json")),
        "product_recommender": os.path.exists(os.path.join(MODEL_DIR, "recommendation_metadata.json")),
        "customer_segmentation": os.path.exists(os.path.join(MODEL_DIR, "segmentation_pipeline.pkl")),
        "cash_flow_forecaster": os.path.exists(os.path.join(MODEL_DIR, "forecasting_best_model.pkl")),
    }

    return HealthResponse(
        status="healthy",
        service="Fintra-AI ML Production Microservice",
        version="1.0.0",
        loaded_models=model_checks,
        server_time=datetime.now().isoformat(),
    )
