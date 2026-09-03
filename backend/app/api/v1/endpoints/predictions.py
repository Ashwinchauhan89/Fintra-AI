"""
REST Endpoints for Machine Learning Predictions and Financial Intelligence.
Directly interfaces with the Fintra-AI ML inference layer.
"""

import os
import sys
from fastapi import APIRouter, HTTPException, status

# Ensure root repository is in Python module search path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.app.schemas.predictions import (
    CategoryPredictRequest,
    CategoryPredictResponse,
    AnomalyCheckRequest,
    AnomalyCheckResponse,
    FraudCheckRequest,
    FraudCheckResponse,
    BudgetRecommendRequest,
    BudgetRecommendResponse,
    HealthScoreRequest,
    HealthScoreResponse,
    GoalTimelineRequest,
    GoalTimelineResponse,
    InvestmentRecommendRequest,
    InvestmentRecommendResponse,
)

router = APIRouter()


@router.post(
    "/predict/category",
    response_model=CategoryPredictResponse,
    summary="Predict Expense Category",
    description="Automatically classifies a transaction into canonical expense categories based on merchant, notes, and amount.",
)
def predict_expense_category(payload: CategoryPredictRequest):
    try:
        from ml.inference.predict import predict_category

        res = predict_category(
            merchant=payload.merchant,
            description=payload.description,
            amount=payload.amount,
            date=payload.date,
        )
        conf_val = res.get("confidence")
        confidence = float(conf_val) if conf_val is not None else 1.0
        is_low = bool(res.get("low_confidence", False) or res.get("is_low_confidence", False))
        return CategoryPredictResponse(
            status="success",
            category=res.get("category", "other-expense"),
            confidence=confidence,
            is_low_confidence=is_low,
            fallback_used=bool(res.get("fallback_used", False)),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Expense categorization error: {str(exc)}",
        )


@router.post(
    "/predict/anomaly",
    response_model=AnomalyCheckResponse,
    summary="Detect Real-Time Spending Anomaly",
    description="Audits a transaction against historical distributions and flags statistical outliers or spikes.",
)
def check_spending_anomaly(payload: AnomalyCheckRequest):
    try:
        from ml.inference.predict_anomaly import detect_transaction_anomaly

        tx_dict = {
            "merchant": payload.merchant,
            "amount": payload.amount,
            "category": payload.category,
            "hour_of_day": payload.hour_of_day,
        }
        res = detect_transaction_anomaly(tx_dict)
        return AnomalyCheckResponse(
            status="success",
            is_anomaly=bool(res.get("is_anomaly", False)),
            severity=str(res.get("severity", "NORMAL")),
            reasons=list(res.get("reasons", [])),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly detection error: {str(exc)}",
        )


@router.post(
    "/predict/fraud",
    response_model=FraudCheckResponse,
    summary="Score Multi-Factor Fraud Risk",
    description="Evaluates transaction velocity, geo-distance, device trust, and merchant risk for fraud probability (0-100%).",
)
def evaluate_fraud_risk(payload: FraudCheckRequest):
    try:
        from ml.inference.predict_anomaly import predict_fraud_risk

        tx_dict = {
            "merchant": payload.merchant,
            "amount": payload.amount,
            "category": payload.category,
            "hour_of_day": payload.hour_of_day,
            "distance_from_home_km": payload.distance_from_home_km,
            "device_trust_score": payload.device_trust_score,
            "merchant_risk_score": payload.merchant_risk_score,
            "is_foreign_currency": payload.is_foreign_currency,
        }
        res = predict_fraud_risk(tx_dict)
        return FraudCheckResponse(
            status="success",
            fraud_probability=float(res.get("fraud_probability", 0.0)),
            fraud_percentage=float(res.get("fraud_percentage", 0.0)),
            risk_level=str(res.get("risk_level", "LOW")),
            recommended_action=str(res.get("recommended_action", "ALLOW")),
            risk_factors=list(res.get("risk_factors", [])),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud scoring error: {str(exc)}",
        )


