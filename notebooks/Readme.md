# 📊 Fintra-AI — Financial Data Analysis & Visualization Module

This directory contains the **Jupyter Notebook-based Financial Data Analysis and Visualization Suite** for **Fintra-AI**. It provides reproducible workflows for exploratory data analysis, spending behavior modeling, anomaly detection, and publication-ready financial visualizations.

---

## 📁 Notebook Catalog

| Notebook | Focus Area | Description |
| :--- | :--- | :--- |
| **[`01_eda.ipynb`](file:///notebooks/01_eda.ipynb)** | **Exploratory Data Analysis** | Multi-source ingestion, schema validation, data cleaning, missing value handling, and distribution profiling. |
| **[`02_financial_analysis.ipynb`](file:///notebooks/02_financial_analysis.ipynb)** | **Financial Metrics & Behavior** | Transaction totals, average ticket sizes, merchant rankings, monthly expense burn, income stability index ($CV$), savings rate, 50/30/20 compliance, and budget adherence. |
| **[`03_anomaly_analysis.ipynb`](file:///notebooks/03_anomaly_analysis.ipynb)** | **Anomaly & Outlier Auditing** | Category-level IQR outliers, global Z-score extreme values, duplicate charge detection, and explainable behavioral reason codes. |
| **[`04_visualizations.ipynb`](file:///notebooks/04_visualizations.ipynb)** | **Visualizations Suite** | Matplotlib, Seaborn, and interactive Plotly charts for expense distribution (KDE), category breakdowns, monthly cash flows, moving averages, savings trends, and budget vs actual. |

---

## 🏗️ Architecture & Reusable Python Modules

To maintain clean and reproducible notebooks, core analytical logic is decoupled into reusable modules located in [`ml/analysis/`](file:///ml/analysis/):

* **`ml.analysis.data_loader`**: Schema harmonization, date/amount validation, and multi-source adapters.
* **`ml.analysis.transaction_analyzer`**: Transaction summaries, frequencies, category distributions, and merchant metrics.
* **`ml.analysis.expense_analyzer`**: Monthly expense aggregation, MoM spending growth trends, and recurring expense heuristics.
* **`ml.analysis.income_analyzer`**: Inflow aggregations, income sources, stability metrics (mean, std, $CV$), and surplus/deficit calculations.
* **`ml.analysis.financial_behavior`**: Safe savings rate calculations, temporal spending breakdowns, 50/30/20 budget allocation compliance, and high-spend burst periods.
* **`ml.analysis.anomaly_analyzer`**: IQR & Z-score outlier detection, duplicate record flagging (non-destructive), and explainable anomaly diagnostic codes.
* **`ml.analysis.visualizer`**: Matplotlib, Seaborn, and Plotly visualizers with currency formatting and robust error handling.

---

## 📋 Canonical Transaction Schema

Transactions are normalized to the following standard schema:

| Column | Type | Description |
| :--- | :--- | :--- |
| `date` | `pd.Timestamp` | Normalized timestamp of the transaction |
| `amount` | `float` | Non-negative transaction amount in INR |
| `type` | `str` | `"INCOME"` or `"EXPENSE"` |
| `category` | `str` | Canonical category (`food`, `shopping`, `transport`, `bills`, `entertainment`, `healthcare`, `education`, `salary`, `investment`, `other`) |
| `merchant` | `str` | Merchant or counterparty entity |
| `description` | `str` | Transaction notes or subcategory description |
| `account_type` | `str` | Origin account/payment method (e.g. `Savings`, `Current`, `Credit Card`) |
| `source` | `str` | Source filename or ingestion stream |

---

## 🧮 Statistical & Heuristic Formulations

1. **Savings Rate (%)**:
   $$\text{Savings Rate} = \frac{\text{Income} - \text{Expenses}}{\text{Income}} \times 100$$
   *(Safely handles zero/negative income by reporting -100% or 0% without division-by-zero errors)*

2. **Income Stability ($CV$)**:
   $$CV = \frac{\sigma_{\text{monthly income}}}{\mu_{\text{monthly income}}}$$
   * $CV \le 0.10$: High Stability (Fixed salary/steady inflow)
   * $0.10 < CV \le 0.30$: Moderate Volatility
   * $CV > 0.30$: High Volatility (Irregular/variable freelance income)

3. **Outlier Detection (IQR)**:
   $$\text{Lower Bound} = \max(0, Q_1 - 1.5 \times IQR), \quad \text{Upper Bound} = Q_3 + 1.5 \times IQR$$

4. **Recurring Subscriptions Heuristic**:
   * Same merchant and category across $\ge 2$ occurrences.
   * Coefficient of variation in amount $CV_{\text{amount}} \le 0.05$.
   * Stable inter-transaction intervals matching standard cadences: Weekly ($\sim 7$d), Monthly ($\sim 30$d), Quarterly ($\sim 90$d), Annual ($\sim 365$d).

5. **Duplicate Transaction Audit**:
   * Matching merchant, category, and identical amount occurring within a 24-hour window.
   * **Rule**: Records are only flagged for auditor review—never deleted automatically.

---

## 🚀 How to Run

1. Ensure the Python environment dependencies are installed:
   ```bash
   pip install -r ml/requirements.txt
   ```
2. Start Jupyter Lab or open in your IDE:
   ```bash
   jupyter lab notebooks/
   ```
   Or execute directly within VS Code / Cursor / Google Colab.
