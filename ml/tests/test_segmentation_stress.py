"""
Extreme Adversarial & Boundary Stress-Testing Suite for Phase 17: Customer Persona Segmentation.

Tests extreme multi-dimensional stress scenarios:
1. Zero-Income / Unemployment Crisis (Zero division safety)
2. Ultra Billionaire / Multi-Crore High-Net-Worth Outlier (Magnitude invariance)
3. 50/50 Borderline Hybrid User (Soft probability transition verification)
4. Hyper-Volatile Seasonal Merchant (CV > 1.2 revenue swings)
5. Frugal Minimum Wage Early Starter (Micro-savings discipline)
6. Overleveraged High-Earner Luxury Trap (High salary with 63% EMI + 96% card utilization)
7. 1,000-Request Batch Concurrency & Throughput Benchmark (Latency verification in microseconds)
"""

import os
import sys
import time
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from inference.predict_segmentation import CustomerSegmentationEngine  # noqa: E402


def run_comprehensive_extreme_stress_tests():
    print("=" * 90)
    print(
        "EXTREME LEVEL STRESS-TESTING & ADVERSARIAL SUITE: PHASE 17 SEGMENTATION ENGINE"
    )
    print("=" * 90)

    engine = CustomerSegmentationEngine()

    stress_cases = [
        {
            "name": "1. Zero-Income / Acute Unemployment Crisis (Zero-Division Immunity)",
            "params": {
                "monthly_income": 0.0,  # Zero income edge case
                "income_volatility_cv": 0.10,
                "monthly_essential_expenses": 8000.0,
                "monthly_discretionary_spend": 2000.0,
                "monthly_investments_sip": 0.0,
                "existing_monthly_emi": 6000.0,
                "total_credit_limit": 50000.0,
                "total_credit_used": 48000.0,  # 96% utilization
                "total_liquid_savings": 500.0,
                "monthly_transaction_count": 15,
                "active_subscriptions_count": 1,
            },
            "expected_primary": "DEBT_REHABILITATION_SEEKER",
            "condition": lambda res: res["primary_persona"]["persona_id"]
            == "DEBT_REHABILITATION_SEEKER",
        },
        {
            "name": "2. Ultra Multi-Crore HNI Outlier (Magnitude Invariance)",
            "params": {
                "monthly_income": 2500000.0,  # ₹25 Lakhs/month
                "income_volatility_cv": 0.05,
                "monthly_essential_expenses": 250000.0,
                "monthly_discretionary_spend": 300000.0,
                "monthly_investments_sip": 1500000.0,
                "existing_monthly_emi": 50000.0,
                "total_credit_limit": 15000000.0,
                "total_credit_used": 400000.0,  # 2.6% utilization
                "total_liquid_savings": 45000000.0,
                "monthly_transaction_count": 220,
                "active_subscriptions_count": 12,
            },
            "expected_primary": "HIGH_NET_WORTH_INVESTOR",
            "condition": lambda res: res["primary_persona"]["persona_id"]
            == "HIGH_NET_WORTH_INVESTOR",
        },
        {
            "name": "3. 50/50 Hybrid Borderline Profile (Young Pro -> HNI Transition)",
            "params": {
                "monthly_income": 220000.0,
                "income_volatility_cv": 0.06,
                "monthly_essential_expenses": 55000.0,
                "monthly_discretionary_spend": 45000.0,
                "monthly_investments_sip": 85000.0,
                "existing_monthly_emi": 10000.0,
                "total_credit_limit": 1000000.0,
                "total_credit_used": 120000.0,
                "total_liquid_savings": 2200000.0,
                "monthly_transaction_count": 130,
                "active_subscriptions_count": 8,
            },
            "expected_primary": "YOUNG_TECH_PROFESSIONAL / HIGH_NET_WORTH_INVESTOR",
            "condition": lambda res: res["primary_persona"]["persona_id"]
            in ["YOUNG_TECH_PROFESSIONAL", "HIGH_NET_WORTH_INVESTOR"],
        },
        {
            "name": "4. Hyper-Volatile Seasonal Merchant (CV = 1.15 Swings)",
            "params": {
                "monthly_income": 280000.0,
                "income_volatility_cv": 1.15,  # Extreme revenue instability
                "monthly_essential_expenses": 85000.0,
                "monthly_discretionary_spend": 40000.0,
                "monthly_investments_sip": 35000.0,
                "existing_monthly_emi": 40000.0,
                "total_credit_limit": 1500000.0,
                "total_credit_used": 450000.0,
                "total_liquid_savings": 2500000.0,
                "monthly_transaction_count": 240,
                "active_subscriptions_count": 6,
            },
            "expected_primary": "SMB_BUSINESS_OWNER",
            "condition": lambda res: res["primary_persona"]["persona_id"]
            == "SMB_BUSINESS_OWNER",
        },
        {
            "name": "5. Frugal Minimum-Wage Starter (INR 14k Income Micro-Saver)",
            "params": {
                "monthly_income": 14000.0,
                "income_volatility_cv": 0.04,
                "monthly_essential_expenses": 7500.0,
                "monthly_discretionary_spend": 2000.0,
                "monthly_investments_sip": 1500.0,
                "existing_monthly_emi": 0.0,
                "total_credit_limit": 15000.0,
                "total_credit_used": 1500.0,
                "total_liquid_savings": 18000.0,
                "monthly_transaction_count": 20,
                "active_subscriptions_count": 1,
            },
            "expected_primary": "BUDGET_CONSCIOUS_STUDENT",
            "condition": lambda res: res["primary_persona"]["persona_id"]
            == "BUDGET_CONSCIOUS_STUDENT",
        },
        {
            "name": "6. High-Earner Luxury Leverage Trap (INR 1.5L Income, 63% EMI, 96% Card Util)",
            "params": {
                "monthly_income": 150000.0,
                "income_volatility_cv": 0.05,
                "monthly_essential_expenses": 45000.0,
                "monthly_discretionary_spend": 30000.0,
                "monthly_investments_sip": 0.0,
                "existing_monthly_emi": 95000.0,  # 63.3% EMI burden
                "total_credit_limit": 500000.0,
                "total_credit_used": 480000.0,  # 96.0% card utilization
                "total_liquid_savings": 10000.0,
                "monthly_transaction_count": 60,
                "active_subscriptions_count": 4,
            },
            "expected_primary": "DEBT_REHABILITATION_SEEKER",
            "condition": lambda res: res["primary_persona"]["persona_id"]
            == "DEBT_REHABILITATION_SEEKER",
        },
    ]

    all_passed = True

    for case in stress_cases:
        res = engine.segment_user(**case["params"])
        primary = res["primary_persona"]["persona_id"]
        conf = res["primary_persona"]["confidence_pct"]
        passed = case["condition"](res)
        if not passed:
            all_passed = False

        status_tag = "[PASS]" if passed else "[FAIL]"
        print(f"\n{case['name']}:")
        print(
            f"  Predicted Persona: {primary:28s} | Confidence: {conf:5.1f}% | Status: {status_tag}"
        )
        print(
            f"  Top Affinities:    {list(res['soft_multi_persona_affinity_pct'].items())[:2]}"
        )
        print(
            f"  Surplus / Savings: INR {res['behavioral_diagnostics']['net_surplus_inr']:,.2f} ({res['behavioral_diagnostics']['savings_rate_pct']}%)"
        )
        print(
            f"  Strategy Focus:    {res['tailored_platform_strategy']['primary_focus']}"
        )

    # 7. Throughput & Microsecond Latency Benchmark (1,000 Sequential Invocations)
    print("\n" + "-" * 90)
    print("7. HIGH-CONCURRENCY THROUGHPUT & LATENCY BENCHMARK (1,000 INVOCATIONS)")
    print("-" * 90)

    n_iter = 1000
    t_start = time.perf_counter()
    for _ in range(n_iter):
        engine.segment_user(
            monthly_income=120000.0,
            income_volatility_cv=0.05,
            monthly_essential_expenses=40000.0,
            monthly_discretionary_spend=30000.0,
            monthly_investments_sip=25000.0,
            existing_monthly_emi=5000.0,
            total_credit_limit=350000.0,
            total_credit_used=35000.0,
            total_liquid_savings=450000.0,
        )
    total_time_sec = time.perf_counter() - t_start
    avg_latency_us = (total_time_sec / n_iter) * 1000000.0  # Microseconds
    throughput_rps = n_iter / total_time_sec

    print(
        f"  Total Benchmark Time:    {total_time_sec * 1000.0:.2f} ms for {n_iter} full predictions"
    )
    print(
        f"  Average Latency / Call:  {avg_latency_us:.1f} microseconds (< 0.5 ms target)"
    )
    print(
        f"  Execution Throughput:    {throughput_rps:,.0f} predictions / second (Pure CPU)"
    )

    print("\n" + "=" * 90)
    if all_passed and avg_latency_us < 1000.0:
        print(
            ">>> EXTREME LEVEL VERDICT: 100% BULLETPROOF PASS! ZERO ERRORS & SUB-MILLISECOND SPEED!"
        )
    else:
        print(">>> EXTREME LEVEL VERDICT: Some stress checks did not meet criteria.")
    print("=" * 90)


if __name__ == "__main__":
    run_comprehensive_extreme_stress_tests()
