"""
Subscription detection taxonomies, cadence estimators, interval analysis, and price hike rules (Phase 14).
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# Curated taxonomy of well-known subscription and recurring SaaS/utility patterns
KNOWN_SUBSCRIPTION_PATTERNS: Dict[str, Dict[str, Any]] = {
    "netflix": {"category": "entertainment", "typical_cadence": "MONTHLY", "typical_cost": 649.0},
    "spotify": {"category": "entertainment", "typical_cadence": "MONTHLY", "typical_cost": 119.0},
    "amazon prime": {"category": "entertainment", "typical_cadence": "ANNUAL", "typical_cost": 1499.0},
    "disney+ hotstar": {"category": "entertainment", "typical_cadence": "ANNUAL", "typical_cost": 899.0},
    "youtube premium": {"category": "entertainment", "typical_cadence": "MONTHLY", "typical_cost": 129.0},
    "apple one": {"category": "entertainment", "typical_cadence": "MONTHLY", "typical_cost": 365.0},
    "icloud": {"category": "bills", "typical_cadence": "MONTHLY", "typical_cost": 75.0},
    "google one": {"category": "bills", "typical_cadence": "MONTHLY", "typical_cost": 130.0},
    "chatgpt plus": {"category": "education", "typical_cadence": "MONTHLY", "typical_cost": 1999.0},
    "github copilot": {"category": "education", "typical_cadence": "MONTHLY", "typical_cost": 850.0},
    "cult.fit": {"category": "healthcare", "typical_cadence": "ANNUAL", "typical_cost": 14999.0},
    "gold's gym": {"category": "healthcare", "typical_cadence": "MONTHLY", "typical_cost": 2500.0},
    "jiofiber": {"category": "bills", "typical_cadence": "MONTHLY", "typical_cost": 825.0},
    "airtel broadband": {"category": "bills", "typical_cadence": "MONTHLY", "typical_cost": 943.0},
    "hometrust rent": {"category": "bills", "typical_cadence": "MONTHLY", "typical_cost": 22000.0},
    "star health insurance": {"category": "healthcare", "typical_cadence": "ANNUAL", "typical_cost": 12500.0},
}

FEATURE_COLUMNS_SUBSCRIPTION: List[str] = [
    "mean_amount",
    "amount_std",
    "is_exact_amount",
    "interval_mean_days",
    "interval_std_days",
    "transaction_count",
]


def estimate_cadence(interval_mean_days: float, interval_std_days: float) -> str:
    """
    Classifies the recurring billing cadence based on historical interval mean and standard deviation.
    """
    if interval_mean_days <= 0:
        return "MONTHLY"

    if 5.0 <= interval_mean_days <= 9.0 and interval_std_days <= 2.5:
        return "WEEKLY"
    elif 25.0 <= interval_mean_days <= 35.0 and interval_std_days <= 5.0:
        return "MONTHLY"
    elif 80.0 <= interval_mean_days <= 100.0 and interval_std_days <= 10.0:
        return "QUARTERLY"
    elif 340.0 <= interval_mean_days <= 390.0 and interval_std_days <= 20.0:
        return "ANNUAL"
    elif interval_std_days > 15.0:
        return "VARIABLE_PERIODIC"
    else:
        return "MONTHLY"


def calculate_next_renewal_date(
    last_date_str: str,
    cadence: str = "MONTHLY",
) -> Tuple[str, int]:
    """
    Predicts the next billing renewal date and days remaining until renewal.
    """
    try:
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        last_date = datetime.now() - timedelta(days=25)

    if cadence == "WEEKLY":
        days_to_add = 7
    elif cadence == "QUARTERLY":
        days_to_add = 90
    elif cadence == "ANNUAL":
        days_to_add = 365
    else:  # MONTHLY / DEFAULT
        days_to_add = 30

    next_date = last_date + timedelta(days=days_to_add)
    now = datetime.now()

    # If the computed next date is in the past, roll forward until future
    while next_date < now:
        next_date += timedelta(days=days_to_add)

    days_remaining = max(0, (next_date - now).days)
    return next_date.strftime("%Y-%m-%d"), days_remaining


def detect_price_hike(amounts: List[float]) -> Optional[Dict[str, Any]]:
    """
    Detects silent price increases across historical billing cycles.
    """
    if len(amounts) < 2:
        return None

    prev_amount = float(amounts[-2])
    current_amount = float(amounts[-1])

    if current_amount > prev_amount * 1.03:  # Price increased by >3%
        diff = current_amount - prev_amount
        pct_hike = round(((current_amount - prev_amount) / prev_amount) * 100.0, 1)
        return {
            "is_price_hike": True,
            "previous_amount": prev_amount,
            "current_amount": current_amount,
            "difference_inr": round(diff, 2),
            "percentage_hike": pct_hike,
            "alert_message": f"Silent Price Hike: Charge increased by {pct_hike}% (+INR {diff:,.2f}) compared to previous cycle.",
        }

    return None
