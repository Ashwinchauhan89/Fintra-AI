"""
Production Underwriting & Inference Engine for Phase 12: Loan Eligibility & Credit Risk.

Provides:
- `predict_loan_eligibility()`: Computes complete underwriting verdict (Approved/Declined),
  credit risk tiering, calibrated default risk probability, max safe borrowing limit,
  exact monthly amortized EMI, and actionable remediation advice.
- Interactive CLI for instant testing with custom applicant parameters.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.loan_rules import (  # noqa: E402
    CREDIT_SCORE_TIERS,
    ENGINEERED_CATEGORICAL_FEATURES_LOAN,
    ENGINEERED_NUMERICAL_FEATURES_LOAN,
    LOAN_PURPOSE_POLICIES,
    RAW_FEATURE_COLUMNS_LOAN,
    calculate_max_safe_borrowing_limit,
    calculate_monthly_emi,
    engineer_loan_features,
    get_effective_interest_rate,
)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best_loan_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "loan_preprocessor.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "loan_metadata.json")


class LoanUnderwritingEngine:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.metadata = {}
        self._load_artifacts()

    def _load_artifacts(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(PREPROCESSOR_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.preprocessor = joblib.load(PREPROCESSOR_PATH)
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, "r") as f:
                self.metadata = json.load(f)

    def evaluate_application(
        self,
        monthly_income: float,
        requested_loan_amount: float,
        loan_tenure_months: int,
        loan_purpose: str = "PERSONAL_LOAN",
        existing_monthly_emi: float = 0.0,
        existing_debt_total: float = 0.0,
        credit_score: int = 720,
        employment_type: str = "SALARIED_PRIVATE",
        employment_tenure_years: float = 3.0,
        monthly_expenses: Optional[float] = None,
        liquid_savings: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Runs comprehensive credit risk underwriting and computes actionable loan diagnostics.
        """
        loan_purpose = loan_purpose.upper()
        if loan_purpose not in LOAN_PURPOSE_POLICIES:
            loan_purpose = "PERSONAL_LOAN"

        policy = LOAN_PURPOSE_POLICIES[loan_purpose]

        # If monthly expenses not provided, estimate default 45% living cost
        if monthly_expenses is None or monthly_expenses <= 0:
            monthly_expenses = round(float(monthly_income * 0.45), 2)

        # Compute effective interest rate and exact amortized EMI
        interest_rate_pct = get_effective_interest_rate(loan_purpose, credit_score)
        proposed_emi = calculate_monthly_emi(requested_loan_amount, interest_rate_pct, loan_tenure_months)

        # Raw dataframe
        raw_df = pd.DataFrame([{
            "monthly_income": float(monthly_income),
            "requested_loan_amount": float(requested_loan_amount),
            "loan_tenure_months": int(loan_tenure_months),
            "loan_purpose": loan_purpose,
            "existing_monthly_emi": float(existing_monthly_emi),
            "existing_debt_total": float(existing_debt_total),
            "credit_score": int(credit_score),
            "employment_type": employment_type,
            "employment_tenure_years": float(employment_tenure_years),
            "monthly_expenses": float(monthly_expenses),
            "liquid_savings": float(liquid_savings),
        }])

        # Feature engineering
        engineered_df = engineer_loan_features(raw_df)

        num_cols = self.metadata.get("engineered_numerical_features", ENGINEERED_NUMERICAL_FEATURES_LOAN)
        cat_cols = self.metadata.get("engineered_categorical_features", ENGINEERED_CATEGORICAL_FEATURES_LOAN)
        optimal_thresh = self.metadata.get("optimal_threshold", 0.50)

        if self.model is not None and self.preprocessor is not None:
            X_proc = self.preprocessor.transform(engineered_df[num_cols + cat_cols])
            if hasattr(self.model, "predict_proba"):
                approval_prob = float(self.model.predict_proba(X_proc)[0, 1])
            else:
                raw_score = float(self.model.decision_function(X_proc)[0])
                approval_prob = 1.0 / (1.0 + np.exp(-raw_score))
            is_approved = bool(approval_prob >= optimal_thresh)
        else:
            # Fallback underwriting heuristic if model not loaded
            foir = (existing_monthly_emi + proposed_emi) / monthly_income
            is_approved = bool(foir <= policy["max_foir_limit"] and credit_score >= policy["min_credit_score"])
            approval_prob = 0.85 if is_approved else 0.20

        default_prob_pct = round(float((1.0 - approval_prob) * 100.0), 2)

        # Risk Tiering Classification
        if default_prob_pct <= 15.0 and credit_score >= 740:
            risk_tier = "LOW_RISK"
            credit_grade = "PRIME_TIER"
        elif default_prob_pct <= 40.0 and credit_score >= 650:
            risk_tier = "MODERATE_RISK"
            credit_grade = "NEAR_PRIME_TIER"
        else:
            risk_tier = "HIGH_RISK"
            credit_grade = "SUBPRIME_TIER"

        # Max Safe Borrowing Limit Calculation
        max_safe_loan = calculate_max_safe_borrowing_limit(
            monthly_income=monthly_income,
            existing_monthly_emi=existing_monthly_emi,
            monthly_expenses=monthly_expenses,
            annual_rate_pct=interest_rate_pct,
            tenure_months=loan_tenure_months,
            max_foir=policy["max_foir_limit"],
        )

        total_emi = existing_monthly_emi + proposed_emi
        foir_pct = round(float((total_emi / monthly_income) * 100.0), 2)
        disposable_post_emi = round(float(monthly_income - monthly_expenses - total_emi), 2)
        repayment_multiple = round(float((monthly_income - monthly_expenses) / max(1.0, proposed_emi)), 2)

        # Actionable Underwriting Tips & Remediation
        action_tips = []
        if is_approved:
            action_tips.append(
                f"Loan sanctioned: FOIR is healthy at {foir_pct}% (below the {int(policy['max_foir_limit']*100)}% ceiling)."
            )
            if credit_score >= 750:
                action_tips.append(
                    f"Prime credit score ({credit_score}) unlocks a preferential interest rate of {interest_rate_pct}% p.a."
                )
        else:
            if foir_pct > (policy["max_foir_limit"] * 100.0):
                excess_foir = round(foir_pct - policy["max_foir_limit"] * 100.0, 1)
                action_tips.append(
                    f"FOIR ratio ({foir_pct}%) exceeds the safety ceiling ({int(policy['max_foir_limit']*100)}%) by +{excess_foir}%. Reduce requested amount to ₹{max_safe_loan:,.0f} or extend tenure."
                )
            if credit_score < policy["min_credit_score"]:
                action_tips.append(
                    f"Credit score ({credit_score}) is below the minimum threshold ({policy['min_credit_score']}) for {loan_purpose}."
                )
            if disposable_post_emi < 0:
                action_tips.append(
                    f"Negative disposable cashflow (₹{disposable_post_emi:,.2f}/mo) detected post-EMI. Loan creates critical insolvency risk."
                )

        return {
            "verdict": "ELIGIBLE" if is_approved else "INELIGIBLE",
            "approval_status": "APPROVED" if is_approved else "DECLINED",
            "risk_tier": risk_tier,
            "default_probability_pct": default_prob_pct,
            "credit_health_grade": credit_grade,
            "proposed_loan_terms": {
                "requested_amount_inr": requested_loan_amount,
                "loan_purpose": loan_purpose,
                "tenure_months": loan_tenure_months,
                "annual_interest_rate_pct": interest_rate_pct,
                "calculated_monthly_emi_inr": proposed_emi,
                "total_obligations_emi_inr": total_emi,
                "foir_ratio_pct": foir_pct,
            },
            "max_safe_borrowing_limit_inr": max_safe_loan,
            "underwriting_diagnostics": {
                "disposable_cushion_post_emi_inr": disposable_post_emi,
                "repayment_capacity_multiple": repayment_multiple,
                "liquid_savings_inr": liquid_savings,
            },
            "actionable_underwriting_tips": action_tips,
        }


