"""
Preprocessing & Synthetic Application Generation Pipeline for Phase 12: Loan Eligibility.

Synthesizes 6,000 multi-demographic loan applications across:
- Income brackets: ₹15,000 to ₹400,000/month
- Credit scores: 300 to 900 (Imbalanced realistic distribution)
- Loan purposes: HOME_LOAN, PERSONAL_LOAN, AUTO_VEHICLE_LOAN, EDUCATION_LOAN, BUSINESS_EXPANSION
- Diverse employment types and tenures

Outputs:
- datasets/processed/loan_train.csv (4,800 rows)
- datasets/processed/loan_test.csv (1,200 rows)
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.loan_rules import (  # noqa: E402
    LOAN_PURPOSE_POLICIES,
    EMPLOYMENT_STABILITY_WEIGHTS,
    RAW_FEATURE_COLUMNS_LOAN,
    TARGET_COLUMN_LOAN,
    calculate_monthly_emi,
    get_effective_interest_rate,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_TRAIN = os.path.join(PROCESSED_DIR, "loan_train.csv")
OUTPUT_TEST = os.path.join(PROCESSED_DIR, "loan_test.csv")


def generate_synthetic_loan_dataset(
    num_samples: int = 6000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates realistic loan applications with ground-truth eligibility, default risk,
    and realistic non-linear borrower friction.
    """
    np.random.seed(seed)
    purposes = list(LOAN_PURPOSE_POLICIES.keys())
    emp_types = list(EMPLOYMENT_STABILITY_WEIGHTS.keys())

    # Incomes: Log-normal distribution (₹15,000 to ₹450,000)
    log_incomes = np.random.normal(loc=11.1, scale=0.68, size=num_samples)
    monthly_incomes = np.clip(np.exp(log_incomes), 15000.0, 450000.0).round(2)

    # Credit scores: 300 to 900 (Bimodal: bulk in 680-780, tail in 350-620)
    cscore_main = np.random.normal(loc=735, scale=55, size=int(num_samples * 0.78))
    cscore_subprime = np.random.normal(loc=560, scale=80, size=num_samples - len(cscore_main))
    credit_scores = np.clip(np.concatenate([cscore_main, cscore_subprime]), 300, 900).astype(int)
    np.random.shuffle(credit_scores)

    # Employment types and tenure
    emp_choices = np.random.choice(
        emp_types,
        p=[0.25, 0.40, 0.15, 0.10, 0.08, 0.02],
        size=num_samples,
    )
    job_tenures = np.clip(np.random.exponential(scale=4.5, size=num_samples), 0.2, 35.0).round(1)

    # Loan Purposes
    purpose_choices = np.random.choice(
        purposes,
        p=[0.30, 0.30, 0.20, 0.10, 0.10],
        size=num_samples,
    )

    rows = []
    for i in range(num_samples):
        income = monthly_incomes[i]
        cscore = int(credit_scores[i])
        emp_type = emp_choices[i]
        tenure_yrs = float(job_tenures[i])
        purpose = purpose_choices[i]
        policy = LOAN_PURPOSE_POLICIES[purpose]

        # Loan tenure requested
        min_t, max_t = policy["min_tenure_months"], policy["max_tenure_months"]
        tenure_months = int(np.random.choice(np.linspace(min_t, max_t, num=6)))

        # Requested loan amount scaled by income and purpose
        if purpose == "HOME_LOAN":
            multiplier = np.clip(np.random.normal(30.0, 12.0), 10.0, 65.0)
            req_amount = round(float(income * multiplier), -4)
        elif purpose == "AUTO_VEHICLE_LOAN":
            multiplier = np.clip(np.random.normal(8.0, 3.5), 3.0, 18.0)
            req_amount = round(float(income * multiplier), -3)
        elif purpose == "PERSONAL_LOAN":
            multiplier = np.clip(np.random.normal(4.5, 2.5), 1.0, 12.0)
            req_amount = round(float(income * multiplier), -3)
        elif purpose == "EDUCATION_LOAN":
            multiplier = np.clip(np.random.normal(12.0, 5.0), 4.0, 25.0)
            req_amount = round(float(income * multiplier), -4)
        else:  # BUSINESS_EXPANSION
            multiplier = np.clip(np.random.normal(15.0, 7.0), 5.0, 35.0)
            req_amount = round(float(income * multiplier), -4)

        req_amount = max(25000.0, req_amount)

        # Baseline living expenses: 35% to 70% of income
        expense_ratio = np.clip(np.random.normal(0.48, 0.08), 0.25, 0.78)
        monthly_expenses = round(float(income * expense_ratio), 2)

        # Existing EMIs & Debt
        has_existing_debt = np.random.rand() < 0.50
        if has_existing_debt:
            existing_foir = np.clip(np.random.normal(0.20, 0.10), 0.05, 0.55)
            existing_monthly_emi = round(float(income * existing_foir), 2)
            existing_debt_total = round(float(existing_monthly_emi * np.random.uniform(12, 48)), 2)
        else:
            existing_monthly_emi = 0.0
            existing_debt_total = 0.0

        # Liquid savings reserve
        savings_multiple = np.clip(np.random.normal(4.0, 3.5), 0.1, 25.0)
        liquid_savings = round(float(monthly_expenses * savings_multiple), 2)

        # Ground-Truth Banking Underwriting Decision Logic
        interest_rate = get_effective_interest_rate(purpose, cscore)
        proposed_emi = calculate_monthly_emi(req_amount, interest_rate, tenure_months)
        total_emi = existing_monthly_emi + proposed_emi
        foir = total_emi / income
        disposable = income - monthly_expenses - total_emi
        emp_weight = EMPLOYMENT_STABILITY_WEIGHTS[emp_type]

        # Multi-factor Eligibility Rule:
        # 1. FOIR must be within policy ceiling (with slight tolerance for high-credit prime borrowers)
        foir_ceiling = policy["max_foir_limit"]
        if cscore >= 760:
            foir_ceiling += 0.05  # 5% leniency for prime borrowers
        elif cscore < 620:
            foir_ceiling -= 0.08  # Stricter for subprime

        # 2. Credit score check
        cscore_pass = cscore >= policy["min_credit_score"]

        # 3. Employment check
        emp_pass = emp_type != "UNEMPLOYED" and (tenure_yrs >= 0.5 or emp_weight >= 0.85)

        # 4. Disposable cushion check (Must have positive free cashflow)
        disposable_pass = disposable > (income * 0.10)

        # Comprehensive Underwriting Verdict:
        is_eligible = int(foir <= foir_ceiling and cscore_pass and emp_pass and disposable_pass)

        # Realistic edge-case noise: ~2.5% manual underwriter override
        if np.random.rand() < 0.025:
            is_eligible = 1 - is_eligible

        row = {
            "monthly_income": income,
            "requested_loan_amount": req_amount,
            "loan_tenure_months": tenure_months,
            "loan_purpose": purpose,
            "existing_monthly_emi": existing_monthly_emi,
            "existing_debt_total": existing_debt_total,
            "credit_score": cscore,
            "employment_type": emp_type,
            "employment_tenure_years": tenure_yrs,
            "monthly_expenses": monthly_expenses,
            "liquid_savings": liquid_savings,
            "is_eligible": is_eligible,
        }
        rows.append(row)

    return pd.DataFrame(rows)


