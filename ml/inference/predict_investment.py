"""
Production Inference Engine for Phase 10: Investment Recommendation & Portfolio Allocator.

Provides:
- `recommend_portfolio_allocation()`: Predicts optimal asset class weights (% sums to 100%),
  calculates monthly SIP distribution in INR (₹), projects multi-year compounding wealth,
  and selects curated investment instruments matching user risk and horizon.
- Interactive CLI for instant testing with custom financial parameters.
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
from utils.investment_rules import (  # noqa: E402
    CURATED_INSTRUMENTS,
    ENGINEERED_CATEGORICAL_FEATURES,
    ENGINEERED_NUMERICAL_FEATURES,
    FEATURE_COLUMNS_INVESTMENT,
    RISK_PROFILES,
    TARGET_COLUMNS_INVESTMENT,
    compute_portfolio_cagr,
    engineer_investment_features,
    normalize_to_simplex,
    project_sip_wealth,
)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best_investment_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "investment_preprocessor.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "investment_metadata.json")


class InvestmentRecommender:
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

    def recommend(
        self,
        monthly_income: float,
        age: int,
        risk_profile: str = "BALANCED",
        investment_horizon_years: int = 5,
        monthly_surplus: Optional[float] = None,
        existing_savings: float = 0.0,
        existing_debt: float = 0.0,
        lump_sum_investment: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Computes tailored asset allocation, monthly SIP allocations in INR,
        compounded wealth milestones, and curated fund instruments.
        """
        risk_profile = risk_profile.upper()
        if risk_profile not in RISK_PROFILES:
            risk_profile = "BALANCED"

        risk_score = RISK_PROFILES[risk_profile]["score"]

        # If monthly surplus is not explicitly specified, estimate 25% savings margin
        if monthly_surplus is None or monthly_surplus <= 0:
            monthly_surplus = round(float(monthly_income * 0.25), 2)

        # Monthly expenses and liquid runway months
        monthly_expenses = max(5000.0, monthly_income - monthly_surplus)
        liquid_runway_months = round(float(existing_savings / monthly_expenses), 1)

        raw_df = pd.DataFrame([{
            "monthly_income": float(monthly_income),
            "age": int(age),
            "monthly_surplus": float(monthly_surplus),
            "existing_savings": float(existing_savings),
            "existing_debt": float(existing_debt),
            "liquid_runway_months": float(liquid_runway_months),
            "investment_horizon_years": int(investment_horizon_years),
            "risk_score": int(risk_score),
            "risk_profile": risk_profile,
        }])

        # Apply domain feature engineering pipeline
        engineered_df = engineer_investment_features(raw_df)

        num_cols = self.metadata.get("engineered_numerical_features", ENGINEERED_NUMERICAL_FEATURES)
        cat_cols = self.metadata.get("engineered_categorical_features", ENGINEERED_CATEGORICAL_FEATURES)

        if self.model is not None and self.preprocessor is not None:
            X_proc = self.preprocessor.transform(engineered_df[num_cols + cat_cols])
            raw_preds = self.model.predict(X_proc)
            norm_preds = normalize_to_simplex(raw_preds) * 100.0
            alloc_vector = norm_preds[0]
        else:
            # Fallback heuristic if model artifact is absent
            alloc_vector = np.array([50.0, 25.0, 10.0, 5.0, 10.0])

        allocations = {
            "equity_pct": round(float(alloc_vector[0]), 1),
            "debt_pct": round(float(alloc_vector[1]), 1),
            "gold_pct": round(float(alloc_vector[2]), 1),
            "reit_pct": round(float(alloc_vector[3]), 1),
            "cash_pct": round(float(alloc_vector[4]), 1),
        }

        # Monthly SIP distribution in INR
        sip_breakdown = {
            "equity_sip_inr": round(float(monthly_surplus * (allocations["equity_pct"] / 100.0)), 2),
            "debt_sip_inr": round(float(monthly_surplus * (allocations["debt_pct"] / 100.0)), 2),
            "gold_sip_inr": round(float(monthly_surplus * (allocations["gold_pct"] / 100.0)), 2),
            "reit_sip_inr": round(float(monthly_surplus * (allocations["reit_pct"] / 100.0)), 2),
            "cash_buffer_inr": round(float(monthly_surplus * (allocations["cash_pct"] / 100.0)), 2),
        }

        # Portfolio CAGR calculation
        portfolio_cagr = compute_portfolio_cagr({
            "equity": allocations["equity_pct"],
            "debt": allocations["debt_pct"],
            "gold": allocations["gold_pct"],
            "reit": allocations["reit_pct"],
            "cash": allocations["cash_pct"],
        })

        # Multi-Horizon Compounding Projections
        projections = project_sip_wealth(
            monthly_sip=monthly_surplus,
            annual_cagr=portfolio_cagr,
            horizon_years=investment_horizon_years,
            initial_lump_sum=lump_sum_investment,
        )

        # Select relevant curated instruments matching risk profile
        recommended_instruments = []
        for asset_key, items in CURATED_INSTRUMENTS.items():
            for item in items:
                if risk_profile in item["suitable_for"]:
                    recommended_instruments.append({
                        "asset_class": asset_key.upper(),
                        "name": item["name"],
                        "category": item["category"],
                        "risk_level": item["risk"],
                        "expected_cagr": item["expected_cagr"],
                        "expense_ratio": item["expense_ratio"],
                    })

        # Strategic financial advice / action tips
        action_tips = []
        if liquid_runway_months < 3.0:
            action_tips.append(
                f"Your emergency runway ({liquid_runway_months} months) is low. Prioritize building a 3-6 month liquid fund cushion before aggressive equity expansion."
            )
        if age < 35 and allocations["equity_pct"] >= 60.0:
            action_tips.append(
                f"Given your young age ({age}) and long horizon, your {allocations['equity_pct']}% equity allocation maximizes compounding growth."
            )
        if allocations["gold_pct"] >= 5.0:
            action_tips.append(
                f"Gold allocation ({allocations['gold_pct']}%) acts as a geopolitical hedge and inflation shock absorber."
            )

        return {
            "status": "success",
            "model_engine": self.metadata.get("best_model_name", "production_ensemble"),
            "user_profile": {
                "monthly_income_inr": monthly_income,
                "age": age,
                "monthly_surplus_inr": monthly_surplus,
                "risk_profile": risk_profile,
                "investment_horizon_years": investment_horizon_years,
                "liquid_runway_months": liquid_runway_months,
            },
            "recommended_allocation_pct": allocations,
            "monthly_sip_distribution_inr": sip_breakdown,
            "portfolio_expected_cagr_pct": round(portfolio_cagr * 100.0, 2),
            "wealth_growth_projections": projections,
            "curated_fund_instruments": recommended_instruments,
            "strategic_financial_tips": action_tips,
        }


