"""
Banking Domain Rules, Credit Underwriting Policies & Feature Utilities for Phase 12: Loan Eligibility.

Defines:
- Loan purpose interest rates, tenure boundaries, and banking FOIR ceilings
- Exact non-linear EMI amortization formula and safe borrowing capacity solver
- Credit health score tiering (CIBIL/FICO 300 to 900)
- Advanced domain feature engineering for credit risk and default probability modeling
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Loan Products & Underwriting Standards
# ---------------------------------------------------------------------------

LOAN_PURPOSE_POLICIES = {
    "HOME_LOAN": {
        "base_interest_rate_pct": 8.50,
        "max_tenure_months": 240,  # 20 years
        "min_tenure_months": 36,
        "max_foir_limit": 0.55,    # Up to 55% FOIR for secured home mortgages
        "min_credit_score": 650,
        "collateral_type": "SECURED",
    },
    "AUTO_VEHICLE_LOAN": {
        "base_interest_rate_pct": 9.25,
        "max_tenure_months": 84,   # 7 years
        "min_tenure_months": 12,
        "max_foir_limit": 0.50,
        "min_credit_score": 630,
        "collateral_type": "SECURED",
    },
    "PERSONAL_LOAN": {
        "base_interest_rate_pct": 12.50,
        "max_tenure_months": 60,   # 5 years
        "min_tenure_months": 6,
        "max_foir_limit": 0.45,    # Stricter 45% FOIR for unsecured debt
        "min_credit_score": 680,
        "collateral_type": "UNSECURED",
    },
    "EDUCATION_LOAN": {
        "base_interest_rate_pct": 9.75,
        "max_tenure_months": 120,  # 10 years
        "min_tenure_months": 12,
        "max_foir_limit": 0.50,
        "min_credit_score": 620,
        "collateral_type": "SEMI_SECURED",
    },
    "BUSINESS_EXPANSION": {
        "base_interest_rate_pct": 11.00,
        "max_tenure_months": 120,  # 10 years
        "min_tenure_months": 12,
        "max_foir_limit": 0.50,
        "min_credit_score": 670,
        "collateral_type": "HYBRID",
    },
}

EMPLOYMENT_STABILITY_WEIGHTS = {
    "SALARIED_GOVT_MNC": 1.00,
    "SALARIED_PRIVATE": 0.85,
    "SELF_EMPLOYED_PROFESSIONAL": 0.80,
    "BUSINESS_OWNER": 0.75,
    "GIG_FREELANCER": 0.55,
    "UNEMPLOYED": 0.05,
}

CREDIT_SCORE_TIERS = {
    "PRIME_EXCELLENT": {"range": (750, 900), "rate_discount_pct": -0.75, "risk_tier": "LOW_RISK"},
    "GOOD": {"range": (700, 749), "rate_discount_pct": 0.00, "risk_tier": "LOW_RISK"},
    "NEAR_PRIME_FAIR": {"range": (650, 699), "rate_discount_pct": 0.75, "risk_tier": "MODERATE_RISK"},
    "SUBPRIME_POOR": {"range": (300, 649), "rate_discount_pct": 2.50, "risk_tier": "HIGH_RISK"},
}

RAW_FEATURE_COLUMNS_LOAN = [
    "monthly_income",
    "requested_loan_amount",
    "loan_tenure_months",
    "loan_purpose",
    "existing_monthly_emi",
    "existing_debt_total",
    "credit_score",
    "employment_type",
    "employment_tenure_years",
    "monthly_expenses",
    "liquid_savings",
]

ENGINEERED_NUMERICAL_FEATURES_LOAN = [
    "monthly_income",
    "requested_loan_amount",
    "loan_tenure_months",
    "existing_monthly_emi",
    "existing_debt_total",
    "credit_score",
    "employment_tenure_years",
    "monthly_expenses",
    "liquid_savings",
    "calculated_emi",
    "foir_ratio",
    "loan_to_annual_income",
    "disposable_cushion",
    "repayment_capacity_multiple",
    "liquid_reserve_coverage",
    "employment_stability_index",
    "credit_health_index",
    "log_income",
    "log_loan_amount",
    "log_savings",
]

ENGINEERED_CATEGORICAL_FEATURES_LOAN = [
    "loan_purpose",
    "employment_type",
]

TARGET_COLUMN_LOAN = "is_eligible"  # 1 = Approved / Eligible, 0 = Ineligible / High Risk

# ---------------------------------------------------------------------------
# Amortization, Safe Limit & Underwriting Math
# ---------------------------------------------------------------------------

def calculate_monthly_emi(principal: float, annual_rate_pct: float, tenure_months: int) -> float:
    """
    Computes exact monthly amortized EMI using standard banking formula:
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    if annual_rate_pct <= 0:
        return round(float(principal / tenure_months), 2)

    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    pow_factor = (1.0 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * pow_factor / (pow_factor - 1.0)
    return round(float(emi), 2)


def calculate_max_safe_borrowing_limit(
    monthly_income: float,
    existing_monthly_emi: float,
    monthly_expenses: float,
    annual_rate_pct: float,
    tenure_months: int,
    max_foir: float = 0.50,
) -> float:
    """
    Calculates the maximum loan principal amount that the applicant can safely service
    under a strict FOIR (Fixed Obligation to Income Ratio) ceiling.
    """
    max_allowable_total_emi = monthly_income * max_foir
    max_allowable_new_emi = max(0.0, max_allowable_total_emi - existing_monthly_emi)

    if max_allowable_new_emi <= 0 or tenure_months <= 0:
        return 0.0

    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    if monthly_rate <= 0:
        return round(float(max_allowable_new_emi * tenure_months), 2)

    pow_factor = (1.0 + monthly_rate) ** tenure_months
    principal = max_allowable_new_emi * (pow_factor - 1.0) / (monthly_rate * pow_factor)
    return round(float(principal), 2)


def get_effective_interest_rate(loan_purpose: str, credit_score: int) -> float:
    """
    Computes risk-adjusted annual interest rate based on loan collateral and credit score tier.
    """
    policy = LOAN_PURPOSE_POLICIES.get(loan_purpose, LOAN_PURPOSE_POLICIES["PERSONAL_LOAN"])
    base_rate = policy["base_interest_rate_pct"]

    rate_adjustment = 0.0
    for tier_info in CREDIT_SCORE_TIERS.values():
        if tier_info["range"][0] <= credit_score <= tier_info["range"][1]:
            rate_adjustment = tier_info["rate_discount_pct"]
            break

    return round(float(max(6.5, base_rate + rate_adjustment)), 2)


# ---------------------------------------------------------------------------
# Domain Feature Engineering Pipeline
# ---------------------------------------------------------------------------

def engineer_loan_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts high-signal financial indicators and non-linear risk indices.
    """
    df = df.copy()
    inc = np.maximum(df["monthly_income"].values, 1.0)
    req_loan = np.maximum(df["requested_loan_amount"].values, 0.0)
    tenure = np.maximum(df["loan_tenure_months"].values, 1)
    existing_emi = np.maximum(df["existing_monthly_emi"].values, 0.0)
    expenses = np.maximum(df["monthly_expenses"].values, 0.0)
    savings = np.maximum(df["liquid_savings"].values, 0.0)
    cscore = df["credit_score"].values
    tenure_yrs = df["employment_tenure_years"].values
    emp_types = df["employment_type"].values
    purposes = df["loan_purpose"].values

    # 1. Compute exact proposed EMI for each record
    emis = []
    for i in range(len(df)):
        rate = get_effective_interest_rate(purposes[i], int(cscore[i]))
        emi = calculate_monthly_emi(float(req_loan[i]), rate, int(tenure[i]))
        emis.append(emi)
    
    calc_emi = np.array(emis)
    df["calculated_emi"] = np.round(calc_emi, 2)

    # 2. Fixed Obligation to Income Ratio (FOIR)
    total_emi = existing_emi + calc_emi
    df["foir_ratio"] = np.round(total_emi / inc, 4)

    # 3. Loan-to-Annual-Income Ratio (LTV Burden)
    df["loan_to_annual_income"] = np.round(req_loan / (inc * 12.0), 4)

    # 4. Net Disposable Buffer Post-EMI
    df["disposable_cushion"] = np.round(inc - expenses - total_emi, 2)

    # 5. Repayment Capacity Multiple
    net_free_cash = np.maximum(0.0, inc - expenses)
    df["repayment_capacity_multiple"] = np.round(net_free_cash / np.maximum(calc_emi, 1.0), 4)

    # 6. Liquid Emergency Reserve Coverage (in months of proposed EMI)
    df["liquid_reserve_coverage"] = np.round(savings / np.maximum(calc_emi, 1.0), 4)

    # 7. Employment Stability Index
    emp_weights = np.array([EMPLOYMENT_STABILITY_WEIGHTS.get(et, 0.60) for et in emp_types])
    df["employment_stability_index"] = np.round(emp_weights * np.clip(tenure_yrs / 5.0, 0.2, 1.5), 4)

    # 8. Credit Health Index (Normalized from 300-900 to 0.0-1.0)
    df["credit_health_index"] = np.round(np.clip((cscore - 300) / 600.0, 0.0, 1.0), 4)

    # 9. Log-Scaled Transformations for Monetary Magnitudes
    df["log_income"] = np.round(np.log1p(inc), 4)
    df["log_loan_amount"] = np.round(np.log1p(req_loan), 4)
    df["log_savings"] = np.round(np.log1p(savings), 4)

    return df
