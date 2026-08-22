"""
Feature extraction, baseline statistics, and explainability utilities for Phase 8 & 9.
Provides multi-factor fraud risk features and anomaly reason codes.
"""

from typing import Any, Dict, List, Optional
import numpy as np

# Standard 7 Categories matching the Fintra-AI ML roadmap
ROADMAP_CATEGORIES: List[str] = [
    "food",
    "shopping",
    "transport",
    "entertainment",
    "bills",
    "healthcare",
    "education",
]

# Baseline median and standard deviation spending benchmarks per category (INR)
CATEGORY_SPENDING_BASELINES: Dict[str, Dict[str, float]] = {
    "food": {"median": 650.0, "std": 950.0, "p95": 2800.0},
    "shopping": {"median": 2200.0, "std": 4500.0, "p95": 14000.0},
    "transport": {"median": 450.0, "std": 800.0, "p95": 2200.0},
    "entertainment": {"median": 750.0, "std": 1200.0, "p95": 3500.0},
    "bills": {"median": 3200.0, "std": 5000.0, "p95": 16000.0},
    "healthcare": {"median": 1200.0, "std": 3500.0, "p95": 9000.0},
    "education": {"median": 2500.0, "std": 6000.0, "p95": 18000.0},
}

FEATURE_COLUMNS: List[str] = [
    "amount",
    "amount_to_category_ratio",
    "hour_of_day",
    "is_night_time",
    "is_weekend",
    "distance_from_home_km",
    "device_trust_score",
    "merchant_risk_score",
    "velocity_1h",
    "is_foreign_currency",
]


def extract_transaction_features(
    amount: float,
    category: str = "shopping",
    hour_of_day: int = 14,
    is_weekend: int = 0,
    distance_from_home_km: float = 5.0,
    device_trust_score: float = 1.0,
    merchant_risk_score: float = 0.1,
    velocity_1h: int = 1,
    is_foreign_currency: int = 0,
) -> Dict[str, float]:
    """
    Extracts numerical feature vector for fraud and anomaly models.
    """
    cat = category.lower() if category.lower() in CATEGORY_SPENDING_BASELINES else "shopping"
    baseline_median = CATEGORY_SPENDING_BASELINES[cat]["median"]
    amount_ratio = float(amount / max(1.0, baseline_median))

    is_night = 1 if (hour_of_day >= 23 or hour_of_day <= 5) else 0

    return {
        "amount": float(amount),
        "amount_to_category_ratio": round(amount_ratio, 3),
        "hour_of_day": int(hour_of_day),
        "is_night_time": int(is_night),
        "is_weekend": int(is_weekend),
        "distance_from_home_km": float(distance_from_home_km),
        "device_trust_score": float(np.clip(device_trust_score, 0.0, 1.0)),
        "merchant_risk_score": float(np.clip(merchant_risk_score, 0.0, 1.0)),
        "velocity_1h": int(velocity_1h),
        "is_foreign_currency": int(is_foreign_currency),
    }


def generate_anomaly_reason_codes(
    features: Dict[str, float],
    category: str = "shopping",
) -> List[str]:
    """
    Generates explainable diagnostic reason codes highlighting why a transaction was flagged.
    """
    reasons = []
    cat = category.lower() if category.lower() in CATEGORY_SPENDING_BASELINES else "shopping"
    baseline = CATEGORY_SPENDING_BASELINES[cat]

    # 1. Amount Outlier / Spike Check
    if features.get("amount_to_category_ratio", 1.0) >= 5.0:
        reasons.append(
            f"Unusual spend spike: Amount is {features['amount_to_category_ratio']:.1f}x higher than the typical {cat} median (INR {baseline['median']:,.0f})."
        )
    elif features.get("amount", 0.0) >= baseline["p95"] * 2.0:
        reasons.append(
            f"High monetary amount: Transaction (INR {features['amount']:,.2f}) significantly exceeds the 95th percentile."
        )

    # 2. Unusual Time
    if features.get("is_night_time", 0) == 1:
        reasons.append(f"Off-hours activity: Transaction initiated at {int(features.get('hour_of_day', 0)):02d}:00 hours.")

    # 3. Device & Location Risk
    if features.get("device_trust_score", 1.0) < 0.35:
        reasons.append("Unrecognized hardware: Transaction performed from a new or untrusted device.")

    if features.get("distance_from_home_km", 0.0) >= 300.0:
        reasons.append(f"Geo-location deviation: Transaction location is {features['distance_from_home_km']:,.0f} km away from registered home base.")

    # 4. Merchant & Currency Risk
    if features.get("merchant_risk_score", 0.0) >= 0.65:
        reasons.append("High merchant risk: Merchant category or terminal has elevated dispute/fraud risk.")

    if features.get("is_foreign_currency", 0) == 1:
        reasons.append("Cross-border transaction: Payment processed in a foreign currency.")

    # 5. Velocity Check
    if features.get("velocity_1h", 1) >= 4:
        reasons.append(f"High velocity burst: {features['velocity_1h']} transactions detected within the last 60 minutes.")

    if not reasons:
        reasons.append("Transaction pattern aligns with normal user behavior.")

    return reasons
