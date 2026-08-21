"""
Inference Pipeline for Budget Recommendation & Financial Health Scoring (Phases 5 & 7).

Provides:
1. recommend_budget: Optimal category budget ceilings, 50/30/20 allocation, and cost-reduction insights.
2. calculate_financial_health_score: Multi-pillar 0-100 financial health diagnosis with actionable advice.
"""

import argparse
import json
import os
import sys
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.budget_rules import (  # noqa: E402
    CATEGORY_CLASSIFICATION,
    DEFAULT_CATEGORY_WEIGHTS,
    LIFESTYLE_PROFILES,
    ROADMAP_CATEGORIES,
    allocate_category_budgets,
)

DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


@lru_cache(maxsize=1)
def load_budget_artifacts(model_dir: str = DEFAULT_MODEL_DIR):
    """
    Loads and caches trained budget recommendation model and metadata.
    """
    model_path = os.path.join(model_dir, "budget_recommender.pkl")
    meta_path = os.path.join(model_dir, "budget_meta.json")

    pipeline = joblib.load(model_path) if os.path.exists(model_path) else None
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)

    return pipeline, meta


def recommend_budget(
    monthly_income: float,
    historical_expenses: Optional[Dict[str, float]] = None,
    savings_target_pct: float = 0.20,
    lifestyle: str = "balanced",
    debt_obligations: float = 0.0,
    model_dir: str = DEFAULT_MODEL_DIR,
) -> Dict[str, Any]:
    """
    Computes ML-recommended category budgets, 50/30/20 benchmarks, variance analysis,
    and actionable spending optimizations.
    """
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than 0.")

    savings_target_pct = float(np.clip(savings_target_pct, 0.05, 0.60))
    lifestyle = lifestyle if lifestyle in LIFESTYLE_PROFILES else "balanced"
    debt_obligations = max(0.0, float(debt_obligations))
    debt_to_income = min(1.0, debt_obligations / monthly_income)

    pipeline, meta = load_budget_artifacts(model_dir)

    # Compute baseline category allocations via analytical constraint solver
    base_allocations = allocate_category_budgets(
        monthly_income=monthly_income,
        savings_target_pct=savings_target_pct,
        lifestyle=lifestyle,
    )

    # Adjust for model predictions if model is available
    if pipeline is not None and historical_expenses:
        hist_total = max(1.0, sum(historical_expenses.values()))
        input_data = {
            "monthly_income": monthly_income,
            "savings_target_pct": savings_target_pct,
            "debt_to_income_ratio": debt_to_income,
            "lifestyle": lifestyle,
        }
        for cat in ROADMAP_CATEGORIES:
            input_data[f"hist_ratio_{cat}"] = historical_expenses.get(cat, 0.0) / hist_total

        df_input = pd.DataFrame([input_data])
        raw_preds = pipeline.predict(df_input)[0]
        
        target_cols = meta.get("target_cols", [f"target_budget_{c}" for c in ROADMAP_CATEGORIES] + ["target_budget_savings"])
        pred_dict = {col.replace("target_budget_", ""): max(0.0, float(raw_preds[i])) for i, col in enumerate(target_cols)}

        # Normalize model outputs so total equals monthly_income
        total_pred = sum(pred_dict.values())
        if total_pred > 0:
            scale_factor = monthly_income / total_pred
            for k in pred_dict:
                base_allocations[k] = round(pred_dict[k] * scale_factor, 2)

    # Calculate 50/30/20 Grouped Totals
    needs_categories = [c for c in ROADMAP_CATEGORIES if CATEGORY_CLASSIFICATION.get(c) == "needs"]
    wants_categories = [c for c in ROADMAP_CATEGORIES if CATEGORY_CLASSIFICATION.get(c) == "wants"]

    recommended_needs = round(sum(base_allocations[c] for c in needs_categories), 2)
    recommended_wants = round(sum(base_allocations[c] for c in wants_categories), 2)
    recommended_savings = round(base_allocations.get("savings", monthly_income * savings_target_pct), 2)

    # Detailed Category Breakdown
    categories_breakdown = {}
    for cat in ROADMAP_CATEGORIES:
        budget_amt = base_allocations[cat]
        cat_type = CATEGORY_CLASSIFICATION[cat]
        cat_info = {
            "recommended_budget": budget_amt,
            "pct_of_income": round((budget_amt / monthly_income) * 100, 1),
            "type": cat_type,
        }

        if historical_expenses and cat in historical_expenses:
            actual = float(historical_expenses[cat])
            diff = round(actual - budget_amt, 2)
            cat_info["actual_spend"] = actual
            cat_info["variance"] = diff
            cat_info["status"] = "OVERSPENT" if diff > (0.05 * budget_amt) else ("UNDERSPENT" if diff < - (0.05 * budget_amt) else "OPTIMAL")
        categories_breakdown[cat] = cat_info

    # Generate Actionable Optimization Tips
    optimizations = []
    if historical_expenses:
        total_actual_spend = sum(historical_expenses.values())
        actual_savings = monthly_income - total_actual_spend - debt_obligations
        
        # Check overall savings gap
        if actual_savings < recommended_savings:
            gap = round(recommended_savings - actual_savings, 2)
            optimizations.append(
                f"You are INR {gap:,.2f} short of your desired monthly savings target (INR {recommended_savings:,.2f})."
            )

        # Check largest overspent categories
        overspent_cats = []
        for cat, info in categories_breakdown.items():
            if info.get("status") == "OVERSPENT":
                overspent_cats.append((cat, info["variance"]))

        overspent_cats.sort(key=lambda x: x[1], reverse=True)
        for cat, excess in overspent_cats[:2]:
            cat_type = CATEGORY_CLASSIFICATION[cat]
            if cat_type == "wants":
                optimizations.append(
                    f"Discretionary spending in '{cat.capitalize()}' exceeded recommended budget by INR {excess:,.2f}. Reallocate this to Savings to optimize cash flow."
                )
            else:
                optimizations.append(
                    f"Essential spending in '{cat.capitalize()}' is INR {excess:,.2f} higher than standard benchmarks. Look for subscription or utility optimizations."
                )

    if not optimizations:
        optimizations.append("Spending habits align well with recommended 50/30/20 benchmarks!")

    return {
        "monthly_income": monthly_income,
        "lifestyle": lifestyle,
        "savings_target_pct": savings_target_pct,
        "recommended_allocations": base_allocations,
        "rule_50_30_20": {
            "needs": {"amount": recommended_needs, "pct": round((recommended_needs / monthly_income) * 100, 1)},
            "wants": {"amount": recommended_wants, "pct": round((recommended_wants / monthly_income) * 100, 1)},
            "savings": {"amount": recommended_savings, "pct": round((recommended_savings / monthly_income) * 100, 1)},
        },
        "category_breakdown": categories_breakdown,
        "optimization_insights": optimizations,
    }


