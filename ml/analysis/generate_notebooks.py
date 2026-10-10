"""
Script to generate valid, cleanly structured Jupyter Notebooks for Fintra-AI.
Generates:
- notebooks/01_eda.ipynb
- notebooks/02_financial_analysis.ipynb
- notebooks/03_anomaly_analysis.ipynb
- notebooks/04_visualizations.ipynb
"""

import os
import nbformat as nbf

NOTEBOOK_DIR = "notebooks"
os.makedirs(NOTEBOOK_DIR, exist_ok=True)


def build_01_eda_notebook():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 📊 Fintra-AI: Exploratory Data Analysis & Schema Normalization (01_eda.ipynb)

### 🎯 Objective
This notebook performs **Exploratory Data Analysis (EDA)** on raw financial transaction records. It validates input schemas, cleans messy financial logs, unifies heterogeneous data sources into canonical Fintra-AI schemas, and assesses baseline data distributions.

---
### 🛠️ Key Pipeline Stages:
1. **Environment Setup & Imports**
2. **Dataset Discovery & Ingestion**
3. **Data Quality & Integrity Validation**
4. **Data Cleaning & Schema Harmonization**
5. **Basic Statistical Profile & Distribution Exploration**
6. **Key Observations & Next Steps**
"""),
        nbf.v4.new_code_cell("""# 1. Imports and System Path Configuration
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to sys.path to enable imports from ml.analysis
sys.path.insert(0, os.path.abspath(".."))

from ml.analysis.data_loader import (
    load_project_dataset,
    validate_and_clean_dataframe,
    generate_sample_financial_dataset,
    CANONICAL_COLUMNS,
    ROADMAP_CATEGORIES
)

# Visual styling
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 100
pd.set_option("display.max_columns", None)

print("[OK] Successfully loaded core analytics modules.")
"""),
        nbf.v4.new_markdown_cell("""## 2. Ingestion & Multi-Source Loading

In Fintra-AI, transaction data originates from multiple source formats (e.g. mobile banking feeds, CSV statements, household expense ledgers).
We load the raw datasets and apply canonical schema transformation.
"""),
        nbf.v4.new_code_cell("""# 2. Load unified transaction records
df = load_project_dataset(include_raw_sources=True)

if df.empty:
    print("[warn] No existing CSV files found at standard paths. Generating realistic synthetic dataset for analysis...")
    df = generate_sample_financial_dataset(n_records=500, seed=42)

print(f"Total Loaded Transactions: {len(df):,}")
print(f"Canonical Columns: {list(df.columns)}")
df.head(8)
"""),
        nbf.v4.new_markdown_cell("""## 3. Data Integrity & Completeness Audit

Before analyzing spending patterns, we systematically inspect:
* Missing values (NaNs in dates, amounts, categories)
* Data types and date validity
* Type breakdown (`INCOME` vs `EXPENSE`)
* Category representation across Fintra-AI's canonical roadmap categories
"""),
        nbf.v4.new_code_cell("""# 3. Data Quality Report
print("--- Missing Values Audit ---")
print(df.isnull().sum())

print("\\n--- Transaction Type Distribution ---")
print(df["type"].value_counts(dropna=False))

print("\\n--- Date Range Span ---")
valid_dates = df.dropna(subset=["date"])
print(f"Earliest Date: {valid_dates['date'].min()}")
print(f"Latest Date:   {valid_dates['date'].max()}")
print(f"Total Span:    {(valid_dates['date'].max() - valid_dates['date'].min()).days} days")

print("\\n--- Category Distribution ---")
print(df["category"].value_counts())
"""),
        nbf.v4.new_markdown_cell("""## 4. Amount Statistics & Distribution Checks

Understanding transaction amount distributions is essential for setting spending limits and outlier thresholds.
"""),
        nbf.v4.new_code_cell("""# 4. Statistical Summary of Transaction Amounts
