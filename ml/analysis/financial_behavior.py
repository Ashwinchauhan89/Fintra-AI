"""
Fintra-AI Financial Behavior Module
Calculates savings rates, spending patterns across time & categories,
budget adherence & utilization, 50/30/20 rule benchmarks, and high-spending burst periods.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from ml.utils.budget_rules import (
    CATEGORY_CLASSIFICATION,
    DEFAULT_50_30_20_TARGETS,
    LIFESTYLE_PROFILES,
    ROADMAP_CATEGORIES,
)


def calculate_savings_rate(
    total_income: float,
    total_expenses: float
) -> Dict[str, Any]:
    """
    Calculates net savings and savings rate safely.
    Handles zero/null income gracefully without division-by-zero errors.
    """
    income = max(0.0, float(total_income)) if not np.isnan(total_income) else 0.0
    expenses = max(0.0, float(total_expenses)) if not np.isnan(total_expenses) else 0.0

    net_savings = round(income - expenses, 2)

    if income <= 0.0:
        savings_rate = -100.0 if expenses > 0.0 else 0.0
        health_status = "CRITICAL_DEFICIT" if expenses > 0.0 else "NO_INFLOW"
    else:
        savings_rate = round((net_savings / income) * 100.0, 2)
        if savings_rate >= 30.0:
            health_status = "EXCELLENT"
        elif savings_rate >= 20.0:
            health_status = "HEALTHY"
        elif savings_rate >= 10.0:
            health_status = "MODERATE"
        elif savings_rate >= 0.0:
            health_status = "TIGHT_MARGIN"
        else:
            health_status = "DEFICIT"

    return {
        "total_income": round(income, 2),
        "total_expenses": round(expenses, 2),
        "net_savings": net_savings,
        "savings_rate_pct": savings_rate,
        "health_status": health_status,
    }


def analyze_temporal_spending_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyzes spending behaviors across temporal dimensions:
    - Day of week (Weekday vs Weekend)
    - Day of month (Early month vs Mid vs Late month)
    - Transaction velocity & average basket size
    """
    if df is None or df.empty:
        return {
            "by_day_of_week": pd.DataFrame(),
            "weekend_vs_weekday": {},
            "by_period_of_month": {},
        }

    expenses = df[df["type"] == "EXPENSE"].dropna(subset=["date"]).copy()
    if expenses.empty:
        return {
            "by_day_of_week": pd.DataFrame(),
            "weekend_vs_weekday": {},
            "by_period_of_month": {},
        }

    expenses["day_name"] = expenses["date"].dt.day_name()
    expenses["day_of_week"] = expenses["date"].dt.dayofweek
    expenses["is_weekend"] = expenses["day_of_week"].isin([5, 6])
    expenses["day_of_month"] = expenses["date"].dt.day

    # 1. Day of week aggregation
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = expenses.groupby("day_name").agg(
        total_spend=("amount", "sum"),
        transaction_count=("amount", "count"),
        avg_spend=("amount", "mean"),
    ).reindex(day_order).fillna(0.0).reset_index()
    dow["total_spend"] = dow["total_spend"].round(2)
    dow["avg_spend"] = dow["avg_spend"].round(2)

    # 2. Weekend vs Weekday
    wknd = expenses[expenses["is_weekend"]]
    wkday = expenses[~expenses["is_weekend"]]
    
    total_wknd_spend = float(wknd["amount"].sum())
    total_wkday_spend = float(wkday["amount"].sum())
    
    weekend_stats = {
        "weekend_total_spend": round(total_wknd_spend, 2),
        "weekday_total_spend": round(total_wkday_spend, 2),
        "weekend_avg_spend": round(float(wknd["amount"].mean()), 2) if not wknd.empty else 0.0,
        "weekday_avg_spend": round(float(wkday["amount"].mean()), 2) if not wkday.empty else 0.0,
        "weekend_tx_count": len(wknd),
        "weekday_tx_count": len(wkday),
        "weekend_spend_share_pct": round((total_wknd_spend / (total_wknd_spend + total_wkday_spend)) * 100.0, 2)
        if (total_wknd_spend + total_wkday_spend) > 0 else 0.0,
    }

    # 3. Period of month (Early 1-10, Mid 11-20, Late 21-31)
    def month_bucket(d: int) -> str:
        if d <= 10:
            return "Early Month (1-10)"
        elif d <= 20:
            return "Mid Month (11-20)"
        return "Late Month (21-31)"

    expenses["month_bucket"] = expenses["day_of_month"].apply(month_bucket)
    period_stats = expenses.groupby("month_bucket").agg(
        total_spend=("amount", "sum"),
        tx_count=("amount", "count"),
        avg_spend=("amount", "mean"),
    ).round(2).to_dict(orient="index")

    return {
        "by_day_of_week": dow,
        "weekend_vs_weekday": weekend_stats,
        "by_period_of_month": period_stats,
    }


