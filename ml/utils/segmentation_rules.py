"""
Customer Persona Segmentation Domain Rules & Multi-Affinity Engine for Phase 17.

Defines:
- 6 FinTech Customer Persona Archetypes (Student, Young Pro, Family, HNI Investor, SMB Owner, Debt Rehabilitator)
- Domain feature engineering pipeline (50/30/20 ratios, surplus allocation, income volatility, debt stress)
- Vectorized Softmax Distance Affinity calculator for multi-persona soft probabilities
- Tailored financial strategy matrix across budgeting, investing, and lending
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants & 6 Persona Archetypes Taxonomy
# ---------------------------------------------------------------------------

PERSONA_ARCHETYPES = {
    0: {
        "id": "BUDGET_CONSCIOUS_STUDENT",
        "name": "Budget-Conscious Student & Early Saver",
        "tagline": "Disciplined starter building credit and financial foundation.",
        "risk_tolerance": "CONSERVATIVE",
        "primary_focus": "Micro-budgeting, student discounts, entry-level credit building",
        "budget_strategy": "Zero-based budgeting; cap dining/entertainment to 15% of allowance",
        "investment_strategy": "Micro-SIP in index funds (INR 500-1,000/mo), high-yield digital savings",
        "credit_strategy": "Secured / Student credit card with low limit to establish on-time CIBIL history",
    },
    1: {
        "id": "YOUNG_TECH_PROFESSIONAL",
        "name": "Young Tech Professional & High-Growth Aspirer",
        "tagline": "High earning power with aggressive wealth accumulation goals.",
        "risk_tolerance": "AGGRESSIVE",
        "primary_focus": "Equity compounding, tax optimization (80C/NPS), lifestyle balancing",
        "budget_strategy": "Automated 50/30/20 rule: route 30%+ surplus directly into automated investments on payday",
        "investment_strategy": "Aggressive equity mutual funds (70%), international ETFs (10%), crypto/reits (10%), debt (10%)",
        "credit_strategy": "Premium rewards credit cards for travel and dining cashbacks; keep utilization < 20%",
    },
    2: {
        "id": "BALANCED_FAMILY_HOMEMAKER",
        "name": "Balanced Mid-Career Family Homemaker",
        "tagline": "Stability-first provider managing family obligations and long-term milestones.",
        "risk_tolerance": "BALANCED",
        "primary_focus": "Emergency buffer (6mo), child education goals, term & health insurance",
        "budget_strategy": "Strict essential expense tracking (rent, groceries, school fees); zero unbudgeted discretionary leaks",
        "investment_strategy": "Balanced multi-asset allocation: Large-cap index (45%), Debt/FD/PPF (35%), Sovereign Gold (15%), Cash (5%)",
        "credit_strategy": "Maintain clean FOIR (<35%) for home/auto mortgage servicing",
    },
    3: {
        "id": "HIGH_NET_WORTH_INVESTOR",
        "name": "High-Net-Worth Investor & Wealth Accumulator",
        "tagline": "Sophisticated portfolio builder focused on capital compounding and asset diversification.",
        "risk_tolerance": "MODERATE_AGGRESSIVE",
        "primary_focus": "Multi-asset diversification, REITs, PMS/AIFs, estate planning",
        "budget_strategy": "Discretionary spend < 25%; maintain 50%+ net investable savings rate",
        "investment_strategy": "Direct equities (50%), Corporate debt/Bonds (25%), Real estate REITs (15%), Gold/Alternatives (10%)",
        "credit_strategy": "Leverage prime credit standing for low-cost asset-backed collateral borrowing",
    },
    4: {
        "id": "SMB_BUSINESS_OWNER",
        "name": "SMB Business Owner & Entrepreneur",
        "tagline": "Dynamic operator managing variable cash flows and business growth.",
        "risk_tolerance": "MODERATE",
        "primary_focus": "Working capital liquidity buffer, GST tax management, business vs personal decoupling",
        "budget_strategy": "Create a 9-month liquid buffer to absorb seasonal revenue fluctuations",
        "investment_strategy": "Liquid debt funds & overnight funds for business reserves; systematic index investing for personal wealth",
        "credit_strategy": "Commercial working capital lines and MSME loan eligibility optimization",
    },
    5: {
        "id": "DEBT_REHABILITATION_SEEKER",
        "name": "Debt Rehabilitation & Overleveraged Seeker",
        "tagline": "Urgent recovery candidate needing debt consolidation and expense restructuring.",
        "risk_tolerance": "VERY_CONSERVATIVE",
        "primary_focus": "Credit card balance payoff, debt avalanche/snowball, emergency stop on new loans",
        "budget_strategy": "Extreme austerity budget: cut discretionary spend to <10%; freeze new credit card swipes",
        "investment_strategy": "Temporarily pause equity SIPs; redirect all free cash flow to 36%+ APR revolving debt reduction",
        "credit_strategy": "Debt consolidation personal loan at 12-14% to extinguish high-interest credit card debt",
    },
}

RAW_FEATURE_COLUMNS_SEGMENTATION = [
    "monthly_income",
    "income_volatility_cv",        # 0.0 to 1.0 (Standard deviation / Mean income over 6 months)
    "monthly_essential_expenses",  # Rent, utilities, groceries, school
    "monthly_discretionary_spend", # Dining, entertainment, shopping, travel
    "monthly_investments_sip",     # Mutual funds, stocks, PPF, gold
    "existing_monthly_emi",        # Existing loan EMIs
    "total_credit_limit",
    "total_credit_used",
    "total_liquid_savings",
    "monthly_transaction_count",   # Total UPI, Card, Netbanking transactions
    "active_subscriptions_count",  # Netflix, Spotify, AWS, SaaS
]

ENGINEERED_NUMERICAL_FEATURES_SEGMENTATION = [
    "savings_rate_pct",
    "essential_expense_ratio",
    "discretionary_expense_ratio",
    "investment_to_income_ratio",
    "investment_to_surplus_ratio",
    "debt_to_income_ratio",
    "credit_utilization_ratio",
    "emergency_fund_months",
    "income_volatility_cv",
    "transaction_intensity",
    "subscription_density",
    "log_monthly_income",
    "log_liquid_savings",
]

TARGET_COLUMN_SEGMENTATION = "persona_cluster"

# ---------------------------------------------------------------------------
# Domain Feature Engineering Pipeline
# ---------------------------------------------------------------------------

def engineer_segmentation_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes normalized behavioral financial ratios, savings discipline, and debt burden indicators.
    """
    df = df.copy()
    inc = np.maximum(df["monthly_income"].values, 1.0)
    ess = np.maximum(df["monthly_essential_expenses"].values, 0.0)
    disc = np.maximum(df["monthly_discretionary_spend"].values, 0.0)
    inv = np.maximum(df["monthly_investments_sip"].values, 0.0)
    emi = np.maximum(df["existing_monthly_emi"].values, 0.0)
    limit = np.maximum(df["total_credit_limit"].values, 0.0)
    used = np.maximum(df["total_credit_used"].values, 0.0)
    savings = np.maximum(df["total_liquid_savings"].values, 0.0)
    tx_count = np.maximum(df["monthly_transaction_count"].values, 0.0)
    subs = np.maximum(df["active_subscriptions_count"].values, 0.0)
    volatility = np.clip(df["income_volatility_cv"].values, 0.0, 1.5)

    # 1. Total Living Expenses & Free Cashflow Surplus
    total_expenses = ess + disc + emi
    free_surplus = inc - total_expenses
    df["savings_rate_pct"] = np.round(np.clip((free_surplus / inc) * 100.0, -50.0, 90.0), 2)

    # 2. 50/30/20 Expense Distribution Ratios
    df["essential_expense_ratio"] = np.round(np.clip(ess / inc, 0.0, 1.2), 4)
    df["discretionary_expense_ratio"] = np.round(np.clip(disc / inc, 0.0, 1.0), 4)

    # 3. Investment Intensity Ratios
    df["investment_to_income_ratio"] = np.round(np.clip(inv / inc, 0.0, 0.8), 4)
    pos_surplus = np.maximum(free_surplus, 1.0)
    df["investment_to_surplus_ratio"] = np.round(np.clip(inv / pos_surplus, 0.0, 1.5), 4)

    # 4. Debt & Credit Utilization Ratios
    df["debt_to_income_ratio"] = np.round(np.clip(emi / inc, 0.0, 1.2), 4)
    df["credit_utilization_ratio"] = np.round(np.clip(used / np.maximum(limit, 1.0), 0.0, 1.5), 4)

    # 5. Liquid Runway (Emergency fund in months of living expenses)
    df["emergency_fund_months"] = np.round(np.clip(savings / np.maximum(ess + disc, 100.0), 0.0, 48.0), 2)

    # 6. Income Volatility Index (CV)
    df["income_volatility_cv"] = np.round(volatility, 4)

    # 7. Engagement & Subscription Density
    df["transaction_intensity"] = np.round(np.clip(tx_count / 100.0, 0.0, 5.0), 4)
    df["subscription_density"] = np.round(np.clip(subs / 10.0, 0.0, 3.0), 4)

    # 8. Logarithmic Magnitude Scaling
    df["log_monthly_income"] = np.round(np.log1p(inc), 4)
    df["log_liquid_savings"] = np.round(np.log1p(savings), 4)

    return df


def compute_soft_persona_affinity(
    distances_to_centroids: np.ndarray,
    temperature: float = 1.0,
) -> np.ndarray:
    """
    Computes smooth, calibrated multi-persona soft probabilities from Euclidean centroid distances.
    Formula: Softmax(-distance^2 / (2 * temperature^2))
    """
    # Negative squared distances scaled by temperature
    scaled_neg_dist = -0.5 * (distances_to_centroids ** 2) / max(0.01, temperature ** 2)
    # Numerical stability via max-subtraction
    exp_scores = np.exp(scaled_neg_dist - np.max(scaled_neg_dist, axis=-1, keepdims=True))
    probabilities = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
    return np.round(probabilities, 4)