desc = df.groupby("type")["amount"].describe().round(2)
desc
"""),
        nbf.v4.new_code_cell("""# 5. Quick EDA Visual Check
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Distribution of expense amounts
expenses = df[df["type"] == "EXPENSE"]
upper_cutoff = expenses["amount"].quantile(0.95)
clipped = expenses[expenses["amount"] <= upper_cutoff]["amount"]

sns.histplot(clipped, kde=True, ax=axes[0], color="#4F46E5", bins=25)
axes[0].set_title("Expense Amounts Distribution (<= 95th percentile)", fontweight="bold")
axes[0].set_xlabel("Amount (INR)")

# Category frequency
cat_order = expenses["category"].value_counts().index
sns.countplot(data=expenses, y="category", order=cat_order, ax=axes[1], palette="viridis")
axes[1].set_title("Transaction Count by Category", fontweight="bold")
axes[1].set_xlabel("Count")

plt.tight_layout()
plt.show()
"""),
        nbf.v4.new_markdown_cell("""## 5. Summary & Exploratory Findings
- **Data Cleanliness**: Dates and amounts are normalized into standard formats (`pd.Timestamp` and positive numeric floats).
- **Categories**: Transactions map cleanly into Fintra-AI canonical categories (`food`, `shopping`, `transport`, `bills`, `entertainment`, `healthcare`, `education`, etc.).
- **Next Steps**: Proceed to [`02_financial_analysis.ipynb`](file:///notebooks/02_financial_analysis.ipynb) for in-depth metrics on transaction volume, expenses, income stability, and 50/30/20 budget adherence.
""")
    ]
    return nb


def build_02_financial_analysis_notebook():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 💰 Fintra-AI: Financial Analysis & Behavioral Insights (02_financial_analysis.ipynb)

### 🎯 Objective
This notebook performs comprehensive personal finance analytics across:
1. **Transaction Metrics**: Total volume, average ticket sizes, and merchant spending rankings.
2. **Expense Analysis**: Monthly burn rates, category rankings, and recurring expense heuristics.
3. **Income Analysis**: Monthly cash inflows, income source diversity, and income stability index ($CV$).
4. **Financial Behavior**: Net savings rate, 50/30/20 rule allocation, budget utilization, and high-spend burst periods.
"""),
        nbf.v4.new_code_cell("""# 1. Setup and Imports
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath(".."))

from ml.analysis.data_loader import load_project_dataset, generate_sample_financial_dataset
from ml.analysis.transaction_analyzer import (
    get_transaction_summary,
    analyze_transaction_frequency,
    analyze_category_distribution,
    analyze_merchants
)
from ml.analysis.expense_analyzer import (
    aggregate_monthly_expenses,
    rank_category_spending,
    calculate_spending_trends,
    detect_recurring_expenses
)
from ml.analysis.income_analyzer import (
    aggregate_monthly_income,
    analyze_income_sources,
    calculate_income_stability,
    compare_income_vs_expenses
)
from ml.analysis.financial_behavior import (
    calculate_savings_rate,
    analyze_temporal_spending_patterns,
    analyze_50_30_20_compliance,
    evaluate_budget_adherence,
    identify_high_spending_periods
)

# Load dataset
df = load_project_dataset(include_raw_sources=True)
if df.empty or len(df[df['type'] == 'INCOME']) == 0:
    df = generate_sample_financial_dataset(n_records=400, seed=42)

print(f"Loaded {len(df)} transactions for financial analysis.")
"""),
        nbf.v4.new_markdown_cell("""## 1. Core Transaction Summary & Merchant Analysis

We calculate global transaction volume, average amounts per transaction type, and top merchants by transaction frequency and monetary volume.
"""),
        nbf.v4.new_code_cell("""# Summary Metrics
summary = get_transaction_summary(df)
for k, v in summary.items():
    print(f"- {k.replace('_', ' ').title()}: {v:,.2f}" if isinstance(v, float) else f"- {k.replace('_', ' ').title()}: {v:,}")
"""),
        nbf.v4.new_code_cell("""# Top Spending Merchants
merchant_analysis = analyze_merchants(df, top_n=8)
print("--- Top Merchants by Spending (INR) ---")
print(merchant_analysis["by_spending"])

print("\\n--- Top Merchants by Transaction Frequency ---")
print(merchant_analysis["by_frequency"])
"""),
        nbf.v4.new_markdown_cell("""## 2. Expense Dynamics & Recurring Subscriptions

We break down monthly expenditure, identify top category contributors, analyze Month-over-Month (MoM) spending growth, and apply recurring payment heuristics.
"""),
        nbf.v4.new_code_cell("""# Monthly Expense & Category Ranking
monthly_exp = aggregate_monthly_expenses(df)
cat_ranking = rank_category_spending(df)

print("--- Monthly Expense Aggregation ---")
print(monthly_exp)

print("\\n--- Category Ranking & Spending Share ---")
print(cat_ranking)
"""),
        nbf.v4.new_code_cell("""# Spending Trends & Growth Rates
trends = calculate_spending_trends(df)
print(trends[["month", "total_expense", "mom_growth_amount", "mom_growth_pct", "trend_direction"]])
"""),
        nbf.v4.new_code_cell("""# Recurring Expense Detection
recurring = detect_recurring_expenses(df, min_occurrences=2)
print(f"Identified {len(recurring)} recurring subscription/bill patterns:")
print(recurring)
"""),
        nbf.v4.new_markdown_cell("""## 3. Income Analysis & Stability Metrics

Income stability is quantified using the **Coefficient of Variation ($CV = \\frac{\\sigma}{\\mu}$)** across monthly cash inflows.
"""),
        nbf.v4.new_code_cell("""# Income Analysis
stability = calculate_income_stability(df)
print("--- Income Stability Report ---")
for k, v in stability.items():
    print(f"  - {k}: {v}")

print("\\n--- Income vs. Expense Comparison ---")
comparison = compare_income_vs_expenses(df)
print(comparison)
"""),
        nbf.v4.new_markdown_cell("""## 4. Financial Behavior, Savings Rate & 50/30/20 Compliance

We compute:
- Net savings amount & savings rate percentage
- 50/30/20 budget framework compliance (Needs vs Wants vs Savings)
- Budget adherence & utilization
- High-spending anomaly burst periods
"""),
        nbf.v4.new_code_cell("""# Savings Rate & Health Assessment
total_inc = df[df["type"] == "INCOME"]["amount"].sum()
total_exp = df[df["type"] == "EXPENSE"]["amount"].sum()

savings_metrics = calculate_savings_rate(total_inc, total_exp)
for k, v in savings_metrics.items():
    print(f"- {k}: {v}")
"""),
        nbf.v4.new_code_cell("""# 50/30/20 Allocation Compliance
compliance = analyze_50_30_20_compliance(df, lifestyle="balanced")
print(f"Lifestyle Profile: {compliance.get('lifestyle_profile', 'balanced').title()}")
print("Actual Allocation (%):", compliance.get("actual_allocation", {}))
print("Target Allocation (%):", compliance.get("target_allocation", {}))
print("Variance (%):          ", compliance.get("variance", {}))
"""),
        nbf.v4.new_code_cell("""# Budget Adherence Matrix
budget_matrix = evaluate_budget_adherence(df)
print(budget_matrix)
"""),
        nbf.v4.new_code_cell("""# High-Spending Burst Dates (IQR Thresholding)
spikes = identify_high_spending_periods(df, period="D")
print(f"Detected {len(spikes)} high-spending burst dates:")
print(spikes.head(10))
""")
    ]
    return nb


