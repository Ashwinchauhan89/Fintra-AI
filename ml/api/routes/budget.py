"""
Budgeting (Phase 5), Savings Projector (Phase 6) & Financial Health Score (Phase 7) Routes.
"""

from fastapi import APIRouter, HTTPException
from api.schemas import (
    BudgetRecommendRequest,
    BudgetRecommendResponse,
    HealthScoreRequest,
    HealthScoreResponse,
    SavingsProjectRequest,
    SavingsProjectResponse,
)
from inference.predict_budget import (
    calculate_financial_health_score,
    recommend_budget,
)
from inference.predict_goals import predict_savings_growth

router = APIRouter(prefix="/api/v1", tags=["Budget, Savings & Health Score"])


@router.post("/budget/recommend", response_model=BudgetRecommendResponse)
def get_budget_recommendations(req: BudgetRecommendRequest):
    """
    Computes 50/30/20 budget allocations and category breakdowns tailored to user lifestyle.
    """
    try:
        res = recommend_budget(
            monthly_income=req.monthly_income,
            lifestyle=req.lifestyle,
            savings_target_pct=req.savings_target_pct,
            historical_expenses=req.historical_expenses,
            debt_obligations=req.debt_obligations,
        )
        return BudgetRecommendResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/savings/project", response_model=SavingsProjectResponse)
def project_savings_growth(req: SavingsProjectRequest):
    """
    Predicts monthly savings capacity and multi-year compound wealth growth.
    """
    try:
        res = predict_savings_growth(
            monthly_income=req.monthly_income,
            monthly_expenses=req.monthly_expenses,
            debt_obligations=req.debt_obligations,
            current_balance=req.current_balance,
            expected_annual_return_pct=req.expected_annual_return_pct,
        )
        return SavingsProjectResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health-score/diagnose", response_model=HealthScoreResponse)
def diagnose_financial_health(req: HealthScoreRequest):
    """
    Calculates 0-100 composite Financial Health Score with 5-pillar diagnostics.
    """
    try:
        res = calculate_financial_health_score(
            monthly_income=req.monthly_income,
            current_balance=req.current_balance,
            monthly_expenses=req.monthly_expenses,
            debt_obligations=req.debt_obligations,
        )
        return HealthScoreResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
