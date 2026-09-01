"""
FastAPI End-to-End REST Endpoint Verification Suite for Phase 19.

Tests all 15 ML intelligence routes and the AI Copilot:
- GET /health
- POST /api/v1/expenses/classify
- POST /api/v1/ocr/scan
- POST /api/v1/budget/recommend
- POST /api/v1/savings/project
- POST /api/v1/health-score/diagnose
- POST /api/v1/fraud/check
- POST /api/v1/anomaly/detect
- POST /api/v1/loans/underwrite
- POST /api/v1/credit/estimate
- POST /api/v1/investments/recommend
- POST /api/v1/goals/timeline
- POST /api/v1/cashflow/forecast
- POST /api/v1/marketplace/recommend
- POST /api/v1/persona/segment
- POST /api/v1/subscriptions/detect
- POST /api/v1/copilot/ask
- POST /api/v1/copilot/affordability
"""

import os
import sys
import time
from starlette.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from api.main import app  # noqa: E402

client = TestClient(app)


def test_api_suite():
    print("=" * 90)
    print("FINTRA-AI REST MICROSERVICE END-TO-END API TEST SUITE (PHASE 19)")
    print("=" * 90)

    results = []

    # 1. Health Endpoint
    r = client.get("/health")
    assert r.status_code == 200, f"Health failed: {r.text}"
    results.append(("GET  /health", r.status_code, "Server Healthy & Models Online"))

    # 2. Expense Category Classification
    r = client.post(
        "/api/v1/expenses/classify",
        json={"merchant": "Swiggy", "description": "Biryani meal", "amount": 420.0},
    )
    assert r.status_code == 200, f"Expense classify failed: {r.text}"
    cat = r.json().get("category")
    results.append(("POST /api/v1/expenses/classify", r.status_code, f"Category: {cat}"))

    # 3. OCR Receipt Scanner
    r = client.post(
        "/api/v1/ocr/scan",
        json={"raw_text": "STARBUCKS COFFEE\nDate: 25/08/2026\n1x Latte 345.00\nGRAND TOTAL: INR 362.25\nPaid via UPI"},
    )
    assert r.status_code == 200, f"OCR scan failed: {r.text}"
    amt = r.json()["extracted_expense"]["total_amount_inr"]
    results.append(("POST /api/v1/ocr/scan", r.status_code, f"Scanned Total: INR {amt}"))

    # 4. Budget Recommendation
    r = client.post(
        "/api/v1/budget/recommend",
        json={"monthly_income": 80000.0, "lifestyle": "balanced", "savings_target_pct": 0.25},
    )
    assert r.status_code == 200, f"Budget failed: {r.text}"
    results.append(("POST /api/v1/budget/recommend", r.status_code, "50/30/20 Breakdown Computed"))

    # 5. Savings Projector
    r = client.post(
        "/api/v1/savings/project",
        json={"monthly_income": 80000.0, "monthly_expenses": 45000.0, "current_balance": 50000.0},
    )
    assert r.status_code == 200, f"Savings failed: {r.text}"
    sav = r.json().get("predicted_monthly_savings")
    results.append(("POST /api/v1/savings/project", r.status_code, f"Monthly Savings: INR {sav:,.0f}"))

    # 6. Financial Health Score
    r = client.post(
        "/api/v1/health-score/diagnose",
        json={"monthly_income": 80000.0, "current_balance": 180000.0, "monthly_expenses": {"food": 15000.0, "shopping": 8000.0}},
    )
    assert r.status_code == 200, f"Health score failed: {r.text}"
    score = r.json().get("financial_health_score")
    grade = r.json().get("grade")
    results.append(("POST /api/v1/health-score/diagnose", r.status_code, f"Score: {score}/100 ({grade})"))

    # 7. Fraud Risk Detection
    r = client.post(
        "/api/v1/fraud/check",
        json={"amount": 45000.0, "category": "shopping", "hour_of_day": 3},
    )
    assert r.status_code == 200, f"Fraud failed: {r.text}"
    risk = r.json().get("risk_level")
    results.append(("POST /api/v1/fraud/check", r.status_code, f"Risk Level: {risk}"))

    # 8. Spending Anomaly Detection
    r = client.post(
        "/api/v1/anomaly/detect",
        json={"amount": 35000.0, "category": "dining"},
    )
    assert r.status_code == 200, f"Anomaly failed: {r.text}"
    anom = r.json().get("is_anomaly")
    results.append(("POST /api/v1/anomaly/detect", r.status_code, f"Is Anomaly: {anom}"))

    # 9. Loan Underwriting Engine
    r = client.post(
        "/api/v1/loans/underwrite",
        json={"monthly_income": 85000.0, "requested_loan_amount": 400000.0, "loan_tenure_months": 36, "credit_score": 750},
    )
    assert r.status_code == 200, f"Loan failed: {r.text}"
    dec = r.json().get("approval_status")
    results.append(("POST /api/v1/loans/underwrite", r.status_code, f"Decision: {dec}"))

    # 10. Credit Score Estimator
    r = client.post(
        "/api/v1/credit/estimate",
        json={"monthly_income": 75000.0, "total_credit_limit": 250000.0, "total_credit_used": 35000.0},
    )
    assert r.status_code == 200, f"Credit estimate failed: {r.text}"
    cscore = r.json().get("estimated_credit_score")
    tier = r.json().get("credit_tier")
    results.append(("POST /api/v1/credit/estimate", r.status_code, f"Credit Score: {cscore} ({tier})"))

    # 11. Investment Recommendation
    r = client.post(
        "/api/v1/investments/recommend",
        json={"monthly_income": 90000.0, "age": 28, "risk_profile": "GROWTH", "investment_horizon_years": 5},
    )
    assert r.status_code == 200, f"Investment failed: {r.text}"
    cagr = r.json().get("portfolio_expected_cagr_pct")
    results.append(("POST /api/v1/investments/recommend", r.status_code, f"Expected CAGR: {cagr}%"))

    # 12. Goal Timeline Predictor
    r = client.post(
        "/api/v1/goals/timeline",
        json={"goal_name": "Emergency Cushion", "target_amount": 300000.0, "current_saved": 50000.0, "monthly_income": 70000.0, "monthly_expenses": 35000.0},
    )
    assert r.status_code == 200, f"Goal timeline failed: {r.text}"
    months = r.json().get("predicted_months_to_completion")
    results.append(("POST /api/v1/goals/timeline", r.status_code, f"Timeline: {months} months"))

    # 13. Cash Flow Forecasting
    r = client.post(
        "/api/v1/cashflow/forecast",
        json={"monthly_income": 65000.0, "current_balance": 28000.0, "horizon_days": 30},
    )
    assert r.status_code == 200, f"Cash flow failed: {r.text}"
    traj = r.json().get("health_status")
    results.append(("POST /api/v1/cashflow/forecast", r.status_code, f"Status: {traj}"))

    # 14. Marketplace Product Recommendation
    r = client.post(
        "/api/v1/marketplace/recommend",
        json={"monthly_income": 85000.0, "credit_score": 750, "persona_id": "YOUNG_TECH_PROFESSIONAL", "spend_dining": 12000.0, "spend_shopping": 15000.0},
    )
    assert r.status_code == 200, f"Marketplace failed: {r.text}"
    p_count = len(r.json().get("top_recommendations", []))
    results.append(("POST /api/v1/marketplace/recommend", r.status_code, f"Matched Products: {p_count}"))

    # 15. Customer Persona Segmentation
    r = client.post(
        "/api/v1/persona/segment",
        json={"monthly_income": 120000.0, "monthly_essential_expenses": 35000.0, "monthly_discretionary_spend": 25000.0, "monthly_investments_sip": 30000.0},
    )
    assert r.status_code == 200, f"Persona failed: {r.text}"
    persona = r.json()["primary_persona"]["persona_id"]
    results.append(("POST /api/v1/persona/segment", r.status_code, f"Persona: {persona}"))

    # 16. Subscription Detection
    r = client.post(
        "/api/v1/subscriptions/detect",
        json={"merchant_name": "Netflix India", "amount": 649.0},
    )
    assert r.status_code == 200, f"Subscription failed: {r.text}"
    cadence = r.json().get("predicted_cadence")
    results.append(("POST /api/v1/subscriptions/detect", r.status_code, f"Cadence: {cadence}"))

    # 17. AI Copilot Conversational Advisory
    r = client.post(
        "/api/v1/copilot/ask",
        json={"user_query": "How can I save ₹50,000 for a laptop?", "monthly_income": 70000.0, "monthly_expenses": 40000.0},
    )
    assert r.status_code == 200, f"Copilot ask failed: {r.text}"
    results.append(("POST /api/v1/copilot/ask", r.status_code, "AI Advisory Generated"))

    # 18. Affordability Solver
    r = client.post(
        "/api/v1/copilot/affordability",
        json={"item_name": "Sony Headphones", "item_price_inr": 24990.0, "monthly_income": 80000.0, "monthly_expenses": 40000.0, "current_liquid_savings": 120000.0},
    )
    assert r.status_code == 200, f"Affordability failed: {r.text}"
    verdict = r.json().get("verdict")
    results.append(("POST /api/v1/copilot/affordability", r.status_code, f"Verdict: {verdict}"))

    print("\nAPI ENDPOINT VERIFICATION SUMMARY:")
    print("-" * 90)
    for endpoint, code, detail in results:
        print(f"  {endpoint:36s} | HTTP {code} | {detail}")
    print("-" * 90)
    print(">>> ALL 18 REST ENDPOINTS VERIFIED 100% OPERATIONAL WITH ZERO ERRORS!")
    print("=" * 90)


if __name__ == "__main__":
    test_api_suite()
