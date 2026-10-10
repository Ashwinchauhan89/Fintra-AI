"""
REST Endpoints for Reinforcement Learning Financial Decision Engine (Issue #54).
Exposes simulation, strategy formulation, model diagnostics, and training triggers.
"""

import os
import sys
from fastapi import APIRouter, Depends, HTTPException, status

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.app.core.security import rate_limit
from backend.app.schemas.rl import (
    RLSimulateRequest,
    RLSimulateResponse,
    RLInfoResponse,
    RLTrainRequest,
    RLTrainResponse,
)

router = APIRouter(dependencies=[Depends(rate_limit(rate=100, window=60))])


@router.post(
    "/simulate",
    response_model=RLSimulateResponse,
    summary="Simulate Financial Decision Trajectory via RL",
    description=(
        "Simulates multi-month financial decisions using a trained Deep Q-Network agent in Gymnasium. "
        "Returns recommended strategies, projected wealth, debt paydown milestones, and month-by-month trajectory."
    ),
)
def simulate_financial_decisions(payload: RLSimulateRequest):
    try:
        from ml.rl.simulator import FinancialDecisionSimulator

        simulator = FinancialDecisionSimulator()
        result = simulator.simulate(
            income=payload.income,
            expenses=payload.expenses,
            savings=payload.savings,
            debt=payload.debt,
            investment=payload.investment,
            emergency_fund=payload.emergency_fund,
            risk_tolerance=payload.risk_tolerance,
            financial_goal=payload.financial_goal,
            goal_progress=payload.goal_progress,
            simulation_period_months=payload.simulation_period_months,
        )

        return RLSimulateResponse(
            status="success",
            recommended_strategy=result["recommended_strategy"],
            projected_savings=result["projected_savings"],
            projected_debt=result["projected_debt"],
            projected_investments=result["projected_investments"],
            projected_emergency_fund=result["projected_emergency_fund"],
            projected_net_worth=result["projected_net_worth"],
            goal_progress=result["goal_progress"],
            simulation_period_months=result["simulation_period_months"],
            monthly_trajectory=result["monthly_trajectory"],
            action_breakdown=result["action_breakdown"],
            risk_indicators=result["risk_indicators"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RL simulation execution failed: {str(exc)}",
        )


@router.get(
    "/info",
    response_model=RLInfoResponse,
    summary="Get RL Model Metadata & Action Space",
    description="Returns metadata about the Gymnasium environment, neural architecture, and discrete action mapping.",
)
def get_rl_engine_info():
    try:
        from ml.rl.environment import FinancialAction, ACTION_DESCRIPTIONS
        from ml.rl.simulator import DEFAULT_MODEL_PATH

        weights_exist = os.path.exists(DEFAULT_MODEL_PATH)
        actions = {int(act): ACTION_DESCRIPTIONS[act] for act in FinancialAction}

        return RLInfoResponse(
            status="success",
            model_name="Double-DQN Financial Decision Advisor",
            framework="PyTorch + Gymnasium",
            state_dimensions=9,
            action_dimensions=6,
            actions=actions,
            weights_loaded=weights_exist,
            weights_path=DEFAULT_MODEL_PATH,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve RL metadata: {str(exc)}",
        )


@router.post(
    "/train",
    response_model=RLTrainResponse,
    summary="Trigger RL Agent Retraining",
    description="Executes training episodes to update the Double-DQN policy network on simulated financial scenarios.",
)
def train_rl_engine(payload: RLTrainRequest):
    try:
        from ml.training.train_rl import train_rl_agent

        meta = train_rl_agent(
            episodes=payload.episodes,
            max_months_per_episode=payload.months_per_episode,
        )

        return RLTrainResponse(
            status="success",
            message=f"Successfully trained RL agent across {payload.episodes} episodes",
            metadata=meta,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RL training failed: {str(exc)}",
        )
