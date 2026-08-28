"""
Financial Domain Rules & Modern Portfolio Theory Utilities for Phase 10: Investment Recommendation.

Defines:
- Risk profiles and quantitative risk scores
- Asset classes, historical CAGR expectations, and volatility benchmarks
- 100-Age heuristic combined with Modern Portfolio Theory bounds
- Curated investment instrument catalog (Indian & Global financial markets)
- Compound interest and SIP wealth projection calculators
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin

# ---------------------------------------------------------------------------
# Constants & Taxonomy
# ---------------------------------------------------------------------------

RISK_PROFILES = {
    "CONSERVATIVE": {
        "score": 1,
        "description": "High capital preservation priority with minimal equity exposure.",
        "equity_range": (0.10, 0.30),
        "debt_range": (0.50, 0.75),
        "gold_range": (0.10, 0.20),
        "reit_range": (0.00, 0.05),
        "cash_range": (0.05, 0.15),
        "expected_cagr": 0.078,  # ~7.8% annualized
    },
    "MODERATE": {
        "score": 2,
        "description": "Balanced steady growth with moderate defensive debt buffer.",
        "equity_range": (0.30, 0.50),
        "debt_range": (0.30, 0.50),
        "gold_range": (0.08, 0.15),
        "reit_range": (0.02, 0.08),
        "cash_range": (0.05, 0.10),
        "expected_cagr": 0.098,  # ~9.8% annualized
    },
    "BALANCED": {
        "score": 3,
        "description": "Equal-weight approach prioritizing both capital appreciation and risk mitigation.",
        "equity_range": (0.45, 0.65),
        "debt_range": (0.20, 0.35),
        "gold_range": (0.05, 0.12),
        "reit_range": (0.05, 0.10),
        "cash_range": (0.03, 0.08),
        "expected_cagr": 0.114,  # ~11.4% annualized
    },
    "GROWTH": {
        "score": 4,
        "description": "Growth-oriented allocation emphasizing equity capital gains over long horizons.",
        "equity_range": (0.60, 0.80),
        "debt_range": (0.10, 0.25),
        "gold_range": (0.05, 0.10),
        "reit_range": (0.05, 0.12),
        "cash_range": (0.02, 0.06),
        "expected_cagr": 0.132,  # ~13.2% annualized
    },
    "AGGRESSIVE": {
        "score": 5,
        "description": "High equity allocation targeting maximum wealth accumulation with higher volatility tolerance.",
        "equity_range": (0.75, 0.90),
        "debt_range": (0.05, 0.15),
        "gold_range": (0.02, 0.08),
        "reit_range": (0.05, 0.15),
        "cash_range": (0.02, 0.05),
        "expected_cagr": 0.148,  # ~14.8% annualized
    },
}

ASSET_CLASSES = ["equity", "debt", "gold", "reit", "cash"]

FEATURE_COLUMNS_INVESTMENT = [
    "monthly_income",
    "age",
    "monthly_surplus",
    "existing_savings",
    "existing_debt",
    "liquid_runway_months",
    "investment_horizon_years",
    "risk_score",
    "risk_profile",
]

# Extended Feature Representation including non-linear domain ratios & log scales
ENGINEERED_NUMERICAL_FEATURES = [
    "monthly_income",
    "age",
    "monthly_surplus",
    "existing_savings",
    "existing_debt",
    "liquid_runway_months",
    "investment_horizon_years",
    "risk_score",
    "savings_ratio",
    "debt_to_income",
    "net_worth",
    "net_worth_ratio",
    "horizon_risk_factor",
    "equity_capacity_score",
    "emergency_adequacy_score",
    "log_income",
    "log_surplus",
    "log_savings",
]

ENGINEERED_CATEGORICAL_FEATURES = [
    "risk_profile",
]

TARGET_COLUMNS_INVESTMENT = [
    "equity_pct",
    "debt_pct",
    "gold_pct",
    "reit_pct",
    "cash_pct",
]


def engineer_investment_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes high-signal domain ratios, interaction terms, and log scales
    from raw user financial parameters.
    """
    df = df.copy()
    inc = np.maximum(df["monthly_income"].values, 1.0)
    surplus = np.maximum(df["monthly_surplus"].values, 0.0)
    savings = np.maximum(df["existing_savings"].values, 0.0)
    debt = np.maximum(df["existing_debt"].values, 0.0)
    age = df["age"].values
    risk_score = df["risk_score"].values
    horizon = df["investment_horizon_years"].values
    runway = df["liquid_runway_months"].values

    df["savings_ratio"] = np.round(surplus / inc, 4)
    df["debt_to_income"] = np.round(debt / (inc * 12.0), 4)
    df["net_worth"] = np.round(savings - debt, 2)
    df["net_worth_ratio"] = np.round((savings - debt) / (inc * 12.0), 4)
    df["horizon_risk_factor"] = np.round(horizon * risk_score, 2)
    
    # Financial capacity indices
    df["equity_capacity_score"] = np.round(
        ((100 - age) / 100.0) * (risk_score / 3.0) * np.clip(horizon / 5.0, 0.2, 1.5), 4
    )
    df["emergency_adequacy_score"] = np.round(np.clip(runway / 6.0, 0.0, 1.0), 4)

    # Log transforms for skewed monetary magnitudes
    df["log_income"] = np.round(np.log1p(inc), 4)
    df["log_surplus"] = np.round(np.log1p(surplus), 4)
    df["log_savings"] = np.round(np.log1p(savings), 4)

    return df

