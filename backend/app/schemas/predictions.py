"""
Pydantic Schemas for Fintra-AI ML Prediction Services.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# --- Expense Category Prediction ---
class CategoryPredictRequest(BaseModel):
    merchant: str = Field(..., description="Name of the merchant or store", example="Swiggy")
    description: str = Field("", description="Transaction notes or items summary", example="Dinner order")
    amount: float = Field(0.0, description="Transaction amount", example=450.0)
    date: Optional[str] = Field(None, description="ISO-8601 transaction date string", example="2026-08-25")


class CategoryPredictResponse(BaseModel):
    status: str = "success"
    category: str
    confidence: float
    is_low_confidence: bool = False
    fallback_used: bool = False


# --- Spending Anomaly Detection ---
class AnomalyCheckRequest(BaseModel):
    merchant: str = Field("", description="Merchant name", example="Electronics Hub")
    amount: float = Field(..., description="Transaction amount in INR", example=45000.0)
    category: str = Field("general", description="Expense category", example="shopping")
    hour_of_day: Optional[int] = Field(None, description="Hour of the transaction (0-23)", example=3)


class AnomalyCheckResponse(BaseModel):
    status: str = "success"
    is_anomaly: bool
    severity: str
    reasons: List[str]


# --- Multi-Factor Fraud Risk Scoring ---
class FraudCheckRequest(BaseModel):
    merchant: str = Field(..., description="Merchant name", example="MacauCasino")
    amount: float = Field(..., description="Transaction amount in INR", example=95000.0)
    category: str = Field("entertainment", description="Expense category", example="entertainment")
    hour_of_day: int = Field(12, description="Hour of the transaction (0-23)", example=3)
    distance_from_home_km: float = Field(0.0, description="Distance from primary location", example=3200.0)
    device_trust_score: float = Field(1.0, description="Device trust score between 0.0 and 1.0", example=0.05)
    merchant_risk_score: float = Field(0.1, description="Merchant risk index between 0.0 and 1.0", example=0.95)
    is_foreign_currency: int = Field(0, description="1 if foreign currency, 0 if domestic", example=1)


class FraudCheckResponse(BaseModel):
    status: str = "success"
    fraud_probability: float
    fraud_percentage: float
    risk_level: str
    recommended_action: str
    risk_factors: List[str]


# --- Budget Recommendation ---
class BudgetRecommendRequest(BaseModel):
    monthly_income: float = Field(..., description="Monthly net take-home income in INR", example=75000.0)
    historical_expenses: Optional[Dict[str, float]] = Field(
        None,
        description="Optional historical category spends",
        example={"food": 18000, "shopping": 12000, "bills": 9000, "transport": 5000}
    )
    savings_target_pct: float = Field(0.20, description="Target savings rate (e.g. 0.20 for 20%)", example=0.20)
    lifestyle: str = Field("balanced", description="Lifestyle profile: conservative, balanced, growth", example="balanced")


class BudgetRecommendResponse(BaseModel):
    status: str = "success"
    monthly_income: float
    recommended_allocations: Dict[str, float]
    rule_50_30_20: Dict[str, Any]
    optimization_insights: List[str]


# --- Financial Health Score ---
class HealthScoreRequest(BaseModel):
    monthly_income: float = Field(..., description="Monthly income in INR", example=80000.0)
    current_balance: float = Field(..., description="Total liquid balance in INR", example=200000.0)
    monthly_expenses: Union[float, Dict[str, float]] = Field(
        ...,
        description="Total monthly expenses as a float or category breakdown map",
        example=45000.0
    )
    debt_obligations: float = Field(0.0, description="Total monthly debt or loan payments", example=5000.0)


class HealthScoreResponse(BaseModel):
    status: str = "success"
    financial_health_score: float
    grade: str
    status_label: str
    pillars: Dict[str, Any]
    recommendations: List[str]


# --- Goal Timeline Prediction ---
class GoalTimelineRequest(BaseModel):
    goal_name: str = Field(..., description="Name of financial goal", example="MacBook Pro M3")
    target_amount: float = Field(..., description="Target cost in INR", example=85000.0)
    current_saved: float = Field(0.0, description="Current funds saved toward goal", example=25000.0)
    monthly_income: float = Field(..., description="Monthly income in INR", example=65000.0)
    monthly_expenses: float = Field(..., description="Monthly expenses in INR", example=38000.0)
    debt_obligations: float = Field(0.0, description="Monthly debt EMIs in INR", example=4000.0)
    intended_months: Optional[int] = Field(None, description="User intended horizon in months", example=6)
    expected_annual_return_pct: float = Field(7.0, description="Expected annual compound return %", example=7.0)


class GoalTimelineResponse(BaseModel):
    status: str = "success"
    goal_name: str
    target_amount: float
    current_saved: float
    predicted_months_to_completion: float
    estimated_completion_date: str
    required_monthly_savings: float
    feasibility: str
    recommendations: List[str]


# --- Investment Allocation ---
class InvestmentRecommendRequest(BaseModel):
    monthly_income: float = Field(..., description="Monthly income in INR", example=90000.0)
    age: int = Field(28, description="User age in years", example=28)
    investment_horizon_years: int = Field(5, description="Investment horizon in years", example=5)
    risk_profile: str = Field("BALANCED", description="Risk profile: CONSERVATIVE, BALANCED, AGGRESSIVE", example="AGGRESSIVE")


class InvestmentRecommendResponse(BaseModel):
    status: str = "success"
    recommended_allocation_pct: Dict[str, float]
    monthly_sip_distribution_inr: Dict[str, float]
    portfolio_expected_cagr_pct: float
    wealth_growth_projections: Dict[str, Any]