@router.post(
    "/predict/budget",
    response_model=BudgetRecommendResponse,
    summary="Recommend 50/30/20 Budget Allocations",
    description="Generates optimal category allocations, overspending diagnostics, and savings targets.",
)
def generate_budget_recommendations(payload: BudgetRecommendRequest):
    try:
        from ml.inference.predict_budget import recommend_budget

        res = recommend_budget(
            monthly_income=payload.monthly_income,
            historical_expenses=payload.historical_expenses,
            savings_target_pct=payload.savings_target_pct,
            lifestyle=payload.lifestyle,
        )
        return BudgetRecommendResponse(
            status="success",
            monthly_income=payload.monthly_income,
            recommended_allocations=res.get("recommended_allocations", {}),
            rule_50_30_20=res.get("rule_50_30_20", {}),
            optimization_insights=res.get("optimization_insights", []),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Budget recommendation error: {str(exc)}",
        )


@router.post(
    "/predict/health-score",
    response_model=HealthScoreResponse,
    summary="Calculate 0-100 Financial Health Score",
    description="Assesses user financial health across 5 calibrated pillars (Savings, Debt, Wants, Runway, Buffer) with letter grading.",
)
def compute_health_score(payload: HealthScoreRequest):
    try:
        from ml.inference.predict_budget import calculate_financial_health_score

        res = calculate_financial_health_score(
            monthly_income=payload.monthly_income,
            current_balance=payload.current_balance,
            monthly_expenses=payload.monthly_expenses,
            debt_obligations=payload.debt_obligations,
        )
        return HealthScoreResponse(
            status="success",
            financial_health_score=float(res.get("financial_health_score", 0.0)),
            grade=str(res.get("grade", "C")),
            status_label=str(res.get("status", "FAIR")),
            pillars=res.get("pillars", {}),
            recommendations=res.get("recommendations", []),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health scoring error: {str(exc)}",
        )


@router.post(
    "/predict/goals",
    response_model=GoalTimelineResponse,
    summary="Forecast Goal Completion Timeline & SIP",
    description="Predicts completion months, milestone date, required monthly savings, and acceleration tips.",
)
def predict_financial_goal(payload: GoalTimelineRequest):
    try:
        from ml.inference.predict_goals import predict_goal_timeline

        res = predict_goal_timeline(
            goal_name=payload.goal_name,
            target_amount=payload.target_amount,
            current_saved=payload.current_saved,
            monthly_income=payload.monthly_income,
            monthly_expenses=payload.monthly_expenses,
            debt_obligations=payload.debt_obligations,
            intended_months=payload.intended_months or 12,
            expected_annual_return_pct=payload.expected_annual_return_pct,
        )
        return GoalTimelineResponse(
            status="success",
            goal_name=str(res.get("goal_name", payload.goal_name)),
            target_amount=float(res.get("target_amount", payload.target_amount)),
            current_saved=float(res.get("current_saved", payload.current_saved)),
            predicted_months_to_completion=float(res.get("predicted_months_to_completion", 0.0)),
            estimated_completion_date=str(res.get("estimated_completion_date", "")),
            required_monthly_savings=float(res.get("required_monthly_savings", 0.0)),
            feasibility=str(res.get("feasibility", "UNKNOWN")),
            recommendations=list(res.get("recommendations", [])),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Goal timeline error: {str(exc)}",
        )


@router.post(
    "/predict/investments",
    response_model=InvestmentRecommendResponse,
    summary="Predict Multi-Asset Portfolio Allocation",
    description="Computes personalized allocation percentages across Equity, Debt, Gold, REITs, and Cash with monthly SIP distribution.",
)
def recommend_investment_portfolio(payload: InvestmentRecommendRequest):
    try:
        from ml.inference.predict_investment import InvestmentRecommender

        recommender = InvestmentRecommender()
        res = recommender.recommend(
            monthly_income=payload.monthly_income,
            age=payload.age,
            investment_horizon_years=payload.investment_horizon_years,
            risk_profile=payload.risk_profile,
        )
        return InvestmentRecommendResponse(
            status="success",
            recommended_allocation_pct=res.get("recommended_allocation_pct", {}),
            monthly_sip_distribution_inr=res.get("monthly_sip_distribution_inr", {}),
            portfolio_expected_cagr_pct=float(res.get("portfolio_expected_cagr_pct", 0.0)),
            wealth_growth_projections=res.get("wealth_growth_projections", {}),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investment recommendation error: {str(exc)}",
        )
