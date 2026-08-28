"""
Preprocessing & Synthetic Profile Generation Pipeline for Phase 10: Investment Recommendation.

Generates 6,000 multi-demographic financial profiles across salary tiers (₹15,000 to ₹500,000/mo),
age ranges (21 to 65), risk tolerances, horizons, existing savings, and debts.
Outputs:
- datasets/processed/investment_train.csv
- datasets/processed/investment_test.csv
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.investment_rules import (  # noqa: E402
    FEATURE_COLUMNS_INVESTMENT,
    TARGET_COLUMNS_INVESTMENT,
    RISK_PROFILES,
    compute_target_asset_allocation,
    normalize_to_simplex,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_TRAIN = os.path.join(PROCESSED_DIR, "investment_train.csv")
OUTPUT_TEST = os.path.join(PROCESSED_DIR, "investment_test.csv")


def generate_synthetic_investment_profiles(
    num_samples: int = 6000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates synthetic multi-demographic investment profiles with realistic
    market behaviors, demographic noise, and target asset allocations.
    """
    np.random.seed(seed)
    risk_names = list(RISK_PROFILES.keys())

    # Income distributions: ₹15,000 to ₹500,000 (Log-normal distribution)
    log_incomes = np.random.normal(loc=11.2, scale=0.70, size=num_samples)
    monthly_incomes = np.clip(np.exp(log_incomes), 15000.0, 500000.0).round(2)

    # Age distribution: 21 to 65
    ages = np.random.randint(21, 66, size=num_samples)

    # Investment horizon: 1 to 15 years
    horizons = np.random.choice([1, 2, 3, 5, 7, 10, 15], p=[0.10, 0.15, 0.25, 0.25, 0.15, 0.08, 0.02], size=num_samples)

    # Risk profile selection probabilities
    risk_choices = np.random.choice(risk_names, p=[0.15, 0.25, 0.30, 0.20, 0.10], size=num_samples)

    rows = []
    for i in range(num_samples):
        income = monthly_incomes[i]
        age = int(ages[i])
        horizon = int(horizons[i])
        risk_profile = risk_choices[i]
        risk_score = RISK_PROFILES[risk_profile]["score"]

        # Savings rate / surplus margin: 10% to 50% of income
        savings_ratio = np.clip(np.random.normal(0.28, 0.09), 0.08, 0.65)
        monthly_surplus = round(float(income * savings_ratio), 2)

        # Existing liquid savings (multiple of income: 0.5x to 25x depending on age)
        age_savings_factor = max(0.5, (age - 20) * 0.35)
        savings_multiple = np.clip(np.random.normal(age_savings_factor, age_savings_factor * 0.4), 0.2, 30.0)
        existing_savings = round(float(income * savings_multiple), 2)

        # Existing debt obligations
        debt_prob = 0.45
        if np.random.rand() < debt_prob:
            debt_ratio = np.clip(np.random.normal(0.18, 0.10), 0.03, 0.50)
            existing_debt = round(float(income * debt_ratio * 12.0), 2)
        else:
            existing_debt = 0.0

        # Liquid runway in months
        monthly_expenses = max(5000.0, income - monthly_surplus)
        liquid_runway_months = round(float(existing_savings / monthly_expenses), 1)

        # Ground-truth asset allocation vector with realistic micro-variations
        alloc = compute_target_asset_allocation(
            age=age,
            risk_profile=risk_profile,
            horizon_years=horizon,
            liquid_runway_months=liquid_runway_months,
        )

        # Add slight realistic investor preference noise and re-project to simplex
        raw_alloc = np.array([
            alloc["equity_pct"] + np.random.normal(0, 0.8),
            alloc["debt_pct"] + np.random.normal(0, 0.8),
            alloc["gold_pct"] + np.random.normal(0, 0.4),
            alloc["reit_pct"] + np.random.normal(0, 0.4),
            alloc["cash_pct"] + np.random.normal(0, 0.4),
        ])
        norm_alloc = normalize_to_simplex(np.clip(raw_alloc, 0, None)) * 100.0

        row = {
            "monthly_income": income,
            "age": age,
            "monthly_surplus": monthly_surplus,
            "existing_savings": existing_savings,
            "existing_debt": existing_debt,
            "liquid_runway_months": liquid_runway_months,
            "investment_horizon_years": horizon,
            "risk_score": risk_score,
            "risk_profile": risk_profile,
            "equity_pct": round(float(norm_alloc[0]), 2),
            "debt_pct": round(float(norm_alloc[1]), 2),
            "gold_pct": round(float(norm_alloc[2]), 2),
            "reit_pct": round(float(norm_alloc[3]), 2),
            "cash_pct": round(float(norm_alloc[4]), 2),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def main():
    print("[info] Generating multi-demographic synthetic investment profiles...")
    df = generate_synthetic_investment_profiles(num_samples=6000, seed=42)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 80/20 Train/Test Split (Stratified across risk profile)
    train_dfs = []
    test_dfs = []
    for profile, group in df.groupby("risk_profile"):
        n_test = int(len(group) * 0.20)
        shuffled = group.sample(frac=1.0, random_state=42)
        test_dfs.append(shuffled.iloc[:n_test])
        train_dfs.append(shuffled.iloc[n_test:])

    train_df = pd.concat(train_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)
    test_df = pd.concat(test_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)

    train_df.to_csv(OUTPUT_TRAIN, index=False)
    test_df.to_csv(OUTPUT_TEST, index=False)

    print(f"[done] Train profiles: {len(train_df)} rows -> {OUTPUT_TRAIN}")
    print(f"[done] Test profiles:  {len(test_df)} rows -> {OUTPUT_TEST}")
    print("\nDataset Sample:")
    print(train_df[["monthly_income", "age", "risk_profile", "investment_horizon_years", "equity_pct", "debt_pct", "gold_pct"]].head())


if __name__ == "__main__":
    main()
