"""
Preprocessing & Dataset Generation Pipeline for Savings & Goal Prediction (Phases 6 & 11).

Generates comprehensive, multi-demographic goal and savings profiles across different
income tiers, spending propensities, debt loads, and financial goal archetypes.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.goal_rules import (  # noqa: E402
    FEATURE_COLUMNS_SAVINGS,
    GOAL_PRESETS,
    calculate_months_to_goal,
    calculate_required_monthly_savings,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_TRAIN = os.path.join(PROCESSED_DIR, "goals_train.csv")
OUTPUT_TEST = os.path.join(PROCESSED_DIR, "goals_test.csv")


def generate_synthetic_goals_dataset(
    num_samples: int = 7500,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates realistic user savings capacity and goal achievement records.
    """
    np.random.seed(seed)
    goal_types = list(GOAL_PRESETS.keys())

    # Income distributions: INR 18,000 to INR 350,000 (Log-normal)
    log_incomes = np.random.normal(loc=11.1, scale=0.62, size=num_samples)
    monthly_incomes = np.clip(np.exp(log_incomes), 18000.0, 400000.0).round(2)

    rows = []

    for i in range(num_samples):
        income = float(monthly_incomes[i])
        goal_type = np.random.choice(goal_types)
        preset = GOAL_PRESETS[goal_type]

        # Expense breakdown
        needs_ratio = float(np.clip(np.random.normal(0.48, 0.08), 0.30, 0.70))
        wants_ratio = float(np.clip(np.random.normal(0.24, 0.06), 0.08, 0.45))
        debt_ratio = float(np.clip(np.random.exponential(0.08), 0.0, 0.35))

        needs_exp = round(income * needs_ratio, 2)
        wants_exp = round(income * wants_ratio, 2)
        total_exp = round(needs_exp + wants_exp, 2)
        debt = round(income * debt_ratio, 2)

        # True net savings capacity
        true_savings_capacity = max(0.0, round(income - total_exp - debt, 2))
        discretionary_ratio = round(wants_exp / max(1.0, total_exp), 3)
        savings_rate = round(true_savings_capacity / income, 3)

        # Liquid balance (0.5 to 12 months living expenses)
        balance_multiple = float(np.clip(np.random.lognormal(mean=0.8, sigma=0.7), 0.2, 12.0))
        current_balance = round(total_exp * balance_multiple, 2)

        # Goal target amounts scaled to income and preset type
        if goal_type == "tech_gadget":
            target_amount = round(float(np.random.uniform(25000.0, 150000.0)), -2)
        elif goal_type == "travel_vacation":
            target_amount = round(float(np.random.uniform(40000.0, 250000.0)), -2)
        elif goal_type == "vehicle":
            target_amount = round(float(np.random.uniform(100000.0, 600000.0)), -2)
        elif goal_type == "emergency_fund":
            target_amount = round(float(total_exp * np.random.choice([3, 6, 9])), -2)
        elif goal_type == "home_downpayment":
            target_amount = round(float(np.random.uniform(500000.0, 2500000.0)), -2)
        else:  # education_fund
            target_amount = round(float(np.random.uniform(150000.0, 800000.0)), -2)

        # Current progress (0% to 65% of target)
        saved_pct = float(np.clip(np.random.beta(a=1.5, b=3.5), 0.0, 0.70))
        current_saved = round(target_amount * saved_pct, 2)

        # Target months (user intended duration)
        intended_months = int(np.random.choice([3, 6, 12, 18, 24, 36, 48, 60]))
        annual_return = float(preset["recommended_annual_return_pct"])

        # Ground truth completion months
        actual_months = calculate_months_to_goal(
            target_amount=target_amount,
            current_saved=current_saved,
            monthly_contribution=true_savings_capacity,
            annual_return_pct=annual_return,
        )

        required_monthly_savings = calculate_required_monthly_savings(
            target_amount=target_amount,
            current_saved=current_saved,
            target_months=intended_months,
            annual_return_pct=annual_return,
        )

        record = {
            "monthly_income": income,
            "total_expenses": total_exp,
            "needs_expenses": needs_exp,
            "wants_expenses": wants_exp,
            "debt_obligations": debt,
            "current_balance": current_balance,
            "discretionary_ratio": discretionary_ratio,
            "savings_rate_baseline": savings_rate,
            "goal_type": goal_type,
            "target_amount": target_amount,
            "current_saved": current_saved,
            "intended_months": intended_months,
            "annual_return_pct": annual_return,
            # Targets to predict
            "target_monthly_savings": true_savings_capacity,
            "target_completion_months": min(120.0, actual_months),
            "target_required_savings": required_monthly_savings,
        }
        rows.append(record)

    df = pd.DataFrame(rows).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def main():
    print("=" * 70)
    print("Preprocess Pipeline: Phase 6 Savings & Phase 11 Goal Datasets")
    print("=" * 70)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df = generate_synthetic_goals_dataset(num_samples=7500, seed=42)

    # 80/20 Train / Test Split
    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size].copy()
    test_df = df.iloc[train_size:].copy()

    train_df.to_csv(OUTPUT_TRAIN, index=False)
    test_df.to_csv(OUTPUT_TEST, index=False)

    print(f"[done] Total Generated Goal Profiles: {len(df):,}")
    print(f"[done] Train Set ({len(train_df):,} rows) -> {OUTPUT_TRAIN}")
    print(f"[done] Test Set  ({len(test_df):,} rows) -> {OUTPUT_TEST}")
    print(f"[info] Median Monthly Savings Capacity: INR {df['target_monthly_savings'].median():,.2f}")
    print(f"[info] Median Goal Target Amount: INR {df['target_amount'].median():,.2f}")
    print("=" * 70)


if __name__ == "__main__":
    main()
