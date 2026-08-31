"""
Fintra-AI Financial Visualization Suite
Provides high-quality Matplotlib, Seaborn, and Plotly visualizations for:
- Expense distributions & KDE
- Category-wise spending breakdowns
- Income vs Expense monthly comparisons
- Spending trends & rolling averages
- Savings rate trends
- Transaction frequency & heatmaps
- Feature correlation matrices
- Outlier box plots
- Cumulative spending time series
- Budget vs actual utilization
"""

from typing import Any, Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

# Set clean aesthetic defaults
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 100


def plot_expense_distribution(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 5)
) -> plt.Figure:
    """Plots histogram with Kernel Density Estimate (KDE) for expense transaction amounts."""
    fig, ax = plt.subplots(figsize=figsize)
    expenses = df[df["type"] == "EXPENSE"]["amount"] if df is not None and not df.empty else pd.Series(dtype=float)

    if expenses.empty:
        ax.text(0.5, 0.5, "No Expense Data Available", ha="center", va="center", fontsize=12)
        ax.set_title("Expense Amount Distribution (Empty)", fontsize=14, fontweight="bold")
        return fig

    # Filter out extreme top 1% for visualization readability if variance is huge
    upper_clip = expenses.quantile(0.99)
    clipped = expenses[expenses <= upper_clip]

    sns.histplot(clipped, kde=True, ax=ax, color="#4F46E5", bins=30, alpha=0.6)
    ax.set_title("Expense Transaction Amount Distribution (up to 99th percentile)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Transaction Amount (INR)", fontsize=11)
    ax.set_ylabel("Transaction Frequency", fontsize=11)
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    return fig


