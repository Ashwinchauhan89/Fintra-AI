"""
Inference API for Subscription & Recurring Charge Detection Engine (Phase 14).

Provides:
1. classify_recurring_merchant: Evaluates individual merchant title and cadence.
2. detect_subscriptions_from_transactions: Full transaction stream scanner that detects active subscriptions,
   predicts upcoming renewal dates, tracks silent price hikes, and computes monthly subscription burn.
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
from utils.subscription_rules import (  # noqa: E402
    FEATURE_COLUMNS_SUBSCRIPTION,
    KNOWN_SUBSCRIPTION_PATTERNS,
    calculate_next_renewal_date,
    detect_price_hike,
    estimate_cadence,
)

DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


@lru_cache(maxsize=1)
def load_subscription_model(model_dir: str = DEFAULT_MODEL_DIR):
    """
    Loads and caches the trained subscription classifier pipeline.
    """
    model_path = os.path.join(model_dir, "subscription_best_model.pkl")
    meta_path = os.path.join(model_dir, "subscriptions_train_metrics.json")

    model = joblib.load(model_path) if os.path.exists(model_path) else None
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)

    return model, meta


def classify_recurring_merchant(
    merchant_name: str,
    amount: float,
    category: str = "entertainment",
    interval_mean_days: float = 30.0,
    interval_std_days: float = 0.5,
    transaction_count: int = 3,
    last_date_str: Optional[str] = None,
    model_dir: str = DEFAULT_MODEL_DIR,
) -> Dict[str, Any]:
    """
    Classifies a single merchant pattern and determines subscription status and cadence.
    """
    merchant = str(merchant_name).strip()
    amt = float(amount)
    cat = str(category).lower()
    last_date = last_date_str or datetime.now().strftime("%Y-%m-%d")

    features = {
        "merchant_name": merchant,
        "category": cat,
        "mean_amount": amt,
        "amount_std": float(np.clip(interval_std_days * 0.1, 0.0, 50.0)),
        "is_exact_amount": 1 if interval_std_days <= 1.0 else 0,
        "interval_mean_days": float(interval_mean_days),
        "interval_std_days": float(interval_std_days),
        "transaction_count": int(transaction_count),
    }

    model, _ = load_subscription_model(model_dir)

    if model is not None:
        df_in = pd.DataFrame([features])
        prob = float(model.predict_proba(df_in)[0, 1])
        is_sub = bool(prob >= 0.50)
    else:
        # Taxonomy heuristic fallback
        is_sub = any(k in merchant.lower() for k in KNOWN_SUBSCRIPTION_PATTERNS)
        prob = 0.95 if is_sub else 0.10

    cadence = estimate_cadence(interval_mean_days, interval_std_days) if is_sub else "NONE"
    next_date, days_left = calculate_next_renewal_date(last_date, cadence)

    # Monthly equivalent cost calculation
    if cadence == "ANNUAL":
        monthly_cost = round(amt / 12.0, 2)
    elif cadence == "WEEKLY":
        monthly_cost = round(amt * 4.33, 2)
    elif cadence == "QUARTERLY":
        monthly_cost = round(amt / 3.0, 2)
    elif cadence == "MONTHLY":
        monthly_cost = round(amt, 2)
    else:
        monthly_cost = 0.0

    return {
        "status": "success",
        "merchant": merchant,
        "amount": amt,
        "category": cat,
        "is_subscription": is_sub,
        "subscription_probability": round(prob, 4),
        "confidence_pct": round(prob * 100.0, 1),
        "cadence": cadence,
        "monthly_equivalent_cost": monthly_cost,
        "next_renewal_date": next_date if is_sub else None,
        "days_until_renewal": days_left if is_sub else None,
    }


def detect_subscriptions_from_transactions(
    transactions: List[Dict[str, Any]],
    model_dir: str = DEFAULT_MODEL_DIR,
) -> Dict[str, Any]:
    """
    Scans full user transaction history, clusters by merchant, predicts recurring subscriptions,
    detects price hikes, and compiles an upcoming renewal schedule.
    """
    if not transactions:
        return {
            "status": "success",
            "active_subscriptions_count": 0,
            "active_subscriptions": [],
            "total_monthly_burn": 0.0,
            "annual_projected_cost": 0.0,
            "upcoming_renewals": [],
            "price_hike_alerts": [],
        }

    # 1. Group transactions by normalized merchant
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for tx in transactions:
        m_raw = str(tx.get("merchant", tx.get("description", "Unknown"))).strip()
        m_key = m_raw.lower()
        if m_key not in groups:
            groups[m_key] = []
        groups[m_key].append(tx)

    active_subscriptions = []
    price_hikes = []
    total_monthly_burn = 0.0

    for m_key, tx_list in groups.items():
        # Sort chronologically
        try:
            sorted_txs = sorted(tx_list, key=lambda x: str(x.get("date", "2026-01-01")))
        except Exception:
            sorted_txs = tx_list

        amounts = [float(t.get("amount", 0.0)) for t in sorted_txs]
        category = str(sorted_txs[0].get("category", "entertainment"))
        merchant_name = str(sorted_txs[0].get("merchant", sorted_txs[0].get("description", m_key.title())))
        last_date = str(sorted_txs[-1].get("date", datetime.now().strftime("%Y-%m-%d")))

        # Compute interval statistics
        if len(sorted_txs) >= 2:
            intervals = []
            for i in range(1, len(sorted_txs)):
                try:
                    d1 = datetime.strptime(str(sorted_txs[i - 1].get("date", "2026-01-01")), "%Y-%m-%d")
                    d2 = datetime.strptime(str(sorted_txs[i].get("date", "2026-01-01")), "%Y-%m-%d")
                    intervals.append(abs((d2 - d1).days))
                except Exception:
                    intervals.append(30)

            interval_mean = float(np.mean(intervals)) if intervals else 30.0
            interval_std = float(np.std(intervals)) if intervals else 0.0
        else:
            # Single occurrence: check against known subscription taxonomy
            is_known = any(k in m_key for k in KNOWN_SUBSCRIPTION_PATTERNS)
            interval_mean = 30.0 if is_known else 0.0
            interval_std = 0.1 if is_known else 20.0

        res = classify_recurring_merchant(
            merchant_name=merchant_name,
            amount=float(np.mean(amounts)),
            category=category,
            interval_mean_days=interval_mean,
            interval_std_days=interval_std,
            transaction_count=len(sorted_txs),
            last_date_str=last_date,
            model_dir=model_dir,
        )

        if res["is_subscription"]:
            active_subscriptions.append(res)
            total_monthly_burn += res["monthly_equivalent_cost"]

            # Check for silent price hike
            hike = detect_price_hike(amounts)
            if hike is not None:
                hike["merchant"] = merchant_name
                price_hikes.append(hike)

    # Sort upcoming renewals by days remaining
    upcoming_renewals = sorted(
        [s for s in active_subscriptions if s["days_until_renewal"] is not None],
        key=lambda x: x["days_until_renewal"],
    )

    return {
        "status": "success",
        "active_subscriptions_count": len(active_subscriptions),
        "total_monthly_burn": round(total_monthly_burn, 2),
        "annual_projected_cost": round(total_monthly_burn * 12.0, 2),
        "active_subscriptions": active_subscriptions,
        "upcoming_renewals": upcoming_renewals,
        "price_hike_alerts": price_hikes,
    }


def main():
    parser = argparse.ArgumentParser(description="Phase 14 Subscription & Recurring Charge Detection API")
    parser.add_argument("--mode", choices=["classify", "scan"], default="classify")
    parser.add_argument("--merchant", default="Netflix", help="Merchant Name")
    parser.add_argument("--amount", type=float, default=649.0, help="Amount in INR")
    parser.add_argument("--category", default="entertainment", help="Category")
    parser.add_argument("--interval-mean", type=float, default=30.0, help="Average interval in days")
    parser.add_argument("--interval-std", type=float, default=0.5, help="Standard deviation of interval in days")
    parser.add_argument("--count", type=int, default=4, help="Historical transaction count")

    args = parser.parse_args()

    if args.mode == "classify":
        res = classify_recurring_merchant(
            merchant_name=args.merchant,
            amount=args.amount,
            category=args.category,
            interval_mean_days=args.interval_mean,
            interval_std_days=args.interval_std,
            transaction_count=args.count,
        )
    else:
        # Sample scan simulation
        sample_txs = [
            {"date": "2026-06-25", "merchant": "Netflix", "amount": 649.0, "category": "entertainment"},
            {"date": "2026-07-25", "merchant": "Netflix", "amount": 649.0, "category": "entertainment"},
            {"date": "2026-08-25", "merchant": "Netflix", "amount": 649.0, "category": "entertainment"},
            {"date": "2026-07-10", "merchant": "Spotify", "amount": 119.0, "category": "entertainment"},
            {"date": "2026-08-10", "merchant": "Spotify", "amount": 149.0, "category": "entertainment"},
            {"date": "2026-08-01", "merchant": "JioFiber", "amount": 825.0, "category": "bills"},
            {"date": "2026-08-05", "merchant": "Swiggy", "amount": 420.0, "category": "food"},
            {"date": "2026-08-09", "merchant": "Swiggy", "amount": 780.0, "category": "food"},
        ]
        res = detect_subscriptions_from_transactions(sample_txs)

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
