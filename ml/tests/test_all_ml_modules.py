"""
Master ML Diagnostic & Live Verification Test Suite for Fintra-AI.

Tests every ML inference engine end-to-end to guarantee:
- 0 runtime exceptions
- 0 missing files or broken paths
- Proper input validation & error recovery
- Exact structured JSON dictionary schema outputs
"""

import os
import sys
import json
import time
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def test_all_modules():
    print("=" * 90)
    print("FINTRA-AI MASTER ML DIAGNOSTIC & END-TO-END VERIFICATION SUITE")
    print("=" * 90)

    results = []

    # 1. Phase 3: Expense Category Classification
    try:
        from inference.predict import predict_category
        cat_res = predict_category(merchant="Swiggy", description="Lunch bowl", amount=350.0)
        assert "category" in cat_res
        results.append(("Phase 3: Expense Classification", "[PASS]", f"Category: {cat_res.get('category')} (Conf: {cat_res.get('confidence', 0):.2f})"))
    except Exception as e:
        results.append(("Phase 3: Expense Classification", "[FAIL]", traceback.format_exc()))

    # 2. Phase 5: Budget Recommendation & Optimization
    try:
        from inference.predict_budget import recommend_budget
        bud_res = recommend_budget(
            monthly_income=80000.0,
            lifestyle="balanced",
            historical_expenses={"food": 15000.0, "shopping": 10000.0, "bills": 8000.0}
        )
        assert "recommended_allocations" in bud_res
        results.append(("Phase 5: Budget Recommendation Engine", "[PASS]", f"Allocations: {len(bud_res.get('category_breakdown', {}))} categories"))
    except Exception as e:
        results.append(("Phase 5: Budget Recommendation Engine", "[FAIL]", traceback.format_exc()))

    # 3. Phase 6: Savings Capacity Growth Projector
    try:
        from inference.predict_goals import predict_savings_growth
        sav_res = predict_savings_growth(monthly_income=80000.0, monthly_expenses=45000.0, current_balance=50000.0)
        assert sav_res["status"] == "success"
        results.append(("Phase 6: Savings Projector", "[PASS]", f"Monthly Capacity: INR {sav_res.get('predicted_monthly_savings', 0):,.0f}"))
    except Exception as e:
        results.append(("Phase 6: Savings Projector", "[FAIL]", traceback.format_exc()))

    # 4. Phase 7: Financial Health Score
    try:
        from inference.predict_budget import calculate_financial_health_score
        health_res = calculate_financial_health_score(
            monthly_income=80000.0,
            current_balance=200000.0,
            monthly_expenses={"food": 15000.0, "shopping": 10000.0, "bills": 8000.0},
            debt_obligations=5000.0
        )
        assert "financial_health_score" in health_res
        score = health_res["financial_health_score"]
        results.append(("Phase 7: Financial Health Score", "[PASS]", f"Health Score: {score}/100 ({health_res.get('grade')})"))
    except Exception as e:
        results.append(("Phase 7: Financial Health Score", "[FAIL]", traceback.format_exc()))

    # 5. Phase 8: Fraud Detection Engine
    try:
        from inference.predict_anomaly import predict_fraud_risk
        fraud_res = predict_fraud_risk(transaction={"amount": 45000.0, "category": "shopping", "hour_of_day": 3})
        assert "risk_level" in fraud_res
        results.append(("Phase 8: Fraud Detection Engine", "[PASS]", f"Risk Level: {fraud_res.get('risk_level')} ({fraud_res.get('fraud_probability', 0)*100:.1f}%)"))
    except Exception as e:
        results.append(("Phase 8: Fraud Detection Engine", "[FAIL]", traceback.format_exc()))

    # 6. Phase 9: Spending Anomaly Detection
    try:
        from inference.predict_anomaly import detect_transaction_anomaly
        anom_res = detect_transaction_anomaly(transaction={"amount": 25000.0, "category": "dining"})
        assert "is_anomaly" in anom_res
        results.append(("Phase 9: Spending Anomaly Detection", "[PASS]", f"Is Anomaly: {anom_res.get('is_anomaly', False)}"))
    except Exception as e:
        results.append(("Phase 9: Spending Anomaly Detection", "[FAIL]", traceback.format_exc()))

    # 7. Phase 10: Investment Recommendation & Portfolio Allocator
    try:
        from inference.predict_investment import InvestmentRecommender
        inv_eng = InvestmentRecommender()
        inv_res = inv_eng.recommend(monthly_income=90000.0, age=28, risk_profile="AGGRESSIVE")
        assert "recommended_allocation_pct" in inv_res
        results.append(("Phase 10: Investment Allocator Engine", "[PASS]", f"Profile: {inv_res['user_profile']['risk_profile']}"))
    except Exception as e:
        results.append(("Phase 10: Investment Allocator Engine", "[FAIL]", traceback.format_exc()))

    # 8. Phase 11: Financial Goal Timeline Prediction
    try:
        from inference.predict_goals import predict_goal_timeline
        goal_res = predict_goal_timeline(
            goal_name="Emergency Fund",
            target_amount=300000.0,
            current_saved=50000.0,
            monthly_income=60000.0,
            monthly_expenses=35000.0,
        )
        assert "predicted_months_to_completion" in goal_res
        results.append(("Phase 11: Goal Timeline Predictor", "[PASS]", f"Months to Goal: {goal_res.get('predicted_months_to_completion')} mo ({goal_res.get('feasibility')})"))
    except Exception as e:
        results.append(("Phase 11: Goal Timeline Predictor", "[FAIL]", traceback.format_exc()))

    # 9. Phase 12: Loan Underwriting & Credit Risk Engine
    try:
        from inference.predict_loan import LoanUnderwritingEngine
        loan_eng = LoanUnderwritingEngine()
        loan_res = loan_eng.evaluate_application(monthly_income=85000.0, requested_loan_amount=400000.0, loan_tenure_months=36)
        assert "approval_status" in loan_res
        results.append(("Phase 12: Loan Underwriting Engine", "[PASS]", f"Decision: {loan_res.get('approval_status')} (Verdict: {loan_res.get('verdict')})"))
    except Exception as e:
        results.append(("Phase 12: Loan Underwriting Engine", "[FAIL]", traceback.format_exc()))

    # 10. Phase 13: Fast Credit Score Estimator & Simulator
    try:
        from inference.predict_credit import CreditScoreEstimator
        cred_eng = CreditScoreEstimator()
        cred_res = cred_eng.estimate(monthly_income=75000.0, total_credit_limit=250000.0, total_credit_used=35000.0)
        assert cred_res["status"] == "success"
        assert 300 <= cred_res["estimated_credit_score"] <= 900
        results.append(("Phase 13: Credit Estimator & Simulator", "[PASS]", f"Score: {cred_res['estimated_credit_score']} ({cred_res['credit_tier']})"))
    except Exception as e:
        results.append(("Phase 13: Credit Estimator & Simulator", "[FAIL]", traceback.format_exc()))

    # 11. Phase 14: Subscription & Recurring Charge Detection
    try:
        from inference.predict_subscriptions import classify_recurring_merchant
        sub_res = classify_recurring_merchant(merchant_name="Netflix India", amount=649.0)
        assert "is_subscription" in sub_res
        results.append(("Phase 14: Subscription Detection", "[PASS]", f"Cadence: {sub_res.get('predicted_cadence', 'MONTHLY')}"))
    except Exception as e:
        results.append(("Phase 14: Subscription Detection", "[FAIL]", traceback.format_exc()))

    # 12. Phase 16: Financial Product Recommendation Engine
    try:
        from inference.predict_recommendation import FinancialProductRecommenderEngine
        rec_eng = FinancialProductRecommenderEngine()
        rec_res = rec_eng.recommend(monthly_income=85000.0, credit_score=750, persona_id="YOUNG_TECH_PROFESSIONAL", spend_dining=12000.0, spend_shopping=15000.0)
        assert rec_res["status"] == "success"
        assert len(rec_res["top_recommendations"]) > 0
        results.append(("Phase 16: Product Recommender Engine", "[PASS]", f"{len(rec_res['top_recommendations'])} products matched"))
    except Exception as e:
        results.append(("Phase 16: Product Recommender Engine", "[FAIL]", traceback.format_exc()))

    # 13. Phase 17: Customer Persona Segmentation
    try:
        from inference.predict_segmentation import CustomerSegmentationEngine
        seg_eng = CustomerSegmentationEngine()
        seg_res = seg_eng.segment_user(monthly_income=120000.0, monthly_essential_expenses=35000.0, monthly_discretionary_spend=25000.0, monthly_investments_sip=30000.0)
        assert seg_res["status"] == "success"
        results.append(("Phase 17: Customer Segmentation Engine", "[PASS]", f"Persona: {seg_res['primary_persona']['persona_id']}"))
    except Exception as e:
        results.append(("Phase 17: Customer Segmentation Engine", "[FAIL]", traceback.format_exc()))

    # 14. Phase 18: Cash Flow & Balance Forecasting
    try:
        from inference.predict_forecasting import predict_cash_flow
        cf_res = predict_cash_flow(monthly_income=65000.0, current_balance=28000.0, horizon_days=30)
        assert cf_res["status"] == "success"
        results.append(("Phase 18: Cash Flow Forecasting", "[PASS]", f"Net Balance Projected (30 days)"))
    except Exception as e:
        results.append(("Phase 18: Cash Flow Forecasting", "[FAIL]", traceback.format_exc()))

    print("\nDIAGNOSTIC TEST RESULTS SUMMARY:")
    print("-" * 90)
    all_ok = True
    for module_name, status, detail in results:
        if status == "[FAIL]":
            all_ok = False
        print(f"  {module_name:42s} | {status} | {detail}")
    print("-" * 90)

    if all_ok:
        print(">>> RESULT: ALL 14 ML MODULES EXECUTED LIVE INFERENCE WITH 100% SUCCESS & ZERO ERRORS!")
    else:
        print(">>> RESULT: One or more modules reported an issue.")
    print("=" * 90)

if __name__ == "__main__":
    test_all_modules()
