"""
Security, Fraud (Phase 8), Anomaly (Phase 9), Loan Underwriting (Phase 12) & Credit Estimator (Phase 13) Routes.
"""

from fastapi import APIRouter, HTTPException
from api.schemas import (
    AnomalyDetectRequest,
    AnomalyDetectResponse,
    CreditEstimateRequest,
    CreditEstimateResponse,
    FraudCheckRequest,
    FraudCheckResponse,
    LoanUnderwriteRequest,
    LoanUnderwriteResponse,
)
from inference.predict_anomaly import (
    detect_transaction_anomaly,
    predict_fraud_risk,
)
from inference.predict_credit import CreditScoreEstimator
from inference.predict_loan import LoanUnderwritingEngine

router = APIRouter(prefix="/api/v1", tags=["Security, Risk & Credit Underwriting"])
loan_engine = LoanUnderwritingEngine()
credit_engine = CreditScoreEstimator()


@router.post("/fraud/check", response_model=FraudCheckResponse)
def check_transaction_fraud(req: FraudCheckRequest):
    """
    Evaluates real-time transaction fraud risk probability and recommended action.
    """
    try:
        txn = {
            "amount": req.amount,
            "category": req.category,
            "hour_of_day": req.hour_of_day,
            "merchant": req.merchant,
        }
        res = predict_fraud_risk(transaction=txn)
        return FraudCheckResponse(
            status=res.get("status", "success"),
            risk_level=res.get("risk_level", "LOW"),
            fraud_probability=res.get("fraud_probability", 0.05),
            recommended_action=res.get("recommended_action", "ALLOW"),
            action_detail=res.get("action_detail", "Normal transaction pattern"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anomaly/detect", response_model=AnomalyDetectResponse)
def detect_spending_anomaly(req: AnomalyDetectRequest):
    """
    Detects unusual outlier spending spikes across merchant categories.
    """
    try:
        txn = {"amount": req.amount, "category": req.category}
        res = detect_transaction_anomaly(transaction=txn)
        return AnomalyDetectResponse(
            status=res.get("status", "success"),
            is_anomaly=res.get("is_anomaly", False),
            anomaly_score=res.get("anomaly_score", 0.0),
            reason_codes=res.get("reason_codes", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/loans/underwrite", response_model=LoanUnderwriteResponse)
def underwrite_loan_application(req: LoanUnderwriteRequest):
    """
    Evaluates loan underwriting, debt-to-income limits, and default risk probability.
    """
    try:
        res = loan_engine.evaluate_application(
            monthly_income=req.monthly_income,
            requested_loan_amount=req.requested_loan_amount,
            loan_tenure_months=req.loan_tenure_months,
            loan_purpose=req.loan_purpose,
            credit_score=req.credit_score,
            existing_monthly_emi=req.existing_monthly_emi,
        )
        return LoanUnderwriteResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credit/estimate", response_model=CreditEstimateResponse)
def estimate_credit_score(req: CreditEstimateRequest):
    """
    Estimates credit score (300-900) across 5 pillars with interactive score simulation.
    """
    try:
        res = credit_engine.estimate(
            monthly_income=req.monthly_income,
            total_credit_limit=req.total_credit_limit,
            total_credit_used=req.total_credit_used,
            on_time_payment_pct=req.on_time_payment_pct,
            missed_payments_count_2yr=req.missed_payments_count_2yr,
            credit_history_years=req.credit_history_years,
            hard_inquiries_last_6mo=req.hard_inquiries_last_6m,
        )
        return CreditEstimateResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
