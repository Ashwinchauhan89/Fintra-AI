"""
Preprocessing & Multi-Archetype Profile Generation Pipeline for Phase 17: Customer Segmentation.

Synthesizes 6,000 multi-demographic user financial records across 6 distinct personas:
0. Budget-Conscious Student & Early Saver
1. Young Tech Professional & High-Growth Aspirer
2. Balanced Mid-Career Family Homemaker
3. High-Net-Worth Investor & Wealth Accumulator
4. SMB Business Owner & Entrepreneur
5. Debt Rehabilitation & Overleveraged Seeker

Outputs:
- datasets/processed/segmentation_train.csv (4,800 rows)
- datasets/processed/segmentation_test.csv (1,200 rows)
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.segmentation_rules import (  # noqa: E402
    PERSONA_ARCHETYPES,
    RAW_FEATURE_COLUMNS_SEGMENTATION,
    TARGET_COLUMN_SEGMENTATION,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_TRAIN = os.path.join(PROCESSED_DIR, "segmentation_train.csv")
OUTPUT_TEST = os.path.join(PROCESSED_DIR, "segmentation_test.csv")


def generate_synthetic_segmentation_dataset(
    num_samples_per_cluster: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Synthesizes multi-demographic financial behavior vectors across all 6 archetypes.
    """
    np.random.seed(seed)
    rows = []

    for cluster_id in range(6):
        n = num_samples_per_cluster

        if cluster_id == 0:  # BUDGET_CONSCIOUS_STUDENT
            # Low income (₹12k - ₹35k), low volatility, tight essential, small savings, low/no debt
            incomes = np.clip(np.random.normal(22000, 5000, n), 12000, 38000)
            volatility = np.clip(np.random.normal(0.08, 0.04, n), 0.02, 0.20)
            ess_pct = np.clip(np.random.normal(0.55, 0.06, n), 0.40, 0.70)
            disc_pct = np.clip(np.random.normal(0.22, 0.05, n), 0.10, 0.35)
            inv_sip = np.clip(np.random.normal(1200, 500, n), 0, 3000)
            emi = np.clip(np.random.normal(500, 400, n), 0, 2000)
            limit = np.clip(np.random.normal(25000, 8000, n), 10000, 50000)
            used = np.clip(limit * np.random.uniform(0.05, 0.25, n), 0, limit)
            savings = np.clip(np.random.normal(35000, 15000, n), 5000, 90000)
            tx_count = np.random.randint(15, 60, n)
            subs = np.random.randint(1, 4, n)

        elif cluster_id == 1:  # YOUNG_TECH_PROFESSIONAL
            # High income (₹90k - ₹250k), steady, high discretionary, high equity SIP, moderate card debt
            incomes = np.clip(np.random.normal(145000, 35000, n), 80000, 280000)
            volatility = np.clip(np.random.normal(0.06, 0.03, n), 0.01, 0.15)
            ess_pct = np.clip(np.random.normal(0.35, 0.05, n), 0.25, 0.48)
            disc_pct = np.clip(np.random.normal(0.32, 0.06, n), 0.18, 0.45)
            inv_sip = np.clip(incomes * np.random.uniform(0.22, 0.40, n), 18000, 90000)
            emi = np.clip(np.random.normal(8000, 5000, n), 0, 25000)
            limit = np.clip(incomes * np.random.uniform(2.5, 5.0, n), 150000, 1000000)
            used = np.clip(limit * np.random.uniform(0.10, 0.28, n), 5000, limit)
            savings = np.clip(incomes * np.random.uniform(3.0, 7.0, n), 200000, 1800000)
            tx_count = np.random.randint(60, 180, n)
            subs = np.random.randint(4, 10, n)

        elif cluster_id == 2:  # BALANCED_FAMILY_HOMEMAKER
            # Mid income (₹60k - ₹140k), highly stable, high essential (rent, school, food), home/auto EMI, conservative savings
            incomes = np.clip(np.random.normal(95000, 20000, n), 55000, 160000)
            volatility = np.clip(np.random.normal(0.04, 0.02, n), 0.01, 0.10)
            ess_pct = np.clip(np.random.normal(0.58, 0.05, n), 0.48, 0.72)
            disc_pct = np.clip(np.random.normal(0.14, 0.04, n), 0.06, 0.22)
            inv_sip = np.clip(incomes * np.random.uniform(0.08, 0.18, n), 5000, 28000)
            emi = np.clip(incomes * np.random.uniform(0.18, 0.32, n), 10000, 50000)
            limit = np.clip(incomes * np.random.uniform(1.5, 3.5, n), 100000, 450000)
            used = np.clip(limit * np.random.uniform(0.15, 0.35, n), 8000, limit)
            savings = np.clip(incomes * np.random.uniform(4.0, 9.0, n), 250000, 1200000)
            tx_count = np.random.randint(35, 95, n)
            subs = np.random.randint(2, 6, n)

        elif cluster_id == 3:  # HIGH_NET_WORTH_INVESTOR
            # Very high income (₹250k - ₹750k+), huge surplus, high investment allocation, large emergency reserve
            incomes = np.clip(np.random.normal(380000, 90000, n), 220000, 800000)
            volatility = np.clip(np.random.normal(0.08, 0.04, n), 0.02, 0.20)
            ess_pct = np.clip(np.random.normal(0.22, 0.04, n), 0.12, 0.32)
            disc_pct = np.clip(np.random.normal(0.20, 0.05, n), 0.10, 0.32)
            inv_sip = np.clip(incomes * np.random.uniform(0.40, 0.65, n), 90000, 450000)
            emi = np.clip(np.random.normal(25000, 15000, n), 0, 75000)
            limit = np.clip(incomes * np.random.uniform(4.0, 8.0, n), 800000, 4000000)
            used = np.clip(limit * np.random.uniform(0.05, 0.18, n), 20000, limit)
            savings = np.clip(incomes * np.random.uniform(8.0, 20.0, n), 1800000, 12000000)
            tx_count = np.random.randint(70, 220, n)
            subs = np.random.randint(5, 12, n)

        elif cluster_id == 4:  # SMB_BUSINESS_OWNER
            # High income with HIGH volatility (CV 0.35 - 0.90), fluctuating revenue, working capital buffer
            incomes = np.clip(np.random.normal(190000, 60000, n), 80000, 450000)
            volatility = np.clip(np.random.normal(0.48, 0.12, n), 0.25, 0.95)
            ess_pct = np.clip(np.random.normal(0.38, 0.06, n), 0.25, 0.52)
            disc_pct = np.clip(np.random.normal(0.18, 0.05, n), 0.08, 0.30)
            inv_sip = np.clip(incomes * np.random.uniform(0.10, 0.25, n), 8000, 60000)
            emi = np.clip(incomes * np.random.uniform(0.12, 0.30, n), 8000, 80000)
            limit = np.clip(incomes * np.random.uniform(2.5, 6.0, n), 200000, 2000000)
            used = np.clip(limit * np.random.uniform(0.20, 0.55, n), 25000, limit)
            savings = np.clip(incomes * np.random.uniform(6.0, 14.0, n), 500000, 4500000)
            tx_count = np.random.randint(80, 260, n)
            subs = np.random.randint(3, 8, n)

        else:  # cluster_id == 5: DEBT_REHABILITATION_SEEKER
            # Overleveraged (Debt/EMI > 45%, Card util > 70%), low/negative surplus, minimal savings
            incomes = np.clip(np.random.normal(45000, 12000, n), 20000, 80000)
            volatility = np.clip(np.random.normal(0.10, 0.05, n), 0.02, 0.25)
            ess_pct = np.clip(np.random.normal(0.52, 0.06, n), 0.40, 0.68)
            disc_pct = np.clip(np.random.normal(0.22, 0.05, n), 0.12, 0.35)
            inv_sip = np.clip(np.random.normal(500, 400, n), 0, 2000)
            emi = np.clip(incomes * np.random.uniform(0.38, 0.65, n), 12000, 45000)
            limit = np.clip(incomes * np.random.uniform(1.8, 3.5, n), 50000, 220000)
            used = np.clip(limit * np.random.uniform(0.72, 0.98, n), 35000, limit)
            savings = np.clip(np.random.normal(8000, 5000, n), 500, 25000)
            tx_count = np.random.randint(25, 75, n)
            subs = np.random.randint(1, 5, n)

        for i in range(n):
            inc_val = round(float(incomes[i]), 2)
            ess_val = round(float(inc_val * ess_pct[i]), 2)
            disc_val = round(float(inc_val * disc_pct[i]), 2)
            rows.append({
                "monthly_income": inc_val,
                "income_volatility_cv": round(float(volatility[i]), 3),
                "monthly_essential_expenses": ess_val,
                "monthly_discretionary_spend": disc_val,
                "monthly_investments_sip": round(float(inv_sip[i]), 2),
                "existing_monthly_emi": round(float(emi[i]), 2),
                "total_credit_limit": round(float(limit[i]), 2),
                "total_credit_used": round(float(used[i]), 2),
                "total_liquid_savings": round(float(savings[i]), 2),
                "monthly_transaction_count": int(tx_count[i]),
                "active_subscriptions_count": int(subs[i]),
                TARGET_COLUMN_SEGMENTATION: cluster_id,
            })

    return pd.DataFrame(rows)


