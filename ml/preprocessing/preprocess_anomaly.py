"""
Preprocessing & Dataset Generation Pipeline for Fraud Detection & Spending Anomaly Engine (Phases 8 & 9).

Synthesizes realistic transaction streams combining empirical distributions with rare, sophisticated
fraud anomalies (velocity bursts, geographical drift, night-time bursts, high risk merchants).
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.anomaly_features import (  # noqa: E402
    CATEGORY_SPENDING_BASELINES,
    FEATURE_COLUMNS,
    ROADMAP_CATEGORIES,
    extract_transaction_features,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_TRAIN = os.path.join(PROCESSED_DIR, "anomaly_train.csv")
OUTPUT_TEST = os.path.join(PROCESSED_DIR, "anomaly_test.csv")


def generate_synthetic_anomaly_dataset(
    num_samples: int = 10000,
    fraud_rate: float = 0.035,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates a balanced realistic transaction stream with labeled fraud (1) vs normal (0).
    """
    np.random.seed(seed)
    num_fraud = int(num_samples * fraud_rate)
    num_normal = num_samples - num_fraud

    records = []

    # 1. Generate Normal Transactions (96.5%)
    for _ in range(num_normal):
        cat = np.random.choice(ROADMAP_CATEGORIES, p=[0.28, 0.26, 0.18, 0.10, 0.10, 0.05, 0.03])
        baseline = CATEGORY_SPENDING_BASELINES[cat]

        # Normal log-normal amount around category median
        amount = float(np.clip(np.random.lognormal(mean=np.log(baseline["median"]), sigma=0.65), 10.0, baseline["p95"] * 1.5))
        amount = round(amount, 2)

        # Normal hours: mostly 8 AM to 10 PM
        hour = int(np.clip(np.random.normal(loc=15, scale=4), 6, 23))
        is_weekend = int(np.random.choice([0, 1], p=[0.72, 0.28]))

        # Normal device and local location
        distance = float(np.clip(np.random.exponential(scale=8.0), 0.5, 45.0))
        device_trust = float(np.clip(np.random.normal(loc=0.92, scale=0.08), 0.65, 1.0))
        merchant_risk = float(np.clip(np.random.beta(a=1.5, b=8.0), 0.01, 0.35))
        velocity = int(np.random.choice([1, 2, 3], p=[0.85, 0.12, 0.03]))
        is_foreign = 0

        feat = extract_transaction_features(
            amount=amount,
            category=cat,
            hour_of_day=hour,
            is_weekend=is_weekend,
            distance_from_home_km=distance,
            device_trust_score=device_trust,
            merchant_risk_score=merchant_risk,
            velocity_1h=velocity,
            is_foreign_currency=is_foreign,
        )
        feat["category"] = cat
        feat["is_fraud"] = 0
        feat["is_anomaly"] = 0
        records.append(feat)

    # 2. Generate Fraud & Anomaly Transactions (3.5%)
    fraud_types = ["spike_amount", "night_foreign", "rapid_burst", "untrusted_device_high_risk"]

    for _ in range(num_fraud):
        f_type = np.random.choice(fraud_types)
        cat = np.random.choice(ROADMAP_CATEGORIES)
        baseline = CATEGORY_SPENDING_BASELINES[cat]

        if f_type == "spike_amount":
            # 6x to 25x normal median
            amount = round(float(baseline["median"] * np.random.uniform(7.0, 25.0)), 2)
            hour = int(np.random.randint(0, 24))
            distance = float(np.random.uniform(50.0, 800.0))
            device_trust = float(np.random.uniform(0.10, 0.60))
            merchant_risk = float(np.random.uniform(0.40, 0.90))
            velocity = int(np.random.choice([1, 2, 4], p=[0.5, 0.3, 0.2]))
            is_foreign = int(np.random.choice([0, 1], p=[0.7, 0.3]))

        elif f_type == "night_foreign":
            amount = round(float(np.random.uniform(15000.0, 95000.0)), 2)
            hour = int(np.random.choice([1, 2, 3, 4, 5]))  # Off-hours
            distance = float(np.random.uniform(800.0, 4500.0))  # Distant location
            device_trust = float(np.random.uniform(0.05, 0.30))  # New device
            merchant_risk = float(np.random.uniform(0.60, 0.95))
            velocity = int(np.random.choice([1, 2], p=[0.7, 0.3]))
            is_foreign = 1

        elif f_type == "rapid_burst":
            amount = round(float(baseline["median"] * np.random.uniform(2.0, 6.0)), 2)
            hour = int(np.random.randint(0, 24))
            distance = float(np.random.uniform(10.0, 300.0))
            device_trust = float(np.random.uniform(0.20, 0.70))
            merchant_risk = float(np.random.uniform(0.50, 0.85))
            velocity = int(np.random.choice([4, 5, 6, 8]))  # High velocity burst
            is_foreign = int(np.random.choice([0, 1], p=[0.8, 0.2]))

        else:  # untrusted_device_high_risk
            amount = round(float(baseline["p95"] * np.random.uniform(1.8, 5.0)), 2)
            hour = int(np.random.choice([0, 1, 2, 22, 23]))
            distance = float(np.random.uniform(400.0, 2000.0))
            device_trust = float(np.random.uniform(0.0, 0.20))
            merchant_risk = float(np.random.uniform(0.70, 0.98))
            velocity = int(np.random.choice([2, 3, 4]))
            is_foreign = int(np.random.choice([0, 1], p=[0.5, 0.5]))

        is_weekend = int(np.random.choice([0, 1]))
        feat = extract_transaction_features(
            amount=amount,
            category=cat,
            hour_of_day=hour,
            is_weekend=is_weekend,
            distance_from_home_km=distance,
            device_trust_score=device_trust,
            merchant_risk_score=merchant_risk,
            velocity_1h=velocity,
            is_foreign_currency=is_foreign,
        )
        feat["category"] = cat
        feat["is_fraud"] = 1
        feat["is_anomaly"] = 1
        records.append(feat)

    df = pd.DataFrame(records).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def main():
    print("=" * 65)
    print("Preprocess Pipeline: Phase 8 Fraud & Phase 9 Anomaly Datasets")
    print("=" * 65)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df = generate_synthetic_anomaly_dataset(num_samples=10000, fraud_rate=0.035, seed=42)

    # 80/20 Stratified Train / Test Split
    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size].copy()
    test_df = df.iloc[train_size:].copy()

    train_df.to_csv(OUTPUT_TRAIN, index=False)
    test_df.to_csv(OUTPUT_TEST, index=False)

    print(f"[done] Total Generated Records: {len(df):,}")
    print(f"[done] Train Set ({len(train_df):,} rows, {train_df['is_fraud'].sum()} fraud) -> {OUTPUT_TRAIN}")
    print(f"[done] Test Set  ({len(test_df):,} rows, {test_df['is_fraud'].sum()} fraud) -> {OUTPUT_TEST}")
    print(f"[info] Baseline Fraud / Anomaly Prevalence: {df['is_fraud'].mean():.2%}")
    print("=" * 65)


if __name__ == "__main__":
    main()
