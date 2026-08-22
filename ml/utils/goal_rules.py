"""
Goal prediction rules, compound interest compounding formulas, and milestone calculators (Phases 6 & 11).
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, clone

class MultiOutputVotingRegressor(BaseEstimator, RegressorMixin):
    """
    Weighted ensemble combining predictions of multiple multi-output regressors.
    """
    def __init__(self, estimators=None, weights=None):
        self.estimators = estimators or []
        self.weights = weights

    def fit(self, X, y):
        self.estimators_ = []
        for name, est in self.estimators:
            fitted_est = clone(est)
            fitted_est.fit(X, y)
            self.estimators_.append((name, fitted_est))
        return self

    def predict(self, X):
        preds = [est.predict(X) for name, est in self.estimators_]
        if self.weights is not None:
            norm_weights = np.array(self.weights) / np.sum(self.weights)
            weighted_preds = sum(w * p for w, p in zip(norm_weights, preds))
            return weighted_preds
        return np.mean(preds, axis=0)

# Standard Goal Archetype Presets
GOAL_PRESETS: Dict[str, Dict[str, Any]] = {
    "emergency_fund": {
        "typical_horizon_months": 12,
        "recommended_annual_return_pct": 5.5,  # High-Yield Liquid Savings / Arbitrage
        "priority": "HIGH",
        "description": "Essential 3-6 months living expenses safety cushion.",
    },
    "tech_gadget": {
        "typical_horizon_months": 6,
        "recommended_annual_return_pct": 4.5,
        "priority": "MEDIUM",
        "description": "Electronics, laptops, mobile devices, hardware upgrades.",
    },
    "vehicle": {
        "typical_horizon_months": 24,
        "recommended_annual_return_pct": 7.0,  # Short-Term Debt / Hybrid Fund
        "priority": "MEDIUM",
        "description": "Two-wheeler or car downpayment / purchase.",
    },
    "travel_vacation": {
        "typical_horizon_months": 9,
        "recommended_annual_return_pct": 5.0,
        "priority": "LOW",
        "description": "Domestic or international holiday and leisure travel.",
    },
    "home_downpayment": {
        "typical_horizon_months": 48,
        "recommended_annual_return_pct": 10.0,  # Equity SIP / Index Funds
        "priority": "HIGH",
        "description": "Real estate downpayment and registry reserves.",
    },
    "education_fund": {
        "typical_horizon_months": 36,
        "recommended_annual_return_pct": 9.0,
        "priority": "HIGH",
        "description": "Higher studies, certifications, executive programs.",
    },
}

FEATURE_COLUMNS_SAVINGS: List[str] = [
    "monthly_income",
    "total_expenses",
    "needs_expenses",
    "wants_expenses",
    "debt_obligations",
    "current_balance",
    "discretionary_ratio",
    "savings_rate_baseline",
]


def calculate_months_to_goal(
    target_amount: float,
    current_saved: float,
    monthly_contribution: float,
    annual_return_pct: float = 7.0,
) -> float:
    """
    Computes exact fractional months required to reach target_amount with compounding returns.
    FV = PV*(1+r)^n + PMT * [((1+r)^n - 1) / r]
    """
    if target_amount <= current_saved:
        return 0.0

    if monthly_contribution <= 0:
        return 999.0  # Infinite / Not reachable without monthly contributions

    r = (annual_return_pct / 100.0) / 12.0  # Monthly interest rate

    if r <= 0:
        # Simple non-compounding linear payoff
        remaining = target_amount - current_saved
        return float(remaining / monthly_contribution)

    # Solve for n using Newton-Raphson or logarithmic formula:
    # FV*r + PMT = (PV*r + PMT) * (1+r)^n
    numerator = (target_amount * r) + monthly_contribution
    denominator = (current_saved * r) + monthly_contribution

    if denominator <= 0 or numerator <= 0:
        return float((target_amount - current_saved) / monthly_contribution)

    try:
        n_months = math.log(numerator / denominator) / math.log(1.0 + r)
        return max(0.1, round(float(n_months), 2))
    except (ValueError, ZeroDivisionError):
        return float((target_amount - current_saved) / monthly_contribution)


def calculate_required_monthly_savings(
    target_amount: float,
    current_saved: float,
    target_months: int,
    annual_return_pct: float = 7.0,
) -> float:
    """
    Calculates the exact monthly contribution (PMT) needed to reach target_amount in target_months.
    """
    if target_amount <= current_saved or target_months <= 0:
        return 0.0

    r = (annual_return_pct / 100.0) / 12.0

    if r <= 0:
        return round((target_amount - current_saved) / max(1, target_months), 2)

    # PMT = (FV - PV * (1+r)^n) * r / ((1+r)^n - 1)
    factor = (1.0 + r) ** target_months
    fv_from_pv = current_saved * factor
    remaining_fv = target_amount - fv_from_pv

    if remaining_fv <= 0:
        return 0.0

    pmt = (remaining_fv * r) / (factor - 1.0)
    return round(float(pmt), 2)


def project_savings_growth(
    monthly_savings_capacity: float,
    current_balance: float = 0.0,
    annual_return_pct: float = 7.0,
    horizons_months: Tuple[int, int, int] = (12, 36, 60),
) -> Dict[str, Dict[str, float]]:
    """
    Projects cumulative savings growth over 1-year, 3-year, and 5-year horizons
    comparing simple liquid cash vs compounded investment growth.
    """
    projections = {}
    r = (annual_return_pct / 100.0) / 12.0

    for months in horizons_months:
        years = months // 12
        key = f"{years}_year" if years > 0 else f"{months}_month"

        # 1. Simple Liquid Cash Accumulation (No Returns)
        simple_total = current_balance + (monthly_savings_capacity * months)

        # 2. Compounded Investment Growth
        if r > 0:
            factor = (1.0 + r) ** months
            compounded_total = (current_balance * factor) + (
                monthly_savings_capacity * ((factor - 1.0) / r)
            )
        else:
            compounded_total = simple_total

        wealth_gain = max(0.0, compounded_total - simple_total)

        projections[key] = {
            "months": months,
            "cash_savings": round(float(simple_total), 2),
            "invested_wealth": round(float(compounded_total), 2),
            "compounding_gain": round(float(wealth_gain), 2),
        }

    return projections


def evaluate_goal_feasibility(
    monthly_savings_capacity: float,
    required_monthly_savings: float,
) -> Tuple[str, str]:
    """
    Determines goal feasibility tier and descriptive feedback.
    """
    if required_monthly_savings <= 0:
        return "ON_TRACK", "Goal already funded or zero additional contribution required."

    ratio = monthly_savings_capacity / required_monthly_savings

    if ratio >= 1.25:
        return "ON_TRACK", "Comfortable surplus! Your current monthly savings exceed the required target pace."
    elif ratio >= 1.0:
        return "FEASIBLE", "On pace! Monthly savings match your goal timeline requirements."
    elif ratio >= 0.70:
        return "STRETCH", "Moderate gap: Minor trimming of discretionary spending is needed to hit the target date."
    else:
        return "AT_RISK", "Significant shortfall: Timeline should be extended or monthly target adjusted."