def main():
    print("[info] Synthesizing 6,000 multi-demographic persona financial records...")
    df = generate_synthetic_segmentation_dataset(num_samples_per_cluster=1000, seed=42)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 80/20 Stratified Split across persona clusters
    train_dfs, test_dfs = [], []
    for cid, group in df.groupby(TARGET_COLUMN_SEGMENTATION):
        n_test = int(len(group) * 0.20)
        shuffled = group.sample(frac=1.0, random_state=42)
        test_dfs.append(shuffled.iloc[:n_test])
        train_dfs.append(shuffled.iloc[n_test:])

    train_df = pd.concat(train_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)
    test_df = pd.concat(test_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)

    train_df.to_csv(OUTPUT_TRAIN, index=False)
    test_df.to_csv(OUTPUT_TEST, index=False)

    print(f"[done] Train records: {len(train_df)} rows -> {OUTPUT_TRAIN}")
    print(f"[done] Test records:  {len(test_df)} rows -> {OUTPUT_TEST}")
    print(f"\nPersona Archetype Distribution (Train Set):")
    for cid, pinfo in PERSONA_ARCHETYPES.items():
        count = int((train_df[TARGET_COLUMN_SEGMENTATION] == cid).sum())
        print(f"  Cluster {cid}: {pinfo['id']:30s} -> {count} profiles ({count/len(train_df)*100:.1f}%)")


if __name__ == "__main__":
    main()
