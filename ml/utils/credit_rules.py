"""
Credit Scoring Domain Rules, 5-Pillar Architecture & What-If Simulation Engine for Phase 13: Credit Score Estimator.

Defines:
- 5-Pillar FICO/CIBIL credit scoring weighting
- Score range boundaries [300, 900] and credit tier taxonomy
- Non-linear domain feature engineering (Utilization curves, delinquency decay, inquiry friction)
- What-If Credit Score Simulation Engine for fast-track credit repair recommendations
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants & 5-Pillar Scoring Architecture
# ---------------------------------------------------------------------------

SCORE_MIN = 300
SCORE_MAX = 900

PILLAR_WEIGHTS = {
    "payment_history": 0.35,      # 35% Weight
    "credit_utilization": 0.30,   # 30% Weight
    "credit_history_age": 0.15,   # 15% Weight
    "credit_mix": 0.10,           # 10% Weight
    "new_inquiries": 0.10,        # 10% Weight
}

CREDIT_TIERS = {
    "EXCELLENT": {
        "range": (780, 900),
        "description": "Prime creditworthiness. Eligible for lowest interest rates and premium credit lines.",
        "risk_grade": "A+",
        "approval_odds": "VERY_HIGH",
    },
    "GOOD": {
        "range": (720, 779),
        "description": "Strong financial discipline. Consistently approved for most prime loan products.",
        "risk_grade": "A",
        "approval_odds": "HIGH",
    },
    "FAIR": {
        "range": (660, 719),
        "description": "Moderate credit standing. May require higher interest rates or co-signers.",
        "risk_grade": "B",
        "approval_odds": "MODERATE",
    },
    "POOR": {
        "range": (580, 659),
        "description": "Subprime tier. High default probability; requires structured debt rehabilitation.",
        "risk_grade": "C",
        "approval_odds": "LOW",
    },
    "VERY_POOR": {
        "range": (300, 579),
        "description": "Severe delinquency or default history. Immediate credit repair required.",
        "risk_grade": "D",
        "approval_odds": "VERY_LOW",
    },
}

RAW_FEATURE_COLUMNS_CREDIT = [
    "monthly_income",
    "total_credit_limit",
    "total_credit_used",
    "on_time_payment_pct",
    "missed_payments_count_2yr",
    "credit_history_years",
    "num_active_credit_lines",
    "secured_loans_count",
    "unsecured_loans_count",
    "hard_inquiries_last_6mo",
    "existing_total_debt",
]

ENGINEERED_NUMERICAL_FEATURES_CREDIT = [
    "monthly_income",
    "total_credit_limit",
    "total_credit_used",
    "on_time_payment_pct",
    "missed_payments_count_2yr",
    "credit_history_years",
    "num_active_credit_lines",
    "secured_loans_count",
    "unsecured_loans_count",
    "hard_inquiries_last_6mo",
    "existing_total_debt",
    "credit_utilization_ratio",
    "utilization_factor",
    "payment_integrity_index",
    "credit_maturity_score",
    "inquiry_friction_index",
    "credit_mix_diversity_ratio",
    "debt_to_income_stress",
    "log_income",
    "log_credit_limit",
    "log_debt",
]

TARGET_COLUMN_CREDIT = "credit_score"  # Bounded in [300, 900]

# ---------------------------------------------------------------------------
# Domain Feature Engineering Pipeline
# ---------------------------------------------------------------------------

def engineer_credit_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes non-linear 5-pillar credit indices, utilization curves, and interaction terms.
    """
    df = df.copy()
    inc = np.maximum(df["monthly_income"].values, 1.0)
    limit = np.maximum(df["total_credit_limit"].values, 0.0)
    used = np.maximum(df["total_credit_used"].values, 0.0)
    on_time = np.clip(df["on_time_payment_pct"].values / 100.0, 0.0, 1.0)
    missed = np.maximum(df["missed_payments_count_2yr"].values, 0)
    c_age = np.maximum(df["credit_history_years"].values, 0.1)
    secured = np.maximum(df["secured_loans_count"].values, 0)
    unsecured = np.maximum(df["unsecured_loans_count"].values, 0)
    inquiries = np.maximum(df["hard_inquiries_last_6mo"].values, 0)
    debt = np.maximum(df["existing_total_debt"].values, 0.0)

    # 1. Credit Utilization Ratio (Capped at 1.0 for normal, tracked raw)
    raw_util = used / np.maximum(limit, 1.0)
    df["credit_utilization_ratio"] = np.round(raw_util, 4)

    # Non-linear Utilization Factor (Exponential score penalty when util > 30% and > 50%)
    util_clipped = np.clip(raw_util, 0.0, 1.0)
    df["utilization_factor"] = np.round(1.0 - (util_clipped ** 1.35), 4)

    # 2. Payment Integrity Index (Exponential decay penalty per missed payment)
    delinquency_penalty = np.exp(-0.45 * missed)
    df["payment_integrity_index"] = np.round(on_time * delinquency_penalty, 4)

    # 3. Credit Maturity Score (Logarithmic longevity curve rewarding trade line age)
    df["credit_maturity_score"] = np.round(np.clip(np.log1p(c_age) / np.log1p(15.0), 0.0, 1.0), 4)

    # 4. Hard Inquiry Friction Index (Heavy penalty for > 2 hard credit pulls in 6 mo)
    df["inquiry_friction_index"] = np.round(np.clip(1.0 - (inquiries * 0.18), 0.0, 1.0), 4)

    # 5. Credit Mix Diversity Ratio (Optimal balance of secured vs unsecured)
    total_accounts = secured + unsecured
    mix_ratio = secured / np.maximum(total_accounts, 1)
    # Balanced mix (0.3 to 0.7) scores highest
    df["credit_mix_diversity_ratio"] = np.round(1.0 - np.abs(mix_ratio - 0.5) * 1.2, 4)

    # 6. Debt-to-Annual-Income Stress
    df["debt_to_income_stress"] = np.round(debt / (inc * 12.0), 4)

    # 7. Log-scale transforms for monetary magnitudes
    df["log_income"] = np.round(np.log1p(inc), 4)
    df["log_credit_limit"] = np.round(np.log1p(limit), 4)
    df["log_debt"] = np.round(np.log1p(debt), 4)

    return df


