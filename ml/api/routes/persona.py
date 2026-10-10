"""
Customer Persona Segmentation (Phase 17) & Subscriptions Detection (Phase 14) Routes.
"""

from fastapi import APIRouter, HTTPException
from api.schemas import (
    PersonaSegmentRequest,
    PersonaSegmentResponse,
    SubscriptionDetectRequest,
    SubscriptionDetectResponse,
)
from inference.predict_segmentation import CustomerSegmentationEngine
from inference.predict_subscriptions import classify_recurring_merchant

router = APIRouter(prefix="/api/v1", tags=["Persona Segmentation & Subscriptions"])
segmentation_engine = CustomerSegmentationEngine()


@router.post("/persona/segment", response_model=PersonaSegmentResponse)
def segment_customer_persona(req: PersonaSegmentRequest):
    """
    Classifies user financial habits into 1 of 6 persona archetypes with multi-persona soft probabilities.
    """
    try:
        res = segmentation_engine.segment_user(
            monthly_income=req.monthly_income,
            income_volatility_cv=req.income_volatility_cv,
            monthly_essential_expenses=req.monthly_essential_expenses,
            monthly_discretionary_spend=req.monthly_discretionary_spend,
            monthly_investments_sip=req.monthly_investments_sip,
            existing_monthly_emi=req.existing_monthly_emi,
            total_credit_limit=req.total_credit_limit,
            total_credit_used=req.total_credit_used,
            total_liquid_savings=req.total_liquid_savings,
        )
        return PersonaSegmentResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/detect", response_model=SubscriptionDetectResponse)
def detect_recurring_subscription(req: SubscriptionDetectRequest):
    """
    Identifies recurring subscriptions, renewal cadences, and projected annual commitments.
    """
    try:
        res = classify_recurring_merchant(
            merchant_name=req.merchant_name,
            amount=req.amount,
            interval_mean_days=req.interval_mean_days,
        )
        return SubscriptionDetectResponse(
            status=res.get("status", "success"),
            merchant=req.merchant_name,
            amount=req.amount,
            is_subscription=res.get("is_subscription", True),
            confidence=res.get("confidence", 0.95),
            predicted_cadence=res.get("predicted_cadence", "MONTHLY"),
            projected_annual_cost=res.get("projected_annual_cost", req.amount * 12.0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
