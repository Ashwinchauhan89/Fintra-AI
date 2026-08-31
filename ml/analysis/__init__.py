"""
Fintra-AI Data Analysis & Visualization Package
Provides reusable metrics, analyzers, heuristic algorithms, and plotting modules.
"""

from ml.analysis.data_loader import (
    CANONICAL_COLUMNS,
    ROADMAP_CATEGORIES,
    generate_sample_financial_dataset,
    load_project_dataset,
    normalize_category,
    validate_and_clean_dataframe,
)
from ml.analysis.transaction_analyzer import (
    analyze_category_distribution,
    analyze_merchants,
    analyze_transaction_frequency,
    get_transaction_summary,
)
from ml.analysis.expense_analyzer import (
    aggregate_monthly_expenses,
    calculate_spending_trends,
    detect_recurring_expenses,
    rank_category_spending,
)
from ml.analysis.income_analyzer import (
    aggregate_monthly_income,
    analyze_income_sources,
    calculate_income_stability,
    compare_income_vs_expenses,
)
from ml.analysis.financial_behavior import (
    analyze_50_30_20_compliance,
    analyze_temporal_spending_patterns,
    calculate_savings_rate,
    evaluate_budget_adherence,
    identify_high_spending_periods,
)
from ml.analysis.anomaly_analyzer import (
    analyze_unexpected_spending_patterns,
    detect_amount_outliers_iqr,
    detect_amount_outliers_zscore,
    detect_duplicate_transactions,
)
from ml.analysis.visualizer import (
    create_interactive_category_pie,
    create_interactive_monthly_trend,
    plot_budget_vs_actual,
    plot_category_spending,
    plot_correlation_heatmap,
    plot_expense_distribution,
    plot_income_vs_expenses,
    plot_monthly_spending_trends,
    plot_outlier_boxplots,
    plot_savings_rate_trend,
    plot_transaction_frequency_by_weekday,
)

__all__ = [
    "CANONICAL_COLUMNS",
    "ROADMAP_CATEGORIES",
    "generate_sample_financial_dataset",
    "load_project_dataset",
    "normalize_category",
    "validate_and_clean_dataframe",
    "get_transaction_summary",
    "analyze_transaction_frequency",
    "analyze_category_distribution",
    "analyze_merchants",
    "aggregate_monthly_expenses",
    "rank_category_spending",
    "calculate_spending_trends",
    "detect_recurring_expenses",
    "aggregate_monthly_income",
    "analyze_income_sources",
    "calculate_income_stability",
    "compare_income_vs_expenses",
    "calculate_savings_rate",
    "analyze_temporal_spending_patterns",
    "analyze_50_30_20_compliance",
    "evaluate_budget_adherence",
    "identify_high_spending_periods",
    "detect_amount_outliers_iqr",
    "detect_amount_outliers_zscore",
    "detect_duplicate_transactions",
    "analyze_unexpected_spending_patterns",
    "plot_expense_distribution",
    "plot_category_spending",
    "plot_income_vs_expenses",
    "plot_monthly_spending_trends",
    "plot_savings_rate_trend",
    "plot_transaction_frequency_by_weekday",
    "plot_outlier_boxplots",
    "plot_correlation_heatmap",
    "plot_budget_vs_actual",
    "create_interactive_category_pie",
    "create_interactive_monthly_trend",
]
