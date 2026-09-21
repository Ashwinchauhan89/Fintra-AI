"""
Gymnasium Reinforcement Learning Environment for Financial Decision Making.
Implements multi-objective financial state evolution, discrete actions,
and sustainable long-term financial health reward formulations.
"""

from enum import IntEnum
from typing import Any, Dict, Optional, Tuple
import numpy as np
import gymnasium as gym
from gymnasium import spaces


class FinancialAction(IntEnum):
    MAINTAIN_CURRENT_STRATEGY = 0
    INCREASE_SAVINGS = 1
    REDUCE_DISCRETIONARY_SPENDING = 2
    PAY_DOWN_DEBT = 3
    INCREASE_EMERGENCY_FUND = 4
    ADJUST_INVESTMENT_ALLOCATION = 5


ACTION_DESCRIPTIONS = {
    FinancialAction.MAINTAIN_CURRENT_STRATEGY: "Maintain current balanced cash flow allocation",
    FinancialAction.INCREASE_SAVINGS: "Direct surplus primarily into high-yield liquid savings",
    FinancialAction.REDUCE_DISCRETIONARY_SPENDING: "Curtail discretionary expenditures to maximize investable cash flow",
    FinancialAction.PAY_DOWN_DEBT: "Aggressively pay down high-interest liabilities (Avalanche/Snowball)",
    FinancialAction.INCREASE_EMERGENCY_FUND: "Channel capital into dedicated liquid emergency reserves (3-6 mo buffer)",
    FinancialAction.ADJUST_INVESTMENT_ALLOCATION: "Optimize multi-asset portfolio allocation to accelerate compounding growth",
}


