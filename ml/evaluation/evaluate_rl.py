"""
Evaluation and Benchmarking Script for RL Financial Decision Engine.
Benchmarks the trained RL policy against standard financial heuristics.
"""

import os
import sys
from typing import Dict, List
import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.rl.environment import FinancialDecisionEnv, FinancialAction
from ml.rl.agent import DQNAgent

DEFAULT_MODEL_PATH = os.path.join(REPO_ROOT, "ml/models/rl_financial_advisor.pt")


def evaluate_policy(policy_type: str, agent: DQNAgent, num_scenarios: int = 50, months: int = 24) -> Dict:
    env = FinancialDecisionEnv(max_months=months)
    rewards: List[float] = []
    final_health_scores: List[float] = []
    net_worth_growths: List[float] = []
    debt_cleared_count = 0
    total_had_debt = 0

    for seed in range(num_scenarios):
        obs, info = env.reset(seed=seed + 1000)
        initial_had_debt = env.state_raw["debt"] > 0
        if initial_had_debt:
            total_had_debt += 1

        initial_nw = (
            env.state_raw["savings"]
            + env.state_raw["investment"]
            + env.state_raw["emergency_fund"]
            - env.state_raw["debt"]
        )

        ep_rew = 0.0
        terminated = False

        while not terminated:
            if policy_type == "rl":
                action, _ = agent.select_action(obs, epsilon=0.0)
            elif policy_type == "naive_maintain":
                action = int(FinancialAction.MAINTAIN_CURRENT_STRATEGY)
            elif policy_type == "random":
                action = int(env.action_space.sample())
            elif policy_type == "heuristic_rule":
                # Standard financial advice: pay debt if exists, else build emergency, else invest
                if env.state_raw["debt"] > 0:
                    action = int(FinancialAction.PAY_DOWN_DEBT)
                elif env.state_raw["emergency_fund"] < env.state_raw["expenses"] * 3.0:
                    action = int(FinancialAction.INCREASE_EMERGENCY_FUND)
                else:
                    action = int(FinancialAction.ADJUST_INVESTMENT_ALLOCATION)
            else:
                action = 0

            obs, reward, terminated, _, step_info = env.step(action)
            ep_rew += reward

        rewards.append(ep_rew)
        final_health_scores.append(step_info["health_score"])

        final_nw = step_info["net_worth"]
        if initial_nw > 0:
            growth = (final_nw - initial_nw) / initial_nw
            net_worth_growths.append(growth)

        if initial_had_debt and step_info["state_raw"]["debt"] == 0.0:
            debt_cleared_count += 1

    debt_clear_rate = (debt_cleared_count / total_had_debt * 100.0) if total_had_debt > 0 else 100.0

    return {
        "policy": policy_type,
        "avg_cumulative_reward": round(float(np.mean(rewards)), 2),
        "avg_final_health_score": round(float(np.mean(final_health_scores)), 1),
        "avg_net_worth_growth_pct": round(float(np.mean(net_worth_growths) * 100.0), 1) if net_worth_growths else 0.0,
        "debt_clearance_rate_pct": round(debt_clear_rate, 1),
    }


def run_benchmark():
    print("=" * 65)
    print("RL Financial Decision Engine Policy Benchmark")
    print("=" * 65)

    agent = DQNAgent(state_dim=9, action_dim=6)
    if os.path.exists(DEFAULT_MODEL_PATH):
        agent.load(DEFAULT_MODEL_PATH)
        print(f"Loaded trained policy: {DEFAULT_MODEL_PATH}")
    else:
        print("Warning: Trained weights not found. Evaluating initialized agent.")

    policies = ["random", "naive_maintain", "heuristic_rule", "rl"]
    results = []

    for p in policies:
        res = evaluate_policy(p, agent, num_scenarios=50, months=24)
        results.append(res)

    print(f"\n{'Policy':<18} | {'Avg Reward':<12} | {'Health Score':<12} | {'NW Growth %':<12} | {'Debt Clear %':<12}")
    print("-" * 75)
    for r in results:
        print(
            f"{r['policy']:<18} | {r['avg_cumulative_reward']:<12.2f} | "
            f"{r['avg_final_health_score']:<12.1f} | {r['avg_net_worth_growth_pct']:<12.1f} | "
            f"{r['debt_clearance_rate_pct']:<12.1f}"
        )


if __name__ == "__main__":
    run_benchmark()
