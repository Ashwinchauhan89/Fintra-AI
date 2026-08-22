"""
Evaluation Pipeline for Savings Capacity & Goal Timeline Prediction Engine (Phases 6 & 11).

Evaluates candidate models on 1,500 held-out goal profiles.
Computes multi-target MAE, R², and validates real-world goal archetypes.
"""

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from inference.predict_goals import predict_goal_timeline, predict_savings_growth  # noqa: E402
from utils.goal_rules import FEATURE_COLUMNS_SAVINGS, MultiOutputVotingRegressor  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "goals_test.csv")
OUTPUT_METRICS = os.path.join(MODEL_DIR, "goals_evaluation_metrics.json")


def evaluate_goals_candidates():
    print("=" * 80)
    print("Held-Out Evaluation & Leaderboard Benchmark: Phases 6 & 11 Savings & Goals")
    print("=" * 80)

    if not os.path.exists(TEST_FILE):
        raise FileNotFoundError(f"Test dataset not found at {TEST_FILE}. Run preprocessing/preprocess_goals.py first.")

    df_test = pd.read_csv(TEST_FILE)
    num_cols = FEATURE_COLUMNS_SAVINGS + ["target_amount", "current_saved", "intended_months", "annual_return_pct"]
    cat_cols = ["goal_type"]
    target_cols = ["target_monthly_savings", "target_completion_months", "target_required_savings"]

    X_test = df_test[num_cols + cat_cols]
    y_test = df_test[target_cols]

    print(f"[eval] Held-out Test Samples: {len(df_test):,}")
    print("-" * 80)

    candidate_names = ["ridge", "random_forest", "extra_trees", "gradient_boosting", "xgboost", "ensemble"]
    leaderboard = {}

    print(f"{'Model Candidate':<22} | {'Test MAE (INR)':<16} | {'Test R2 Score':<14} | {'Max Peak Error'}")
    print("-" * 80)

    for name in candidate_names:
        model_path = os.path.join(MODEL_DIR, f"goals_{name}.pkl")
        if not os.path.exists(model_path):
            continue

        pipeline = joblib.load(model_path)
        preds = pipeline.predict(X_test)

        mae = float(mean_absolute_error(y_test, preds))
        r2 = float(r2_score(y_test, preds, multioutput="uniform_average"))
        max_err = float(np.max(np.abs(y_test.values - preds)))

        leaderboard[name] = {
            "test_mae": round(mae, 2),
            "test_r2": round(r2, 4),
            "max_error": round(max_err, 2),
        }

        print(f"{name:<22} | INR {mae:>9,.2f} | {r2:>12.4f} | INR {max_err:>10,.2f}")

    print("-" * 80)

    # -------------------------------------------------------------
    # Production Best Model In-Depth Summary
    # -------------------------------------------------------------
    best_path = os.path.join(MODEL_DIR, "savings_best_model.pkl")
    best_pipeline = joblib.load(best_path)
    best_preds = best_pipeline.predict(X_test)

    best_mae = float(mean_absolute_error(y_test, best_preds))
    best_r2 = float(r2_score(y_test, best_preds, multioutput="uniform_average"))

    # Granular breakdown per target
    savings_mae = float(mean_absolute_error(y_test["target_monthly_savings"], best_preds[:, 0]))
    months_mae = float(mean_absolute_error(y_test["target_completion_months"], best_preds[:, 1]))
    required_mae = float(mean_absolute_error(y_test["target_required_savings"], best_preds[:, 2]))

    print("\n[Production Best Model Target Breakdown]")
    print(f"  * Monthly Savings Capacity MAE : INR {savings_mae:,.2f}")
    print(f"  * Goal Completion Timeline MAE : {months_mae:.2f} months")
    print(f"  * Required Monthly SIP MAE     : INR {required_mae:,.2f}")
    print(f"  * Overall Multi-Target R2      : {best_r2:.4f}")

    metrics = {
        "test_samples": len(df_test),
        "leaderboard": leaderboard,
        "production_best": {
            "overall_mae": round(best_mae, 2),
            "overall_r2": round(best_r2, 4),
            "target_breakdown": {
                "monthly_savings_capacity_mae": round(savings_mae, 2),
                "goal_completion_months_mae": round(months_mae, 2),
                "required_monthly_savings_mae": round(required_mae, 2),
            },
        },
    }

    with open(OUTPUT_METRICS, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] Saved evaluation metrics -> {OUTPUT_METRICS}")
    return metrics


def evaluate_goal_archetypes():
    print("\n" + "=" * 85)
    print("Real-World Goal Archetype Validation: Phase 6 & Phase 11")
    print("=" * 85)

    archetypes = [
        {
            "goal": "MacBook Pro M3",
            "type": "tech_gadget",
            "target": 85000.0,
            "saved": 25000.0,
            "income": 55000.0,
            "expenses": 32000.0,
            "debt": 3000.0,
            "intended_months": 6,
            "return_pct": 5.0,
        },
        {
            "goal": "Emergency Fund (6-Mo)",
            "type": "emergency_fund",
            "target": 180000.0,
            "saved": 40000.0,
            "income": 75000.0,
            "expenses": 42000.0,
            "debt": 5000.0,
            "intended_months": 12,
            "return_pct": 5.5,
        },
        {
            "goal": "Electric Scooter",
            "type": "vehicle",
            "target": 120000.0,
            "saved": 30000.0,
            "income": 45000.0,
            "expenses": 28000.0,
            "debt": 2000.0,
            "intended_months": 8,
            "return_pct": 6.5,
        },
        {
            "goal": "Europe Trip",
            "type": "travel_vacation",
            "target": 250000.0,
            "saved": 50000.0,
            "income": 110000.0,
            "expenses": 60000.0,
            "debt": 8000.0,
            "intended_months": 9,
            "return_pct": 6.0,
        },
        {
            "goal": "House Downpayment",
            "type": "home_downpayment",
            "target": 1200000.0,
            "saved": 350000.0,
            "income": 150000.0,
            "expenses": 75000.0,
            "debt": 15000.0,
            "intended_months": 36,
            "return_pct": 10.0,
        },
    ]

    print(f"{'Goal Persona Archetype':<26} | {'Target (INR)':<13} | {'Savings/Mo':<12} | {'Months':<8} | {'Feasibility':<11} | {'Milestone Date'}")
    print("-" * 85)

    for arch in archetypes:
        res = predict_goal_timeline(
            goal_name=arch["goal"],
            target_amount=arch["target"],
            current_saved=arch["saved"],
            monthly_income=arch["income"],
            monthly_expenses=arch["expenses"],
            debt_obligations=arch["debt"],
            intended_months=arch["intended_months"],
            expected_annual_return_pct=arch["return_pct"],
            goal_type=arch["type"],
        )
        print(
            f"{arch['goal']:<26} | INR {arch['target']:>8,.0f} | INR {res['current_monthly_savings_capacity']:>7,.0f} | "
            f"{res['predicted_months_to_completion']:>5.1f} mo | {res['feasibility']:<11} | {res['estimated_completion_date']}"
        )

    print("=" * 85)


def main():
    evaluate_goals_candidates()
    evaluate_goal_archetypes()


if __name__ == "__main__":
    main()