def get_credit_tier_info(score: int) -> Dict[str, Any]:
    """
    Returns taxonomy classification and risk grade for a given credit score.
    """
    score = int(np.clip(score, SCORE_MIN, SCORE_MAX))
    for tier_name, info in CREDIT_TIERS.items():
        if info["range"][0] <= score <= info["range"][1]:
            return {
                "tier": tier_name,
                "range": info["range"],
                "description": info["description"],
                "risk_grade": info["risk_grade"],
                "approval_odds": info["approval_odds"],
            }
    return CREDIT_TIERS["VERY_POOR"]


def compute_pillar_scores(
    utilization_ratio: float,
    on_time_pct: float,
    missed_count: int,
    history_years: float,
    secured_count: int,
    unsecured_count: int,
    inquiries_6mo: int,
) -> Dict[str, Any]:
    """
    Calculates normalized 0-100 scores for each of the 5 credit health pillars.
    """
    # 1. Payment History (35%)
    pay_score = max(0.0, (on_time_pct / 100.0) * np.exp(-0.40 * missed_count) * 100.0)

    # 2. Utilization (30%)
    if utilization_ratio <= 0.10:
        util_score = 100.0
    elif utilization_ratio <= 0.30:
        util_score = 100.0 - (utilization_ratio - 0.10) * 125.0  # 100 to 75
    elif utilization_ratio <= 0.50:
        util_score = 75.0 - (utilization_ratio - 0.30) * 175.0   # 75 to 40
    else:
        util_score = max(0.0, 40.0 - (utilization_ratio - 0.50) * 80.0)

    # 3. Credit Age (15%)
    age_score = min(100.0, (history_years / 10.0) * 100.0)

    # 4. Credit Mix (10%)
    total_acc = secured_count + unsecured_count
    if total_acc == 0:
        mix_score = 40.0
    elif secured_count > 0 and unsecured_count > 0:
        mix_score = 100.0
    elif secured_count > 0:
        mix_score = 80.0
    else:
        mix_score = 65.0

    # 5. Inquiries (10%)
    if inquiries_6mo == 0:
        inq_score = 100.0
    elif inquiries_6mo <= 2:
        inq_score = 85.0
    elif inquiries_6mo <= 4:
        inq_score = 55.0
    else:
        inq_score = max(10.0, 100.0 - (inquiries_6mo * 18.0))

    return {
        "payment_history": {"weight_pct": 35, "score_100": round(pay_score, 1), "rating": "EXCELLENT" if pay_score >= 90 else "NEEDS_WORK"},
        "credit_utilization": {"weight_pct": 30, "score_100": round(util_score, 1), "rating": "EXCELLENT" if util_score >= 80 else "HIGH_UTILIZATION"},
        "credit_history_age": {"weight_pct": 15, "score_100": round(age_score, 1), "rating": "MATURE" if age_score >= 70 else "BUILDING"},
        "credit_mix": {"weight_pct": 10, "score_100": round(mix_score, 1), "rating": "DIVERSIFIED" if mix_score >= 80 else "UNBALANCED"},
        "new_inquiries": {"weight_pct": 10, "score_100": round(inq_score, 1), "rating": "OPTIMAL" if inq_score >= 80 else "FREQUENT_PULLS"},
    }


