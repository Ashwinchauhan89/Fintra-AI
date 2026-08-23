"""
Preprocessing & Dataset Generation Pipeline for Subscription & Recurring Charge Detection (Phase 14).

Synthesizes realistic merchant transaction sequences across fixed subscriptions, variable utilities,
and irregular one-off discretionary purchases.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.subscription_rules import (  # noqa: E402
    FEATURE_COLUMNS_SUBSCRIPTION,
    KNOWN_SUBSCRIPTION_PATTERNS,
    estimate_cadence,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_TRAIN = os.path.join(PROCESSED_DIR, "subscriptions_train.csv")
OUTPUT_TEST = os.path.join(PROCESSED_DIR, "subscriptions_test.csv")

ADHOC_MERCHANTS = [
    ("Swiggy", "food", 350.0, 950.0),
    ("Zomato", "food", 400.0, 1100.0),
    ("Amazon India", "shopping", 800.0, 4500.0),
    ("Flipkart", "shopping", 1200.0, 6000.0),
    ("Uber", "transport", 150.0, 750.0),
    ("Ola Cabs", "transport", 180.0, 650.0),
    ("Blinkit", "food", 300.0, 1200.0),
    ("Zepto", "food", 250.0, 900.0),
    ("Zara Retail", "shopping", 2500.0, 8500.0),
    ("Apollo Pharmacy", "healthcare", 350.0, 2200.0),
    ("PVR Cinemas", "entertainment", 600.0, 1800.0),
    ("Starbucks", "food", 450.0, 1200.0),
]


def generate_synthetic_subscriptions_dataset(
    num_samples: int = 8000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates structured merchant history profiles labeled as subscription (1) vs ad-hoc (0).
    """
    np.random.seed(seed)
    records = []

    # 1. Generate True Subscriptions (45%)
    num_sub = int(num_samples * 0.45)
    known_keys = list(KNOWN_SUBSCRIPTION_PATTERNS.keys())

    for _ in range(num_sub):
        key = np.random.choice(known_keys)
        info = KNOWN_SUBSCRIPTION_PATTERNS[key]
        cadence = info["typical_cadence"]
        cat = info["category"]
        base_cost = info["typical_cost"]

        # Exact or minor variance in cost
        cost_std = float(np.random.choice([0.0, np.random.uniform(0.0, base_cost * 0.02)]))
        is_exact = 1 if cost_std == 0.0 else 0
        tx_count = int(np.random.randint(3, 24))

        if cadence == "MONTHLY":
            interval_mean = float(np.random.normal(30.2, 0.6))
            interval_std = float(np.random.uniform(0.1, 1.8))
        elif cadence == "ANNUAL":
            interval_mean = float(np.random.normal(365.0, 1.5))
            interval_std = float(np.random.uniform(0.2, 3.0))
        elif cadence == "WEEKLY":
            interval_mean = float(np.random.normal(7.0, 0.4))
            interval_std = float(np.random.uniform(0.1, 0.8))
        else:  # QUARTERLY
            interval_mean = float(np.random.normal(90.0, 1.0))
            interval_std = float(np.random.uniform(0.2, 2.5))

        records.append({
            "merchant_name": key.title(),
            "mean_amount": round(base_cost, 2),
            "amount_std": round(cost_std, 2),
            "is_exact_amount": is_exact,
            "interval_mean_days": round(interval_mean, 2),
            "interval_std_days": round(interval_std, 2),
            "transaction_count": tx_count,
            "category": cat,
            "cadence": cadence,
            "is_subscription": 1,
        })

    # 2. Generate Variable Periodic Utilities (20%)
    num_util = int(num_samples * 0.20)
    util_names = [("Bescom Electricity", "bills"), ("Delhi Jal Board", "bills"), ("Airtel Postpaid", "bills"), ("Tata Power", "bills"), ("Mahanagar Gas", "bills")]

    for _ in range(num_util):
        name, cat = util_names[np.random.randint(0, len(util_names))]
        mean_cost = float(np.random.uniform(650.0, 4500.0))
        cost_std = float(mean_cost * np.random.uniform(0.08, 0.25))  # Moderate variance
        tx_count = int(np.random.randint(3, 18))
        interval_mean = float(np.random.normal(30.5, 1.2))
        interval_std = float(np.random.uniform(1.2, 4.5))

        records.append({
            "merchant_name": name,
            "mean_amount": round(mean_cost, 2),
            "amount_std": round(cost_std, 2),
            "is_exact_amount": 0,
            "interval_mean_days": round(interval_mean, 2),
            "interval_std_days": round(interval_std, 2),
            "transaction_count": tx_count,
            "category": cat,
            "cadence": "MONTHLY",
            "is_subscription": 1,
        })

    # 3. Generate Ad-Hoc / One-Off Random Purchases (35%)
    num_adhoc = num_samples - len(records)
    for _ in range(num_adhoc):
        name, cat, min_c, max_c = ADHOC_MERCHANTS[np.random.randint(0, len(ADHOC_MERCHANTS))]
        mean_cost = float(np.random.uniform(min_c, max_c))
        cost_std = float(mean_cost * np.random.uniform(0.35, 0.90))  # High variance in amount
        tx_count = int(np.random.randint(1, 15))
        # Erratic random intervals
        interval_mean = float(np.random.uniform(3.0, 45.0))
        interval_std = float(np.random.uniform(12.0, 35.0))  # High interval variance

        records.append({
            "merchant_name": name,
            "mean_amount": round(mean_cost, 2),
            "amount_std": round(cost_std, 2),
            "is_exact_amount": 0,
            "interval_mean_days": round(interval_mean, 2),
            "interval_std_days": round(interval_std, 2),
            "transaction_count": tx_count,
            "category": cat,
            "cadence": "NONE",
            "is_subscription": 0,
        })

    df = pd.DataFrame(records).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def main():
    print("=" * 70)
    print("Preprocess Pipeline: Phase 14 Subscription & Recurring Datasets")
    print("=" * 70)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df = generate_synthetic_subscriptions_dataset(num_samples=8000, seed=42)

    # 80/20 Train / Test Split
    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size].copy()
    test_df = df.iloc[train_size:].copy()

    train_df.to_csv(OUTPUT_TRAIN, index=False)
    test_df.to_csv(OUTPUT_TEST, index=False)

    print(f"[done] Total Generated Sequences: {len(df):,}")
    print(f"[done] Train Set ({len(train_df):,} rows, {train_df['is_subscription'].sum()} subscriptions) -> {OUTPUT_TRAIN}")
    print(f"[done] Test Set  ({len(test_df):,} rows, {test_df['is_subscription'].sum()} subscriptions) -> {OUTPUT_TEST}")
    print(f"[info] Subscription Class Prevalence: {df['is_subscription'].mean():.2%}")
    print("=" * 70)


if __name__ == "__main__":
    main()