def main():
    print("[info] Synthesizing 6,000 multi-demographic loan application profiles...")
    df = generate_synthetic_loan_dataset(num_samples=6000, seed=42)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 80/20 Stratified Split across target is_eligible
    train_dfs, test_dfs = [], []
    for val, group in df.groupby(TARGET_COLUMN_LOAN):
        n_test = int(len(group) * 0.20)
        shuffled = group.sample(frac=1.0, random_state=42)
        test_dfs.append(shuffled.iloc[:n_test])
        train_dfs.append(shuffled.iloc[n_test:])

    train_df = pd.concat(train_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)
    test_df = pd.concat(test_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)

    train_df.to_csv(OUTPUT_TRAIN, index=False)
    test_df.to_csv(OUTPUT_TEST, index=False)

    print(f"[done] Train applications: {len(train_df)} rows -> {OUTPUT_TRAIN}")
    print(f"[done] Test applications:  {len(test_df)} rows -> {OUTPUT_TEST}")
    print(f"\nTarget Class Distribution:")
    print(f"  Approved (1): {int((train_df[TARGET_COLUMN_LOAN] == 1).sum())} ({train_df[TARGET_COLUMN_LOAN].mean()*100:.1f}%)")
    print(f"  Rejected (0): {int((train_df[TARGET_COLUMN_LOAN] == 0).sum())} ({(1 - train_df[TARGET_COLUMN_LOAN].mean())*100:.1f}%)")


if __name__ == "__main__":
    main()
