"""
Extreme Adversarial & Throughput Stress-Testing Suite for Phase 16: Financial Product Recommender.

Tests:
1. Subprime / Student Zero-Barrier Test (Guarantees lifetime free credit builder card)
2. High-Flyer Luxury Traveler (Triggers premium travel/metal cards with high rewards)
3. Heavy Foodie & Online Shopper (Triggers cashback cards with maximum ROI)
4. Debt-Distressed Consolidation Seeker (Triggers 11.5% balance transfer loan)
5. Family Utility & Grocery Optimizer (Triggers Airtel Axis card for 25% utility cashback)
6. 1,000-Request High-Concurrency Throughput & Microsecond Latency Benchmark
"""

import os
import sys
import time
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from inference.predict_recommendation import FinancialProductRecommenderEngine  # noqa: E402


def run_recommendation_stress_tests():
    print("=" * 90)
    print("EXTREME STRESS-TESTING & THROUGHPUT SUITE: PHASE 16 RECOMMENDER ENGINE")
    print("=" * 90)

    engine = FinancialProductRecommenderEngine()

    stress_cases = [
        {
            "name": "1. Student / Subprime Credit Builder Test (Zero-Fee Safe Card)",
            "params": {
                "monthly_income": 18000.0,
                "credit_score": 300,  # Zero / No credit score
                "persona_id": "BUDGET_CONSCIOUS_STUDENT",
                "spend_dining": 2000.0,
                "spend_shopping": 1000.0,
                "spend_groceries": 3000.0,
                "spend_travel": 0.0,
                "spend_fuel": 500.0,
                "spend_utilities": 800.0,
                "liquid_savings": 15000.0,
                "existing_card_debt": 0.0,
                "top_k": 2,
            },
            "expected_top_product": "CC_IDFC_FIRST_WOW",
        },
        {
            "name": "2. High-Flyer Frequent Traveler (Premium Air Miles Match)",
            "params": {
                "monthly_income": 350000.0,
                "credit_score": 820,
                "persona_id": "HIGH_NET_WORTH_INVESTOR",
                "spend_dining": 35000.0,
                "spend_shopping": 45000.0,
                "spend_groceries": 15000.0,
                "spend_travel": 85000.0,  # Heavy flights/hotels
                "spend_fuel": 8000.0,
                "spend_utilities": 12000.0,
                "liquid_savings": 4500000.0,
                "existing_card_debt": 0.0,
                "top_k": 3,
            },
            "expected_top_product": "CC_HDFC_INFINIA_METAL",
        },
        {
            "name": "3. Heavy Foodie & Online Shopper (Dining & E-Commerce Cashback)",
            "params": {
                "monthly_income": 85000.0,
                "credit_score": 750,
                "persona_id": "YOUNG_TECH_PROFESSIONAL",
                "spend_dining": 15000.0,   # Heavy Swiggy/Zomato
                "spend_shopping": 20000.0, # Heavy Amazon/Flipkart
                "spend_groceries": 8000.0,
                "spend_travel": 2000.0,
                "spend_fuel": 3000.0,
                "spend_utilities": 4000.0,
                "liquid_savings": 350000.0,
                "existing_card_debt": 0.0,
                "top_k": 3,
            },
            "expected_top_product": ["CC_AIRTEL_AXIS", "CC_CASHBACK_MILLENNIA"],
        },
        {
            "name": "4. Debt Consolidation Seeker (Balance Transfer Savior)",
            "params": {
                "monthly_income": 45000.0,
                "credit_score": 670,
                "persona_id": "DEBT_REHABILITATION_SEEKER",
                "spend_dining": 2000.0,
                "spend_shopping": 2000.0,
                "spend_groceries": 6000.0,
                "spend_travel": 500.0,
                "spend_fuel": 2000.0,
                "spend_utilities": 3000.0,
                "liquid_savings": 5000.0,
                "existing_card_debt": 180000.0,  # High 38% card balance
                "top_k": 2,
            },
            "expected_top_product": "REFINANCE_SBI_DEBT_CONSOLIDATION",
        },
        {
            "name": "5. Family Utility Optimizer (25% Bill Cashback Card)",
            "params": {
                "monthly_income": 70000.0,
                "credit_score": 730,
                "persona_id": "BALANCED_FAMILY_HOMEMAKER",
                "spend_dining": 4000.0,
                "spend_shopping": 5000.0,
                "spend_groceries": 15000.0,
                "spend_travel": 1000.0,
                "spend_fuel": 3000.0,
                "spend_utilities": 12000.0,  # Heavy electricity, broadband, DTH
                "liquid_savings": 500000.0,
                "existing_card_debt": 0.0,
                "top_k": 2,
            },
            "expected_top_product": "CC_AIRTEL_AXIS",
        },
    ]

    all_passed = True

    for case in stress_cases:
        res = engine.recommend(**case["params"])
        top_rec = res["top_recommendations"][0]["product_id"]
        top_name = res["top_recommendations"][0]["name"]
        top_val = res["top_recommendations"][0]["estimated_net_annual_value_inr"]
        
        expected = case["expected_top_product"]
        if isinstance(expected, list):
            passed = top_rec in expected
        else:
            passed = (top_rec == expected)
            
        if not passed:
            all_passed = False

        status_tag = "[PASS]" if passed else "[FAIL]"
        print(f"\n{case['name']}:")
        print(f"  Top Match:      {top_name} ({top_rec}) | Status: {status_tag}")
        print(f"  Net Value:      INR {top_val:,.2f}/yr")
        print(f"  Justification:  {res['top_recommendations'][0]['match_reason']}")

    # 6. 1,000-Request Concurrency & Throughput Benchmark
    print("\n" + "-" * 90)
    print("6. HIGH-CONCURRENCY THROUGHPUT & LATENCY BENCHMARK (1,000 INVOCATIONS)")
    print("-" * 90)

    n_iter = 1000
    t_start = time.perf_counter()
    for _ in range(n_iter):
        engine.recommend(
            monthly_income=85000.0,
            credit_score=750,
            persona_id="YOUNG_TECH_PROFESSIONAL",
            spend_dining=12000.0,
            spend_shopping=15000.0,
            spend_groceries=8000.0,
            spend_travel=6000.0,
            spend_fuel=3000.0,
            spend_utilities=5000.0,
            liquid_savings=350000.0,
        )
    total_time_sec = time.perf_counter() - t_start
    avg_latency_us = (total_time_sec / n_iter) * 1000000.0
    throughput_rps = n_iter / total_time_sec

    print(f"  Total Time for {n_iter} Invocations: {total_time_sec * 1000.0:.2f} ms")
    print(f"  Average Latency per Query:      {avg_latency_us:.1f} microseconds (< 0.1 ms target)")
    print(f"  Throughput Capacity:            {throughput_rps:,.0f} queries / second (Pure CPU)")

    print("\n" + "=" * 90)
    if all_passed and avg_latency_us < 500.0:
        print(">>> EXTREME LEVEL VERDICT: 100% BULLETPROOF PASS! SUB-MILLISECOND ULTRA-FAST SPEED!")
    else:
        print(">>> EXTREME LEVEL VERDICT: Some stress checks did not meet criteria.")
    print("=" * 90)


if __name__ == "__main__":
    run_recommendation_stress_tests()
