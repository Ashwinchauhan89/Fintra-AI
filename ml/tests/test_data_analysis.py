"""
Comprehensive Unit Tests for Fintra-AI Data Analysis & Visualization Module.
Tests metrics, calculations, edge cases, heuristics, and visualizers.
"""

import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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


class DataAnalysisAndVisualizationTests(unittest.TestCase):
    def setUp(self):
        # Create standard test dataframe
        self.sample_df = pd.DataFrame([
            {"date": "2026-01-01 10:00:00", "amount": 50000.0, "type": "INCOME", "category": "salary", "merchant": "Employer", "description": "Salary"},
            {"date": "2026-01-05 12:00:00", "amount": 1000.0, "type": "EXPENSE", "category": "food", "merchant": "Zomato", "description": "Lunch"},
            {"date": "2026-01-10 14:00:00", "amount": 3000.0, "type": "EXPENSE", "category": "shopping", "merchant": "Amazon", "description": "Books"},
            {"date": "2026-01-15 18:00:00", "amount": 1000.0, "type": "EXPENSE", "category": "food", "merchant": "Zomato", "description": "Dinner"},
            {"date": "2026-01-15 18:05:00", "amount": 1000.0, "type": "EXPENSE", "category": "food", "merchant": "Zomato", "description": "Duplicate test"},
            {"date": "2026-01-20 09:00:00", "amount": 649.0, "type": "EXPENSE", "category": "entertainment", "merchant": "Netflix", "description": "Subscription"},
            {"date": "2026-02-01 10:00:00", "amount": 50000.0, "type": "INCOME", "category": "salary", "merchant": "Employer", "description": "Salary"},
            {"date": "2026-02-05 12:00:00", "amount": 1200.0, "type": "EXPENSE", "category": "food", "merchant": "Swiggy", "description": "Food"},
            {"date": "2026-02-20 09:00:00", "amount": 649.0, "type": "EXPENSE", "category": "entertainment", "merchant": "Netflix", "description": "Subscription"},
            {"date": "2026-03-20 09:00:00", "amount": 649.0, "type": "EXPENSE", "category": "entertainment", "merchant": "Netflix", "description": "Subscription"},
        ])
        self.clean_sample = validate_and_clean_dataframe(self.sample_df)

    def tearDown(self):
        plt.close("all")

    # -------------------------------------------------------------
    # 1. DataLoader & Schema Validation Tests
    # -------------------------------------------------------------
    def test_empty_dataframe_cleaning(self):
        empty_clean = validate_and_clean_dataframe(pd.DataFrame())
        self.assertEqual(list(empty_clean.columns), CANONICAL_COLUMNS)
        self.assertTrue(empty_clean.empty)

    def test_category_normalization(self):
        self.assertEqual(normalize_category("Online Shopping"), "shopping")
        self.assertEqual(normalize_category("GROCERY"), "food")
        self.assertEqual(normalize_category(None), "other")

    def test_synthetic_data_generation(self):
        df_synth = generate_sample_financial_dataset(n_records=50)
        self.assertEqual(len(df_synth), 50 + 7)  # 50 expenses + salary entries
        self.assertTrue("INCOME" in df_synth["type"].values)
        self.assertTrue("EXPENSE" in df_synth["type"].values)

    # -------------------------------------------------------------
    # 2. Transaction Analysis Tests
    # -------------------------------------------------------------
    def test_transaction_summary(self):
        summary = get_transaction_summary(self.clean_sample)
        self.assertEqual(summary["total_transactions"], 10)
        self.assertEqual(summary["total_income_count"], 2)
        self.assertEqual(summary["total_expense_count"], 8)
        self.assertEqual(summary["average_income_amount"], 50000.0)

    def test_transaction_frequency(self):
        freq = analyze_transaction_frequency(self.clean_sample)
        self.assertFalse(freq["daily_frequency"].empty)
        self.assertFalse(freq["monthly_frequency"].empty)
        self.assertGreater(freq["avg_daily_transactions"], 0)

    def test_category_distribution(self):
        dist = analyze_category_distribution(self.clean_sample)
        self.assertFalse(dist.empty)
        self.assertTrue("percentage_count" in dist.columns)
        self.assertTrue("percentage_amount" in dist.columns)
        self.assertAlmostEqual(dist["percentage_amount"].sum(), 100.0, delta=0.5)

    def test_merchant_analysis(self):
        merchants = analyze_merchants(self.clean_sample)
        self.assertIn("by_frequency", merchants)
        self.assertIn("by_spending", merchants)
        self.assertEqual(merchants["by_frequency"].iloc[0]["merchant"], "Netflix")

    # -------------------------------------------------------------
    # 3. Expense Analysis Tests
    # -------------------------------------------------------------
    def test_aggregate_monthly_expenses(self):
        monthly = aggregate_monthly_expenses(self.clean_sample)
        self.assertEqual(len(monthly), 3)  # Jan, Feb, Mar
        self.assertTrue("total_expense" in monthly.columns)

    def test_rank_category_spending(self):
        ranked = rank_category_spending(self.clean_sample)
        self.assertEqual(ranked.iloc[0]["rank"], 1)
        self.assertEqual(ranked.iloc[0]["category"], "food")
        self.assertEqual(ranked.iloc[0]["total_expense"], 4200.0)

    def test_spending_trends(self):
        trends = calculate_spending_trends(self.clean_sample)
        self.assertIn("mom_growth_pct", trends.columns)
        self.assertIn("trend_direction", trends.columns)

    def test_recurring_expense_detection(self):
        recurring = detect_recurring_expenses(self.clean_sample, min_occurrences=2)
        self.assertFalse(recurring.empty)
        netflix_row = recurring[recurring["merchant"] == "Netflix"]
        self.assertFalse(netflix_row.empty)
        self.assertEqual(netflix_row.iloc[0]["cadence"], "MONTHLY")

    # -------------------------------------------------------------
    # 4. Income Analysis Tests
    # -------------------------------------------------------------
    def test_income_stability(self):
        stability = calculate_income_stability(self.clean_sample)
        self.assertEqual(stability["months_analyzed"], 2)
        self.assertEqual(stability["stability_tier"], "HIGH_STABILITY")
        self.assertEqual(stability["coefficient_of_variation"], 0.0)

    def test_income_vs_expenses_comparison(self):
        comp = compare_income_vs_expenses(self.clean_sample)
        self.assertEqual(len(comp), 3)
        jan_row = comp[comp["month"] == "2026-01"].iloc[0]
        self.assertEqual(jan_row["total_income"], 50000.0)
        self.assertEqual(jan_row["status"], "SURPLUS")
        self.assertGreater(jan_row["savings_rate_pct"], 0.0)

    # -------------------------------------------------------------
    # 5. Financial Behavior Tests
    # -------------------------------------------------------------
    def test_savings_rate_calculations(self):
        # Normal positive case
        r1 = calculate_savings_rate(100000.0, 40000.0)
        self.assertEqual(r1["net_savings"], 60000.0)
        self.assertEqual(r1["savings_rate_pct"], 60.0)
        self.assertEqual(r1["health_status"], "EXCELLENT")

        # Zero income edge case
        r2 = calculate_savings_rate(0.0, 5000.0)
        self.assertEqual(r2["savings_rate_pct"], -100.0)
        self.assertEqual(r2["health_status"], "CRITICAL_DEFICIT")

    def test_50_30_20_compliance(self):
        comp = analyze_50_30_20_compliance(self.clean_sample)
        self.assertIn("actual_allocation", comp)
        self.assertIn("target_allocation", comp)

    def test_budget_adherence(self):
        budget_limits = {"food": 5000.0, "shopping": 2000.0, "entertainment": 2000.0}
        adherence = evaluate_budget_adherence(self.clean_sample, budget_targets=budget_limits)
        self.assertFalse(adherence.empty)
        shopping_row = adherence[adherence["category"] == "shopping"].iloc[0]
        self.assertEqual(shopping_row["status"], "OVER_BUDGET")

    # -------------------------------------------------------------
    # 6. Anomaly & Duplicate Tests
    # -------------------------------------------------------------
    def test_duplicate_transaction_detection(self):
        dupes = detect_duplicate_transactions(self.clean_sample, time_window_hours=24.0)
        self.assertFalse(dupes.empty)
        self.assertEqual(dupes.iloc[0]["merchant"], "Zomato")
        self.assertLessEqual(dupes.iloc[0]["time_gap_hours"], 1.0)

    def test_outlier_detection_empty_safety(self):
        empty_outliers = detect_amount_outliers_iqr(pd.DataFrame())
        self.assertTrue(empty_outliers.empty)

        empty_z = detect_amount_outliers_zscore(pd.DataFrame())
        self.assertTrue(empty_z.empty)

    def test_unexpected_spending_patterns(self):
        patterns = analyze_unexpected_spending_patterns(self.clean_sample)
        # Should not crash on clean data
        self.assertIsInstance(patterns, pd.DataFrame)

    # -------------------------------------------------------------
    # 7. Visualizer Tests (Smoke Test No Crashes)
    # -------------------------------------------------------------
    def test_visualizer_smoke_tests(self):
        fig1 = plot_expense_distribution(self.clean_sample)
        self.assertIsNotNone(fig1)

        fig2 = plot_category_spending(self.clean_sample)
        self.assertIsNotNone(fig2)

        fig3 = plot_income_vs_expenses(self.clean_sample)
        self.assertIsNotNone(fig3)

        fig4 = plot_monthly_spending_trends(self.clean_sample)
        self.assertIsNotNone(fig4)

        fig5 = plot_savings_rate_trend(self.clean_sample)
        self.assertIsNotNone(fig5)

        fig6 = plot_transaction_frequency_by_weekday(self.clean_sample)
        self.assertIsNotNone(fig6)

        fig7 = plot_outlier_boxplots(self.clean_sample)
        self.assertIsNotNone(fig7)

        fig8 = plot_correlation_heatmap(self.clean_sample)
        self.assertIsNotNone(fig8)

        adherence = evaluate_budget_adherence(self.clean_sample)
        fig9 = plot_budget_vs_actual(adherence)
        self.assertIsNotNone(fig9)

        # Plotly smoke tests
        p_pie = create_interactive_category_pie(self.clean_sample)
        self.assertIsNotNone(p_pie)

        p_trend = create_interactive_monthly_trend(self.clean_sample)
        self.assertIsNotNone(p_trend)


if __name__ == "__main__":
    unittest.main()
