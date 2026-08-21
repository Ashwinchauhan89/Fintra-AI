"""
Enhanced Evaluation & Benchmark Pipeline for Budget Recommendation (Phases 5 & 7).

Evaluates all candidate models on the held-out test set (1,200 samples),
measures per-category precision, conservation constraints, and archetype health stability.
"""

import json
import os
import sys
from typing import Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from inference.predict_budget import calculate_financial_health_score  # noqa: E402
from training.train_budget import MultiOutputVotingRegressor  # noqa: F401, E402
from utils.budget_rules import ROADMAP_CATEGORIES  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "budget_test.csv")
OUTPUT_METRICS = os.path.join(MODEL_DIR, "budget_evaluation_metrics.json")


def evaluate_all_candidate_models():
    print("=" * 75)
    print("Held-Out Evaluation & Model Selection Benchmark: Phase 5 Budget Engine")
    print("=" * 75)

    if not os.path.exists(TEST_FILE):
        raise FileNotFoundError(f"Test dataset not found at {TEST_FILE}. Run preprocessing/preprocess_budget.py first.")

    df_test = pd.read_csv(TEST_FILE)

    num_cols = ["monthly_income", "savings_target_pct", "debt_to_income_ratio"]
    hist_cols = [f"hist_ratio_{cat}" for cat in ROADMAP_CATEGORIES]
    cat_cols = ["lifestyle"]
    target_cols = [f"target_budget_{cat}" for cat in ROADMAP_CATEGORIES] + ["target_budget_savings"]

    X_test = df_test[num_cols + hist_cols + cat_cols]
    y_true = df_test[target_cols]

    candidate_names = ["ridge", "random_forest", "extra_trees", "gradient_boosting", "xgboost", "ensemble"]
    leaderboard = {}

    print(f"{'Model Candidate':<22} | {'Test MAE':<14} | {'Test R2':<10} | {'Max Peak Error':<16} | {'Status'}")
    print("-" * 75)

    for name in candidate_names:
        model_path = os.path.join(MODEL_DIR, f"budget_{name}.pkl")
        if not os.path.exists(model_path):
            continue

        model = joblib.load(model_path)
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred, multioutput="uniform_average")
        max_err = float(np.max(np.abs(y_true.values - y_pred)))

        leaderboard[name] = {
            "test_mae": round(float(mae), 2),
            "test_r2": round(float(r2), 4),
            "test_max_error": round(float(max_err), 2),
        }
        print(f"{name:<22} | INR {mae:>8,.2f} | {r2:>8.4f} | INR {max_err:>12,.2f} | Fitted")

    print("-" * 75)

    # Detailed Category Breakdown for Best Production Model
    best_model_path = os.path.join(MODEL_DIR, "budget_recommender.pkl")
    best_model = joblib.load(best_model_path)
    y_pred_best = best_model.predict(X_test)

    best_mae = mean_absolute_error(y_true, y_pred_best)
    best_r2 = r2_score(y_true, y_pred_best, multioutput="uniform_average")

    print(f"\n[Production Best Model Summary]")
    print(f"  * Overall Multi-Target Test MAE: INR {best_mae:,.2f}")
    print(f"  * Overall Multi-Target Test R2 : {best_r2:.4f}")
    print("-" * 75)
    print(f"{'Category / Target':<25} | {'Test MAE':<16} | {'Test R2 Score':<12}")
    print("-" * 75)

    category_metrics = {}
    for i, col in enumerate(target_cols):
        cat_name = col.replace("target_budget_", "").capitalize()
        mae_cat = mean_absolute_error(y_true.iloc[:, i], y_pred_best[:, i])
        r2_cat = r2_score(y_true.iloc[:, i], y_pred_best[:, i])
        category_metrics[cat_name] = {"mae": round(float(mae_cat), 2), "r2": round(float(r2_cat), 4)}
        print(f"{cat_name:<25} | INR {mae_cat:>10,.2f} | {r2_cat:>12.4f}")

    print("-" * 75)

    # Constraint Conservation check
    pred_sums = np.sum(y_pred_best, axis=1)
    income_sums = df_test["monthly_income"].values
    mean_discrepancy = float(np.mean(np.abs(pred_sums - income_sums)))
    print(f"[constraint] Mean Budget Discrepancy : INR {mean_discrepancy:.2f}")

    metrics = {
        "test_samples": len(df_test),
        "leaderboard": leaderboard,
        "production_best": {
            "overall_mae": round(float(best_mae), 2),
            "overall_r2": round(float(best_r2), 4),
            "mean_discrepancy": round(mean_discrepancy, 2),
            "category_metrics": category_metrics,
        },
    }

    with open(OUTPUT_METRICS, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] Saved benchmark report -> {OUTPUT_METRICS}")
    return metrics


def evaluate_financial_health_archetypes():
    print("\n" + "=" * 75)
    print("Financial Health Score Archetype Validation: Phase 7")
    print("=" * 75)

    archetypes = [
        {
            "name": "1. High Saver / Frugal",
            "income": 100000.0,
            "balance": 500000.0,
            "expenses": {"food": 12000, "bills": 10000, "transport": 5000, "shopping": 3000, "entertainment": 2000, "healthcare": 2000, "education": 0},
            "debt": 0.0,
        },
        {
            "name": "2. Average Balanced Professional",
            "income": 75000.0,
            "balance": 120000.0,
            "expenses": {"food": 15000, "bills": 12000, "transport": 6000, "shopping": 8000, "entertainment": 5000, "healthcare": 2000, "education": 0},
            "debt": 5000.0,
        },
        {
            "name": "3. High Discretionary Spender",
            "income": 60000.0,
            "balance": 30000.0,
            "expenses": {"food": 14000, "bills": 10000, "transport": 4000, "shopping": 20000, "entertainment": 9000, "healthcare": 1000, "education": 0},
            "debt": 4000.0,
        },
        {
            "name": "4. Overleveraged / Debt Heavy",
            "income": 50000.0,
            "balance": 5000.0,
            "expenses": {"food": 12000, "bills": 15000, "transport": 4000, "shopping": 6000, "entertainment": 3000, "healthcare": 2000, "education": 0},
            "debt": 22000.0,
        },
    ]

    print(f"{'Archetype':<34} | {'Score':<6} | {'Grade':<5} | {'Status':<16} | {'Runway'}")
    print("-" * 75)
    for arch in archetypes:
        res = calculate_financial_health_score(
            monthly_income=arch["income"],
            current_balance=arch["balance"],
            monthly_expenses=arch["expenses"],
            debt_obligations=arch["debt"],
        )
        print(f"{arch['name']:<34} | {res['financial_health_score']:>5.1f} | {res['grade']:<5} | {res['status']:<16} | {res['runway_months']} mo")

    print("=" * 75)


def main():
    evaluate_all_candidate_models()
    evaluate_financial_health_archetypes()


if __name__ == "__main__":
    main()