def calculate_financial_health_score(
    monthly_income: float,
    current_balance: float,
    monthly_expenses: Union[Dict[str, float], float],
    debt_obligations: float = 0.0,
    monthly_savings: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Computes 0-100 composite Financial Health Score and letter grade across 5 pillars.
    """
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than 0.")

    current_balance = max(0.0, float(current_balance))
    debt_obligations = max(0.0, float(debt_obligations))

    # Parse expenses
    if isinstance(monthly_expenses, dict):
        total_expenses = float(sum(monthly_expenses.values()))
        shopping_spend = float(monthly_expenses.get("shopping", 0.0))
        entertainment_spend = float(monthly_expenses.get("entertainment", 0.0))
        discretionary_spend = shopping_spend + entertainment_spend
        bills_spend = float(monthly_expenses.get("bills", 0.0))
    else:
        total_expenses = max(0.0, float(monthly_expenses))
        discretionary_spend = total_expenses * 0.30
        bills_spend = total_expenses * 0.25

    if monthly_savings is None:
        actual_savings = max(-monthly_income, monthly_income - total_expenses - debt_obligations)
    else:
        actual_savings = float(monthly_savings)

    # -------------------------------------------------------------
    # Pillar 1: Savings Rate (Weight 25%)
    # -------------------------------------------------------------
    savings_rate = actual_savings / monthly_income
    if savings_rate >= 0.30:
        savings_score = 100.0
    elif savings_rate >= 0.20:
        savings_score = 85.0 + ((savings_rate - 0.20) / 0.10) * 15.0
    elif savings_rate >= 0.10:
        savings_score = 60.0 + ((savings_rate - 0.10) / 0.10) * 25.0
    elif savings_rate > 0.0:
        savings_score = 30.0 + (savings_rate / 0.10) * 30.0
    else:
        savings_score = max(0.0, 30.0 + savings_rate * 50.0)

    # -------------------------------------------------------------
    # Pillar 2: Debt & Fixed Obligation Ratio (Weight 25%)
    # -------------------------------------------------------------
    fixed_obligation_ratio = (debt_obligations + bills_spend) / monthly_income
    if fixed_obligation_ratio <= 0.25:
        debt_score = 100.0
    elif fixed_obligation_ratio <= 0.35:
        debt_score = 85.0 + ((0.35 - fixed_obligation_ratio) / 0.10) * 15.0
    elif fixed_obligation_ratio <= 0.50:
        debt_score = 55.0 + ((0.50 - fixed_obligation_ratio) / 0.15) * 30.0
    elif fixed_obligation_ratio <= 0.70:
        debt_score = 25.0 + ((0.70 - fixed_obligation_ratio) / 0.20) * 30.0
    else:
        debt_score = max(0.0, 25.0 - (fixed_obligation_ratio - 0.70) * 50.0)

    # -------------------------------------------------------------
    # Pillar 3: Discretionary Spending Control (Weight 20%)
    # -------------------------------------------------------------
    discretionary_ratio = (discretionary_spend / total_expenses) if total_expenses > 0 else 0.30
    if discretionary_ratio <= 0.25:
        discretionary_score = 100.0
    elif discretionary_ratio <= 0.35:
        discretionary_score = 85.0 + ((0.35 - discretionary_ratio) / 0.10) * 15.0
    elif discretionary_ratio <= 0.50:
        discretionary_score = 55.0 + ((0.50 - discretionary_ratio) / 0.15) * 30.0
    elif discretionary_ratio <= 0.70:
        discretionary_score = 25.0 + ((0.70 - discretionary_ratio) / 0.20) * 30.0
    else:
        discretionary_score = max(0.0, 25.0 - (discretionary_ratio - 0.70) * 50.0)

    # -------------------------------------------------------------
    # Pillar 4: Emergency Runway / Liquidity (Weight 15%)
    # -------------------------------------------------------------
    burn_rate = max(100.0, total_expenses + debt_obligations)
    runway_months = current_balance / burn_rate
    if runway_months >= 6.0:
        runway_score = 100.0
    elif runway_months >= 3.0:
        runway_score = 80.0 + ((runway_months - 3.0) / 3.0) * 20.0
    elif runway_months >= 1.0:
        runway_score = 50.0 + ((runway_months - 1.0) / 2.0) * 30.0
    elif runway_months > 0.0:
        runway_score = runway_months * 50.0
    else:
        runway_score = 0.0

    # -------------------------------------------------------------
    # Pillar 5: Spending Buffer & Solvency (Weight 15%)
    # -------------------------------------------------------------
    net_buffer_ratio = (monthly_income - total_expenses - debt_obligations) / monthly_income
    if net_buffer_ratio >= 0.20:
        buffer_score = 100.0
    elif net_buffer_ratio >= 0.05:
        buffer_score = 70.0 + ((net_buffer_ratio - 0.05) / 0.15) * 30.0
    elif net_buffer_ratio >= 0.0:
        buffer_score = 50.0 + (net_buffer_ratio / 0.05) * 20.0
    else:
        buffer_score = max(0.0, 50.0 + net_buffer_ratio * 100.0)

    # -------------------------------------------------------------
    # Composite Score Calculation (0-100)
    # -------------------------------------------------------------
    overall_score = round(
        (savings_score * 0.25)
        + (debt_score * 0.25)
        + (discretionary_score * 0.20)
        + (runway_score * 0.15)
        + (buffer_score * 0.15),
        1,
    )
    overall_score = float(np.clip(overall_score, 0.0, 100.0))

    # Grade determination
    if overall_score >= 90:
        grade, status = "A+", "EXCEPTIONAL"
    elif overall_score >= 80:
        grade, status = "A", "HEALTHY"
    elif overall_score >= 70:
        grade, status = "B", "GOOD"
    elif overall_score >= 55:
        grade, status = "C", "NEEDS_ATTENTION"
    else:
        grade, status = "D", "CRITICAL"

    # Actionable AI Insights
    action_items = []
    if savings_score < 70:
        action_items.append(f"Boost monthly savings rate (currently {savings_rate * 100:.1f}%) towards 20% by setting up auto-investments.")
    if debt_score < 70:
        action_items.append(f"Fixed obligations and debt take up {fixed_obligation_ratio * 100:.1f}% of income. Target debt paydown to free up cash flow.")
    if discretionary_score < 70:
        action_items.append(f"Discretionary wants account for {discretionary_ratio * 100:.1f}% of expenses. Trimming non-essentials can quickly raise your score.")
    if runway_score < 70:
        action_items.append(f"Emergency liquidity covers {runway_months:.1f} month(s). Aim for at least 3-6 months of expenses (INR {burn_rate * 3:,.2f}).")
    if not action_items:
        action_items.append("Excellent financial health! Maintain current investment strategy and emergency runway.")

    return {
        "financial_health_score": overall_score,
        "grade": grade,
        "status": status,
        "runway_months": round(runway_months, 1),
        "savings_rate_pct": round(savings_rate * 100, 1),
        "pillars": {
            "savings_rate": {"score": round(savings_score, 1), "weight_pct": 25},
            "debt_and_obligations": {"score": round(debt_score, 1), "weight_pct": 25},
            "discretionary_control": {"score": round(discretionary_score, 1), "weight_pct": 20},
            "emergency_runway": {"score": round(runway_score, 1), "weight_pct": 15},
            "spending_buffer": {"score": round(buffer_score, 1), "weight_pct": 15},
        },
        "recommendations": action_items,
    }


def main():
    parser = argparse.ArgumentParser(description="Phase 5 & 7 Budget & Financial Health Inference API")
    parser.add_argument("--mode", choices=["budget", "health"], default="budget")
    parser.add_argument("--income", type=float, required=True, help="Monthly income (INR)")
    parser.add_argument("--savings-target", type=float, default=0.20, help="Target savings rate (0.05 to 0.50)")
    parser.add_argument("--lifestyle", choices=list(LIFESTYLE_PROFILES.keys()), default="balanced")
    parser.add_argument("--balance", type=float, default=50000.0, help="Current liquid bank balance")
    parser.add_argument("--expenses", type=float, default=40000.0, help="Total monthly expenses")
    parser.add_argument("--debt", type=float, default=0.0, help="Monthly debt/loan obligations")

    args = parser.parse_args()

    if args.mode == "budget":
        result = recommend_budget(
            monthly_income=args.income,
            savings_target_pct=args.savings_target,
            lifestyle=args.lifestyle,
            debt_obligations=args.debt,
        )
    else:
        result = calculate_financial_health_score(
            monthly_income=args.income,
            current_balance=args.balance,
            monthly_expenses=args.expenses,
            debt_obligations=args.debt,
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