class FinancialDecisionEnv(gym.Env):
    """
    Financial Simulation Environment adhering to the Gymnasium Env interface.
    Each episode represents a series of months (e.g., 12 to 36 months) of financial decisions.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        initial_state: Optional[Dict[str, float]] = None,
        max_months: int = 24,
        seed: Optional[int] = None,
    ):
        super().__init__()

        self.max_months = max_months
        self.initial_state_config = initial_state or {}

        # 9 Continuous State Features, normalized in [0, 1]
        # [income_norm, expenses_ratio, savings_ratio, debt_ratio,
        #  investment_ratio, emergency_runway_ratio, risk_tolerance, goal_ratio, goal_progress]
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(9,),
            dtype=np.float32,
        )

        # 6 Discrete Strategy Actions
        self.action_space = spaces.Discrete(6)

        # Economic Assumptions
        self.annual_debt_interest_rate = 0.14  # 14% p.a. on debt
        self.annual_savings_interest_rate = 0.045  # 4.5% p.a. on cash savings
        self.annual_equity_expected_return = 0.12  # 12% p.a. base market return
        self.annual_debt_fund_return = 0.07  # 7% p.a. fixed income

        self.current_step = 0
        self.state_raw: Dict[str, float] = {}
        self.np_random = np.random.default_rng(seed)

    def _normalize_state(self, raw: Dict[str, float]) -> np.ndarray:
        """Converts raw rupee values into a bounded [0, 1] observation vector."""
        income = max(1000.0, raw.get("income", 50000.0))
        expenses = max(0.0, raw.get("expenses", 30000.0))
        savings = max(0.0, raw.get("savings", 50000.0))
        debt = max(0.0, raw.get("debt", 0.0))
        investment = max(0.0, raw.get("investment", 20000.0))
        emergency_fund = max(0.0, raw.get("emergency_fund", 20000.0))
        risk_tolerance = float(np.clip(raw.get("risk_tolerance", 0.5), 0.0, 1.0))
        goal_target = max(1000.0, raw.get("financial_goal", 500000.0))
        goal_progress = float(np.clip(raw.get("goal_progress", 0.0), 0.0, 1.0))

        # Normalized features
        income_norm = float(np.clip(income / 200000.0, 0.0, 1.0))
        expenses_ratio = float(np.clip(expenses / income, 0.0, 1.0))
        savings_ratio = float(np.clip(savings / max(1000.0, 6.0 * expenses), 0.0, 1.0))
        debt_ratio = float(np.clip(debt / max(1000.0, 12.0 * income), 0.0, 1.0))
        investment_ratio = float(np.clip(investment / max(1000.0, 10.0 * income), 0.0, 1.0))
        emergency_runway = float(np.clip(emergency_fund / max(1000.0, 6.0 * expenses), 0.0, 1.0))
        goal_ratio = float(np.clip(goal_target / max(1000.0, 10.0 * income), 0.0, 1.0))

        obs = np.array(
            [
                income_norm,
                expenses_ratio,
                savings_ratio,
                debt_ratio,
                investment_ratio,
                emergency_runway,
                risk_tolerance,
                goal_ratio,
                goal_progress,
            ],
            dtype=np.float32,
        )
        return obs

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        if seed is not None:
            self.np_random = np.random.default_rng(seed)

        self.current_step = 0

        # Use passed options or pre-configured state or generate realistic scenario
        config = (options or {}).get("initial_state") or self.initial_state_config

        if config:
            self.state_raw = {
                "income": float(config.get("income", 60000.0)),
                "expenses": float(config.get("expenses", 35000.0)),
                "savings": float(config.get("savings", 150000.0)),
                "debt": float(config.get("debt", 50000.0)),
                "investment": float(config.get("investment", 100000.0)),
                "emergency_fund": float(
                    config.get("emergency_fund", min(config.get("savings", 150000.0) * 0.4, 60000.0))
                ),
                "risk_tolerance": float(config.get("risk_tolerance", 0.6)),
                "financial_goal": float(config.get("financial_goal", 500000.0)),
                "goal_progress": float(config.get("goal_progress", 0.45)),
            }
        else:
            # Random synthetic profile for training
            income = float(self.np_random.uniform(35000.0, 150000.0))
            expense_rate = float(self.np_random.uniform(0.45, 0.75))
            expenses = income * expense_rate
            has_debt = bool(self.np_random.random() < 0.60)
            # Keep synthetic debt achievable within 24 months (0.2x to 1.5x monthly income)
            debt = float(self.np_random.uniform(income * 0.2, income * 1.5)) if has_debt else 0.0
            savings = float(self.np_random.uniform(10000.0, income * 2.5))
            emergency_fund = min(savings * float(self.np_random.uniform(0.2, 0.7)), expenses * 6.0)
            investment = float(self.np_random.uniform(0.0, income * 2.0))
            risk_tolerance = float(self.np_random.uniform(0.2, 0.9))
            goal = float(self.np_random.uniform(200000.0, 1200000.0))
            current_net_worth = max(0.0, savings + investment - debt)
            goal_progress = float(np.clip(current_net_worth / goal, 0.0, 0.95))

            self.state_raw = {
                "income": income,
                "expenses": expenses,
                "savings": savings,
                "debt": debt,
                "investment": investment,
                "emergency_fund": emergency_fund,
                "risk_tolerance": risk_tolerance,
                "financial_goal": goal,
                "goal_progress": goal_progress,
            }

        obs = self._normalize_state(self.state_raw)
        info = {"month": 0, "state_raw": dict(self.state_raw), "health_score": self._calculate_health_score()}
        return obs, info

    def _calculate_health_score(self) -> float:
        """Computes comprehensive 0-100 financial health index."""
        income = max(1.0, self.state_raw["income"])
        expenses = max(1.0, self.state_raw["expenses"])
        savings = self.state_raw["savings"]
        debt = self.state_raw["debt"]
        investments = self.state_raw["investment"]
        emergency = self.state_raw["emergency_fund"]

        # 1. Emergency Runway (up to 30 pts)
        runway_months = emergency / expenses
        score_runway = min(30.0, (runway_months / 6.0) * 30.0)

        # 2. Debt Burden (up to 25 pts)
        dti = debt / (income * 12.0)
        if dti <= 0.0:
            score_debt = 25.0
        elif dti < 0.2:
            score_debt = 20.0
        elif dti < 0.5:
            score_debt = 10.0
        else:
            score_debt = max(0.0, 25.0 - (dti * 30.0))

        # 3. Savings & Wealth Accumulation (up to 25 pts)
        wealth_ratio = (savings + investments) / (income * 6.0)
        score_wealth = min(25.0, wealth_ratio * 25.0)

        # 4. Cash Flow Surplus Margin (up to 20 pts)
        surplus_ratio = max(0.0, (income - expenses) / income)
        score_surplus = min(20.0, (surplus_ratio / 0.3) * 20.0)

        return float(np.clip(score_runway + score_debt + score_wealth + score_surplus, 0.0, 100.0))

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        self.current_step += 1
        action = int(action)

        prev_health = self._calculate_health_score()
        prev_debt = self.state_raw["debt"]
        prev_savings = self.state_raw["savings"]
        prev_investment = self.state_raw["investment"]
        prev_emergency = self.state_raw["emergency_fund"]
        prev_net_worth = prev_savings + prev_investment + prev_emergency - prev_debt

        income = self.state_raw["income"]
        base_expenses = self.state_raw["expenses"]
        debt = self.state_raw["debt"]
        savings = self.state_raw["savings"]
        investment = self.state_raw["investment"]
        emergency_fund = self.state_raw["emergency_fund"]
        risk_tol = self.state_raw["risk_tolerance"]
        goal = self.state_raw["financial_goal"]

        # Action execution
        current_expenses = base_expenses
        expense_reduction_bonus = 0.0

        if action == FinancialAction.REDUCE_DISCRETIONARY_SPENDING:
            # Cut discretionary expenses by 18%
            current_expenses = base_expenses * 0.82
            expense_reduction_bonus = 0.5

        # Monthly surplus
        surplus = max(0.0, income - current_expenses)

        # Capital Allocation based on Action
        debt_payment = 0.0
        savings_alloc = 0.0
        investment_alloc = 0.0
        emergency_alloc = 0.0

        if action == FinancialAction.PAY_DOWN_DEBT:
            if debt > 0:
                debt_payment = min(debt, surplus * 0.90)
                rem = surplus - debt_payment
                emergency_alloc = rem * 0.50
                savings_alloc = rem * 0.50
            else:
                # Debt already 0, redirect to investments
                investment_alloc = surplus * 0.65
                savings_alloc = surplus * 0.35

        elif action == FinancialAction.INCREASE_EMERGENCY_FUND:
            target_buffer = current_expenses * 6.0
            needed = max(0.0, target_buffer - emergency_fund)
            emergency_alloc = min(needed, surplus * 0.80) if needed > 0 else surplus * 0.30
            rem = surplus - emergency_alloc
            if debt > 0:
                debt_payment = min(debt, rem * 0.50)
                savings_alloc = rem - debt_payment
            else:
                savings_alloc = rem * 0.60
                investment_alloc = rem * 0.40

        elif action == FinancialAction.INCREASE_SAVINGS:
            savings_alloc = surplus * 0.70
            rem = surplus * 0.30
            if debt > 0:
                debt_payment = min(debt, rem * 0.60)
                investment_alloc = rem - debt_payment
            else:
                investment_alloc = rem

        elif action == FinancialAction.ADJUST_INVESTMENT_ALLOCATION:
            # Check if emergency runway is critically low first
            if emergency_fund < current_expenses * 2.0:
                emergency_alloc = surplus * 0.40
                investment_alloc = surplus * 0.40
                savings_alloc = surplus * 0.20
            else:
                investment_alloc = surplus * 0.75
                savings_alloc = surplus * 0.25

        elif action == FinancialAction.REDUCE_DISCRETIONARY_SPENDING:
            # Balanced distribution of higher surplus
            if debt > 0:
                debt_payment = min(debt, surplus * 0.55)
                rem = surplus - debt_payment
                emergency_alloc = rem * 0.35
                investment_alloc = rem * 0.35
                savings_alloc = rem * 0.30
            else:
                investment_alloc = surplus * 0.50
                emergency_alloc = surplus * 0.25
                savings_alloc = surplus * 0.25

        else:  # MAINTAIN_CURRENT_STRATEGY
            if debt > 0:
                debt_payment = min(debt, surplus * 0.40)
                rem = surplus - debt_payment
                savings_alloc = rem * 0.40
                investment_alloc = rem * 0.35
                emergency_alloc = rem * 0.25
            else:
                savings_alloc = surplus * 0.45
                investment_alloc = surplus * 0.35
                emergency_alloc = surplus * 0.20

        # Apply interest & investment returns
        # 1. Debt accrues monthly interest, then gets reduced by debt_payment
        monthly_debt_rate = self.annual_debt_interest_rate / 12.0
        new_debt = max(0.0, (debt * (1.0 + monthly_debt_rate)) - debt_payment)
        if new_debt <= 10.0:
            new_debt = 0.0

        # 2. Savings accrues modest risk-free interest
        monthly_savings_rate = self.annual_savings_interest_rate / 12.0
        new_savings = (savings * (1.0 + monthly_savings_rate)) + savings_alloc

        # 3. Emergency fund is cash liquid
        new_emergency = (emergency_fund * (1.0 + monthly_savings_rate)) + emergency_alloc

        # 4. Investment expected return weighted by user risk tolerance
        portfolio_annual_return = (
            risk_tol * self.annual_equity_expected_return
            + (1.0 - risk_tol) * self.annual_debt_fund_return
        )
        # Small realistic monthly return variation
        market_shock = float(self.np_random.normal(0.0, 0.015 * risk_tol))
        monthly_inv_rate = (portfolio_annual_return / 12.0) + market_shock
        new_investment = max(0.0, (investment * (1.0 + monthly_inv_rate)) + investment_alloc)

        # Update Net Worth & Goal Progress
        new_net_worth = new_savings + new_investment + new_emergency - new_debt
        goal_progress = float(np.clip(max(0.0, new_net_worth) / max(1.0, goal), 0.0, 1.0))

        # Store updated raw state
        self.state_raw.update(
            {
                "expenses": current_expenses,
                "debt": float(new_debt),
                "savings": float(new_savings),
                "investment": float(new_investment),
                "emergency_fund": float(new_emergency),
                "goal_progress": goal_progress,
            }
        )

        new_health = self._calculate_health_score()

        # --- MULTI-OBJECTIVE REWARD FUNCTION ---
        # 1. Savings & Investment Capital Growth
        savings_growth = (new_savings + new_investment - prev_savings - prev_investment) / max(1.0, income)
        r_savings = float(np.clip(savings_growth * 2.0, -1.0, 3.0))

        # 2. Debt Reduction Reward (Prioritizes eliminating high-interest liabilities)
        debt_paid_down = prev_debt - new_debt
        if prev_debt > 0:
            debt_reduction_ratio = debt_paid_down / max(1.0, income)
            r_debt = float(debt_reduction_ratio * 4.5)
            if new_debt == 0.0 and prev_debt > 0:
                r_debt += 4.0  # Milestone bonus for reaching debt freedom!
        else:
            r_debt = 1.0  # Maintaining zero debt

        # 3. Goal Progress Reward
        goal_delta = goal_progress - (prev_net_worth / max(1.0, goal))
        r_goal = float(np.clip(goal_delta * 4.0, -0.5, 2.0))

        # 4. Emergency Fund Health (Prioritize 3-6 months runway)
        runway_months = new_emergency / max(1.0, current_expenses)
        if runway_months < 1.0:
            r_emergency = -2.0  # Severe risk penalty
        elif runway_months < 3.0:
            r_emergency = 0.5
        elif 3.0 <= runway_months <= 6.0:
            r_emergency = 2.0  # Optimal safe runway
        else:
            r_emergency = 1.0  # Safe, but avoid excessive cash drag

        # 5. Financial Risk Penalty
        risk_penalty = 0.0
        if new_debt > 0:
            # Penalize reckless aggressive investing while in toxic debt
            if action == FinancialAction.ADJUST_INVESTMENT_ALLOCATION:
                risk_penalty += 3.0
            risk_penalty += min(2.5, (new_debt / max(1.0, income)) * 1.5)

        if runway_months < 1.0:
            risk_penalty += 2.0

        # 6. Holistic Health Score Change
        r_health_delta = (new_health - prev_health) * 0.1

        # Total Composite Sustainable Reward
        total_reward = float(
            (1.5 * r_savings)
            + (2.5 * r_debt)
            + (1.0 * r_goal)
            + (1.2 * r_emergency)
            + (1.0 * r_health_delta)
            + expense_reduction_bonus
            - risk_penalty
        )

        terminated = bool(self.current_step >= self.max_months)
        truncated = False

        obs = self._normalize_state(self.state_raw)
        info = {
            "month": self.current_step,
            "action": action,
            "action_name": ACTION_DESCRIPTIONS[FinancialAction(action)],
            "state_raw": dict(self.state_raw),
            "health_score": new_health,
            "reward_components": {
                "r_savings": r_savings,
                "r_debt": r_debt,
                "r_goal": r_goal,
                "r_emergency": r_emergency,
                "risk_penalty": risk_penalty,
            },
            "net_worth": new_net_worth,
            "debt_free": bool(new_debt == 0.0),
        }

        return obs, total_reward, terminated, truncated, info
