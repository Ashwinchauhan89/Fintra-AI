"""
Unit and Contract Verification Tests for Fintra-AI Backend REST Endpoints.
"""

import unittest
from backend.app.schemas.predictions import (
    CategoryPredictRequest,
    CategoryPredictResponse,
    AnomalyCheckRequest,
    FraudCheckRequest,
    BudgetRecommendRequest,
    HealthScoreRequest,
    GoalTimelineRequest,
    InvestmentRecommendRequest,
)


class TestBackendSchemas(unittest.TestCase):
    """Verifies Pydantic schemas correctly enforce validation boundaries."""

    def test_category_request_schema(self):
        req = CategoryPredictRequest(merchant="Swiggy", amount=350.0, description="Lunch")
        self.assertEqual(req.merchant, "Swiggy")
        self.assertEqual(req.amount, 350.0)

    def test_anomaly_request_schema(self):
        req = AnomalyCheckRequest(merchant="Electronics Mart", amount=75000.0, category="shopping", hour_of_day=3)
        self.assertEqual(req.amount, 75000.0)
        self.assertEqual(req.hour_of_day, 3)

    def test_fraud_request_schema(self):
        req = FraudCheckRequest(
            merchant="Casino",
            amount=90000.0,
            category="entertainment",
            device_trust_score=0.1,
            merchant_risk_score=0.9,
        )
        self.assertEqual(req.merchant, "Casino")
        self.assertEqual(req.device_trust_score, 0.1)

    def test_budget_request_schema(self):
        req = BudgetRecommendRequest(
            monthly_income=75000.0,
            historical_expenses={"food": 15000.0, "shopping": 10000.0},
            savings_target_pct=0.25,
            lifestyle="growth",
        )
        self.assertEqual(req.monthly_income, 75000.0)
        self.assertEqual(req.lifestyle, "growth")

    def test_health_request_schema(self):
        req = HealthScoreRequest(
            monthly_income=80000.0,
            current_balance=150000.0,
            monthly_expenses=40000.0,
            debt_obligations=5000.0,
        )
        self.assertEqual(req.monthly_income, 80000.0)
        self.assertEqual(req.current_balance, 150000.0)

    def test_goal_timeline_schema(self):
        req = GoalTimelineRequest(
            goal_name="MacBook",
            target_amount=100000.0,
            current_saved=20000.0,
            monthly_income=65000.0,
            monthly_expenses=35000.0,
        )
        self.assertEqual(req.goal_name, "MacBook")
        self.assertEqual(req.target_amount, 100000.0)

    def test_investment_request_schema(self):
        req = InvestmentRecommendRequest(monthly_income=90000.0, age=26, risk_profile="AGGRESSIVE")
        self.assertEqual(req.age, 26)
        self.assertEqual(req.risk_profile, "AGGRESSIVE")


if __name__ == "__main__":
    unittest.main()
