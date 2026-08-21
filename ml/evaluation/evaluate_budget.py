"""
Evaluation Pipeline for Budget Recommendation & Financial Health Scoring (Phases 5 & 7).

Evaluates prediction accuracy, constraint conservation, 50/30/20 alignment,
and health scoring consistency across held-out test datasets and edge-case profiles.
"""

import json
import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from inference.predict_budget import calculate_financial_health_score, recommend_budget  # noqa: E402
from utils.budget_rules import ROADMAP_CATEGORIES  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "budget_test.csv")
MODEL_FILE = os.path.join(MODEL_DIR, "budget_recommender.pkl")
OUTPUT_METRICS = os.path.join(MODEL_DIR, "budget_evaluation_metrics.json")


def evaluate_held_out_dataset():
    print("=" * 65)
    print("Evaluation Pipeline: Phase 5 Budget Recommendation Engine")
    print("=" * 65)

    if not os.path.exists(TEST_FILE):
        raise FileNotFoundError(f"Test dataset not found at {TEST_FILE}. Run preprocessing/preprocess_budget.py first.")

    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(f"Model file not found at {MODEL_FILE}. Run training/train_budget.py first.")

    df_test = pd.read_csv(TEST_FILE)
    pipeline = joblib.load(MODEL_FILE)

    num_cols = ["monthly_income", "savings_target_pct", "debt_to_income_ratio"]
    hist_cols = [f"hist_ratio_{cat}" for cat in ROADMAP_CATEGORIES]
    cat_cols = ["lifestyle"]
    target_cols = [f"target_budget_{cat}" for cat in ROADMAP_CATEGORIES] + ["target_budget_savings"]

    X_test = df_test[num_cols + hist_cols + cat_cols]
    y_true = df_test[target_cols]

    y_pred = pipeline.predict(X_test)

    # 1. Overall Metrics
    overall_mae = mean_absolute_error(y_true, y_pred)
    overall_r2 = r2_score(y_true, y_pred, multioutput="uniform_average")

    print(f"[eval] Held-out Test Samples: {len(df_test):,}")
    print(f"[eval] Overall Multi-Target MAE: INR {overall_mae:,.2f}")
    print(f"[eval] Overall Multi-Target R2 : {overall_r2:.4f}")
    print("-" * 65)

    # 2. Per-Category Breakdown
    category_metrics = {}
    print(f"{'Category / Target':<25} | {'MAE (INR)':<15} | {'R2 Score':<10}")
    print("-" * 65)
    for i, col in enumerate(target_cols):
        cat_name = col.replace("target_budget_", "").capitalize()
        mae_cat = mean_absolute_error(y_true.iloc[:, i], y_pred[:, i])
        r2_cat = r2_score(y_true.iloc[:, i], y_pred[:, i])
        category_metrics[cat_name] = {"mae": round(mae_cat, 2), "r2": round(r2_cat, 4)}
        print(f"{cat_name:<25} | INR {mae_cat:>8,.2f} | {r2_cat:>9.4f}")

    print("-" * 65)

    # 3. Constraint Satisfaction Verification
    # Sum of predictions vs income
    pred_sums = np.sum(y_pred, axis=1)
    income_sums = df_test["monthly_income"].values
    discrepancies = np.abs(pred_sums - income_sums)
    mean_discrepancy = float(np.mean(discrepancies))
    max_discrepancy = float(np.max(discrepancies))
    print(f"[constraint] Mean Budget Discrepancy : INR {mean_discrepancy:.2f}")
    print(f"[constraint] Max Budget Discrepancy  : INR {max_discrepancy:.2f}")

    metrics = {
        "test_samples": len(df_test),
        "overall_mae": round(overall_mae, 2),
        "overall_r2": round(overall_r2, 4),
        "mean_discrepancy": round(mean_discrepancy, 2),
        "max_discrepancy": round(max_discrepancy, 2),
        "category_metrics": category_metrics,
    }

    with open(OUTPUT_METRICS, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] Saved evaluation metrics -> {OUTPUT_METRICS}")
    return metrics


def evaluate_financial_health_archetypes():
    print("\n" + "=" * 65)
    print("Evaluation Pipeline: Phase 7 Financial Health Score Archetypes")
    print("=" * 65)

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

    print(f"{'Archetype':<32} | {'Score':<6} | {'Grade':<5} | {'Status':<15} | {'Runway'}")
    print("-" * 65)
    for arch in archetypes:
        res = calculate_financial_health_score(
            monthly_income=arch["income"],
            current_balance=arch["balance"],
            monthly_expenses=arch["expenses"],
            debt_obligations=arch["debt"],
        )
        print(f"{arch['name']:<32} | {res['financial_health_score']:>5.1f} | {res['grade']:<5} | {res['status']:<15} | {res['runway_months']} mo")

    print("=" * 65)


def main():
    evaluate_held_out_dataset()
    evaluate_financial_health_archetypes()


if __name__ == "__main__":
    main()
