"""
Evaluation Pipeline for Fraud Detection & Spending Anomaly Engine (Phases 8 & 9).

Evaluates candidate fraud and anomaly models on 2,000 held-out transactions.
Computes PR-AUC, ROC-AUC, Recall, Precision, F1, and validates edge-case transaction archetypes.
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
from inference.predict_anomaly import detect_transaction_anomaly, predict_fraud_risk  # noqa: E402
from utils.anomaly_features import FEATURE_COLUMNS  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "anomaly_test.csv")
OUTPUT_METRICS = os.path.join(MODEL_DIR, "fraud_evaluation_metrics.json")


def evaluate_fraud_candidates():
    print("=" * 80)
    print("Held-Out Evaluation & Leaderboard Benchmark: Phase 8 Fraud Detection")
    print("=" * 80)

    if not os.path.exists(TEST_FILE):
        raise FileNotFoundError(f"Test dataset not found at {TEST_FILE}. Run preprocessing/preprocess_anomaly.py first.")

    df_test = pd.read_csv(TEST_FILE)
    feature_cols = FEATURE_COLUMNS + ["category"]
    X_test = df_test[feature_cols]
    y_test = df_test["is_fraud"]

    print(f"[eval] Held-out Test Samples: {len(df_test):,} (Total Fraud: {y_test.sum()}, Normal: {len(y_test) - y_test.sum()})")
    print("-" * 80)

    candidate_names = ["random_forest", "extra_trees", "gradient_boosting", "xgboost", "ensemble"]
    leaderboard = {}

    print(f"{'Model Candidate':<22} | {'PR-AUC':<10} | {'ROC-AUC':<10} | {'Recall':<9} | {'Precision':<11} | {'F1-Score':<9} | {'FPR'}")
    print("-" * 80)

    for name in candidate_names:
        model_path = os.path.join(MODEL_DIR, f"fraud_{name}.pkl")
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

    # -------------------------------------------------------------
    # Production Best Model In-Depth Summary
    # -------------------------------------------------------------
    best_path = os.path.join(MODEL_DIR, "fraud_best_model.pkl")
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
    print(f"  * Fraud Recall (Caught)     : {best_rec:.2%} ({tp}/{tp + fn} frauds caught)")
    print(f"  * Precision                 : {best_prec:.2%}")
    print(f"  * False Positive Rate (FPR) : {fp / (fp + tn):.2%} ({fp}/{fp + tn} false alarms)")
    print(f"  * F1-Score                  : {best_f1:.4f}")

    metrics = {
        "test_samples": len(df_test),
        "total_frauds": int(y_test.sum()),
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


def evaluate_transaction_archetypes():
    print("\n" + "=" * 80)
    print("Real-World Transaction Archetype Validation: Phases 8 & 9")
    print("=" * 80)

    archetypes = [
        {
            "name": "1. Legitimate Grocery Spend",
            "tx": {"merchant": "Swiggy Instamart", "amount": 420.0, "category": "food", "hour_of_day": 19, "distance_from_home_km": 2.0, "device_trust_score": 1.0, "merchant_risk_score": 0.05, "velocity_1h": 1, "is_foreign_currency": 0},
            "expected_fraud": "LOW",
        },
        {
            "name": "2. High Amount Spike (Jewelry)",
            "tx": {"merchant": "Tanishq", "amount": 85000.0, "category": "shopping", "hour_of_day": 16, "distance_from_home_km": 12.0, "device_trust_score": 0.9, "merchant_risk_score": 0.20, "velocity_1h": 1, "is_foreign_currency": 0},
            "expected_fraud": "MEDIUM",
        },
        {
            "name": "3. Late Night Foreign Casino",
            "tx": {"merchant": "Macau Grand Casino", "amount": 95000.0, "category": "entertainment", "hour_of_day": 3, "distance_from_home_km": 3200.0, "device_trust_score": 0.05, "merchant_risk_score": 0.95, "velocity_1h": 2, "is_foreign_currency": 1},
            "expected_fraud": "HIGH",
        },
        {
            "name": "4. Rapid High-Velocity Burst",
            "tx": {"merchant": "Apple Store Online", "amount": 12900.0, "category": "shopping", "hour_of_day": 11, "distance_from_home_km": 80.0, "device_trust_score": 0.40, "merchant_risk_score": 0.50, "velocity_1h": 6, "is_foreign_currency": 0},
            "expected_fraud": "HIGH",
        },
        {
            "name": "5. Travel Hotel Booking",
            "tx": {"merchant": "Taj Hotels", "amount": 11500.0, "category": "transport", "hour_of_day": 14, "distance_from_home_km": 450.0, "device_trust_score": 0.85, "merchant_risk_score": 0.15, "velocity_1h": 1, "is_foreign_currency": 0},
            "expected_fraud": "LOW",
        },
    ]

    print(f"{'Archetype Scenario':<30} | {'Amount (INR)':<13} | {'Fraud Prob':<12} | {'Risk Tier':<10} | {'Action'}")
    print("-" * 80)

    for arch in archetypes:
        res = predict_fraud_risk(arch["tx"])
        print(
            f"{arch['name']:<30} | INR {arch['tx']['amount']:>8,.2f} | {res['fraud_percentage']:>9.1f}% | "
            f"{res['risk_level']:<10} | {res['recommended_action']}"
        )

    print("=" * 80)


def main():
    evaluate_fraud_candidates()
    evaluate_transaction_archetypes()


if __name__ == "__main__":
    main()
