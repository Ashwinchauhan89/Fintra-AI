"""
Fintra-AI Income Analyzer Module
Provides monthly income aggregation, income source breakdowns, income stability metrics
(mean, std dev, CV), and income vs expense surplus/deficit calculations.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def aggregate_monthly_income(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates income transactions by year-month and computes monthly totals, counts, and averages.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["month", "total_income", "transaction_count", "average_income"])

    income_df = df[df["type"] == "INCOME"].dropna(subset=["date"]).copy()
    if income_df.empty:
        return pd.DataFrame(columns=["month", "total_income", "transaction_count", "average_income"])

    income_df["month"] = income_df["date"].dt.to_period("M").astype(str)

    monthly = income_df.groupby("month").agg(
        total_income=("amount", "sum"),
        transaction_count=("amount", "count"),
        average_income=("amount", "mean"),
    ).reset_index()

    monthly["total_income"] = monthly["total_income"].round(2)
    monthly["average_income"] = monthly["average_income"].round(2)
    return monthly.sort_values(by="month").reset_index(drop=True)


def analyze_income_sources(df: pd.DataFrame) -> pd.DataFrame:
    """
    Breaks down income by source merchant / description category.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["source_name", "category", "transaction_count", "total_income", "percentage_contribution"])

    income_df = df[df["type"] == "INCOME"].copy()
    if income_df.empty:
        return pd.DataFrame(columns=["source_name", "category", "transaction_count", "total_income", "percentage_contribution"])

    total_income = income_df["amount"].sum()
    
    # Use merchant or description as source
    income_df["source_name"] = income_df["merchant"].fillna(income_df["description"]).fillna("Direct Deposit")

    grouped = income_df.groupby(["source_name", "category"]).agg(
        transaction_count=("amount", "count"),
        total_income=("amount", "sum"),
        avg_income=("amount", "mean"),
    ).reset_index()

    grouped["percentage_contribution"] = (
        round((grouped["total_income"] / total_income) * 100.0, 2) if total_income > 0 else 0.0
    )
    grouped["total_income"] = grouped["total_income"].round(2)
    grouped["avg_income"] = grouped["avg_income"].round(2)

    return grouped.sort_values(by="total_income", ascending=False).reset_index(drop=True)


def calculate_income_stability(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates income stability statistics across all observed months.
    - Mean Monthly Income
    - Standard Deviation
    - Coefficient of Variation (CV = std / mean)
    - Stability Classification (HIGH_STABILITY, MODERATE_VOLATILITY, HIGH_VOLATILITY)
    """
    monthly = aggregate_monthly_income(df)
    if monthly.empty or len(monthly) == 0:
        return {
            "months_analyzed": 0,
            "mean_monthly_income": 0.0,
            "std_monthly_income": 0.0,
            "coefficient_of_variation": 0.0,
            "min_monthly_income": 0.0,
            "max_monthly_income": 0.0,
            "stability_tier": "NO_INCOME_DATA",
            "description": "No income records found to evaluate stability.",
        }

    monthly_totals = monthly["total_income"].values
    mean_val = float(np.mean(monthly_totals))
    std_val = float(np.std(monthly_totals)) if len(monthly_totals) > 1 else 0.0
    cv = (std_val / mean_val) if mean_val > 0 else 0.0

    if cv <= 0.10:
        tier = "HIGH_STABILITY"
        desc = "Extremely predictable monthly cash flow (e.g. fixed salary/pension)."
    elif cv <= 0.30:
        tier = "MODERATE_VOLATILITY"
        desc = "Predictable base income with periodic bonuses or variable overtime."
    else:
        tier = "HIGH_VOLATILITY"
        desc = "Irregular or variable freelance/commission-based income stream."

    return {
        "months_analyzed": len(monthly),
        "mean_monthly_income": round(mean_val, 2),
        "std_monthly_income": round(std_val, 2),
        "coefficient_of_variation": round(cv, 4),
        "min_monthly_income": round(float(np.min(monthly_totals)), 2),
        "max_monthly_income": round(float(np.max(monthly_totals)), 2),
        "stability_tier": tier,
        "description": desc,
    }


def compare_income_vs_expenses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compares monthly income against monthly expenses.
    Calculates monthly net surplus/deficit, net savings, and savings rate.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "month", "total_income", "total_expense", "net_savings", 
            "savings_rate_pct", "status"
        ])

    valid = df.dropna(subset=["date"]).copy()
    if valid.empty:
        return pd.DataFrame(columns=[
            "month", "total_income", "total_expense", "net_savings", 
            "savings_rate_pct", "status"
        ])

    valid["month"] = valid["date"].dt.to_period("M").astype(str)

    monthly_inc = valid[valid["type"] == "INCOME"].groupby("month")["amount"].sum().rename("total_income")
    monthly_exp = valid[valid["type"] == "EXPENSE"].groupby("month")["amount"].sum().rename("total_expense")

    all_months = sorted(list(set(monthly_inc.index).union(set(monthly_exp.index))))
    comparison = pd.DataFrame(index=all_months)
    comparison = comparison.join(monthly_inc).join(monthly_exp).fillna(0.0).reset_index().rename(columns={"index": "month"})

    comparison["net_savings"] = (comparison["total_income"] - comparison["total_expense"]).round(2)
    
    # Safe savings rate calculation (handle zero/negative income)
    def calc_rate(row):
        inc = row["total_income"]
        net = row["net_savings"]
        if inc <= 0:
            return -100.0 if row["total_expense"] > 0 else 0.0
        return round((net / inc) * 100.0, 2)

    comparison["savings_rate_pct"] = comparison.apply(calc_rate, axis=1)
    comparison["status"] = comparison["net_savings"].apply(lambda x: "SURPLUS" if x >= 0 else "DEFICIT")
    comparison["total_income"] = comparison["total_income"].round(2)
    comparison["total_expense"] = comparison["total_expense"].round(2)

    return comparison