def main():
    parser = argparse.ArgumentParser(description="Phase 10 Investment Recommendation & Portfolio Allocator CLI")
    parser.add_argument("--income", type=float, default=75000.0, help="Monthly income in INR")
    parser.add_argument("--age", type=int, default=28, help="User age")
    parser.add_argument("--risk", type=str, default="GROWTH", choices=["CONSERVATIVE", "MODERATE", "BALANCED", "GROWTH", "AGGRESSIVE"], help="Risk profile")
    parser.add_argument("--horizon", type=int, default=5, help="Investment horizon in years")
    parser.add_argument("--surplus", type=float, default=None, help="Monthly surplus in INR")
    parser.add_argument("--savings", type=float, default=150000.0, help="Existing savings in INR")
    parser.add_argument("--debt", type=float, default=0.0, help="Existing debt in INR")
    parser.add_argument("--lump-sum", type=float, default=50000.0, help="Initial lump sum investment in INR")

    args = parser.parse_args()

    engine = InvestmentRecommender()
    result = engine.recommend(
        monthly_income=args.income,
        age=args.age,
        risk_profile=args.risk,
        investment_horizon_years=args.horizon,
        monthly_surplus=args.surplus,
        existing_savings=args.savings,
        existing_debt=args.debt,
        lump_sum_investment=args.lump_sum,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
