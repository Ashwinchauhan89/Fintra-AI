"""
Financial Decision Simulation Engine.
Runs forward multi-month trajectory rollouts using the trained RL policy
and generates actionable, personalized financial strategies and analytics.
"""

import os
from collections import Counter
from typing import Any, Dict, List, Optional
import numpy as np

from ml.rl.environment import FinancialDecisionEnv, FinancialAction, ACTION_DESCRIPTIONS
from ml.rl.agent import DQNAgent

DEFAULT_MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../models/rl_financial_advisor.pt")
)


class FinancialDecisionSimulator:
    """
    Simulates multi-month financial trajectories using the RL policy
    and synthesizes actionable insights.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.agent = DQNAgent(state_dim=9, action_dim=6)
        self.is_model_loaded = False

        if os.path.exists(self.model_path):
            try:
                self.agent.load(self.model_path)
                self.is_model_loaded = True
            except Exception as e:
                print(f"Warning: Could not load RL weights from {self.model_path}: {e}")

    def simulate(
        self,
        income: float,
        expenses: float,
        savings: float,
        debt: float,
        investment: float,
        emergency_fund: Optional[float] = None,
        risk_tolerance: float = 0.6,
        financial_goal: Optional[float] = None,
        goal_progress: Optional[float] = None,
        simulation_period_months: int = 24,
    ) -> Dict[str, Any]:
        """
        Executes a multi-month simulation using the RL agent.
        """
        months = max(6, min(60, int(simulation_period_months)))
        emergency = emergency_fund if emergency_fund is not None else min(savings * 0.4, expenses * 3.0)
        goal = financial_goal if financial_goal is not None else max(500000.0, income * 10.0)

        initial_net_worth = savings + investment + emergency - debt
        calculated_progress = (
            goal_progress
            if goal_progress is not None
            else float(np.clip(max(0.0, initial_net_worth) / max(1.0, goal), 0.0, 1.0))
        )

        initial_state = {
            "income": float(income),
            "expenses": float(expenses),
            "savings": float(savings),
            "debt": float(debt),
            "investment": float(investment),
            "emergency_fund": float(emergency),
            "risk_tolerance": float(risk_tolerance),
            "financial_goal": float(goal),
            "goal_progress": float(calculated_progress),
        }

        env = FinancialDecisionEnv(initial_state=initial_state, max_months=months)
        obs, info = env.reset()

        trajectory: List[Dict[str, Any]] = []
        action_history: List[int] = []
        debt_free_month: Optional[int] = None
        goal_achieved_month: Optional[int] = None

        initial_health = info["health_score"]

        # Record Month 0 (Starting Baseline)
        trajectory.append(
            {
                "month": 0,
                "income": round(income),
                "expenses": round(expenses),
                "savings": round(savings),
                "debt": round(debt),
                "investment": round(investment),
                "emergency_fund": round(emergency),
                "net_worth": round(initial_net_worth),
                "goal_progress": round(calculated_progress, 4),
                "action_id": -1,
                "action_name": "Starting Baseline",
                "health_score": round(initial_health, 1),
                "reward": 0.0,
            }
        )

        # Multi-month rollout
        terminated = False
        step_idx = 0

        while not terminated and step_idx < months:
            step_idx += 1
            # RL Policy selects action
            action, q_vals = self.agent.select_action(obs, epsilon=0.0)

            # Rule safety guardrail: if debt > 0 and no model is loaded yet, prioritize debt paydown / emergency
            if not self.is_model_loaded:
                current_debt = env.state_raw["debt"]
                current_emergency = env.state_raw["emergency_fund"]
                if current_debt > 0 and current_debt > env.state_raw["income"] * 0.3:
                    action = int(FinancialAction.PAY_DOWN_DEBT)
                elif current_emergency < env.state_raw["expenses"] * 2.0:
                    action = int(FinancialAction.INCREASE_EMERGENCY_FUND)
                elif risk_tolerance > 0.5 and current_debt == 0:
                    action = int(FinancialAction.ADJUST_INVESTMENT_ALLOCATION)
                else:
                    action = int(FinancialAction.INCREASE_SAVINGS)

            obs, reward, terminated, truncated, step_info = env.step(action)
            action_history.append(action)

            raw = step_info["state_raw"]
            month_net_worth = raw["savings"] + raw["investment"] + raw["emergency_fund"] - raw["debt"]

            if (raw["debt"] <= 10.0 or round(raw["debt"]) == 0) and debt_free_month is None and debt > 0:
                debt_free_month = step_idx

            if raw["goal_progress"] >= 1.0 and goal_achieved_month is None:
                goal_achieved_month = step_idx

            trajectory.append(
                {
                    "month": step_idx,
                    "income": round(raw["income"]),
                    "expenses": round(raw["expenses"]),
                    "savings": round(raw["savings"]),
                    "debt": round(raw["debt"]),
                    "investment": round(raw["investment"]),
                    "emergency_fund": round(raw["emergency_fund"]),
                    "net_worth": round(month_net_worth),
                    "goal_progress": round(raw["goal_progress"], 4),
                    "action_id": action,
                    "action_name": step_info["action_name"],
                    "health_score": round(step_info["health_score"], 1),
                    "reward": round(reward, 2),
                }
            )

        final_raw = env.state_raw
        final_net_worth = (
            final_raw["savings"] + final_raw["investment"] + final_raw["emergency_fund"] - final_raw["debt"]
        )
        final_health = env._calculate_health_score()

        # Synthesize strategy summary
        recommended_strategy = self._synthesize_strategy(
            initial_state=initial_state,
            final_state=final_raw,
            action_history=action_history,
            debt_free_month=debt_free_month,
            months=months,
        )

        # Action Breakdown
        action_counts = Counter(action_history)
        action_breakdown = {
            ACTION_DESCRIPTIONS[FinancialAction(act_id)]: count
            for act_id, count in sorted(action_counts.items())
        }

        # Risk Indicators
        initial_runway = emergency / max(1.0, expenses)
        final_runway = final_raw["emergency_fund"] / max(1.0, final_raw["expenses"])
        initial_dti = debt / max(1.0, income * 12.0)
        final_dti = final_raw["debt"] / max(1.0, income * 12.0)

        risk_indicators = {
            "initial_emergency_runway_months": round(initial_runway, 1),
            "final_emergency_runway_months": round(final_runway, 1),
            "initial_debt_to_income_ratio": round(initial_dti, 3),
            "final_debt_to_income_ratio": round(final_dti, 3),
            "initial_health_score": round(initial_health, 1),
            "final_health_score": round(final_health, 1),
            "health_score_gain": round(final_health - initial_health, 1),
            "debt_free_month": debt_free_month,
            "goal_achieved_month": goal_achieved_month,
        }

        return {
            "recommended_strategy": recommended_strategy,
            "projected_savings": round(final_raw["savings"]),
            "projected_debt": round(final_raw["debt"]),
            "projected_investments": round(final_raw["investment"]),
            "projected_emergency_fund": round(final_raw["emergency_fund"]),
            "projected_net_worth": round(final_net_worth),
            "goal_progress": round(final_raw["goal_progress"], 2),
            "simulation_period_months": months,
            "monthly_trajectory": trajectory,
            "action_breakdown": action_breakdown,
            "risk_indicators": risk_indicators,
        }

    def _synthesize_strategy(
        self,
        initial_state: Dict[str, float],
        final_state: Dict[str, float],
        action_history: List[int],
        debt_free_month: Optional[int],
        months: int,
    ) -> str:
        """Constructs an executive recommendation sentence tailored to the policy actions taken."""
        counts = Counter(action_history)
        has_debt = initial_state["debt"] > 0
        cleared_debt = has_debt and (final_state["debt"] <= 10.0 or round(final_state["debt"]) == 0)

        # Direct canonical response pattern from Issue #54 when both savings are grown and debt is cleared
        if has_debt and cleared_debt and (
            counts.get(int(FinancialAction.INCREASE_SAVINGS), 0) >= 3
            or final_state["savings"] >= initial_state["savings"] * 1.5
        ):
            return "Increase savings and accelerate debt repayment"

        dominant_action = counts.most_common(1)[0][0] if counts else 0

        parts: List[str] = []

        if has_debt:
            if cleared_debt and debt_free_month:
                parts.append(f"Accelerate debt repayment to become completely debt-free by Month {debt_free_month}")
            else:
                parts.append("Aggressively curtail high-interest liabilities")

        if counts.get(int(FinancialAction.INCREASE_EMERGENCY_FUND), 0) > 2:
            parts.append("build a robust 6-month liquid emergency runway")

        if counts.get(int(FinancialAction.REDUCE_DISCRETIONARY_SPENDING), 0) > 2:
            parts.append("reduce discretionary expenditures by 18%")

        if counts.get(int(FinancialAction.ADJUST_INVESTMENT_ALLOCATION), 0) > 3 or (
            cleared_debt and months > (debt_free_month or 0)
        ):
            parts.append("reallocate freed cash flow into compounding diversified market investments")
        elif counts.get(int(FinancialAction.INCREASE_SAVINGS), 0) > 3:
            parts.append("increase high-yield savings buffer")

        if not parts:
            if has_debt and cleared_debt:
                return "Increase savings and accelerate debt repayment"
            elif dominant_action == int(FinancialAction.INCREASE_SAVINGS):
                return "Increase savings and build long-term liquid reserves"
            elif dominant_action == int(FinancialAction.ADJUST_INVESTMENT_ALLOCATION):
                return "Optimize multi-asset portfolio allocation to maximize compound returns"
            else:
                return "Maintain disciplined surplus allocation and sustain positive net cash flow"

        # Combine executive strategy
        if len(parts) == 1:
            return parts[0].capitalize()
        elif len(parts) == 2:
            return f"{parts[0].capitalize()} and {parts[1]}"
        else:
            return f"{parts[0].capitalize()}, {parts[1]}, and {parts[2]}"