# Historical annualized CAGRs and estimated standard deviations (volatilities)
ASSET_RETURNS = {
    "equity": {"cagr": 0.135, "std": 0.160},
    "debt": {"cagr": 0.072, "std": 0.025},
    "gold": {"cagr": 0.095, "std": 0.110},
    "reit": {"cagr": 0.105, "std": 0.090},
    "cash": {"cagr": 0.045, "std": 0.005},
}

# ---------------------------------------------------------------------------
# Curated Financial Instruments Catalog
# ---------------------------------------------------------------------------

CURATED_INSTRUMENTS = {
    "equity": [
        {
            "name": "Nifty 50 Index Fund / ETF",
            "category": "Large Cap Equity",
            "risk": "Moderate-High",
            "horizon": "3+ years",
            "suitable_for": ["CONSERVATIVE", "MODERATE", "BALANCED", "GROWTH", "AGGRESSIVE"],
            "expected_cagr": "12.0% - 13.5%",
            "expense_ratio": "0.10% - 0.20%",
        },
        {
            "name": "Parag Parikh Flexi Cap Fund",
            "category": "Diversified / Multi Cap Equity",
            "risk": "High",
            "horizon": "5+ years",
            "suitable_for": ["BALANCED", "GROWTH", "AGGRESSIVE"],
            "expected_cagr": "14.0% - 16.0%",
            "expense_ratio": "0.60% - 0.75%",
        },
        {
            "name": "Nifty Midcap 150 / Small Cap Fund",
            "category": "Mid & Small Cap Equity",
            "risk": "Very High",
            "horizon": "7+ years",
            "suitable_for": ["GROWTH", "AGGRESSIVE"],
            "expected_cagr": "15.0% - 18.0%",
            "expense_ratio": "0.40% - 0.80%",
        },
    ],
    "debt": [
        {
            "name": "Short-Duration / Banking & PSU Debt Fund",
            "category": "Low-Volatility Debt",
            "risk": "Low-Moderate",
            "horizon": "1-3 years",
            "suitable_for": ["CONSERVATIVE", "MODERATE", "BALANCED", "GROWTH", "AGGRESSIVE"],
            "expected_cagr": "7.0% - 7.5%",
            "expense_ratio": "0.25% - 0.35%",
        },
        {
            "name": "Corporate Bond / Target Maturity Govt Index Fund",
            "category": "High Quality Fixed Income",
            "risk": "Low",
            "horizon": "3-5 years",
            "suitable_for": ["CONSERVATIVE", "MODERATE", "BALANCED"],
            "expected_cagr": "7.2% - 7.8%",
            "expense_ratio": "0.15% - 0.30%",
        },
    ],
    "gold": [
        {
            "name": "Sovereign Gold Bonds (SGB) / Gold ETFs",
            "category": "Hedge / Precious Metals",
            "risk": "Moderate",
            "horizon": "3+ years",
            "suitable_for": ["CONSERVATIVE", "MODERATE", "BALANCED", "GROWTH"],
            "expected_cagr": "9.0% - 10.5% + 2.5% SGB coupon",
            "expense_ratio": "0.00% (SGB) / 0.30% (ETF)",
        },
    ],
    "reit": [
        {
            "name": "Embassy Office Parks / Brookfield India REIT",
            "category": "Commercial Real Estate Yield + Capital Growth",
            "risk": "Moderate-High",
            "horizon": "3-5+ years",
            "suitable_for": ["BALANCED", "GROWTH", "AGGRESSIVE"],
            "expected_cagr": "10.0% - 11.5% (Yield + Growth)",
            "expense_ratio": "Direct Market Listing",
        },
    ],
    "cash": [
        {
            "name": "Overnight / Liquid Funds & High-Interest Savings",
            "category": "Emergency & Instant Liquidity Buffer",
            "risk": "Very Low",
            "horizon": "Instant / 0-12 months",
            "suitable_for": ["CONSERVATIVE", "MODERATE", "BALANCED", "GROWTH", "AGGRESSIVE"],
            "expected_cagr": "5.5% - 6.8%",
            "expense_ratio": "0.10% - 0.15%",
        },
    ],
}