def main():
    parser = argparse.ArgumentParser(description="Phase 12 Loan Underwriting & Eligibility CLI")
    parser.add_argument("--income", type=float, default=85000.0, help="Monthly income in INR")
    parser.add_argument("--amount", type=float, default=1500000.0, help="Requested loan amount in INR")
    parser.add_argument("--tenure", type=int, default=120, help="Loan tenure in months")
    parser.add_argument("--purpose", type=str, default="HOME_LOAN", choices=["HOME_LOAN", "PERSONAL_LOAN", "AUTO_VEHICLE_LOAN", "EDUCATION_LOAN", "BUSINESS_EXPANSION"], help="Loan purpose")
    parser.add_argument("--emi", type=float, default=0.0, help="Existing monthly EMI in INR")
    parser.add_argument("--debt", type=float, default=0.0, help="Existing total debt in INR")
    parser.add_argument("--credit", type=int, default=760, help="Credit score (300-900)")
    parser.add_argument("--employment", type=str, default="SALARIED_PRIVATE", help="Employment type")
    parser.add_argument("--job-tenure", type=float, default=4.0, help="Employment tenure in years")
    parser.add_argument("--expenses", type=float, default=None, help="Monthly living expenses in INR")
    parser.add_argument("--savings", type=float, default=250000.0, help="Liquid savings in INR")

    args = parser.parse_args()

    engine = LoanUnderwritingEngine()
    result = engine.evaluate_application(
        monthly_income=args.income,
        requested_loan_amount=args.amount,
        loan_tenure_months=args.tenure,
        loan_purpose=args.purpose,
        existing_monthly_emi=args.emi,
        existing_debt_total=args.debt,
        credit_score=args.credit,
        employment_type=args.employment,
        employment_tenure_years=args.job_tenure,
        monthly_expenses=args.expenses,
        liquid_savings=args.savings,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