def build_03_anomaly_analysis_notebook():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 🚨 Fintra-AI: Anomaly, Outlier & Duplicate Analysis (03_anomaly_analysis.ipynb)

### 🎯 Objective
This notebook implements robust statistical methods to identify:
1. **Unusual Transaction Amounts**: Extreme monetary values using Interquartile Range (IQR) and Z-score methods.
2. **Duplicate & Double-Charge Records**: Multiple charges with matching merchant and amount within short time windows.
3. **Behavioral Spending Pattern Anomalies**: Transactions deviating significantly from category baselines, flagged with explainable diagnostic reason codes.

> **Important**: This analysis identifies statistical anomalies for budget auditing and user awareness. It strictly avoids labelling transactions as fraudulent without external fraud ground-truth.
"""),
        nbf.v4.new_code_cell("""# 1. Imports and Setup
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath(".."))

from ml.analysis.data_loader import load_project_dataset, generate_sample_financial_dataset
from ml.analysis.anomaly_analyzer import (
    detect_amount_outliers_iqr,
    detect_amount_outliers_zscore,
    detect_duplicate_transactions,
    analyze_unexpected_spending_patterns
)

# Load data
df = load_project_dataset(include_raw_sources=True)
if df.empty:
    df = generate_sample_financial_dataset(n_records=400, seed=42)