# ---------------------------------------------------------------------------
# Simplex Projection & MPT Optimization Helpers
# ---------------------------------------------------------------------------

def normalize_to_simplex(weights: np.ndarray) -> np.ndarray:
    """
    Projects raw continuous predictions onto the standard probability simplex:
    w_i >= 0 and sum(w_i) = 1.0 (100%).
    """
    clipped = np.clip(weights, 0.0, None)
    total = np.sum(clipped, axis=-1, keepdims=True)
    total = np.where(total == 0, 1.0, total)
    return clipped / total


def compute_portfolio_cagr(allocation_pct: Dict[str, float]) -> float:
    """
    Calculates the expected portfolio annualized CAGR based on asset weights.
    """
    cagr = 0.0
    for asset, weight in allocation_pct.items():
        if asset in ASSET_RETURNS:
            cagr += (weight / 100.0) * ASSET_RETURNS[asset]["cagr"]
    return round(float(cagr), 4)


def project_sip_wealth(
    monthly_sip: float,
    annual_cagr: float,
    horizon_years: int,
    initial_lump_sum: float = 0.0,
) -> Dict[str, Any]:
    """
    Projects compounding monthly SIP wealth accumulation across time horizons.
    Formula: FV = P * (1+r)^n + PMT * [((1+i)^n - 1) / i] * (1+i)
    """
    monthly_rate = (1.0 + annual_cagr) ** (1.0 / 12.0) - 1.0
    total_months = horizon_years * 12
    total_invested = initial_lump_sum + (monthly_sip * total_months)

    # Future value calculation
    fv_lump_sum = initial_lump_sum * ((1.0 + monthly_rate) ** total_months)
    if monthly_rate > 0:
        fv_sip = monthly_sip * (((1.0 + monthly_rate) ** total_months - 1.0) / monthly_rate) * (1.0 + monthly_rate)
    else:
        fv_sip = monthly_sip * total_months

    projected_total = round(fv_lump_sum + fv_sip, 2)
    estimated_gains = round(projected_total - total_invested, 2)

    # Multi-horizon trajectory checkpoints
    milestones = {}
    for yr in [1, 3, 5, 10]:
        if yr <= horizon_years or yr in [1, 3, 5, 10]:
            m = yr * 12
            inv = initial_lump_sum + (monthly_sip * m)
            fv_l = initial_lump_sum * ((1.0 + monthly_rate) ** m)
            fv_s = (
                monthly_sip * (((1.0 + monthly_rate) ** m - 1.0) / monthly_rate) * (1.0 + monthly_rate)
                if monthly_rate > 0
                else monthly_sip * m
            )
            milestones[f"{yr}_year"] = {
                "invested_inr": round(inv, 2),
                "projected_wealth_inr": round(fv_l + fv_s, 2),
                "wealth_gain_inr": round((fv_l + fv_s) - inv, 2),
            }

    return {
        "monthly_sip_inr": round(monthly_sip, 2),
        "initial_lump_sum_inr": round(initial_lump_sum, 2),
        "horizon_years": horizon_years,
        "expected_cagr_pct": round(annual_cagr * 100.0, 2),
        "total_invested_inr": round(total_invested, 2),
        "projected_wealth_inr": projected_total,
        "estimated_gains_inr": estimated_gains,
        "growth_multiple": round(projected_total / total_invested, 2) if total_invested > 0 else 1.0,
        "trajectory_milestones": milestones,
    }