def plot_category_spending(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 5)
) -> plt.Figure:
    """Plots a horizontal bar chart showing category spending and percentage contributions."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty:
        ax.text(0.5, 0.5, "No Expense Data Available", ha="center", va="center", fontsize=12)
        ax.set_title("Category Spending (Empty)", fontsize=14, fontweight="bold")
        return fig

    expenses = df[df["type"] == "EXPENSE"].copy()
    if expenses.empty:
        ax.text(0.5, 0.5, "No Expense Data Available", ha="center", va="center", fontsize=12)
        ax.set_title("Category Spending (Empty)", fontsize=14, fontweight="bold")
        return fig

    cat_totals = expenses.groupby("category")["amount"].sum().sort_values(ascending=True)
    total_spend = cat_totals.sum()

    colors = sns.color_palette("viridis", len(cat_totals))
    bars = ax.barh(cat_totals.index, cat_totals.values, color=colors, edgecolor="none", height=0.6)

    for bar in bars:
        width = bar.get_width()
        pct = (width / total_spend * 100.0) if total_spend > 0 else 0.0
        ax.text(width + (total_spend * 0.01), bar.get_y() + bar.get_height() / 2,
                f"₹{width:,.0f} ({pct:.1f}%)", va="center", fontsize=9, fontweight="medium")

    ax.set_title("Total Spending Breakdown by Category", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Total Spend (INR)", fontsize=11)
    ax.set_ylabel("Category", fontsize=11)
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
    ax.set_xlim(0, max(cat_totals.values) * 1.2 if not cat_totals.empty else 100)
    plt.tight_layout()
    return fig


def plot_income_vs_expenses(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (11, 5)
) -> plt.Figure:
    """Plots side-by-side monthly income vs expenses bar chart with net savings line."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty or "date" not in df.columns:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=12)
        ax.set_title("Monthly Income vs Expense (Empty)", fontsize=14, fontweight="bold")
        return fig

    valid = df.dropna(subset=["date"]).copy()
    if valid.empty:
        ax.text(0.5, 0.5, "No Valid Dates Available", ha="center", va="center", fontsize=12)
        return fig

    valid["month"] = valid["date"].dt.to_period("M").astype(str)
    monthly_inc = valid[valid["type"] == "INCOME"].groupby("month")["amount"].sum().rename("Income")
    monthly_exp = valid[valid["type"] == "EXPENSE"].groupby("month")["amount"].sum().rename("Expense")

    all_months = sorted(list(set(monthly_inc.index).union(set(monthly_exp.index))))
    if not all_months:
        ax.text(0.5, 0.5, "No Monthly Data Available", ha="center", va="center", fontsize=12)
        return fig

    summary = pd.DataFrame(index=all_months).join(monthly_inc).join(monthly_exp).fillna(0.0)

    x = np.arange(len(summary))
    width = 0.35

    ax.bar(x - width/2, summary["Income"], width, label="Income", color="#10B981", alpha=0.85)
    ax.bar(x + width/2, summary["Expense"], width, label="Expense", color="#EF4444", alpha=0.85)

    # Net savings line
    net_savings = summary["Income"] - summary["Expense"]
    ax.plot(x, net_savings, color="#3B82F6", marker="o", linewidth=2.5, label="Net Cash Flow")

    ax.set_title("Monthly Income vs Expenses & Net Cash Flow", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(summary.index, rotation=35, ha="right")
    ax.set_ylabel("Amount (INR)", fontsize=11)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
    ax.legend(frameon=True, facecolor="white", edgecolor="none")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    plt.tight_layout()
    return fig


def plot_monthly_spending_trends(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 5)
) -> plt.Figure:
    """Plots time-series spending trend with a 7-period moving average."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty or "date" not in df.columns:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=12)
        return fig

    expenses = df[df["type"] == "EXPENSE"].dropna(subset=["date"]).sort_values(by="date").copy()
    if expenses.empty:
        ax.text(0.5, 0.5, "No Expense Data", ha="center", va="center", fontsize=12)
        return fig

    # Group by date
    daily = expenses.groupby(expenses["date"].dt.date)["amount"].sum().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values(by="date")

    ax.plot(daily["date"], daily["amount"], color="#94A3B8", alpha=0.5, label="Daily Spending")
    
    if len(daily) >= 7:
        daily["rolling_7"] = daily["amount"].rolling(window=7, min_periods=1).mean()
        ax.plot(daily["date"], daily["rolling_7"], color="#4F46E5", linewidth=2.5, label="7-Day Moving Avg")

    ax.set_title("Daily Spending Trend & Moving Average", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Spending Amount (INR)", fontsize=11)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
    ax.legend(frameon=True)
    plt.tight_layout()
    return fig


def plot_savings_rate_trend(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 5)
) -> plt.Figure:
    """Plots the monthly savings rate percentage over time with a 20% benchmark line."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty or "date" not in df.columns:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=12)
        return fig

    valid = df.dropna(subset=["date"]).copy()
    valid["month"] = valid["date"].dt.to_period("M").astype(str)

    monthly_inc = valid[valid["type"] == "INCOME"].groupby("month")["amount"].sum().rename("income")
    monthly_exp = valid[valid["type"] == "EXPENSE"].groupby("month")["amount"].sum().rename("expense")

    all_months = sorted(list(set(monthly_inc.index).union(set(monthly_exp.index))))
    summary = pd.DataFrame(index=all_months).join(monthly_inc).join(monthly_exp).fillna(0.0)

    if summary.empty:
        ax.text(0.5, 0.5, "No Monthly Data", ha="center", va="center", fontsize=12)
        return fig

    summary["savings_rate"] = np.where(
        summary["income"] > 0,
        ((summary["income"] - summary["expense"]) / summary["income"]) * 100.0,
        -100.0
    )

    colors = np.where(summary["savings_rate"] >= 20.0, "#10B981", np.where(summary["savings_rate"] >= 0.0, "#F59E0B", "#EF4444"))

    ax.plot(summary.index, summary["savings_rate"], color="#3B82F6", marker="o", linewidth=2.0)
    ax.scatter(summary.index, summary["savings_rate"], color=colors, s=80, zorder=5)

    # 20% standard savings rule benchmark
    ax.axhline(20.0, color="#10B981", linestyle="--", linewidth=1.5, label="Target Benchmark (20%)")
    ax.axhline(0.0, color="gray", linestyle="-", linewidth=1.0, alpha=0.7)

    ax.set_title("Monthly Savings Rate (%) Trend", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Savings Rate (%)", fontsize=11)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    ax.legend(frameon=True)
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    return fig


def plot_transaction_frequency_by_weekday(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (8, 4.5)
) -> plt.Figure:
    """Plots transaction count and spend across days of the week."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty or "date" not in df.columns:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=12)
        return fig

    valid = df.dropna(subset=["date"]).copy()
    valid["day_name"] = valid["date"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    counts = valid["day_name"].value_counts().reindex(day_order).fillna(0)

    colors = ["#4F46E5" if d not in ["Saturday", "Sunday"] else "#F59E0B" for d in day_order]
    bars = ax.bar(day_order, counts.values, color=colors, width=0.55)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1, f"{int(height)}", ha="center", va="bottom", fontsize=9)

    ax.set_title("Transaction Volume by Day of Week", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Day of Week", fontsize=11)
    ax.set_ylabel("Number of Transactions", fontsize=11)
    plt.xticks(rotation=25)
    plt.tight_layout()
    return fig


def plot_outlier_boxplots(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (11, 5)
) -> plt.Figure:
    """Plots categorical boxplots to identify amount outliers across categories."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=12)
        return fig

    expenses = df[df["type"] == "EXPENSE"].copy()
    if expenses.empty:
        ax.text(0.5, 0.5, "No Expense Data", ha="center", va="center", fontsize=12)
        return fig

    # Filter categories with at least 3 transactions
    cat_counts = expenses["category"].value_counts()
    valid_cats = cat_counts[cat_counts >= 3].index
    filtered = expenses[expenses["category"].isin(valid_cats)]

    if filtered.empty:
        filtered = expenses

    sns.boxplot(
        data=filtered,
        x="category",
        y="amount",
        hue="category",
        legend=False,
        palette="Set2",
        ax=ax,
        fliersize=5,
        flierprops={"marker": "o", "markerfacecolor": "red", "alpha": 0.6}
    )

    ax.set_title("Expense Distribution & Outliers by Category", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Category", fontsize=11)
    ax.set_ylabel("Amount (INR)", fontsize=11)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (7, 5)
) -> plt.Figure:
    """Plots correlation matrix among engineered transaction features."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=12)
        return fig

    features_df = df.copy()
    if "date" in features_df.columns:
        features_df["day_of_week"] = features_df["date"].dt.dayofweek
        features_df["day_of_month"] = features_df["date"].dt.day
        features_df["hour"] = features_df["date"].dt.hour

    numeric_cols = features_df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        ax.text(0.5, 0.5, "Insufficient numeric features for correlation", ha="center", va="center", fontsize=11)
        return fig

    corr = features_df[numeric_cols].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, cbar=True, square=True, linewidths=0.5)

    ax.set_title("Feature Correlation Matrix", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    return fig


def plot_budget_vs_actual(
    adherence_df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 5)
) -> plt.Figure:
    """Plots comparative grouped bar chart comparing actual spend against allocated budget."""
    fig, ax = plt.subplots(figsize=figsize)
    if adherence_df is None or adherence_df.empty:
        ax.text(0.5, 0.5, "No Budget Data Available", ha="center", va="center", fontsize=12)
        ax.set_title("Budget vs Actual Spending (Empty)", fontsize=14, fontweight="bold")
        return fig

    df_sorted = adherence_df.sort_values(by="allocated_budget", ascending=False).reset_index(drop=True)
    x = np.arange(len(df_sorted))
    width = 0.35

    ax.bar(x - width/2, df_sorted["allocated_budget"], width, label="Allocated Budget", color="#6366F1", alpha=0.85)
    
    # Color actual bar red if over budget
    actual_colors = np.where(df_sorted["actual_spend"] > df_sorted["allocated_budget"], "#EF4444", "#10B981")
    ax.bar(x + width/2, df_sorted["actual_spend"], width, label="Actual Spend", color=actual_colors, alpha=0.85)

    ax.set_title("Budget vs. Actual Spending by Category", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(df_sorted["category"], rotation=30, ha="right")
    ax.set_ylabel("Amount (INR)", fontsize=11)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
    ax.legend(frameon=True)
    plt.tight_layout()
    return fig


def create_interactive_category_pie(df: pd.DataFrame):
    """Generates an interactive Plotly Donut chart for category spending."""
    import plotly.express as px
    if df is None or df.empty:
        return None

    expenses = df[df["type"] == "EXPENSE"].copy()
    if expenses.empty:
        return None

    cat_totals = expenses.groupby("category")["amount"].sum().reset_index()
    fig = px.pie(
        cat_totals,
        values="amount",
        names="category",
        hole=0.45,
        title="<b>Interactive Expense Breakdown by Category</b>",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(showlegend=True, margin=dict(t=50, b=20, l=20, r=20))
    return fig


def create_interactive_monthly_trend(df: pd.DataFrame):
    """Generates an interactive Plotly line chart comparing Monthly Income and Expenses."""
    import plotly.graph_objects as go
    if df is None or df.empty or "date" not in df.columns:
        return None

    valid = df.dropna(subset=["date"]).copy()
    valid["month"] = valid["date"].dt.to_period("M").astype(str)

    monthly_inc = valid[valid["type"] == "INCOME"].groupby("month")["amount"].sum().rename("income")
    monthly_exp = valid[valid["type"] == "EXPENSE"].groupby("month")["amount"].sum().rename("expense")

    all_months = sorted(list(set(monthly_inc.index).union(set(monthly_exp.index))))
    summary = pd.DataFrame(index=all_months).join(monthly_inc).join(monthly_exp).fillna(0.0).reset_index().rename(columns={"index": "month"})

    fig = go.Figure()
    fig.add_trace(go.Bar(x=summary["month"], y=summary["income"], name="Income", marker_color="#10B981"))
    fig.add_trace(go.Bar(x=summary["month"], y=summary["expense"], name="Expense", marker_color="#EF4444"))
    fig.add_trace(go.Scatter(x=summary["month"], y=summary["income"] - summary["expense"], name="Net Cash Flow", line=dict(color="#3B82F6", width=3)))

    fig.update_layout(
        title="<b>Interactive Monthly Cash Flow Analysis</b>",
        barmode="group",
        xaxis_title="Month",
        yaxis_title="Amount (INR)",
        hovermode="x unified",
        margin=dict(t=50, b=30, l=30, r=30)
    )
    return fig