print(f"Loaded {len(df)} transactions for anomaly analysis.")
"""),
        nbf.v4.new_markdown_cell("""## 1. Outlier Detection: IQR vs. Z-Score Methods

* **IQR Method**: Robust against skewed financial distributions. $IQR = Q_3 - Q_1$, Outliers $> Q_3 + 1.5 \\times IQR$.
* **Z-Score Method**: Standard deviations from the mean ($|Z| \\ge 3.0$).
"""),
        nbf.v4.new_code_cell("""# Category-specific IQR Outlier Detection
iqr_outliers = detect_amount_outliers_iqr(df, group_by_category=True, iqr_multiplier=1.5)
print(f"Total Category-level IQR Outliers Flagged: {len(iqr_outliers)}")
print(iqr_outliers[["date", "merchant", "category", "amount", "iqr_upper_bound", "deviation_from_median"]].head(10))
"""),
        nbf.v4.new_code_cell("""# Global Z-Score Outliers
z_outliers = detect_amount_outliers_zscore(df, threshold=3.0)
print(f"Total Z-Score Extreme Outliers (|Z| >= 3.0): {len(z_outliers)}")
print(z_outliers[["date", "merchant", "category", "amount", "z_score"]].head(10))
"""),
        nbf.v4.new_markdown_cell("""## 2. Duplicate Transaction & Double-Charge Audit

Detects transactions occurring at the same merchant for the same amount within a 24-hour window.
"""),
        nbf.v4.new_code_cell("""# Duplicate Audit (Flagged for Review)
duplicates = detect_duplicate_transactions(df, time_window_hours=24.0)
print(f"Potential Duplicate Transactions Flagged for Review: {len(duplicates)}")
print(duplicates)
"""),
        nbf.v4.new_markdown_cell("""## 3. Explainable Behavioral Spending Anomaly Diagnostics

Each flagged transaction is assigned a human-readable reason code explaining why it was flagged (e.g., $5\\times$ category median, late night off-hours).
"""),
        nbf.v4.new_code_cell("""# Behavioral Spending Pattern Analysis