def compute_target_asset_allocation(
    age: int,
    risk_profile: str,
    horizon_years: int,
    liquid_runway_months: float,
) -> Dict[str, float]:
    """
    Financial domain ground-truth synthesizer for generating optimal MPT portfolio allocations.
    Combines:
    1. 100 - Age equity rule
    2. Risk tolerance multiplier
    3. Investment horizon elongation bonus (longer horizons allow higher equity)
    4. Emergency liquidity buffer penalty (low liquid buffer requires higher cash allocation)
    """
    profile = RISK_PROFILES.get(risk_profile, RISK_PROFILES["BALANCED"])
    risk_multiplier = profile["score"] / 3.0  # 1.0 for BALANCED

    # Base equity percentage from 100 - Age heuristic
    base_equity = (100 - age) / 100.0

    # Adjust for horizon (short horizon restricts equity)
    if horizon_years <= 1:
        horizon_equity_factor = 0.30
    elif horizon_years <= 3:
        horizon_equity_factor = 0.65
    elif horizon_years <= 5:
        horizon_equity_factor = 0.90
    else:
        horizon_equity_factor = 1.10

    raw_equity = base_equity * risk_multiplier * horizon_equity_factor
    equity = np.clip(raw_equity, profile["equity_range"][0], profile["equity_range"][1])

    # Cash buffer allocation based on liquid runway
    if liquid_runway_months < 3.0:
        cash = max(profile["cash_range"][1], 0.15)
    elif liquid_runway_months < 6.0:
        cash = (profile["cash_range"][0] + profile["cash_range"][1]) / 2.0
    else:
        cash = profile["cash_range"][0]

    # Gold allocation (Hedging asset)
    gold = (profile["gold_range"][0] + profile["gold_range"][1]) / 2.0

    # REIT allocation (Real estate yield for longer horizons)
    if horizon_years >= 3 and profile["score"] >= 3:
        reit = (profile["reit_range"][0] + profile["reit_range"][1]) / 2.0
    else:
        reit = profile["reit_range"][0]

    # Residual goes to Debt (Fixed income stabilizer)
    allocated_so_far = equity + gold + reit + cash
    debt = max(0.05, 1.0 - allocated_so_far)

    # Normalize weights to exactly 100.0%
    raw_vector = np.array([equity, debt, gold, reit, cash])
    norm_vector = normalize_to_simplex(raw_vector) * 100.0

    return {
        "equity_pct": round(float(norm_vector[0]), 2),
        "debt_pct": round(float(norm_vector[1]), 2),
        "gold_pct": round(float(norm_vector[2]), 2),
        "reit_pct": round(float(norm_vector[3]), 2),
        "cash_pct": round(float(norm_vector[4]), 2),
    }


# ---------------------------------------------------------------------------
# Custom Constrained Stacking Regressor for Multi-Output Simplex Output
# ---------------------------------------------------------------------------

from scipy.optimize import minimize  # noqa: E402


class ConstrainedMultiOutputVotingRegressor(BaseEstimator, RegressorMixin):
    """
    Ensemble regressor combining multi-output predictions with SLSQP optimal weight learning
    and a post-prediction Simplex Normalization step to ensure predicted asset allocation weights
    sum strictly to 100.0%.
    """

    def __init__(self, estimators: List[Tuple[str, Any]], weights: List[float] = None, optimize_weights: bool = True):
        self.estimators = estimators
        self.weights = weights
        self.optimize_weights = optimize_weights
        self.fitted_estimators_ = []
        self.learned_weights_ = None

    def fit(self, X, y):
        self.fitted_estimators_ = []
        base_preds = []

        for name, est in self.estimators:
            fitted = est.fit(X, y)
            self.fitted_estimators_.append((name, fitted))
            p = fitted.predict(X)
            base_preds.append(p)

        n_models = len(self.fitted_estimators_)
        if self.optimize_weights and n_models > 1:
            def loss_fn(w):
                w_norm = np.array(w) / np.sum(w)
                weighted_pred = sum(w_norm[i] * base_preds[i] for i in range(n_models))
                weighted_pred = normalize_to_simplex(weighted_pred) * 100.0
                return np.mean(np.abs(y - weighted_pred))

            init_w = np.ones(n_models) / n_models
            bounds = [(0.0, 1.0) for _ in range(n_models)]
            constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

            res = minimize(loss_fn, init_w, method="SLSQP", bounds=bounds, constraints=constraints)
            if res.success:
                opt_w = np.clip(res.x, 0.0, 1.0)
                self.learned_weights_ = (opt_w / np.sum(opt_w)).tolist()
            else:
                self.learned_weights_ = self.weights if self.weights is not None else (np.ones(n_models) / n_models).tolist()
        else:
            self.learned_weights_ = self.weights if self.weights is not None else (np.ones(n_models) / n_models).tolist()

        return self

    def predict(self, X):
        preds = []
        w_list = self.learned_weights_ if self.learned_weights_ is not None else [1.0] * len(self.fitted_estimators_)
        w_total = sum(w_list)

        for (name, est), w in zip(self.fitted_estimators_, w_list):
            p = est.predict(X)
            preds.append(p * (w / w_total))

        ensemble_pred = np.sum(preds, axis=0)

        # Apply Simplex Projection so output rows sum to 100.0%
        normalized_pred = normalize_to_simplex(ensemble_pred) * 100.0
        return normalized_pred

