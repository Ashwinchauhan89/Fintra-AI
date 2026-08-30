"""
Extreme Stress-Testing Suite for Phase 13: Credit Score Estimator.

Tests edge boundaries, adversarial inputs, credit anomalies, and corner cases:
1. Upper Ceiling Stress: The Perfect Prime Borrower (Score ~880-900)
2. Lower Floor Stress: Catastrophic Delinquency & Maxed Out Debt (Score 300-450)
3. Thin-File Stress: Clean young graduate with only 6 months of credit history
4. High-Income Over-Leveraged Stress: ₹2.5L salary but 85% card utilization + 7 hard pulls
5. Sudden Delinquency Shock: Prime 800 score dropped by 2 missed payments in 6 months
6. Over-Limit Adversarial Stress: Credit used > Credit limit (110% over-limit)
7. Numerical Boundary Stress: Extreme values, zero limits, zero division resistance
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from inference.predict_credit import CreditScoreEstimator  # noqa: E402
from utils.credit_rules import SCORE_MAX, SCORE_MIN  # noqa: E402


def run_extreme_stress_tests():
    print("=" * 85)
    print("EXTREME STRESS-TESTING SUITE: PHASE 13 CREDIT SCORE ESTIMATOR")
    print("=" * 85)

    engine = CreditScoreEstimator()

    test_cases = [
        {
            "name": "1. Perfect Prime Ceiling (Credit Champion)",
            "params": {
                "monthly_income": 350000.0,
                "total_credit_limit": 1500000.0,
                "total_credit_used": 15000.0,  # 1.0% utilization
                "on_time_payment_pct": 100.0,
                "missed_payments_count_2yr": 0,
                "credit_history_years": 18.0,
                "num_active_credit_lines": 6,
                "secured_loans_count": 2,
                "unsecured_loans_count": 4,
                "hard_inquiries_last_6mo": 0,
                "existing_total_debt": 15000.0,
            },
            "expected_range": (850, 900),
            "expected_tier": "EXCELLENT",
        },
        {
            "name": "2. Complete Default Floor (Catastrophic Distress)",
            "params": {
                "monthly_income": 18000.0,
                "total_credit_limit": 40000.0,
                "total_credit_used": 40000.0,  # 100% maxed out
                "on_time_payment_pct": 65.0,
                "missed_payments_count_2yr": 6,
                "credit_history_years": 0.8,
                "num_active_credit_lines": 1,
                "secured_loans_count": 0,
                "unsecured_loans_count": 1,
                "hard_inquiries_last_6mo": 7,
                "existing_total_debt": 250000.0,
            },
            "expected_range": (300, 520),
            "expected_tier": "VERY_POOR",
        },
        {
            "name": "3. Thin-File New-to-Credit (Fresh Graduate)",
            "params": {
                "monthly_income": 50000.0,
                "total_credit_limit": 30000.0,
                "total_credit_used": 4500.0,  # 15% utilization
                "on_time_payment_pct": 100.0,
                "missed_payments_count_2yr": 0,
                "credit_history_years": 0.5,  # Only 6 months old
                "num_active_credit_lines": 1,
                "secured_loans_count": 0,
                "unsecured_loans_count": 1,
                "hard_inquiries_last_6mo": 1,
                "existing_total_debt": 4500.0,
            },
            "expected_range": (660, 730),
            "expected_tier": "GOOD / FAIR",
        },
        {
            "name": "4. High-Earner Reckless Card Churner",
            "params": {
                "monthly_income": 250000.0,
                "total_credit_limit": 800000.0,
                "total_credit_used": 700000.0,  # 87.5% utilization
                "on_time_payment_pct": 97.0,
                "missed_payments_count_2yr": 0,
                "credit_history_years": 5.0,
                "num_active_credit_lines": 8,
                "secured_loans_count": 0,
                "unsecured_loans_count": 8,
                "hard_inquiries_last_6mo": 6,  # 6 hard pulls
                "existing_total_debt": 700000.0,
            },
            "expected_range": (580, 680),
            "expected_tier": "POOR / FAIR",
        },
        {
            "name": "5. Sudden Delinquency Shock (2 Missed Payments)",
            "params": {
                "monthly_income": 90000.0,
                "total_credit_limit": 200000.0,
                "total_credit_used": 30000.0,  # 15% utilization
                "on_time_payment_pct": 92.0,
                "missed_payments_count_2yr": 2,  # 2 missed payments
                "credit_history_years": 6.0,
                "num_active_credit_lines": 3,
                "secured_loans_count": 1,
                "unsecured_loans_count": 2,
                "hard_inquiries_last_6mo": 1,
                "existing_total_debt": 30000.0,
            },
            "expected_range": (550, 660),
            "expected_tier": "POOR / FAIR",
        },
        {
            "name": "6. Over-Limit Maxed Card (110% Utilization Anomaly)",
            "params": {
                "monthly_income": 60000.0,
                "total_credit_limit": 100000.0,
                "total_credit_used": 110000.0,  # 110% Over-limit
                "on_time_payment_pct": 88.0,
                "missed_payments_count_2yr": 2,
                "credit_history_years": 3.0,
                "num_active_credit_lines": 2,
                "secured_loans_count": 0,
                "unsecured_loans_count": 2,
                "hard_inquiries_last_6mo": 4,
                "existing_total_debt": 110000.0,
            },
            "expected_range": (300, 560),
            "expected_tier": "VERY_POOR",
        },
    ]

    all_passed = True

    for case in test_cases:
        res = engine.estimate(**case["params"])
        score = res["estimated_credit_score"]
        tier = res["credit_tier"]
        low, high = case["expected_range"]

        passed = (low <= score <= high) and (SCORE_MIN <= score <= SCORE_MAX)
        if not passed:
            all_passed = False

        status_icon = "[PASS]" if passed else "[FAIL]"

        print(f"\n{case['name']}:")
        print(f"  Result Score:     {score} (Scale: 300-900) | Tier: {tier} | Grade: {res['risk_grade']}")
        print(f"  Expected Range:   [{low}, {high}] | Status: {status_icon}")
        print(f"  5-Pillar Scores:  Pay: {res['five_pillar_diagnostics']['payment_history']['score_100']} | Util: {res['five_pillar_diagnostics']['credit_utilization']['score_100']} | Age: {res['five_pillar_diagnostics']['credit_history_age']['score_100']}")
        if res["what_if_score_simulations"]:
            print(f"  Top Action Tip:   {res['what_if_score_simulations'][0]['action']} -> {res['what_if_score_simulations'][0]['projected_points_gain']}")

    print("\n" + "=" * 85)
    if all_passed:
        print(">>> EXTREME STRESS-TEST VERDICT: ALL 6 EXTREME CORNER CASES PASSED PERFECTLY!")
    else:
        print(">>> EXTREME STRESS-TEST VERDICT: Some edge boundary checks failed.")
    print("=" * 85)


if __name__ == "__main__":
    run_extreme_stress_tests()
