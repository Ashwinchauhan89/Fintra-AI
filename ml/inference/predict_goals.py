"""
Inference API for Savings Capacity Forecasting & Goal Timeline Prediction (Phases 6 & 11).

Provides:
1. predict_savings_growth: Multi-horizon (1/3/5-year) savings capacity and compound investment wealth forecast.
2. predict_goal_timeline: Fractional months to goal, milestone completion date, required SIP, and feasibility score.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.goal_rules import (  # noqa: E402
    FEATURE_COLUMNS_SAVINGS,
    GOAL_PRESETS,
    MultiOutputVotingRegressor,
    calculate_months_to_goal,
    calculate_required_monthly_savings,
    evaluate_goal_feasibility,
    project_savings_growth,
)

DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


@lru_cache(maxsize=1)
def load_goals_model(model_dir: str = DEFAULT_MODEL_DIR):
    """
    Loads and caches the trained best savings/goal model pipeline.
    """
    model_path = os.path.join(model_dir, "savings_best_model.pkl")
    meta_path = os.path.join(model_dir, "goals_train_metrics.json")

    model = joblib.load(model_path) if os.path.exists(model_path) else None
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)

    return model, meta


def predict_savings_growth(
    monthly_income: float,
    monthly_expenses: Union[float, Dict[str, float]],
    debt_obligations: float = 0.0,
    current_balance: float = 0.0,
    expected_annual_return_pct: float = 7.0,
    model_dir: str = DEFAULT_MODEL_DIR,
) -> Dict[str, Any]:
    """
    Predicts monthly savings capacity and multi-year compounded growth projections (Phase 6).
    """
    income = float(monthly_income)
    debt = float(debt_obligations)
    balance = float(current_balance)

    if isinstance(monthly_expenses, dict):
        total_exp = float(sum(monthly_expenses.values()))
        needs_exp = float(
            monthly_expenses.get("food", 0)
            + monthly_expenses.get("bills", 0)
            + monthly_expenses.get("transport", 0)
            + monthly_expenses.get("healthcare", 0)
            + monthly_expenses.get("education", 0)
        )
        wants_exp = float(monthly_expenses.get("shopping", 0) + monthly_expenses.get("entertainment", 0))
    else:
        total_exp = float(monthly_expenses)
        needs_exp = float(total_exp * 0.65)
        wants_exp = float(total_exp * 0.35)

    discretionary_ratio = round(wants_exp / max(1.0, total_exp), 3)

    # 1. Predict Savings Capacity via ML Model
    model, _ = load_goals_model(model_dir)

    if model is not None:
        input_data = pd.DataFrame([{
            "monthly_income": income,
            "total_expenses": total_exp,
            "needs_expenses": needs_exp,
            "wants_expenses": wants_exp,
            "debt_obligations": debt,
            "current_balance": balance,
            "discretionary_ratio": discretionary_ratio,
            "savings_rate_baseline": (income - total_exp - debt) / max(1.0, income),
            "goal_type": "emergency_fund",
            "target_amount": total_exp * 3.0,
            "current_saved": balance,
            "intended_months": 12,
            "annual_return_pct": expected_annual_return_pct,
        }])
        pred = model.predict(input_data)[0]
        monthly_savings = max(0.0, round(float(pred[0]), 2))
    else:
        monthly_savings = max(0.0, round(income - total_exp - debt, 2))

    # 2. Savings Rate & Discretionary Optimization Potential
    savings_rate = round((monthly_savings / max(1.0, income)) * 100.0, 1)
    unlockable_discretionary = round(wants_exp * 0.30, 2)  # 30% of discretionary wants can be saved
    optimized_monthly_savings = round(monthly_savings + unlockable_discretionary, 2)

    # 3. Growth Projections across 1-yr, 3-yr, 5-yr horizons
    projections = project_savings_growth(
        monthly_savings_capacity=monthly_savings,
        current_balance=balance,
        annual_return_pct=expected_annual_return_pct,
    )

    # Actionable optimization insights
    insights = []
    if savings_rate < 20.0:
        insights.append(
            f"Your current savings rate ({savings_rate}%) is below the 20% benchmark (INR {income * 0.20:,.2f}/mo). Trimming non-essential shopping/entertainment can unlock INR {unlockable_discretionary:,.2f}/month."
        )
    else:
        insights.append(
            f"Strong savings pace! You are saving {savings_rate}% of your income. Compounding via monthly SIP can generate INR {projections['5_year']['compounding_gain']:,.2f} in wealth gain over 5 years."
        )

    return {
        "status": "success",
        "monthly_income": income,
        "total_expenses": total_exp,
        "debt_obligations": debt,
        "predicted_monthly_savings": monthly_savings,
        "savings_rate_pct": savings_rate,
        "discretionary_optimization_potential": unlockable_discretionary,
        "optimized_monthly_savings": optimized_monthly_savings,
        "expected_annual_return_pct": expected_annual_return_pct,
        "wealth_growth_projections": projections,
        "actionable_insights": insights,
    }


def predict_goal_timeline(
    goal_name: str,
    target_amount: float,
    current_saved: float = 0.0,
    monthly_income: float = 60000.0,
    monthly_expenses: Union[float, Dict[str, float]] = 35000.0,
    debt_obligations: float = 0.0,
    intended_months: int = 12,
    expected_annual_return_pct: float = 7.0,
    goal_type: str = "tech_gadget",
    model_dir: str = DEFAULT_MODEL_DIR,
) -> Dict[str, Any]:
    """
    Predicts goal timeline, milestone date, required SIP, and feasibility score (Phase 11).
    """
    target = float(target_amount)
    saved = float(current_saved)
    income = float(monthly_income)
    debt = float(debt_obligations)

    if isinstance(monthly_expenses, dict):
        total_exp = float(sum(monthly_expenses.values()))
        needs_exp = float(
            monthly_expenses.get("food", 0)
            + monthly_expenses.get("bills", 0)
            + monthly_expenses.get("transport", 0)
            + monthly_expenses.get("healthcare", 0)
            + monthly_expenses.get("education", 0)
        )
        wants_exp = float(monthly_expenses.get("shopping", 0) + monthly_expenses.get("entertainment", 0))
    else:
        total_exp = float(monthly_expenses)
        needs_exp = float(total_exp * 0.65)
        wants_exp = float(total_exp * 0.35)

    discretionary_ratio = round(wants_exp / max(1.0, total_exp), 3)

    # 1. Predict True Savings Capacity via ML Model
    model, _ = load_goals_model(model_dir)

    if model is not None:
        input_data = pd.DataFrame([{
            "monthly_income": income,
            "total_expenses": total_exp,
            "needs_expenses": needs_exp,
            "wants_expenses": wants_exp,
            "debt_obligations": debt,
            "current_balance": saved,
            "discretionary_ratio": discretionary_ratio,
            "savings_rate_baseline": (income - total_exp - debt) / max(1.0, income),
            "goal_type": goal_type if goal_type in GOAL_PRESETS else "tech_gadget",
            "target_amount": target,
            "current_saved": saved,
            "intended_months": intended_months,
            "annual_return_pct": expected_annual_return_pct,
        }])
        pred = model.predict(input_data)[0]
        monthly_savings = max(0.0, round(float(pred[0]), 2))
    else:
        monthly_savings = max(0.0, round(income - total_exp - debt, 2))

    # 2. Timeline & Required Monthly SIP
    months_to_complete = calculate_months_to_goal(
        target_amount=target,
        current_saved=saved,
        monthly_contribution=monthly_savings,
        annual_return_pct=expected_annual_return_pct,
    )

    required_monthly_savings = calculate_required_monthly_savings(
        target_amount=target,
        current_saved=saved,
        target_months=intended_months,
        annual_return_pct=expected_annual_return_pct,
    )

    # Estimated completion date
    days_to_add = int(months_to_complete * 30.44)
    completion_date = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")

    # Feasibility Grading
    feasibility, feasibility_feedback = evaluate_goal_feasibility(
        monthly_savings_capacity=monthly_savings,
        required_monthly_savings=required_monthly_savings,
    )

    # Accelerated Timeline with 25% Discretionary Spend Optimization
    extra_savings = round(wants_exp * 0.25, 2)
    accelerated_months = calculate_months_to_goal(
        target_amount=target,
        current_saved=saved,
        monthly_contribution=monthly_savings + extra_savings,
        annual_return_pct=expected_annual_return_pct,
    )
    months_saved = max(0.0, round(months_to_complete - accelerated_months, 1))

    recommendations = [feasibility_feedback]
    if months_saved >= 0.5:
        recommendations.append(
            f"Boost Pace: Reallocating INR {extra_savings:,.2f}/month from discretionary spending will achieve '{goal_name}' {months_saved} months earlier!"
        )

    return {
        "status": "success",
        "goal_name": goal_name,
        "target_amount": target,
        "current_saved": saved,
        "remaining_amount": max(0.0, round(target - saved, 2)),
        "predicted_months_to_completion": months_to_complete,
        "estimated_completion_date": completion_date,
        "user_intended_months": intended_months,
        "required_monthly_savings": required_monthly_savings,
        "current_monthly_savings_capacity": monthly_savings,
        "feasibility": feasibility,
        "accelerated_timeline_months": accelerated_months,
        "potential_months_saved": months_saved,
        "recommendations": recommendations,
    }


def main():
    parser = argparse.ArgumentParser(description="Phase 6 Savings & Phase 11 Goal Prediction API")
    parser.add_argument("--mode", choices=["savings", "goal"], default="goal")
    parser.add_argument("--goal", default="MacBook Pro", help="Goal Name")
    parser.add_argument("--target", type=float, default=80000.0, help="Target Amount in INR")
    parser.add_argument("--saved", type=float, default=25000.0, help="Current Saved Amount in INR")
    parser.add_argument("--income", type=float, default=65000.0, help="Monthly Income in INR")
    parser.add_argument("--expenses", type=float, default=38000.0, help="Monthly Living Expenses in INR")
    parser.add_argument("--debt", type=float, default=4000.0, help="Debt Obligations in INR")
    parser.add_argument("--intended-months", type=int, default=12, help="Intended Target Months")
    parser.add_argument("--annual-return", type=float, default=7.0, help="Expected annual return percentage")

    args = parser.parse_args()

    if args.mode == "savings":
        res = predict_savings_growth(
            monthly_income=args.income,
            monthly_expenses=args.expenses,
            debt_obligations=args.debt,
            current_balance=args.saved,
            expected_annual_return_pct=args.annual_return,
        )
    else:
        res = predict_goal_timeline(
            goal_name=args.goal,
            target_amount=args.target,
            current_saved=args.saved,
            monthly_income=args.income,
            monthly_expenses=args.expenses,
            debt_obligations=args.debt,
            intended_months=args.intended_months,
            expected_annual_return_pct=args.annual_return,
        )

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
