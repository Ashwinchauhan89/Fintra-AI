"""
Pydantic Schemas for Reinforcement Learning Financial Decision Engine (Issue #54).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RLSimulateRequest(BaseModel):
    income: float = Field(..., description="Monthly net income in currency units", example=60000.0)
    expenses: float = Field(..., description="Monthly total expenses in currency units", example=35000.0)
    savings: float = Field(..., description="Current liquid cash savings", example=150000.0)
    debt: float = Field(0.0, description="Total outstanding debt liabilities", example=50000.0)
    investment: float = Field(0.0, description="Current investment portfolio value", example=100000.0)
    emergency_fund: Optional[float] = Field(None, description="Dedicated liquid emergency reserves", example=50000.0)
    risk_tolerance: float = Field(0.6, ge=0.0, le=1.0, description="Risk tolerance between 0.0 (conservative) and 1.0 (aggressive)", example=0.6)
    financial_goal: Optional[float] = Field(None, description="Target financial goal amount", example=500000.0)
    goal_progress: Optional[float] = Field(None, ge=0.0, le=1.0, description="Current progress towards goal (0.0 to 1.0)", example=0.45)
    simulation_period_months: int = Field(24, ge=6, le=60, description="Simulation horizon in months (6 to 60)", example=24)


class RLTrajectoryPoint(BaseModel):
    month: int
    income: float
    expenses: float
    savings: float
    debt: float
    investment: float
    emergency_fund: float
    net_worth: float
    goal_progress: float
    action_id: int
    action_name: str
    health_score: float
    reward: float


class RLRiskIndicators(BaseModel):
    initial_emergency_runway_months: float
    final_emergency_runway_months: float
    initial_debt_to_income_ratio: float
    final_debt_to_income_ratio: float
    initial_health_score: float
    final_health_score: float
    health_score_gain: float
    debt_free_month: Optional[int] = None
    goal_achieved_month: Optional[int] = None


class RLSimulateResponse(BaseModel):
    status: str = "success"
    recommended_strategy: str = Field(..., description="Actionable executive strategy synthesized by RL policy")
    projected_savings: float = Field(..., description="Projected liquid savings balance at horizon end")
    projected_debt: float = Field(..., description="Projected remaining debt balance at horizon end")
    projected_investments: Optional[float] = Field(None, description="Projected investment portfolio value")
    projected_emergency_fund: Optional[float] = Field(None, description="Projected emergency buffer")
    projected_net_worth: Optional[float] = Field(None, description="Projected total net worth")
    goal_progress: float = Field(..., description="Final goal progress metric (0.0 to 1.0)")
    simulation_period_months: int = Field(..., description="Duration of simulation in months")
    monthly_trajectory: Optional[List[Dict[str, Any]]] = Field(None, description="Month-by-month financial state progression")
    action_breakdown: Optional[Dict[str, int]] = Field(None, description="Count of decisions across each action type")
    risk_indicators: Optional[Dict[str, Any]] = Field(None, description="Financial risk diagnostic indicators")


class RLInfoResponse(BaseModel):
    status: str = "success"
    model_name: str
    framework: str
    state_dimensions: int
    action_dimensions: int
    actions: Dict[int, str]
    weights_loaded: bool
    weights_path: str


class RLTrainRequest(BaseModel):
    episodes: int = Field(150, ge=20, le=1000, description="Number of episodes to train")
    months_per_episode: int = Field(24, ge=12, le=36, description="Months per simulated episode")


class RLTrainResponse(BaseModel):
    status: str = "success"
    message: str
    metadata: Dict[str, Any]
