"""
Preprocessing Pipeline for Budget Recommendation & Financial Health Profiling (Phases 5 & 7).

Generates diverse, realistic user monthly financial profiles across different income brackets,
spending habits, debt levels, and lifestyle preferences.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.budget_rules import (  # noqa: E402
    ROADMAP_CATEGORIES,
    LIFESTYLE_PROFILES,
    DEFAULT_CATEGORY_WEIGHTS,
    allocate_category_budgets,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_TRAIN = os.path.join(PROCESSED_DIR, "budget_train.csv")
OUTPUT_TEST = os.path.join(PROCESSED_DIR, "budget_test.csv")


def extract_empirical_category_ratios(processed_dir: str = PROCESSED_DIR) -> dict:
    """
    Computes empirical category ratios from processed transaction records.
    """
    train_path = os.path.join(processed_dir, "train.csv")
    if not os.path.exists(train_path):
        return {cat: DEFAULT_CATEGORY_WEIGHTS.get(cat, 0.15) for cat in ROADMAP_CATEGORIES}

    df = pd.read_csv(train_path)
    cat_totals = df.groupby("category")["amount"].sum()
    total_spend = cat_totals.sum()
    
    ratios = {}
    for cat in ROADMAP_CATEGORIES:
        ratios[cat] = float(cat_totals.get(cat, 0.0) / total_spend) if total_spend > 0 else 0.14
    return ratios


def generate_synthetic_user_profiles(
    num_samples: int = 5000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates synthetic multi-demographic user monthly profiles with realistic
    spending noise, income brackets, debt obligations, and target allocations.
    """
    np.random.seed(seed)
    lifestyles = list(LIFESTYLE_PROFILES.keys())

    # Income distributions: ₹15,000 to ₹350,000 (Log-normal distribution reflecting realistic demographics)
    log_incomes = np.random.normal(loc=11.0, scale=0.65, size=num_samples)
    monthly_incomes = np.clip(np.exp(log_incomes), 15000.0, 400000.0).round(2)

    rows = []
    empirical_ratios = extract_empirical_category_ratios()

    for i in range(num_samples):
        income = monthly_incomes[i]
        lifestyle = np.random.choice(lifestyles, p=[0.25, 0.45, 0.20, 0.10])
        savings_target = round(float(np.clip(np.random.normal(0.22, 0.08), 0.05, 0.50)), 2)

        # Generate noisy historical spending ratios
        noise = np.random.dirichlet([np.maximum(empirical_ratios[cat] * 10, 1.0) for cat in ROADMAP_CATEGORIES])
        historical_ratios = {cat: float(noise[idx]) for idx, cat in enumerate(ROADMAP_CATEGORIES)}

        # Debt obligation (0 to 35% of income)
        debt_ratio = float(np.clip(np.random.exponential(scale=0.10), 0.0, 0.50))
        debt_amount = round(income * debt_ratio, 2)

        # Calculate ground truth optimal budget allocations
        optimal_allocations = allocate_category_budgets(
            monthly_income=income,
            savings_target_pct=savings_target,
            lifestyle=lifestyle,
        )

        # Build training record
        record = {
            "monthly_income": income,
            "savings_target_pct": savings_target,
            "lifestyle": lifestyle,
            "debt_obligations": debt_amount,
            "debt_to_income_ratio": debt_ratio,
        }

        # Historical ratios
        for cat in ROADMAP_CATEGORIES:
            record[f"hist_ratio_{cat}"] = round(historical_ratios[cat], 4)

        # Ground truth target budget outputs
        for cat in ROADMAP_CATEGORIES:
            record[f"target_budget_{cat}"] = optimal_allocations[cat]
        record["target_budget_savings"] = optimal_allocations["savings"]

        rows.append(record)

    return pd.DataFrame(rows)


def main():
    print("=" * 60)
    print("Preprocess Pipeline: Phase 5 & 7 Budget & Financial Health Datasets")
    print("=" * 60)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df = generate_synthetic_user_profiles(num_samples=6000, seed=42)

    # Train/Test Split (80/20)
    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size].copy()
    test_df = df.iloc[train_size:].copy()

    train_df.to_csv(OUTPUT_TRAIN, index=False)
    test_df.to_csv(OUTPUT_TEST, index=False)

    print(f"[done] Generated {len(df)} user financial profiles.")
    print(f"[done] Saved Train Set ({len(train_df)} rows) -> {OUTPUT_TRAIN}")
    print(f"[done] Saved Test Set ({len(test_df)} rows) -> {OUTPUT_TEST}")
    print(f"[info] Income Range: INR {df['monthly_income'].min():,.2f} to INR {df['monthly_income'].max():,.2f}")
    print(f"[info] Median Income: INR {df['monthly_income'].median():,.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
