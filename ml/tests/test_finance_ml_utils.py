import unittest

import pandas as pd

from ml.utils.goal_rules import (
    calculate_months_to_goal,
    calculate_required_monthly_savings,
    evaluate_goal_feasibility,
    project_savings_growth,
)
from ml.utils.timeseries_features import add_lag_features, add_rolling_features


class GoalRulesTests(unittest.TestCase):
    def test_completed_goal_requires_no_more_months(self):
        self.assertEqual(calculate_months_to_goal(10_000, 10_000, 500), 0.0)
        self.assertEqual(calculate_required_monthly_savings(10_000, 10_000, 12), 0.0)

    def test_unfunded_goal_with_no_contribution_is_not_reachable(self):
        self.assertEqual(calculate_months_to_goal(10_000, 0, 0), 999.0)

    def test_required_savings_is_positive_for_unfunded_goal(self):
        required = calculate_required_monthly_savings(12_000, 0, 12, 0)
        self.assertEqual(required, 1_000.0)

    def test_growth_projection_preserves_simple_cash_total(self):
        projection = project_savings_growth(1_000, 2_000, 0)
        self.assertEqual(projection["1_year"]["cash_savings"], 14_000.0)
        self.assertEqual(projection["1_year"]["invested_wealth"], 14_000.0)
        self.assertEqual(projection["1_year"]["compounding_gain"], 0.0)

    def test_feasibility_tiers_are_stable(self):
        self.assertEqual(evaluate_goal_feasibility(1_250, 1_000)[0], "ON_TRACK")
        self.assertEqual(evaluate_goal_feasibility(1_000, 1_000)[0], "FEASIBLE")
        self.assertEqual(evaluate_goal_feasibility(0, 1_000)[0], "AT_RISK")


class TimeSeriesFeatureTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame(
            {
                "date": pd.date_range("2026-01-01", periods=4, freq="D"),
                "total_spend": [10.0, 20.0, 30.0, 40.0],
            }
        )

    def test_lag_features_use_only_previous_rows(self):
        result = add_lag_features(self.frame, lags=[1, 2])
        self.assertTrue(pd.isna(result.loc[0, "lag_1"]))
        self.assertEqual(result.loc[3, "lag_1"], 30.0)
        self.assertEqual(result.loc[3, "lag_2"], 20.0)

    def test_rolling_features_are_shifted_to_prevent_target_leakage(self):
        result = add_rolling_features(self.frame, windows=[3])
        self.assertTrue(pd.isna(result.loc[0, "rolling_mean_3"]))
        self.assertEqual(result.loc[3, "rolling_mean_3"], 20.0)
        self.assertEqual(result.loc[3, "rolling_max_3"], 30.0)
        self.assertNotEqual(result.loc[3, "rolling_mean_3"], 25.0)


if __name__ == "__main__":
    unittest.main()
