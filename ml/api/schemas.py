"""
Pydantic v2 Request & Response Validation Schemas for Fintra-AI ML REST Microservice (Phase 19).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. Health & Server Status
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = Field(default="healthy")
    service: str = Field(default="Fintra-AI ML Production Microservice")
    version: str = Field(default="1.0.0")
    loaded_models: Dict[str, bool]
    server_time: str


# ---------------------------------------------------------------------------
# 2. Expense Classification (Phase 3) & OCR Scanner (Phase 15)
# ---------------------------------------------------------------------------

class ExpenseClassifyRequest(BaseModel):
    merchant: str = Field(..., example="Swiggy")
    description: str = Field(..., example="Lunch bowl order")
    amount: float = Field(..., gt=0, example=350.0)
    date: Optional[str] = Field(None, example="2026-08-25")


class ExpenseClassifyResponse(BaseModel):
    category: str
    confidence: Optional[float] = None
    low_confidence: Optional[bool] = False


class OCRScanRequest(BaseModel):
    raw_text: str = Field(..., example="STARBUCKS COFFEE\nDate: 25/08/2026\n1x Latte 345.00\nGRAND TOTAL: INR 362.25\nPaid via UPI")


class OCRScanResponse(BaseModel):
    status: str
    extracted_expense: Dict[str, Any]
    extraction_confidence: float
    entity_confidences: Dict[str, float]


# ---------------------------------------------------------------------------
# 3. Budgeting (Phase 5), Savings (Phase 6) & Health Score (Phase 7)
# ---------------------------------------------------------------------------

class BudgetRecommendRequest(BaseModel):
    monthly_income: float = Field(..., gt=0, example=80000.0)
    lifestyle: str = Field(default="balanced", example="balanced")
    savings_target_pct: float = Field(default=0.20, ge=0.05, le=0.60)
    historical_expenses: Optional[Dict[str, float]] = Field(None, example={"food": 15000.0, "shopping": 10000.0, "bills": 8000.0})
    debt_obligations: float = Field(default=0.0, ge=0)


class BudgetRecommendResponse(BaseModel):
    monthly_income: float
    lifestyle: str
    savings_target_pct: float
    recommended_allocations: Dict[str, float]
    rule_50_30_20: Dict[str, Any]
    category_breakdown: Dict[str, Any]
    optimization_insights: List[str]


class SavingsProjectRequest(BaseModel):
    monthly_income: float = Field(..., gt=0, example=80000.0)
    monthly_expenses: float = Field(..., ge=0, example=45000.0)
    debt_obligations: float = Field(default=0.0, ge=0)
    current_balance: float = Field(default=50000.0, ge=0)
    expected_annual_return_pct: float = Field(default=7.0, ge=0, le=30)


class SavingsProjectResponse(BaseModel):
    status: str
    monthly_income: float
    predicted_monthly_savings: float
    savings_rate_pct: float
    wealth_growth_projections: Dict[str, Any]
    actionable_insights: List[str]


class HealthScoreRequest(BaseModel):
    monthly_income: float = Field(..., gt=0, example=80000.0)
    current_balance: float = Field(default=150000.0, ge=0)
    monthly_expenses: Dict[str, float] = Field(..., example={"food": 15000.0, "shopping": 8000.0, "bills": 10000.0})
    debt_obligations: float = Field(default=5000.0, ge=0)


class HealthScoreResponse(BaseModel):
    financial_health_score: float
    grade: str
    status: str
    runway_months: float
    savings_rate_pct: float
    pillars: Dict[str, Any]
    recommendations: Optional[List[str]] = None
    action_items: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# 4. Security & Risk: Fraud (Phase 8), Anomaly (Phase 9), Loan (Phase 12), Credit (Phase 13)
# ---------------------------------------------------------------------------

class FraudCheckRequest(BaseModel):
    amount: float = Field(..., gt=0, example=45000.0)
    category: str = Field(default="shopping", example="shopping")
    hour_of_day: int = Field(default=14, ge=0, le=23)
    merchant: Optional[str] = Field("Online Store")


class FraudCheckResponse(BaseModel):
    status: str
    risk_level: str
    fraud_probability: float
    recommended_action: str
    action_detail: str


class AnomalyDetectRequest(BaseModel):
    amount: float = Field(..., gt=0, example=25000.0)
    category: str = Field(default="dining", example="dining")


class AnomalyDetectResponse(BaseModel):
    status: str
    is_anomaly: bool
    anomaly_score: float
    reason_codes: List[str]


class LoanUnderwriteRequest(BaseModel):
    monthly_income: float = Field(..., gt=0, example=85000.0)
    requested_loan_amount: float = Field(..., gt=0, example=400000.0)
    loan_tenure_months: int = Field(..., gt=0, example=36)
    loan_purpose: str = Field(default="PERSONAL_LOAN", example="PERSONAL_LOAN")
    credit_score: int = Field(default=740, ge=300, le=900)
    existing_monthly_emi: float = Field(default=5000.0, ge=0)


class LoanUnderwriteResponse(BaseModel):
    verdict: str
    approval_status: str
    risk_tier: str
    default_probability_pct: float
    credit_health_grade: str
    proposed_loan_terms: Dict[str, Any]
    max_safe_borrowing_limit_inr: float
    underwriting_diagnostics: Optional[Dict[str, Any]] = None
    actionable_underwriting_tips: Optional[List[str]] = None
    underwriting_action_tips: Optional[List[str]] = None


class CreditEstimateRequest(BaseModel):
    monthly_income: float = Field(..., gt=0, example=75000.0)
    total_credit_limit: float = Field(..., gt=0, example=250000.0)
    total_credit_used: float = Field(..., ge=0, example=35000.0)
    on_time_payment_pct: float = Field(default=98.0, ge=0, le=100)
    missed_payments_count_2yr: int = Field(default=0, ge=0)
    credit_history_years: float = Field(default=5.0, ge=0)
    hard_inquiries_last_6m: int = Field(default=1, ge=0)


class CreditEstimateResponse(BaseModel):
    status: str
    model_engine: Optional[str] = None
    estimated_credit_score: int
    score_scale: str
    credit_tier: str
    risk_grade: str
    tier_description: Optional[str] = None
    loan_approval_odds: str
    credit_summary: Dict[str, Any]
    five_pillar_diagnostics: Dict[str, Any]
    what_if_score_simulations: List[Dict[str, Any]]
    strategic_credit_improvement_tips: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# 5. Wealth: Investment (Phase 10), Goals (Phase 11), Forecasting (Phase 18), Marketplace (Phase 16)
# ---------------------------------------------------------------------------

class InvestmentRecommendRequest(BaseModel):
    monthly_income: float = Field(..., gt=0, example=90000.0)
    age: int = Field(..., ge=18, le=100, example=28)
    risk_profile: str = Field(default="BALANCED", example="BALANCED")
    monthly_surplus: Optional[float] = Field(None, ge=0)
    investment_horizon_years: int = Field(default=5, ge=1, le=40)
    liquid_savings: float = Field(default=200000.0, ge=0)


class InvestmentRecommendResponse(BaseModel):
    status: str
    model_engine: str
    user_profile: Dict[str, Any]
    recommended_allocation_pct: Dict[str, float]
    monthly_sip_distribution_inr: Dict[str, float]
    portfolio_expected_cagr_pct: float
    wealth_growth_projections: Dict[str, Any]
    curated_fund_instruments: List[Dict[str, Any]]
    strategic_financial_tips: List[str]


class GoalTimelineRequest(BaseModel):
    goal_name: str = Field(..., example="Emergency Fund")
    target_amount: float = Field(..., gt=0, example=300000.0)
    current_saved: float = Field(default=50000.0, ge=0)
    monthly_income: float = Field(default=60000.0, gt=0)
    monthly_expenses: float = Field(default=35000.0, ge=0)
    intended_months: int = Field(default=12, gt=0)
    expected_annual_return_pct: float = Field(default=7.0, ge=0)


class GoalTimelineResponse(BaseModel):
    status: str
    goal_name: str
    target_amount: float
    current_saved: float
    remaining_amount: float
    predicted_months_to_completion: float
    estimated_completion_date: str
    user_intended_months: int
    required_monthly_savings: float
    current_monthly_savings_capacity: float
    feasibility: str
    accelerated_timeline_months: float
    potential_months_saved: float
    recommendations: List[str]


class CashflowForecastRequest(BaseModel):
    monthly_income: float = Field(default=65000.0, gt=0)
    current_balance: float = Field(default=28000.0, ge=0)
    horizon_days: int = Field(default=30, ge=7, le=90)
    payday_of_month: int = Field(default=1, ge=1, le=31)


class CashflowForecastResponse(BaseModel):
    status: str
    initial_balance: float
    monthly_income: float
    projected_total_income: float
    projected_total_expense: float
    projected_net_savings: float
    savings_rate_pct: float
    final_projected_balance: float
    minimum_projected_balance: float
    health_status: str
    recommendation: str
    category_breakdown: Dict[str, Any]
    cash_flow_trajectory: List[Dict[str, Any]]


class MarketplaceRecommendRequest(BaseModel):
    monthly_income: float = Field(default=85000.0, gt=0)
    credit_score: int = Field(default=750, ge=300, le=900)
    persona_id: str = Field(default="YOUNG_TECH_PROFESSIONAL")
    spend_dining: float = Field(default=12000.0, ge=0)
    spend_shopping: float = Field(default=15000.0, ge=0)
    spend_groceries: float = Field(default=8000.0, ge=0)
    spend_travel: float = Field(default=6000.0, ge=0)
    spend_fuel: float = Field(default=3000.0, ge=0)
    spend_utilities: float = Field(default=5000.0, ge=0)
    liquid_savings: float = Field(default=350000.0, ge=0)
    existing_card_debt: float = Field(default=0.0, ge=0)
    top_k: int = Field(default=3, ge=1, le=10)


class MarketplaceRecommendResponse(BaseModel):
    status: str
    model_engine: str
    marketplace_recommendations_count: int
    total_projected_annual_value_inr: float
    top_recommendations: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# 6. Persona (Phase 17) & Subscriptions (Phase 14)
# ---------------------------------------------------------------------------

class PersonaSegmentRequest(BaseModel):
    monthly_income: float = Field(..., gt=0, example=120000.0)
    income_volatility_cv: float = Field(default=0.05, ge=0, le=2.0)
    monthly_essential_expenses: float = Field(default=35000.0, ge=0)
    monthly_discretionary_spend: float = Field(default=25000.0, ge=0)
    monthly_investments_sip: float = Field(default=30000.0, ge=0)
    existing_monthly_emi: float = Field(default=0.0, ge=0)
    total_credit_limit: float = Field(default=300000.0, ge=0)
    total_credit_used: float = Field(default=25000.0, ge=0)
    total_liquid_savings: float = Field(default=450000.0, ge=0)


class PersonaSegmentResponse(BaseModel):
    status: str
    model_engine: Optional[str] = None
    primary_persona: Dict[str, Any]
    soft_multi_persona_affinity_pct: Dict[str, float]
    behavioral_diagnostics: Dict[str, Any]
    tailored_platform_strategy: Dict[str, Any]


class SubscriptionDetectRequest(BaseModel):
    merchant_name: str = Field(..., example="Netflix India")
    amount: float = Field(..., gt=0, example=649.0)
    interval_mean_days: float = Field(default=30.0, gt=0)


class SubscriptionDetectResponse(BaseModel):
    status: str
    merchant: str
    amount: float
    is_subscription: bool
    confidence: float
    predicted_cadence: str
    projected_annual_cost: float


# ---------------------------------------------------------------------------
# 7. AI Copilot (Phase 19)
# ---------------------------------------------------------------------------

class CopilotAskRequest(BaseModel):
    user_query: str = Field(..., example="How can I save ₹1 Lakh in 6 months for a vacation?")
    monthly_income: Optional[float] = Field(75000.0)
    monthly_expenses: Optional[float] = Field(42000.0)
    current_balance: Optional[float] = Field(80000.0)
    credit_score: Optional[int] = Field(740)
    persona_id: Optional[str] = Field("YOUNG_TECH_PROFESSIONAL")


class CopilotAskResponse(BaseModel):
    status: str
    query: str
    ai_advisory: str
    deterministic_ml_context: Dict[str, Any]
    action_checklist: List[str]


class AffordabilityCheckRequest(BaseModel):
    item_name: str = Field(..., example="MacBook Pro M3")
    item_price_inr: float = Field(..., gt=0, example=114900.0)
    monthly_income: float = Field(..., gt=0, example=85000.0)
    monthly_expenses: float = Field(..., ge=0, example=45000.0)
    current_liquid_savings: float = Field(..., ge=0, example=150000.0)
    existing_monthly_emi: float = Field(default=0.0, ge=0)


class AffordabilityCheckResponse(BaseModel):
    status: str
    item_name: str
    item_price_inr: float
    verdict: str  # AFFORDABLE_CASH, AFFORDABLE_EMI, NOT_RECOMMENDED
    recommended_strategy: str
    impact_on_emergency_fund: Dict[str, Any]
    ai_copilot_advice: str
