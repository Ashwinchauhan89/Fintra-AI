"""
Fintra-AI Transaction Analyzer Module
Provides core transaction metrics, volume counts, averages, frequency breakdowns,
category distributions, and merchant spending rankings.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def get_transaction_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates overall transaction counts and average amounts across income, expense, and total.
    Handles empty or missing data safely.
    """
    if df is None or df.empty:
        return {
            "total_transactions": 0,
            "total_income_count": 0,
            "total_expense_count": 0,
            "total_volume_amount": 0.0,
            "average_transaction_amount": 0.0,
            "average_income_amount": 0.0,
            "average_expense_amount": 0.0,
        }

    income_df = df[df["type"] == "INCOME"]
    expense_df = df[df["type"] == "EXPENSE"]

    total_count = len(df)
    income_count = len(income_df)
    expense_count = len(expense_df)

    avg_overall = float(df["amount"].mean()) if total_count > 0 else 0.0
    avg_income = float(income_df["amount"].mean()) if income_count > 0 else 0.0
    avg_expense = float(expense_df["amount"].mean()) if expense_count > 0 else 0.0

    return {
        "total_transactions": total_count,
        "total_income_count": income_count,
        "total_expense_count": expense_count,
        "total_volume_amount": round(float(df["amount"].sum()), 2),
        "average_transaction_amount": round(avg_overall, 2),
        "average_income_amount": round(avg_income, 2),
        "average_expense_amount": round(avg_expense, 2),
    }


def analyze_transaction_frequency(
    df: pd.DataFrame,
    threshold_std: float = 2.0
) -> Dict[str, Any]:
    """
    Computes transaction frequency over daily, weekly, and monthly periods.
    Identifies anomalous high-activity burst dates (mean + threshold_std * std).
    """
    if df is None or df.empty or "date" not in df.columns:
        return {
            "daily_frequency": pd.DataFrame(),
            "weekly_frequency": pd.DataFrame(),
            "monthly_frequency": pd.DataFrame(),
            "avg_daily_transactions": 0.0,
            "avg_weekly_transactions": 0.0,
            "avg_monthly_transactions": 0.0,
            "high_activity_periods": pd.DataFrame(),
        }

    valid_dates = df.dropna(subset=["date"]).copy()
    if valid_dates.empty:
        return {
            "daily_frequency": pd.DataFrame(),
            "weekly_frequency": pd.DataFrame(),
            "monthly_frequency": pd.DataFrame(),
            "avg_daily_transactions": 0.0,
            "avg_weekly_transactions": 0.0,
            "avg_monthly_transactions": 0.0,
            "high_activity_periods": pd.DataFrame(),
        }

    # Daily aggregation
    daily = valid_dates.groupby(valid_dates["date"].dt.date).agg(
        transaction_count=("amount", "count"),
        total_amount=("amount", "sum")
    ).reset_index().rename(columns={"date": "period"})

    # Weekly aggregation
    weekly = valid_dates.groupby(valid_dates["date"].dt.to_period("W")).agg(
        transaction_count=("amount", "count"),
        total_amount=("amount", "sum")
    ).reset_index()
    weekly["period"] = weekly["date"].astype(str)
    weekly = weekly[["period", "transaction_count", "total_amount"]]

    # Monthly aggregation
    monthly = valid_dates.groupby(valid_dates["date"].dt.to_period("M")).agg(
        transaction_count=("amount", "count"),
        total_amount=("amount", "sum")
    ).reset_index()
    monthly["period"] = monthly["date"].astype(str)
    monthly = monthly[["period", "transaction_count", "total_amount"]]

    # Identify high-activity days
    if not daily.empty and len(daily) > 1:
        mean_tx = daily["transaction_count"].mean()
        std_tx = daily["transaction_count"].std()
        cutoff = mean_tx + (threshold_std * std_tx) if not np.isnan(std_tx) else mean_tx * 1.5
        high_activity = daily[daily["transaction_count"] > cutoff].copy().reset_index(drop=True)
    else:
        high_activity = pd.DataFrame()

    return {
        "daily_frequency": daily,
        "weekly_frequency": weekly,
        "monthly_frequency": monthly,
        "avg_daily_transactions": round(float(daily["transaction_count"].mean()), 2) if not daily.empty else 0.0,
        "avg_weekly_transactions": round(float(weekly["transaction_count"].mean()), 2) if not weekly.empty else 0.0,
        "avg_monthly_transactions": round(float(monthly["transaction_count"].mean()), 2) if not monthly.empty else 0.0,
        "high_activity_periods": high_activity,
    }


def analyze_category_distribution(
    df: pd.DataFrame,
    transaction_type: Optional[str] = "EXPENSE"
) -> pd.DataFrame:
    """
    Computes count, sum, percentage of transactions, and percentage of spend per category.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["category", "count", "percentage_count", "total_amount", "percentage_amount"])

    subset = df.copy()
    if transaction_type:
        subset = subset[subset["type"] == transaction_type]

    if subset.empty:
        return pd.DataFrame(columns=["category", "count", "percentage_count", "total_amount", "percentage_amount"])

    total_count = len(subset)
    total_spend = subset["amount"].sum()

    grouped = subset.groupby("category").agg(
        count=("amount", "count"),
        total_amount=("amount", "sum"),
        avg_amount=("amount", "mean"),
    ).reset_index()

    grouped["percentage_count"] = round((grouped["count"] / total_count) * 100.0, 2)
    grouped["percentage_amount"] = round((grouped["total_amount"] / total_spend) * 100.0, 2) if total_spend > 0 else 0.0
    grouped["total_amount"] = grouped["total_amount"].round(2)
    grouped["avg_amount"] = grouped["avg_amount"].round(2)

    return grouped.sort_values(by="total_amount", ascending=False).reset_index(drop=True)


def analyze_merchants(
    df: pd.DataFrame,
    top_n: int = 10,
    transaction_type: Optional[str] = "EXPENSE"
) -> Dict[str, pd.DataFrame]:
    """
    Calculates most frequent merchants, highest spend merchants,
    total spend, and average transaction amount per merchant.
    """
    if df is None or df.empty:
        empty = pd.DataFrame(columns=["merchant", "transaction_count", "total_amount", "avg_amount"])
        return {"by_frequency": empty, "by_spending": empty}

    subset = df.copy()
    if transaction_type:
        subset = subset[subset["type"] == transaction_type]

    if subset.empty:
        empty = pd.DataFrame(columns=["merchant", "transaction_count", "total_amount", "avg_amount"])
        return {"by_frequency": empty, "by_spending": empty}

    grouped = subset.groupby("merchant").agg(
        transaction_count=("amount", "count"),
        total_amount=("amount", "sum"),
        avg_amount=("amount", "mean"),
    ).reset_index()

    grouped["total_amount"] = grouped["total_amount"].round(2)
    grouped["avg_amount"] = grouped["avg_amount"].round(2)

    by_freq = grouped.sort_values(by="transaction_count", ascending=False).head(top_n).reset_index(drop=True)
    by_spend = grouped.sort_values(by="total_amount", ascending=False).head(top_n).reset_index(drop=True)

    return {
        "by_frequency": by_freq,
        "by_spending": by_spend,
        "all_merchants": grouped,
    }
