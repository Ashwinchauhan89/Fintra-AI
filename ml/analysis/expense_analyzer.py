"""
Fintra-AI Expense Analyzer Module
Provides monthly expense aggregation, category rankings, MoM spending trends,
and recurring expense pattern detection heuristics.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def aggregate_monthly_expenses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates expenses by year-month and computes monthly totals, counts, and averages.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["month", "total_expense", "transaction_count", "average_expense"])

    expenses = df[df["type"] == "EXPENSE"].dropna(subset=["date"]).copy()
    if expenses.empty:
        return pd.DataFrame(columns=["month", "total_expense", "transaction_count", "average_expense"])

    expenses["month"] = expenses["date"].dt.to_period("M").astype(str)

    monthly = expenses.groupby("month").agg(
        total_expense=("amount", "sum"),
        transaction_count=("amount", "count"),
        average_expense=("amount", "mean"),
    ).reset_index()

    monthly["total_expense"] = monthly["total_expense"].round(2)
    monthly["average_expense"] = monthly["average_expense"].round(2)
    return monthly.sort_values(by="month").reset_index(drop=True)


def rank_category_spending(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ranks expense categories by total spending and computes percentage contributions.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["rank", "category", "total_expense", "percentage_contribution"])

    expenses = df[df["type"] == "EXPENSE"].copy()
    if expenses.empty:
        return pd.DataFrame(columns=["rank", "category", "total_expense", "percentage_contribution"])

    total_spend = expenses["amount"].sum()
    cat_spend = expenses.groupby("category")["amount"].sum().reset_index()
    cat_spend = cat_spend.rename(columns={"amount": "total_expense"})
    cat_spend = cat_spend.sort_values(by="total_expense", ascending=False).reset_index(drop=True)

    cat_spend["rank"] = range(1, len(cat_spend) + 1)
    cat_spend["percentage_contribution"] = round((cat_spend["total_expense"] / total_spend) * 100.0, 2) if total_spend > 0 else 0.0
    cat_spend["total_expense"] = cat_spend["total_expense"].round(2)

    return cat_spend[["rank", "category", "total_expense", "percentage_contribution"]]


def calculate_spending_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes Month-over-Month (MoM) spending growth rates and directional trends.
    """
    monthly = aggregate_monthly_expenses(df)
    if monthly.empty or len(monthly) < 2:
        if not monthly.empty:
            monthly["mom_growth_amount"] = 0.0
            monthly["mom_growth_pct"] = 0.0
            monthly["trend_direction"] = "STABLE"
        return monthly

    monthly["mom_growth_amount"] = monthly["total_expense"].diff().round(2).fillna(0.0)
    monthly["mom_growth_pct"] = (
        (monthly["total_expense"].pct_change() * 100.0).round(2).fillna(0.0)
    )

    def classify_trend(pct: float) -> str:
        if pct > 5.0:
            return "INCREASING"
        elif pct < -5.0:
            return "DECREASING"
        return "STABLE"

    monthly["trend_direction"] = monthly["mom_growth_pct"].apply(classify_trend)
    return monthly


def detect_recurring_expenses(
    df: pd.DataFrame,
    min_occurrences: int = 2,
    amount_tolerance_pct: float = 0.05,
    max_interval_std_days: float = 12.0
) -> pd.DataFrame:
    """
    Identifies recurring expense patterns using documented statistical heuristics.
    
    Heuristic criteria:
    1. Same merchant and category across multiple transactions (>= min_occurrences)
    2. Low coefficient of variation in transaction amounts (std / mean <= amount_tolerance_pct)
    3. Regular time intervals between consecutive transactions (std(interval_days) <= max_interval_std_days)
    
    Classifies cadence:
    - Weekly: interval ~ 7 days (std <= 3)
    - Monthly: interval ~ 30 days (std <= 7)
    - Quarterly: interval ~ 90 days (std <= 14)
    - Annual: interval ~ 365 days (std <= 25)
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "merchant", "category", "occurrences", "mean_amount", 
            "amount_std", "interval_mean_days", "interval_std_days", "cadence", "confidence"
        ])

    expenses = df[df["type"] == "EXPENSE"].dropna(subset=["date"]).sort_values(by="date").copy()
    if expenses.empty:
        return pd.DataFrame(columns=[
            "merchant", "category", "occurrences", "mean_amount", 
            "amount_std", "interval_mean_days", "interval_std_days", "cadence", "confidence"
        ])

    recurring_candidates = []

    for (merchant, category), group in expenses.groupby(["merchant", "category"]):
        if len(group) < min_occurrences:
            continue

        amounts = group["amount"].values
        mean_amount = float(np.mean(amounts))
        std_amount = float(np.std(amounts))
        cv_amount = std_amount / mean_amount if mean_amount > 0 else 1.0

        dates = pd.to_datetime(group["date"]).sort_values()
        intervals = (dates.diff().dropna().dt.total_seconds() / 86400.0).values

        if len(intervals) == 0:
            continue

        mean_interval = float(np.mean(intervals))
        std_interval = float(np.std(intervals)) if len(intervals) > 1 else 0.0

        # Check if amount variance is low
        is_consistent_amount = cv_amount <= amount_tolerance_pct or std_amount <= 5.0
        
        # Check cadence
        if 5.0 <= mean_interval <= 10.0 and std_interval <= 4.0:
            cadence = "WEEKLY"
            confidence = "HIGH" if is_consistent_amount else "MEDIUM"
        elif 22.0 <= mean_interval <= 38.0 and std_interval <= max_interval_std_days:
            cadence = "MONTHLY"
            confidence = "HIGH" if is_consistent_amount else "MEDIUM"
        elif 80.0 <= mean_interval <= 105.0 and std_interval <= 18.0:
            cadence = "QUARTERLY"
            confidence = "HIGH" if is_consistent_amount else "MEDIUM"
        elif 340.0 <= mean_interval <= 390.0 and std_interval <= 30.0:
            cadence = "ANNUAL"
            confidence = "HIGH" if is_consistent_amount else "MEDIUM"
        elif is_consistent_amount and len(group) >= 3 and std_interval <= 20.0:
            cadence = "PERIODIC"
            confidence = "MEDIUM"
        else:
            continue

        recurring_candidates.append({
            "merchant": merchant,
            "category": category,
            "occurrences": len(group),
            "mean_amount": round(mean_amount, 2),
            "amount_std": round(std_amount, 2),
            "interval_mean_days": round(mean_interval, 1),
            "interval_std_days": round(std_interval, 1),
            "cadence": cadence,
            "confidence": confidence,
        })

    if not recurring_candidates:
        return pd.DataFrame(columns=[
            "merchant", "category", "occurrences", "mean_amount", 
            "amount_std", "interval_mean_days", "interval_std_days", "cadence", "confidence"
        ])

    res_df = pd.DataFrame(recurring_candidates)
    return res_df.sort_values(by=["occurrences", "mean_amount"], ascending=[False, False]).reset_index(drop=True)