# ---------------------------------------------------------------------------
# What-If Credit Score Simulation Engine
# ---------------------------------------------------------------------------

def simulate_credit_score_actions(
    current_score: int,
    total_limit: float,
    current_used: float,
    missed_count: int,
    inquiries_6mo: int,
) -> List[Dict[str, Any]]:
    """
    Simulates concrete actions and projects potential points gained on the credit score.
    """
    current_util = current_used / max(1.0, total_limit)
    simulations = []

    # Scenario 1: Pay down credit card balance to under 20%
    if current_util > 0.25:
        target_used = total_limit * 0.18
        reduction_amount = current_used - target_used
        potential_gain = int(min(65, (current_util - 0.18) * 110.0))
        simulations.append({
            "action": f"Pay down revolving credit card balance by INR {reduction_amount:,.0f}",
            "target_utilization_pct": 18.0,
            "projected_points_gain": f"+{potential_gain} points",
            "projected_new_score": min(SCORE_MAX, current_score + potential_gain),
            "estimated_timeframe": "30-60 days (Next Bureau Cycle)",
            "impact_tier": "HIGH_IMPACT",
        })

    # Scenario 2: Increase credit limit to organically lower utilization
    if current_util > 0.35 and total_limit < 500000:
        simulations.append({
            "action": "Request a credit limit enhancement on primary credit cards (no extra spending)",
            "projected_points_gain": "+15 to +25 points",
            "projected_new_score": min(SCORE_MAX, current_score + 20),
            "estimated_timeframe": "45 days",
            "impact_tier": "MODERATE_IMPACT",
        })

    # Scenario 3: 6 Consecutive Months of 100% On-Time Payments
    if missed_count > 0 or current_score < 750:
        simulations.append({
            "action": "Maintain 100% on-time automated repayments for the next 6 billing cycles",
            "projected_points_gain": "+25 to +40 points",
            "projected_new_score": min(SCORE_MAX, current_score + 32),
            "estimated_timeframe": "6 months",
            "impact_tier": "HIGH_IMPACT",
        })

    # Scenario 4: Freeze new hard credit inquiries
    if inquiries_6mo >= 3:
        simulations.append({
            "action": "Avoid applying for new personal loans or credit cards for 6 months (allow hard pulls to age)",
            "projected_points_gain": "+12 to +18 points",
            "projected_new_score": min(SCORE_MAX, current_score + 15),
            "estimated_timeframe": "3-6 months",
            "impact_tier": "MODERATE_IMPACT",
        })

    return simulations
