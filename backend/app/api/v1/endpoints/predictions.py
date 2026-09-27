"""
REST Endpoints for Machine Learning Predictions and Financial Intelligence.
Directly interfaces with the Fintra-AI ML inference layer.
"""

import os
import sys
from fastapi import APIRouter, Depends, HTTPException, status

# Ensure root repository is in Python module search path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.app.core.security import rate_limit
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
    OCRScanRequest,
    OCRScanResponse,
    AffordabilityEvaluateRequest,
    AffordabilityEvaluateResponse,
)

router = APIRouter(dependencies=[Depends(rate_limit(rate=100, window=60))])


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


@router.post(
    "/predict/ocr",
    response_model=OCRScanResponse,
    summary="Scan OCR Receipt Text (Phase 15)",
    description="Parses raw OCR text into structured financial fields: merchant, date, total INR, tax, category, and payment mode.",
)
def scan_receipt_ocr(payload: OCRScanRequest):
    try:
        from ml.inference.predict_ocr import SmartReceiptScannerEngine

        engine = SmartReceiptScannerEngine()
        res = engine.scan_receipt_text(payload.raw_text)
        if res.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=res.get("message", "Invalid receipt text"),
            )
        return OCRScanResponse(
            status="success",
            extracted_expense=res.get("extracted_expense", {}),
            extraction_confidence=float(res.get("extraction_confidence", 0.0)),
            entity_confidences=res.get("entity_confidences", {}),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR receipt scanning error: {str(exc)}",
        )


