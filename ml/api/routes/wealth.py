"""
Wealth: Investment Allocator (Phase 10), Goal Timeline (Phase 11), Marketplace Matchmaker (Phase 16) & Cash Flow Forecast (Phase 18) Routes.
"""

from fastapi import APIRouter, HTTPException
from api.schemas import (
    CashflowForecastRequest,
    CashflowForecastResponse,
    GoalTimelineRequest,
    GoalTimelineResponse,
    InvestmentRecommendRequest,
    InvestmentRecommendResponse,
    MarketplaceRecommendRequest,
    MarketplaceRecommendResponse,
)
from inference.predict_forecasting import predict_cash_flow
from inference.predict_goals import predict_goal_timeline
from inference.predict_investment import InvestmentRecommender
from inference.predict_recommendation import FinancialProductRecommenderEngine

router = APIRouter(prefix="/api/v1", tags=["Wealth, Goals & Smart Marketplace"])
investment_engine = InvestmentRecommender()
marketplace_engine = FinancialProductRecommenderEngine()


@router.post("/investments/recommend", response_model=InvestmentRecommendResponse)
def recommend_investment_portfolio(req: InvestmentRecommendRequest):
    """
    Computes simplex asset allocation (Equity, Debt, Gold, REITs, Cash) and compound wealth projections.
    """
    try:
        res = investment_engine.recommend(
            monthly_income=req.monthly_income,
            age=req.age,
            risk_profile=req.risk_profile,
            monthly_surplus=req.monthly_surplus,
            investment_horizon_years=req.investment_horizon_years,
            existing_savings=req.liquid_savings,
        )
        return InvestmentRecommendResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/goals/timeline", response_model=GoalTimelineResponse)
def predict_financial_goal_timeline(req: GoalTimelineRequest):
    """
    Predicts goal completion timeline and feasibility roadmap with accelerated SIP boosts.
    """
    try:
        res = predict_goal_timeline(
            goal_name=req.goal_name,
            target_amount=req.target_amount,
            current_saved=req.current_saved,
            monthly_income=req.monthly_income,
            monthly_expenses=req.monthly_expenses,
            intended_months=req.intended_months,
            expected_annual_return_pct=req.expected_annual_return_pct,
        )
        return GoalTimelineResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cashflow/forecast", response_model=CashflowForecastResponse)
def forecast_cash_flow_trajectory(req: CashflowForecastRequest):
    """
    Simulates forward 30-to-90 day account balance and cash flow trajectory.
    """
    try:
        res = predict_cash_flow(
            monthly_income=req.monthly_income,
            current_balance=req.current_balance,
            horizon_days=req.horizon_days,
            payday_of_month=req.payday_of_month,
        )
        return CashflowForecastResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marketplace/recommend", response_model=MarketplaceRecommendResponse)
def recommend_financial_products(req: MarketplaceRecommendRequest):
    """
    Ranks Credit Cards, High-Yield FDs, and Insurance with exact Net Annual Value (INR/yr).
    """
    try:
        res = marketplace_engine.recommend(
            monthly_income=req.monthly_income,
            credit_score=req.credit_score,
            persona_id=req.persona_id,
            spend_dining=req.spend_dining,
            spend_shopping=req.spend_shopping,
            spend_groceries=req.spend_groceries,
            spend_travel=req.spend_travel,
            spend_fuel=req.spend_fuel,
            spend_utilities=req.spend_utilities,
            liquid_savings=req.liquid_savings,
            existing_card_debt=req.existing_card_debt,
            top_k=req.top_k,
        )
        return MarketplaceRecommendResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
