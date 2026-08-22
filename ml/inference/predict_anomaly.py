"""
Inference Pipeline for Fraud Detection & Spending Anomaly Engine (Phases 8 & 9).

Provides:
1. detect_transaction_anomaly: Real-time outlier detection, duplicate payment checks, and reason codes.
2. predict_fraud_risk: Multi-factor fraud probability scoring (0-100%), risk tier, and action recommendations.
"""

import argparse
import json
import os
import sys
from functools import lru_cache
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.anomaly_features import (  # noqa: E402
    CATEGORY_SPENDING_BASELINES,
    FEATURE_COLUMNS,
    ROADMAP_CATEGORIES,
    extract_transaction_features,
    generate_anomaly_reason_codes,
)

DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


@lru_cache(maxsize=1)
def load_anomaly_artifacts(model_dir: str = DEFAULT_MODEL_DIR):
    """
    Loads and caches trained unsupervised and supervised models.
    """
    iso_path = os.path.join(model_dir, "anomaly_isolation_forest.pkl")
    fraud_path = os.path.join(model_dir, "fraud_best_model.pkl")
    meta_path = os.path.join(model_dir, "fraud_train_metrics.json")

    iso_model = joblib.load(iso_path) if os.path.exists(iso_path) else None
    fraud_model = joblib.load(fraud_path) if os.path.exists(fraud_path) else None

    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)

    return iso_model, fraud_model, meta


def detect_transaction_anomaly(
    transaction: Dict[str, Any],
    recent_transactions: Optional[List[Dict[str, Any]]] = None,
    model_dir: str = DEFAULT_MODEL_DIR,
) -> Dict[str, Any]:
    """
    Detects spending anomalies (outlier amounts, duplicate payments, abnormal off-hours).
    """
    amount = float(transaction.get("amount", 0.0))
    category = str(transaction.get("category", "shopping")).lower()
    merchant = str(transaction.get("merchant", "Unknown"))
    hour = int(transaction.get("hour_of_day", 14))

    features = extract_transaction_features(
        amount=amount,
        category=category,
        hour_of_day=hour,
        is_weekend=int(transaction.get("is_weekend", 0)),
        distance_from_home_km=float(transaction.get("distance_from_home_km", 5.0)),
        device_trust_score=float(transaction.get("device_trust_score", 1.0)),
        merchant_risk_score=float(transaction.get("merchant_risk_score", 0.1)),
        velocity_1h=int(transaction.get("velocity_1h", 1)),
        is_foreign_currency=int(transaction.get("is_foreign_currency", 0)),
    )

    # 1. Duplicate Transaction Detection Check
    is_duplicate = False
    if recent_transactions:
        for prev in recent_transactions:
            prev_merchant = str(prev.get("merchant", "")).lower()
            prev_amount = float(prev.get("amount", 0.0))
            if prev_merchant == merchant.lower() and abs(prev_amount - amount) < 0.01:
                is_duplicate = True
                break

    # 2. Unsupervised Outlier Evaluation
    iso_bundle, _, _ = load_anomaly_artifacts(model_dir)
    is_outlier = False
    anomaly_score = 0.0

    if iso_bundle is not None:
        preprocessor, iso_model = iso_bundle
        df_in = pd.DataFrame([{**features, "category": category}])
        X_proc = preprocessor.transform(df_in)
        pred = iso_model.predict(X_proc)[0]  # -1 for anomaly, 1 for inlier
        raw_score = float(iso_model.decision_function(X_proc)[0])
        is_outlier = bool(pred == -1)
        anomaly_score = round(float(-raw_score), 4)
    else:
        # Statistical rule fallback
        baseline = CATEGORY_SPENDING_BASELINES.get(category, CATEGORY_SPENDING_BASELINES["shopping"])
        if amount > baseline["p95"] * 2.0 or features["amount_to_category_ratio"] >= 6.0:
            is_outlier = True
            anomaly_score = 0.65

    reasons = generate_anomaly_reason_codes(features, category=category)
    if is_duplicate:
        reasons.insert(0, f"Potential duplicate payment: An identical charge of INR {amount:,.2f} at '{merchant}' was found in recent transactions.")

    # Determine Severity
    is_flagged = bool(is_outlier or is_duplicate or features["amount_to_category_ratio"] >= 5.0)
    if is_duplicate or features["amount_to_category_ratio"] >= 10.0:
        severity = "CRITICAL"
    elif is_flagged:
        severity = "WARNING"
    else:
        severity = "NORMAL"

    return {
        "status": "success",
        "merchant": merchant,
        "amount": amount,
        "category": category,
        "is_anomaly": is_flagged,
        "severity": severity,
        "is_duplicate_payment": is_duplicate,
        "anomaly_score": anomaly_score,
        "features": features,
        "reasons": reasons,
    }


