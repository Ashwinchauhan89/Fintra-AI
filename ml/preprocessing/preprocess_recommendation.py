"""
Preprocessing & Synthetic Profile Generation Pipeline for Phase 16: Financial Product Recommendation.

Synthesizes 6,000 multi-demographic user records with category spends, credit profiles,
persona archetypes, and optimal product engagement targets across:
- Dining / Foodie spenders
- Frequent flyers & Travel spenders
- Utility & Grocery family spenders
- High-Net-Worth investors
- Debt-distressed users needing balance transfers

Outputs:
- datasets/processed/recommendation_train.csv (4,800 rows)
- datasets/processed/recommendation_test.csv (1,200 rows)
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.recommendation_rules import (  # noqa: E402
    PRODUCT_CATALOG,
    calculate_product_net_annual_value,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_TRAIN = os.path.join(PROCESSED_DIR, "recommendation_train.csv")
OUTPUT_TEST = os.path.join(PROCESSED_DIR, "recommendation_test.csv")


def generate_synthetic_recommendation_dataset(
    num_samples: int = 6000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates synthetic user spending records and computes optimal product matches.
    """
    np.random.seed(seed)
    personas = [
        "BUDGET_CONSCIOUS_STUDENT",
        "YOUNG_TECH_PROFESSIONAL",
        "BALANCED_FAMILY_HOMEMAKER",
        "HIGH_NET_WORTH_INVESTOR",
        "SMB_BUSINESS_OWNER",
        "DEBT_REHABILITATION_SEEKER",
    ]

    rows = []
    for _ in range(num_samples):
        persona = np.random.choice(personas, p=[0.18, 0.25, 0.25, 0.12, 0.10, 0.10])

        if persona == "BUDGET_CONSCIOUS_STUDENT":
            income = float(np.random.uniform(15000, 35000))
            cscore = int(np.random.choice([300, 650, 710, 730], p=[0.35, 0.25, 0.25, 0.15]))
            dining = float(np.random.uniform(1500, 6000))
            shopping = float(np.random.uniform(1000, 4000))
            groceries = float(np.random.uniform(2000, 5000))
            travel = float(np.random.uniform(500, 2000))
            fuel = float(np.random.uniform(500, 1500))
            utilities = float(np.random.uniform(800, 2000))
            savings = float(np.random.uniform(10000, 50000))
            debt = 0.0

        elif persona == "YOUNG_TECH_PROFESSIONAL":
            income = float(np.random.uniform(90000, 260000))
            cscore = int(np.random.uniform(730, 830))
            dining = float(np.random.uniform(8000, 25000))
            shopping = float(np.random.uniform(12000, 35000))
            groceries = float(np.random.uniform(6000, 15000))
            travel = float(np.random.uniform(10000, 45000))
            fuel = float(np.random.uniform(2000, 8000))
            utilities = float(np.random.uniform(3000, 8000))
            savings = float(np.random.uniform(250000, 1500000))
            debt = float(np.random.uniform(0, 50000))

        elif persona == "BALANCED_FAMILY_HOMEMAKER":
            income = float(np.random.uniform(65000, 140000))
            cscore = int(np.random.uniform(710, 790))
            dining = float(np.random.uniform(3000, 9000))
            shopping = float(np.random.uniform(5000, 15000))
            groceries = float(np.random.uniform(12000, 28000))
            travel = float(np.random.uniform(2000, 8000))
            fuel = float(np.random.uniform(4000, 12000))
            utilities = float(np.random.uniform(6000, 18000))
            savings = float(np.random.uniform(300000, 1200000))
            debt = float(np.random.uniform(10000, 120000))

        elif persona == "HIGH_NET_WORTH_INVESTOR":
            income = float(np.random.uniform(280000, 750000))
            cscore = int(np.random.uniform(780, 890))
            dining = float(np.random.uniform(20000, 60000))
            shopping = float(np.random.uniform(30000, 90000))
            groceries = float(np.random.uniform(15000, 35000))
            travel = float(np.random.uniform(40000, 150000))
            fuel = float(np.random.uniform(6000, 20000))
            utilities = float(np.random.uniform(8000, 25000))
            savings = float(np.random.uniform(2500000, 15000000))
            debt = float(np.random.uniform(0, 150000))

        elif persona == "SMB_BUSINESS_OWNER":
            income = float(np.random.uniform(120000, 400000))
            cscore = int(np.random.uniform(690, 780))
            dining = float(np.random.uniform(6000, 20000))
            shopping = float(np.random.uniform(10000, 40000))
            groceries = float(np.random.uniform(8000, 20000))
            travel = float(np.random.uniform(12000, 40000))
            fuel = float(np.random.uniform(8000, 25000))
            utilities = float(np.random.uniform(10000, 35000))
            savings = float(np.random.uniform(600000, 3500000))
            debt = float(np.random.uniform(50000, 300000))

        else:  # DEBT_REHABILITATION_SEEKER
            income = float(np.random.uniform(30000, 75000))
            cscore = int(np.random.uniform(520, 640))
            dining = float(np.random.uniform(2000, 6000))
            shopping = float(np.random.uniform(3000, 8000))
            groceries = float(np.random.uniform(6000, 14000))
            travel = float(np.random.uniform(1000, 3000))
            fuel = float(np.random.uniform(2000, 5000))
            utilities = float(np.random.uniform(3000, 7000))
            savings = float(np.random.uniform(2000, 30000))
            debt = float(np.random.uniform(80000, 350000))

        user_spends = {
            "dining": round(dining, 2),
            "shopping": round(shopping, 2),
            "groceries": round(groceries, 2),
            "travel": round(travel, 2),
            "fuel": round(fuel, 2),
            "utilities": round(utilities, 2),
            "monthly_income": round(income, 2),
        }

        # Calculate optimal ground-truth product (Highest Net Annual Value among eligible products)
        best_pid = None
        best_nav = -1e9

        for prod in PRODUCT_CATALOG:
            # Eligibility check
            if cscore < prod["min_credit_score"] or income < prod["min_monthly_income"]:
                continue
            nav, _ = calculate_product_net_annual_value(prod, user_spends, savings, debt)
            if nav > best_nav:
                best_nav = nav
                best_pid = prod["product_id"]

        if best_pid is None:
            best_pid = "CC_IDFC_FIRST_WOW"  # Fallback zero-barrier card

        row = {
            "persona_id": persona,
            "monthly_income": round(income, 2),
            "credit_score": cscore,
            "spend_dining": round(dining, 2),
            "spend_shopping": round(shopping, 2),
            "spend_groceries": round(groceries, 2),
            "spend_travel": round(travel, 2),
            "spend_fuel": round(fuel, 2),
            "spend_utilities": round(utilities, 2),
            "liquid_savings": round(savings, 2),
            "existing_debt": round(debt, 2),
            "optimal_product_id": best_pid,
            "top_net_annual_value": round(best_nav, 2),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def main():
    print("[info] Synthesizing 6,000 multi-demographic financial recommendation records...")
    df = generate_synthetic_recommendation_dataset(num_samples=6000, seed=42)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 80/20 Train/Test Split
    shuffled = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    n_test = int(len(df) * 0.20)

    test_df = shuffled.iloc[:n_test].reset_index(drop=True)
    train_df = shuffled.iloc[n_test:].reset_index(drop=True)

    train_df.to_csv(OUTPUT_TRAIN, index=False)
    test_df.to_csv(OUTPUT_TEST, index=False)

    print(f"[done] Train records: {len(train_df)} rows -> {OUTPUT_TRAIN}")
    print(f"[done] Test records:  {len(test_df)} rows -> {OUTPUT_TEST}")
    print("\nOptimal Product Distribution in Train Set:")
    print(train_df["optimal_product_id"].value_counts())


if __name__ == "__main__":
    main()