def analyze_50_30_20_compliance(
    df: pd.DataFrame,
    lifestyle: str = "balanced"
) -> Dict[str, Any]:
    """
    Evaluates spending against the 50/30/20 financial rule using the repository's
    budget rules taxonomy (Needs, Wants, Savings).
    """
    if df is None or df.empty:
        return {"status": "NO_DATA", "details": {}}

    income_total = float(df[df["type"] == "INCOME"]["amount"].sum())
    expenses = df[df["type"] == "EXPENSE"].copy()

    # Map categories to Needs vs Wants
    expenses["need_want"] = expenses["category"].map(CATEGORY_CLASSIFICATION).fillna("wants")

    needs_spend = float(expenses[expenses["need_want"] == "needs"]["amount"].sum())
    wants_spend = float(expenses[expenses["need_want"] == "wants"]["amount"].sum())
    actual_savings = max(0.0, income_total - (needs_spend + wants_spend))

    base_income = income_total if income_total > 0 else (needs_spend + wants_spend)
    if base_income <= 0:
        return {"status": "NO_ACTIVITY", "details": {}}

    profile = LIFESTYLE_PROFILES.get(lifestyle, LIFESTYLE_PROFILES["balanced"])

    actual_needs_pct = round((needs_spend / base_income) * 100.0, 2)
    actual_wants_pct = round((wants_spend / base_income) * 100.0, 2)
    actual_savings_pct = round((actual_savings / base_income) * 100.0, 2)

    target_needs_pct = round(profile["needs_target"] * 100.0, 2)
    target_wants_pct = round(profile["wants_target"] * 100.0, 2)
    target_savings_pct = round(profile["savings_target"] * 100.0, 2)

    return {
        "base_income": round(base_income, 2),
        "actual_allocation": {
            "needs_amount": round(needs_spend, 2),
            "wants_amount": round(wants_spend, 2),
            "savings_amount": round(actual_savings, 2),
            "needs_pct": actual_needs_pct,
            "wants_pct": actual_wants_pct,
            "savings_pct": actual_savings_pct,
        },
        "target_allocation": {
            "needs_pct": target_needs_pct,
            "wants_pct": target_wants_pct,
            "savings_pct": target_savings_pct,
        },
        "variance": {
            "needs_variance_pct": round(actual_needs_pct - target_needs_pct, 2),
            "wants_variance_pct": round(actual_wants_pct - target_wants_pct, 2),
            "savings_variance_pct": round(actual_savings_pct - target_savings_pct, 2),
        },
        "lifestyle_profile": lifestyle,
    }


def evaluate_budget_adherence(
    df: pd.DataFrame,
    budget_targets: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Compares actual category spending against allocated budget limits.
    Calculates variance and utilization rate (Actual / Budget * 100).
    If budget_targets is not provided, uses the project's automatic budget allocation rule.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "category", "allocated_budget", "actual_spend", 
            "variance", "utilization_pct", "status"
        ])

    expenses = df[df["type"] == "EXPENSE"].copy()
    if expenses.empty:
        return pd.DataFrame(columns=[
            "category", "allocated_budget", "actual_spend", 
            "variance", "utilization_pct", "status"
        ])

    actual_spend = expenses.groupby("category")["amount"].sum().round(2).to_dict()
    all_categories = sorted(list(set(actual_spend.keys()).union(set((budget_targets or {}).keys()))))

    # If no budget provided, compute transparent baseline targets based on income/total spend
    if not budget_targets:
        total_exp = sum(actual_spend.values())
        # Default distribution benchmark
        budget_targets = {cat: round(total_exp * 0.15, 2) for cat in all_categories}

    rows = []
    for cat in all_categories:
        actual = actual_spend.get(cat, 0.0)
        budget = budget_targets.get(cat, 0.0)
        variance = round(budget - actual, 2)
        utilization = round((actual / budget) * 100.0, 2) if budget > 0 else 0.0
        
        if utilization > 100.0:
            status = "OVER_BUDGET"
        elif utilization >= 85.0:
            status = "NEAR_LIMIT"
        else:
            status = "WITHIN_BUDGET"

        rows.append({
            "category": cat,
            "allocated_budget": budget,
            "actual_spend": actual,
            "variance": variance,
            "utilization_pct": utilization,
            "status": status,
        })

    return pd.DataFrame(rows).sort_values(by="actual_spend", ascending=False).reset_index(drop=True)


def identify_high_spending_periods(
    df: pd.DataFrame,
    period: str = "D",
    iqr_multiplier: float = 1.5
) -> pd.DataFrame:
    """
    Identifies days, weeks, or months with statistically high spending bursts using IQR thresholding.
    """
    if df is None or df.empty or "date" not in df.columns:
        return pd.DataFrame(columns=["period", "total_spend", "tx_count", "upper_threshold", "excess_spend"])

    expenses = df[df["type"] == "EXPENSE"].dropna(subset=["date"]).copy()
    if expenses.empty:
        return pd.DataFrame(columns=["period", "total_spend", "tx_count", "upper_threshold", "excess_spend"])

    if period.upper() == "D":
        grouped = expenses.groupby(expenses["date"].dt.date).agg(
            total_spend=("amount", "sum"),
            tx_count=("amount", "count")
        ).reset_index().rename(columns={"date": "period"})
    elif period.upper() == "W":
        grouped = expenses.groupby(expenses["date"].dt.to_period("W")).agg(
            total_spend=("amount", "sum"),
            tx_count=("amount", "count")
        ).reset_index()
        grouped["period"] = grouped["date"].astype(str)
    else:  # Monthly
        grouped = expenses.groupby(expenses["date"].dt.to_period("M")).agg(
            total_spend=("amount", "sum"),
            tx_count=("amount", "count")
        ).reset_index()
        grouped["period"] = grouped["date"].astype(str)

    if len(grouped) < 3:
        return pd.DataFrame(columns=["period", "total_spend", "tx_count", "upper_threshold", "excess_spend"])

    q1 = grouped["total_spend"].quantile(0.25)
    q3 = grouped["total_spend"].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + (iqr_multiplier * iqr)

    spikes = grouped[grouped["total_spend"] > upper_bound].copy()
    spikes["upper_threshold"] = round(upper_bound, 2)
    spikes["excess_spend"] = (spikes["total_spend"] - upper_bound).round(2)
    spikes["total_spend"] = spikes["total_spend"].round(2)

    return spikes.sort_values(by="total_spend", ascending=False).reset_index(drop=True)
