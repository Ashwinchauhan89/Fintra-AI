"""
Preprocessing & Synthetic Profile Generation Pipeline for Phase 13: Credit Score Estimator.

Synthesizes 6,000 multi-demographic financial profiles across all credit health tiers:
- Excellent (780–900)
- Good (720–779)
- Fair / Near-Prime (660–719)
- Poor (580–659)
- Very Poor / Subprime (300–579)

Outputs:
- datasets/processed/credit_train.csv (4,800 rows)
- datasets/processed/credit_test.csv (1,200 rows)
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.credit_rules import (  # noqa: E402
    RAW_FEATURE_COLUMNS_CREDIT,
    SCORE_MAX,
    SCORE_MIN,
    TARGET_COLUMN_CREDIT,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_TRAIN = os.path.join(PROCESSED_DIR, "credit_train.csv")
OUTPUT_TEST = os.path.join(PROCESSED_DIR, "credit_test.csv")


def generate_synthetic_credit_dataset(
    num_samples: int = 6000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates realistic user credit records with ground-truth CIBIL/FICO 5-pillar scores.
    """
    np.random.seed(seed)

    # Incomes: Log-normal distribution (₹15,000 to ₹400,000)
    log_incomes = np.random.normal(loc=11.1, scale=0.68, size=num_samples)
    monthly_incomes = np.clip(np.exp(log_incomes), 15000.0, 450000.0).round(2)

    # Credit History Length (Years): 0.5 to 25.0 years
    credit_ages = np.clip(np.random.exponential(scale=5.5, size=num_samples), 0.5, 25.0).round(1)

    # Active credit accounts
    num_accounts = np.random.randint(1, 12, size=num_samples)

    # Hard inquiries in last 6 months (Poisson distributed)
    inquiries = np.clip(np.random.poisson(lam=1.4, size=num_samples), 0, 8)

    rows = []
    for i in range(num_samples):
        income = monthly_incomes[i]
        c_age = float(credit_ages[i])
        n_acc = int(num_accounts[i])
        n_inq = int(inquiries[i])

        # Credit Limit: 1x to 15x monthly income
        limit_multiple = np.clip(np.random.normal(3.5, 2.0), 0.5, 18.0)
        total_limit = round(float(income * limit_multiple), -3)
        total_limit = max(15000.0, total_limit)

        # Credit Utilization: Beta distribution (Clusters around 15-35%, with long tail to 95%)
        util_ratio = np.clip(np.random.beta(a=1.8, b=3.5), 0.02, 0.98)
        total_used = round(float(total_limit * util_ratio), 2)

        # Repayment Discipline
        # Subprime vs Prime segmentation
        is_subprime_tendency = np.random.rand() < 0.22
        if is_subprime_tendency:
            on_time_pct = round(float(np.random.uniform(70.0, 94.0)), 1)
            missed_count = int(np.random.choice([2, 3, 4, 5], p=[0.4, 0.3, 0.2, 0.1]))
        else:
            on_time_pct = round(float(np.random.uniform(96.0, 100.0)), 1)
            missed_count = int(np.random.choice([0, 1], p=[0.85, 0.15]))

        # Credit Mix (Secured vs Unsecured)
        secured_count = int(np.random.choice([0, 1, 2], p=[0.45, 0.40, 0.15]))
        unsecured_count = max(1, n_acc - secured_count)

        # Existing total debt
        existing_debt = round(float(total_used + (secured_count * income * np.random.uniform(5, 25))), 2)

        # Ground-truth 5-Pillar Score Calculation (Base 300 to 900)
        # Pillar 1: Payment History (35% -> up to 210 points)
        pay_points = (on_time_pct / 100.0) * np.exp(-0.48 * missed_count) * 210.0

        # Direct Delinquency Shock: Each missed payment drops score by an additional -40 points
        direct_missed_penalty = missed_count * 45.0

        # Pillar 2: Credit Utilization (30% -> up to 180 points)
        if util_ratio <= 0.10:
            util_points = 180.0
        elif util_ratio <= 0.30:
            util_points = 180.0 - (util_ratio - 0.10) * 220.0  # 180 to 136
        elif util_ratio <= 0.50:
            util_points = 136.0 - (util_ratio - 0.30) * 320.0  # 136 to 72
        else:
            util_points = max(10.0, 72.0 - (util_ratio - 0.50) * 140.0)

        # Pillar 3: Credit Age & Maturity (15% -> up to 90 points)
        age_points = min(90.0, (c_age / 12.0) * 90.0)

        # Pillar 4: Credit Mix & Diversity (10% -> up to 60 points)
        if secured_count > 0 and unsecured_count > 0:
            mix_points = 60.0
        elif secured_count > 0:
            mix_points = 48.0
        else:
            mix_points = 35.0

        # Pillar 5: New Inquiries & Hard Pulls (10% -> up to 60 points)
        if n_inq == 0:
            inq_points = 60.0
        elif n_inq <= 2:
            inq_points = 48.0
        elif n_inq <= 4:
            inq_points = 28.0
        else:
            inq_points = max(0.0, 60.0 - (n_inq * 12.0))

        # Thin-File Seasoning Dampener (Accounts under 2.0 years old cannot get a 800+ score without history)
        thin_file_dampener = 1.0
        if c_age < 1.0:
            thin_file_dampener = 0.88
        elif c_age < 2.0:
            thin_file_dampener = 0.94

        # Base 300 + Pillar Points (Max 600) + Realistic demographic Gaussian jitter
        raw_pillar_sum = (pay_points + util_points + age_points + mix_points + inq_points) * thin_file_dampener
        raw_score = 300.0 + raw_pillar_sum - direct_missed_penalty
        final_score = int(np.clip(raw_score + np.random.normal(0, 2.5), SCORE_MIN, SCORE_MAX))

        row = {
            "monthly_income": income,
            "total_credit_limit": total_limit,
            "total_credit_used": total_used,
            "on_time_payment_pct": on_time_pct,
            "missed_payments_count_2yr": missed_count,
            "credit_history_years": c_age,
            "num_active_credit_lines": n_acc,
            "secured_loans_count": secured_count,
            "unsecured_loans_count": unsecured_count,
            "hard_inquiries_last_6mo": n_inq,
            "existing_total_debt": existing_debt,
            "credit_score": final_score,
        }
        rows.append(row)

    return pd.DataFrame(rows)


def main():
    print("[info] Synthesizing 6,000 multi-demographic credit score records...")
    df = generate_synthetic_credit_dataset(num_samples=6000, seed=42)

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
    print(f"\nCredit Score Distribution Summary:")
    print(f"  Mean Score: {train_df[TARGET_COLUMN_CREDIT].mean():.1f}")
    print(f"  Min Score:  {train_df[TARGET_COLUMN_CREDIT].min()}")
    print(f"  Max Score:  {train_df[TARGET_COLUMN_CREDIT].max()}")


if __name__ == "__main__":
    main()