pattern_anomalies = analyze_unexpected_spending_patterns(df)
print(f"Transactions Flagged with Behavioral Diagnostics: {len(pattern_anomalies)}")
print(pattern_anomalies[["date", "merchant", "category", "amount", "spend_ratio", "severity", "diagnostic_reasons"]].head(12))
""")
    ]
    return nb


def build_04_visualizations_notebook():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 📈 Fintra-AI: Visualizations Suite (04_visualizations.ipynb)

### 🎯 Objective
This notebook renders the complete suite of financial charts and interactive widgets using **Matplotlib**, **Seaborn**, and **Plotly**.

---
### 🎨 Chart Catalog:
1. **Expense Amount Distribution (KDE)**
2. **Category-Wise Spending Breakdown**
3. **Monthly Income vs. Expense Cash Flow**
4. **Daily Spending Trends & 7-Day Moving Average**
5. **Savings Rate (%) Benchmark Trend**
6. **Transaction Volume by Day of Week**
7. **Feature Correlation Heatmap**
8. **Categorical Outlier Boxplots**
9. **Budget vs. Actual Spending Comparison**
10. **Interactive Plotly Dashboards (Category Donut & Monthly Cash Flow)**
"""),
        nbf.v4.new_code_cell("""# 1. Imports and Setup
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath(".."))

from ml.analysis.data_loader import load_project_dataset, generate_sample_financial_dataset
from ml.analysis.financial_behavior import evaluate_budget_adherence
from ml.analysis.visualizer import (
    plot_expense_distribution,
    plot_category_spending,
    plot_income_vs_expenses,
    plot_monthly_spending_trends,
    plot_savings_rate_trend,
    plot_transaction_frequency_by_weekday,
    plot_outlier_boxplots,
    plot_correlation_heatmap,
    plot_budget_vs_actual,
    create_interactive_category_pie,
    create_interactive_monthly_trend
)

# Load data
df = load_project_dataset(include_raw_sources=True)
if df.empty or len(df[df['type'] == 'INCOME']) == 0:
    df = generate_sample_financial_dataset(n_records=450, seed=42)

print(f"Loaded {len(df)} transactions for visualization rendering.")
"""),
        nbf.v4.new_markdown_cell("""## 1. Expense Distribution & Category Breakdown"""),
        nbf.v4.new_code_cell("""# Expense Distribution (KDE)
fig1 = plot_expense_distribution(df)
plt.show()

# Category Spending Horizontal Bar
fig2 = plot_category_spending(df)
plt.show()
"""),
        nbf.v4.new_markdown_cell("""## 2. Monthly Cash Flow & Savings Rate Trends"""),
        nbf.v4.new_code_cell("""# Monthly Income vs Expenses
fig3 = plot_income_vs_expenses(df)
plt.show()

# Monthly Savings Rate Trend with 20% Benchmark
fig4 = plot_savings_rate_trend(df)
plt.show()
"""),
        nbf.v4.new_markdown_cell("""## 3. Temporal Dynamics & Transaction Frequency"""),
        nbf.v4.new_code_cell("""# Daily Spending Trend with 7-Day Moving Avg
fig5 = plot_monthly_spending_trends(df)
plt.show()

# Transaction Volume by Day of Week
fig6 = plot_transaction_frequency_by_weekday(df)
plt.show()
"""),
        nbf.v4.new_markdown_cell("""## 4. Outliers, Correlations & Budget Adherence"""),
        nbf.v4.new_code_cell("""# Category Boxplots (Outlier Inspection)
fig7 = plot_outlier_boxplots(df)
plt.show()

# Feature Correlation Matrix
fig8 = plot_correlation_heatmap(df)
plt.show()

# Budget vs Actual Spending
adherence = evaluate_budget_adherence(df)
fig9 = plot_budget_vs_actual(adherence)
plt.show()
"""),
        nbf.v4.new_markdown_cell("""## 5. Interactive Plotly Dashboards"""),
        nbf.v4.new_code_cell("""# Interactive Category Breakdown Donut
plotly_pie = create_interactive_category_pie(df)
if plotly_pie:
    try:
        plotly_pie.show()
    except Exception:
        print("[info] Plotly chart generated successfully.")
"""),
        nbf.v4.new_code_cell("""# Interactive Monthly Cash Flow Analysis
plotly_flow = create_interactive_monthly_trend(df)
if plotly_flow:
    try:
        plotly_flow.show()
    except Exception:
        print("[info] Plotly interactive trend generated successfully.")
""")
    ]
    return nb


def main():
    notebooks = {
        "notebooks/01_eda.ipynb": build_01_eda_notebook(),
        "notebooks/02_financial_analysis.ipynb": build_02_financial_analysis_notebook(),
        "notebooks/03_anomaly_analysis.ipynb": build_03_anomaly_analysis_notebook(),
        "notebooks/04_visualizations.ipynb": build_04_visualizations_notebook(),
    }

    for path, nb in notebooks.items():
        with open(path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)
        print(f"[success] Generated {path} successfully.")


if __name__ == "__main__":
    main()
