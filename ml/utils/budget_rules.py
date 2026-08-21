"""
Budget rules, taxonomies, and constraint satisfaction utilities for Phase 5 & 7.
"""

from typing import Dict, List

# Standard 7 Categories matching the Fintra-AI ML roadmap
ROADMAP_CATEGORIES: List[str] = [
    "food",
    "shopping",
    "transport",
    "entertainment",
    "bills",
    "healthcare",
    "education",
]

# Classification of categories into Needs vs Wants
CATEGORY_CLASSIFICATION: Dict[str, str] = {
    "food": "needs",
    "bills": "needs",
    "healthcare": "needs",
    "transport": "needs",
    "education": "needs",
    "shopping": "wants",
    "entertainment": "wants",
}

# Baseline 50/30/20 standard budget distribution benchmarks (as % of total income)
DEFAULT_50_30_20_TARGETS: Dict[str, float] = {
    "needs": 0.50,
    "wants": 0.30,
    "savings": 0.20,
}

# Default category share within Needs and Wants
DEFAULT_CATEGORY_WEIGHTS: Dict[str, float] = {
    # Needs (Sum to 1.0 within Needs bucket)
    "food": 0.40,
    "bills": 0.25,
    "transport": 0.15,
    "healthcare": 0.10,
    "education": 0.10,
    # Wants (Sum to 1.0 within Wants bucket)
    "shopping": 0.60,
    "entertainment": 0.40,
}

# Lifestyle profiles and their savings / wants adjustments
LIFESTYLE_PROFILES: Dict[str, Dict[str, float]] = {
    "conservative": {
        "needs_target": 0.50,
        "wants_target": 0.20,
        "savings_target": 0.30,
        "description": "High savings priority, minimized discretionary spending, strong buffer building.",
    },
    "balanced": {
        "needs_target": 0.50,
        "wants_target": 0.30,
        "savings_target": 0.20,
        "description": "Standard 50/30/20 balanced rule balancing living expenses, lifestyle, and wealth building.",
    },
    "growth_oriented": {
        "needs_target": 0.45,
        "wants_target": 0.20,
        "savings_target": 0.35,
        "description": "Aggressive wealth accumulation and investment-focused allocation.",
    },
    "flexible": {
        "needs_target": 0.55,
        "wants_target": 0.35,
        "savings_target": 0.10,
        "description": "Relaxed budget suitable for high-income or transitional life stages.",
    },
}


def allocate_category_budgets(
    monthly_income: float,
    savings_target_pct: float = 0.20,
    lifestyle: str = "balanced",
    category_weights: Dict[str, float] | None = None,
) -> Dict[str, float]:
    """
    Computes exact mathematically-constrained budget allocation per category.
    Guarantees sum(category_budgets) + savings == monthly_income.
    """
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than 0.")

    savings_target_pct = max(0.05, min(0.60, float(savings_target_pct)))
    profile = LIFESTYLE_PROFILES.get(lifestyle, LIFESTYLE_PROFILES["balanced"])
    
    # Calculate total disposable spend after savings
    savings_amount = round(monthly_income * savings_target_pct, 2)
    spendable_income = monthly_income - savings_amount

    # Split spendable income between needs and wants according to profile ratio
    profile_needs_ratio = profile["needs_target"] / (profile["needs_target"] + profile["wants_target"])
    profile_wants_ratio = 1.0 - profile_needs_ratio

    total_needs_budget = spendable_income * profile_needs_ratio
    total_wants_budget = spendable_income * profile_wants_ratio

    weights = category_weights or DEFAULT_CATEGORY_WEIGHTS

    allocations = {}
    # Needs allocation
    for cat in ["food", "bills", "transport", "healthcare", "education"]:
        weight = weights.get(cat, DEFAULT_CATEGORY_WEIGHTS[cat])
        allocations[cat] = round(total_needs_budget * weight, 2)

    # Wants allocation
    for cat in ["shopping", "entertainment"]:
        weight = weights.get(cat, DEFAULT_CATEGORY_WEIGHTS[cat])
        allocations[cat] = round(total_wants_budget * weight, 2)

    # Reconcile rounding discrepancy to keep sum exact
    budget_sum = sum(allocations.values())
    discrepancy = round(spendable_income - budget_sum, 2)
    if discrepancy != 0:
        allocations["food"] = round(allocations["food"] + discrepancy, 2)

    allocations["savings"] = savings_amount
    return allocations