@router.post(
    "/predict/affordability",
    response_model=AffordabilityEvaluateResponse,
    summary="Buy or Wait? AI Affordability Evaluation",
    description="Evaluates purchase affordability considering verified liquid balance, recurring commitments, safe runway, and payment alternatives.",
)
def evaluate_purchase_affordability(payload: AffordabilityEvaluateRequest):
    try:
        import math

        bal = float(payload.current_liquid_balance)
        inc = float(payload.monthly_income)
        ess = max(1.0, float(payload.monthly_essential_expenses))
        cost = float(payload.amount)
        urg = payload.urgency.upper()

        # 1. Runway and Cushion
        cushion_required = ess * 3.0  # 3 months minimum safe emergency runway
        safe_discretionary = max(0.0, bal - cushion_required)
        monthly_surplus_before = inc - ess

        runway_before = round(bal / ess, 1)
        runway_after = round(max(0.0, bal - cost) / ess, 1)

        savings_rate_before = (monthly_surplus_before / inc) * 100 if inc > 0 else 0.0

        tradeoffs = []
        alternative_options = []
        recommendation = "WAIT"
        rec_title = "Wait Before Purchasing"
        risk_level = "MEDIUM"
        confidence_score = 0.92

        # 2. Decision logic
        if cost <= safe_discretionary and monthly_surplus_before > 0:
            recommendation = "PAY_IN_FULL"
            rec_title = "Safely Affordable — Pay Upfront"
            risk_level = "LOW"
            confidence_score = 0.96
            action_verdict = f"Your verified capital can safely absorb ${cost:,.2f} while keeping {runway_after} months of essential runway intact."
            tradeoffs.append(f"Emergency runway adjusts from {runway_before} mo to {runway_after} mo (safely above the 3.0 mo threshold).")
            tradeoffs.append(f"Liquidity cushion drops by ${cost:,.2f}, leaving ${max(0.0, bal - cost):,.2f} in liquid reserves.")

        elif payload.installment_months and payload.installment_months > 0:
            n_months = payload.installment_months
            apr = float(payload.installment_interest_rate_pct or 0.0) / 100.0
            emi = (cost * (1.0 + apr * (n_months / 12.0))) / n_months

            if emi <= monthly_surplus_before * 0.4 and bal >= cushion_required * 0.75:
                recommendation = "INSTALLMENTS"
                rec_title = f"Spread via {n_months}-Month Installments"
                risk_level = "LOW" if apr == 0 else "MEDIUM"
                confidence_score = 0.91
                action_verdict = f"Financing at ${emi:,.2f}/month preserves your upfront liquid cushion of ${bal:,.2f} with minimal surplus strain."
                tradeoffs.append(f"Commits ${emi:,.2f}/month of your ${monthly_surplus_before:,.2f} monthly surplus for {n_months} months.")
                if apr > 0:
                    total_paid = emi * n_months
                    tradeoffs.append(f"Incurs ${total_paid - cost:,.2f} in interest charges over the tenure.")
            else:
                recommendation = "WAIT"
                risk_level = "HIGH"
                rec_title = "Installment Strain Too High — Wait"
                action_verdict = f"The proposed EMI (${emi:,.2f}/mo) consumes more than 40% of your free cash flow. Postponing is advised."

        elif bal >= cost and urg == "ESSENTIAL":
            recommendation = "PAY_PARTIALLY"
            rec_title = "Split via Down Payment & Buffer"
            risk_level = "MEDIUM"
            confidence_score = 0.88
            down_payment = round(safe_discretionary, 2)
            action_verdict = f"This essential item eats into your emergency cushion. Consider paying ${down_payment:,.2f} down and staggering the rest."
            tradeoffs.append(f"Reduces emergency runway down to {runway_after} months (caution zone).")

        elif bal >= cost:
            deficit = cost - safe_discretionary
            days_to_save = max(14, int(math.ceil((deficit / max(100.0, monthly_surplus_before)) * 30)))
            recommendation = "WAIT"
            risk_level = "MEDIUM"
            confidence_score = 0.90
            rec_title = f"Postpone & Save for {days_to_save} Days"
            action_verdict = f"Buying now drops your liquid runway from {runway_before} mo to {runway_after} mo. Waiting {days_to_save} days accumulates safe surplus."
            tradeoffs.append(f"Immediate purchase leaves only {runway_after} months of living expenses liquid.")
            tradeoffs.append(f"Postponing preserves your safety margin while avoiding debt.")

        else:
            recommendation = "DO_NOT_PROCEED"
            rec_title = "Immediate Overdraft Hazard — Do Not Proceed"
            risk_level = "CRITICAL"
            confidence_score = 0.98
            action_verdict = f"This expense of ${cost:,.2f} exceeds your total liquid balance (${bal:,.2f}). Purchasing now risks immediate insolvency."
            tradeoffs.append("Would require high-interest emergency borrowing or punitive overdraft fees.")

        # Alternative paths
        if recommendation != "PAY_IN_FULL":
            alternative_options.append({
                "type": "POSTPONE",
                "label": "Wait for Next Pay Cycle",
                "impact": f"Rebuilds free cash flow by +${monthly_surplus_before:,.2f}/month."
            })
            alternative_options.append({
                "type": "NO_COST_EMI",
                "label": "Explore 0% Interest 3-6 Month Financing",
                "impact": f"Reduces upfront liquidity impact to ~${(cost / 3):,.2f}/month."
            })

        # 30-Day Day-by-Day Cash Flow Projection
        projection = []
        daily_income_rate = inc / 30.0
        daily_expense_rate = ess / 30.0

        cur_base = bal
        cur_post = max(0.0, bal - cost) if recommendation in ["PAY_IN_FULL", "PAY_PARTIALLY"] else bal

        for day in range(0, 31, 5):
            projection.append({
                "day": f"Day {day}",
                "baseline_balance": round(cur_base),
                "with_purchase_balance": round(cur_post),
            })
            cur_base += (daily_income_rate - daily_expense_rate) * 5
            cur_post += (daily_income_rate - daily_expense_rate) * 5

        monthly_surplus_after = monthly_surplus_before
        savings_rate_after = savings_rate_before

        return AffordabilityEvaluateResponse(
            status="success",
            item_name=payload.item_name,
            amount=cost,
            recommendation=recommendation,
            recommendation_title=rec_title,
            risk_level=risk_level,
            confidence_score=confidence_score,
            amount_safe_to_spend=round(safe_discretionary, 2),
            runway_before_months=runway_before,
            runway_after_months=runway_after,
            monthly_surplus_before=round(monthly_surplus_before, 2),
            monthly_surplus_after=round(monthly_surplus_after, 2),
            savings_rate_impact_pct=round(savings_rate_before - savings_rate_after, 1),
            cashflow_projection_30d=projection,
            tradeoffs=tradeoffs,
            alternative_options=alternative_options,
            action_verdict=action_verdict,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Affordability evaluation error: {str(exc)}",
        )


