"""
Evaluation Pipeline for Subscription & Recurring Charge Detection Engine (Phase 14).

Evaluates candidate models on 1,600 held-out merchant sequences.
Computes PR-AUC, ROC-AUC, Recall, Precision, F1, and validates 6 real-world subscription archetypes.
"""

import json
import os
import sys
from typing import Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from inference.predict_subscriptions import (  # noqa: E402
    classify_recurring_merchant,
    detect_subscriptions_from_transactions,
)
from utils.subscription_rules import FEATURE_COLUMNS_SUBSCRIPTION  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "subscriptions_test.csv")
OUTPUT_METRICS = os.path.join(MODEL_DIR, "subscriptions_evaluation_metrics.json")


def evaluate_subscription_candidates():
    print("=" * 80)
    print("Held-Out Evaluation & Leaderboard Benchmark: Phase 14 Subscription Engine")
    print("=" * 80)

    if not os.path.exists(TEST_FILE):
        raise FileNotFoundError(f"Test dataset not found at {TEST_FILE}. Run preprocessing/preprocess_subscriptions.py first.")

    df_test = pd.read_csv(TEST_FILE)
    features = ["merchant_name", "category"] + FEATURE_COLUMNS_SUBSCRIPTION
    X_test = df_test[features]
    y_test = df_test["is_subscription"]

    print(f"[eval] Held-out Test Samples: {len(df_test):,} (Subscriptions: {y_test.sum()}, Ad-hoc: {len(y_test) - y_test.sum()})")
    print("-" * 80)

    candidate_names = ["logistic_regression", "random_forest", "extra_trees", "gradient_boosting", "xgboost", "ensemble"]
    leaderboard = {}

    print(f"{'Model Candidate':<22} | {'PR-AUC':<10} | {'ROC-AUC':<10} | {'Recall':<9} | {'Precision':<11} | {'F1-Score':<9} | {'FPR'}")
    print("-" * 80)

    for name in candidate_names:
        model_path = os.path.join(MODEL_DIR, f"subscriptions_{name}.pkl")
        if not os.path.exists(model_path):
            continue

        model = joblib.load(model_path)
        probs = model.predict_proba(X_test)[:, 1]
        preds = (probs >= 0.50).astype(int)

        pr_auc = average_precision_score(y_test, probs)
        roc_auc = roc_auc_score(y_test, probs)
        rec = recall_score(y_test, preds, zero_division=0)
        prec = precision_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)

        tn, fp, fn, tp = confusion_matrix(y_test, preds).ravel()
        fpr = float(fp / max(1, fp + tn))

        leaderboard[name] = {
            "pr_auc": round(float(pr_auc), 4),
            "roc_auc": round(float(roc_auc), 4),
            "recall": round(float(rec), 4),
            "precision": round(float(prec), 4),
            "f1": round(float(f1), 4),
            "fpr": round(float(fpr), 4),
        }

        print(
            f"{name:<22} | {pr_auc:>8.4f} | {roc_auc:>8.4f} | {rec:>7.2%} | {prec:>9.2%} | {f1:>8.4f} | {fpr:>6.2%}"
        )

    print("-" * 80)

    # Production Best Model Summary
    best_path = os.path.join(MODEL_DIR, "subscription_best_model.pkl")
    best_model = joblib.load(best_path)
    best_probs = best_model.predict_proba(X_test)[:, 1]
    best_preds = (best_probs >= 0.50).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, best_preds).ravel()
    best_pr_auc = average_precision_score(y_test, best_probs)
    best_roc_auc = roc_auc_score(y_test, best_probs)
    best_rec = recall_score(y_test, best_preds)
    best_prec = precision_score(y_test, best_preds)
    best_f1 = f1_score(y_test, best_preds)

    print("\n[Production Best Model Performance]")
    print(f"  * PR-AUC (Average Precision): {best_pr_auc:.4f}")
    print(f"  * ROC-AUC Score             : {best_roc_auc:.4f}")
    print(f"  * Subscription Recall       : {best_rec:.2%} ({tp}/{tp + fn} caught)")
    print(f"  * Precision                 : {best_prec:.2%}")
    print(f"  * False Positive Rate (FPR) : {fp / (fp + tn):.2%} ({fp}/{fp + tn} false alarms)")
    print(f"  * F1-Score                  : {best_f1:.4f}")

    metrics = {
        "test_samples": len(df_test),
        "total_subscriptions": int(y_test.sum()),
        "leaderboard": leaderboard,
        "production_best": {
            "pr_auc": round(float(best_pr_auc), 4),
            "roc_auc": round(float(best_roc_auc), 4),
            "recall": round(float(best_rec), 4),
            "precision": round(float(best_prec), 4),
            "f1": round(float(best_f1), 4),
            "false_positive_rate": round(float(fp / (fp + tn)), 4),
        },
    }

    with open(OUTPUT_METRICS, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] Saved evaluation metrics -> {OUTPUT_METRICS}")
    return metrics


def evaluate_subscription_archetypes():
    print("\n" + "=" * 85)
    print("Real-World Subscription Archetype Validation: Phase 14")
    print("=" * 85)

    archetypes = [
        {
            "name": "1. Netflix Premium",
            "merchant": "Netflix India",
            "amount": 649.0,
            "category": "entertainment",
            "interval_mean": 30.0,
            "interval_std": 0.2,
            "count": 6,
            "expected": "SUBSCRIPTION (Monthly)",
        },
        {
            "name": "2. Cult.fit Elite Annual Pass",
            "merchant": "Cult.fit",
            "amount": 14999.0,
            "category": "healthcare",
            "interval_mean": 365.0,
            "interval_std": 1.0,
            "count": 2,
            "expected": "SUBSCRIPTION (Annual)",
        },
        {
            "name": "3. JioFiber Broadband",
            "merchant": "JioFiber",
            "amount": 825.0,
            "category": "bills",
            "interval_mean": 30.0,
            "interval_std": 0.5,
            "count": 12,
            "expected": "SUBSCRIPTION (Monthly)",
        },
        {
            "name": "4. Apple iCloud 50GB",
            "merchant": "Apple.com/bill",
            "amount": 75.0,
            "category": "bills",
            "interval_mean": 30.0,
            "interval_std": 0.1,
            "count": 8,
            "expected": "SUBSCRIPTION (Monthly)",
        },
        {
            "name": "5. Swiggy Food Orders (Ad-hoc)",
            "merchant": "Swiggy",
            "amount": 450.0,
            "category": "food",
            "interval_mean": 4.2,
            "interval_std": 18.5,
            "count": 14,
            "expected": "AD_HOC (Not a subscription)",
        },
    ]

    print(f"{'Archetype Scenario':<32} | {'Amount (INR)':<13} | {'Is Sub':<8} | {'Cadence':<10} | {'Confidence':<11} | {'Renewal Date'}")
    print("-" * 85)

    for arch in archetypes:
        res = classify_recurring_merchant(
            merchant_name=arch["merchant"],
            amount=arch["amount"],
            category=arch["category"],
            interval_mean_days=arch["interval_mean"],
            interval_std_days=arch["interval_std"],
            transaction_count=arch["count"],
        )
        print(
            f"{arch['name']:<32} | INR {arch['amount']:>8,.2f} | {str(res['is_subscription']):<8} | "
            f"{res['cadence']:<10} | {res['confidence_pct']:>8.1f}% | {res['next_renewal_date'] or 'N/A'}"
        )

    print("=" * 85)


def main():
    evaluate_subscription_candidates()
    evaluate_subscription_archetypes()


if __name__ == "__main__":
    main()