def predict_fraud_risk(
    transaction: Dict[str, Any],
    model_dir: str = DEFAULT_MODEL_DIR,
) -> Dict[str, Any]:
    """
    Predicts transaction fraud probability (0-100%) and categorizes risk.
    """
    amount = float(transaction.get("amount", 0.0))
    category = str(transaction.get("category", "shopping")).lower()
    merchant = str(transaction.get("merchant", "Unknown"))
    hour = int(transaction.get("hour_of_day", 14))

    features = extract_transaction_features(
        amount=amount,
        category=category,
        hour_of_day=hour,
        is_weekend=int(transaction.get("is_weekend", 0)),
        distance_from_home_km=float(transaction.get("distance_from_home_km", 5.0)),
        device_trust_score=float(transaction.get("device_trust_score", 1.0)),
        merchant_risk_score=float(transaction.get("merchant_risk_score", 0.1)),
        velocity_1h=int(transaction.get("velocity_1h", 1)),
        is_foreign_currency=int(transaction.get("is_foreign_currency", 0)),
    )

    _, fraud_pipeline, meta = load_anomaly_artifacts(model_dir)

    if fraud_pipeline is not None:
        df_in = pd.DataFrame([{**features, "category": category}])
        probs = fraud_pipeline.predict_proba(df_in)[0]
        fraud_prob = float(probs[1])
    else:
        # Rule-based fallback if weights not loaded
        prob = 0.05
        if features["amount_to_category_ratio"] >= 7.0:
            prob += 0.40
        if features["is_night_time"]:
            prob += 0.20
        if features["device_trust_score"] < 0.3:
            prob += 0.25
        if features["merchant_risk_score"] > 0.6:
            prob += 0.20
        fraud_prob = float(np.clip(prob, 0.01, 0.99))

    fraud_percentage = round(fraud_prob * 100.0, 1)

    # Risk Tiering & Recommended Action
    if fraud_prob >= 0.70:
        risk_level = "HIGH"
        recommended_action = "BLOCK_TRANSACTION"
        action_detail = "High probability of unauthorized fraud. Block charge and prompt user verification via OTP/SMS."
    elif fraud_prob >= 0.30:
        risk_level = "MEDIUM"
        recommended_action = "MANUAL_REVIEW"
        action_detail = "Elevated risk detected. Surface in-app confirmation banner to verify legitimacy."
    else:
        risk_level = "LOW"
        recommended_action = "ALLOW"
        action_detail = "Transaction pattern matches genuine cardholder profile."

    reasons = generate_anomaly_reason_codes(features, category=category)

    return {
        "status": "success",
        "merchant": merchant,
        "amount": amount,
        "category": category,
        "fraud_probability": round(fraud_prob, 4),
        "fraud_percentage": fraud_percentage,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "action_detail": action_detail,
        "risk_factors": reasons,
    }


def main():
    parser = argparse.ArgumentParser(description="Phase 8 Fraud & Phase 9 Spending Anomaly Inference API")
    parser.add_argument("--mode", choices=["anomaly", "fraud"], default="fraud")
    parser.add_argument("--merchant", default="Swiggy", help="Merchant / Store Name")
    parser.add_argument("--amount", type=float, required=True, help="Transaction amount in INR")
    parser.add_argument("--category", choices=ROADMAP_CATEGORIES, default="shopping")
    parser.add_argument("--hour", type=int, default=14, help="Hour of transaction (0-23)")
    parser.add_argument("--distance", type=float, default=5.0, help="Geo-distance from home in km")
    parser.add_argument("--device-trust", type=float, default=0.9, help="Device trust score (0.0 to 1.0)")
    parser.add_argument("--merchant-risk", type=float, default=0.1, help="Merchant risk score (0.0 to 1.0)")
    parser.add_argument("--velocity", type=int, default=1, help="Transactions in last 1 hour")
    parser.add_argument("--foreign", type=int, default=0, help="Is foreign currency transaction (0 or 1)")

    args = parser.parse_args()

    tx = {
        "merchant": args.merchant,
        "amount": args.amount,
        "category": args.category,
        "hour_of_day": args.hour,
        "distance_from_home_km": args.distance,
        "device_trust_score": args.device_trust,
        "merchant_risk_score": args.merchant_risk,
        "velocity_1h": args.velocity,
        "is_foreign_currency": args.foreign,
    }

    if args.mode == "anomaly":
        res = detect_transaction_anomaly(tx)
    else:
        res = predict_fraud_risk(tx)

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
