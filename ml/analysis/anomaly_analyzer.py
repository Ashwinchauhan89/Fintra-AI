"""
Fintra-AI Anomaly & Outlier Analyzer Module
Provides statistical outlier detection (IQR & Z-score), duplicate transaction detection,
and unexpected behavioral spending pattern detection with explainable reason codes.

IMPORTANT: This module focuses on statistical anomalies in personal finance
and deliberately distinguishes statistical deviations from fraud.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from ml.utils.anomaly_features import (
    CATEGORY_SPENDING_BASELINES,
    generate_anomaly_reason_codes,
)


def detect_amount_outliers_iqr(
    df: pd.DataFrame,
    group_by_category: bool = True,
    iqr_multiplier: float = 1.5
) -> pd.DataFrame:
    """
    Identifies amount outliers using the Interquartile Range (IQR) method.
    
    Statistical formula:
    - IQR = Q3 - Q1
    - Lower Bound = Q1 - (iqr_multiplier * IQR)
    - Upper Bound = Q3 + (iqr_multiplier * IQR)
    
    Can evaluate globally or per category to account for varying category price baselines.
    """
    if df is None or df.empty or "amount" not in df.columns:
        return pd.DataFrame()

    expenses = df[df["type"] == "EXPENSE"].copy()
    if expenses.empty:
        return pd.DataFrame()

    flagged_dfs = []

    if group_by_category and "category" in expenses.columns:
        for cat, group in expenses.groupby("category"):
            if len(group) < 4:
                continue
            q1 = group["amount"].quantile(0.25)
            q3 = group["amount"].quantile(0.75)
            iqr = q3 - q1
            if iqr <= 0:
                continue
            lower_bound = max(0.0, q1 - (iqr_multiplier * iqr))
            upper_bound = q3 + (iqr_multiplier * iqr)

            outliers = group[(group["amount"] < lower_bound) | (group["amount"] > upper_bound)].copy()
            if not outliers.empty:
                outliers["outlier_method"] = "IQR_CATEGORY"
                outliers["iqr_lower_bound"] = round(lower_bound, 2)
                outliers["iqr_upper_bound"] = round(upper_bound, 2)
                outliers["deviation_from_median"] = (
                    outliers["amount"] - group["amount"].median()
                ).round(2)
                flagged_dfs.append(outliers)
    else:
        q1 = expenses["amount"].quantile(0.25)
        q3 = expenses["amount"].quantile(0.75)
        iqr = q3 - q1
        lower_bound = max(0.0, q1 - (iqr_multiplier * iqr))
        upper_bound = q3 + (iqr_multiplier * iqr)

        outliers = expenses[(expenses["amount"] < lower_bound) | (expenses["amount"] > upper_bound)].copy()
        if not outliers.empty:
            outliers["outlier_method"] = "IQR_GLOBAL"
            outliers["iqr_lower_bound"] = round(lower_bound, 2)
            outliers["iqr_upper_bound"] = round(upper_bound, 2)
            outliers["deviation_from_median"] = (
                outliers["amount"] - expenses["amount"].median()
            ).round(2)
            flagged_dfs.append(outliers)

    if not flagged_dfs:
        return pd.DataFrame()

    res = pd.concat(flagged_dfs, ignore_index=True)
    return res.sort_values(by="amount", ascending=False).reset_index(drop=True)


def detect_amount_outliers_zscore(
    df: pd.DataFrame,
    threshold: float = 3.0
) -> pd.DataFrame:
    """
    Identifies extreme amount outliers using standard Z-score statistical thresholding.
    
    Formula: Z = (amount - mean) / std
    Flagged if |Z| >= threshold (default 3.0 standard deviations).
    """
    if df is None or df.empty or len(df) < 5:
        return pd.DataFrame()

    expenses = df[df["type"] == "EXPENSE"].copy()
    if len(expenses) < 5:
        return pd.DataFrame()

    mean_val = expenses["amount"].mean()
    std_val = expenses["amount"].std()

    if std_val == 0 or np.isnan(std_val):
        return pd.DataFrame()

    expenses["z_score"] = ((expenses["amount"] - mean_val) / std_val).round(2)
    outliers = expenses[expenses["z_score"].abs() >= threshold].copy()
    outliers["outlier_method"] = "Z_SCORE"
    return outliers.sort_values(by="z_score", ascending=False).reset_index(drop=True)


def detect_duplicate_transactions(
    df: pd.DataFrame,
    time_window_hours: float = 24.0,
    amount_tolerance: float = 0.0
) -> pd.DataFrame:
    """
    Identifies potential duplicate or double-charged transactions.
    
    CRITICAL: Does NOT delete records. Only flags them for user/auditor review.
    
    Detection Criteria:
    - Same merchant and category
    - Identical or near-identical amount (within amount_tolerance)
    - Occurring within time_window_hours of each other
    """
    if df is None or df.empty:
        return pd.DataFrame()

    valid = df.dropna(subset=["date"]).sort_values(by="date").copy()
    if len(valid) < 2:
        return pd.DataFrame()

    flagged_indices = set()
    duplicate_pairs = []

    for (merchant, cat), group in valid.groupby(["merchant", "category"]):
        if len(group) < 2:
            continue

        records = group.to_dict(orient="records")
        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                t1 = records[i]
                t2 = records[j]
                
                time_diff = abs((t2["date"] - t1["date"]).total_seconds() / 3600.0)
                if time_diff > time_window_hours:
                    break  # Sorted by date, so no subsequent record will be closer

                amount_diff = abs(t2["amount"] - t1["amount"])
                if amount_diff <= amount_tolerance:
                    duplicate_pairs.append({
                        "merchant": merchant,
                        "category": cat,
                        "amount": t1["amount"],
                        "original_date": t1["date"],
                        "potential_duplicate_date": t2["date"],
                        "time_gap_hours": round(time_diff, 2),
                        "flag_reason": f"Identical amount (INR {t1['amount']}) charged within {time_diff:.1f} hours at {merchant}.",
                    })

    if not duplicate_pairs:
        return pd.DataFrame()

    return pd.DataFrame(duplicate_pairs).sort_values(by="time_gap_hours").reset_index(drop=True)


def analyze_unexpected_spending_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates spending events against category baseline medians and typical time-of-day distributions.
    Produces human-readable diagnostic explanations for each flagged anomaly.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    expenses = df[df["type"] == "EXPENSE"].dropna(subset=["date"]).copy()
    if expenses.empty:
        return pd.DataFrame()

    flagged_records = []

    for _, row in expenses.iterrows():
        cat = str(row["category"]).lower()
        amount = float(row["amount"])
        dt = row["date"]
        hour = dt.hour if hasattr(dt, "hour") else 12

        baseline = CATEGORY_SPENDING_BASELINES.get(cat, CATEGORY_SPENDING_BASELINES["shopping"])
        median_spend = baseline["median"]
        p95_spend = baseline["p95"]

        reasons = []
        severity = "NORMAL"

        # Check 1: Spend multiplier vs median
        ratio = amount / max(1.0, median_spend)
        if ratio >= 6.0:
            reasons.append(f"Spending spike: Amount is {ratio:.1f}x higher than the typical {cat} benchmark (INR {median_spend:,.0f}).")
            severity = "HIGH"
        elif ratio >= 3.5:
            reasons.append(f"Elevated spend: Amount is {ratio:.1f}x above typical {cat} benchmark.")
            severity = "MEDIUM"

        # Check 2: Top-percentile check
        if amount >= p95_spend * 2.0:
            reasons.append(f"Extreme amount: Exceeds 2x the 95th percentile benchmark (INR {p95_spend:,.0f}).")
            severity = "HIGH"

        # Check 3: Off-hours / Night time transaction
        if hour >= 23 or hour <= 4:
            reasons.append(f"Off-hours transaction: Initiated during late night ({hour:02d}:00 hrs).")
            if severity == "NORMAL":
                severity = "LOW"

        if reasons:
            flagged_records.append({
                "date": row["date"],
                "merchant": row["merchant"],
                "category": cat,
                "amount": amount,
                "benchmark_median": median_spend,
                "spend_ratio": round(ratio, 2),
                "severity": severity,
                "diagnostic_reasons": " | ".join(reasons),
            })

    if not flagged_records:
        return pd.DataFrame()

    return pd.DataFrame(flagged_records).sort_values(by="amount", ascending=False).reset_index(drop=True)
