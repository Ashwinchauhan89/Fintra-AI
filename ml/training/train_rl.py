"""
Training Pipeline for Fintra-AI Reinforcement Learning Financial Decision Engine.
Trains Double-DQN Agent on simulated financial environments and saves model artifacts.
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List
import numpy as np

# Ensure root directory is in sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.rl.environment import FinancialDecisionEnv
from ml.rl.agent import DQNAgent

MODELS_DIR = os.path.join(REPO_ROOT, "ml/models")
DEFAULT_MODEL_PATH = os.path.join(MODELS_DIR, "rl_financial_advisor.pt")
DEFAULT_META_PATH = os.path.join(MODELS_DIR, "rl_metadata.json")


def train_rl_agent(
    episodes: int = 300,
    max_months_per_episode: int = 24,
    batch_size: int = 64,
    lr: float = 1e-3,
    epsilon_start: float = 1.0,
    epsilon_end: float = 0.05,
    epsilon_decay: float = 0.992,
    model_save_path: str = DEFAULT_MODEL_PATH,
    meta_save_path: str = DEFAULT_META_PATH,
) -> Dict:
    os.makedirs(MODELS_DIR, exist_ok=True)

    print("=" * 60)
    print(f"Starting RL Financial Decision Engine Training")
    print(f"Episodes: {episodes} | Max Months: {max_months_per_episode} | Batch Size: {batch_size}")
    print("=" * 60)

    env = FinancialDecisionEnv(max_months=max_months_per_episode)
    agent = DQNAgent(state_dim=9, action_dim=6, lr=lr, batch_size=batch_size)

    epsilon = epsilon_start
    episode_rewards: List[float] = []
    health_scores: List[float] = []
    losses: List[float] = []

    start_time = time.time()

    for ep in range(1, episodes + 1):
        obs, info = env.reset()
        ep_reward = 0.0
        ep_losses = []
        terminated = False

        while not terminated:
            action, _ = agent.select_action(obs, epsilon=epsilon)
            next_obs, reward, terminated, truncated, step_info = env.step(action)

            loss = agent.step(obs, action, reward, next_obs, terminated)
            if loss is not None:
                ep_losses.append(loss)

            obs = next_obs
            ep_reward += reward

        epsilon = max(epsilon_end, epsilon * epsilon_decay)
        episode_rewards.append(float(ep_reward))
        health_scores.append(float(step_info["health_score"]))
        if ep_losses:
            losses.append(float(np.mean(ep_losses)))

        if ep % 50 == 0 or ep == episodes:
            avg_rew = float(np.mean(episode_rewards[-50:]))
            avg_health = float(np.mean(health_scores[-50:]))
            avg_loss = float(np.mean(losses[-50:])) if losses else 0.0
            print(
                f"Episode {ep:4d}/{episodes} | "
                f"Reward (avg 50): {avg_rew:6.2f} | "
                f"Health Score: {avg_health:5.1f}/100 | "
                f"Loss: {avg_loss:.4f} | "
                f"Epsilon: {epsilon:.3f}"
            )

    elapsed_sec = time.time() - start_time
    print(f"\nTraining completed in {elapsed_sec:.2f} seconds.")

    # Save model weights
    agent.save(model_save_path)
    print(f"Saved trained RL model weights to: {model_save_path}")

    metadata = {
        "model_name": "Double-DQN Financial Decision Advisor",
        "algorithm": "Double DQN with Experience Replay",
        "framework": "PyTorch + Gymnasium",
        "state_dimension": 9,
        "action_dimension": 6,
        "episodes_trained": episodes,
        "max_months_per_episode": max_months_per_episode,
        "batch_size": batch_size,
        "learning_rate": lr,
        "final_average_reward": float(np.mean(episode_rewards[-50:])),
        "final_average_health_score": float(np.mean(health_scores[-50:])),
        "training_duration_seconds": round(elapsed_sec, 2),
        "actions_map": {
            0: "MAINTAIN_CURRENT_STRATEGY",
            1: "INCREASE_SAVINGS",
            2: "REDUCE_DISCRETIONARY_SPENDING",
            3: "PAY_DOWN_DEBT",
            4: "INCREASE_EMERGENCY_FUND",
            5: "ADJUST_INVESTMENT_ALLOCATION",
        },
    }

    with open(meta_save_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved RL model metadata to: {meta_save_path}")

    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RL Financial Decision Engine")
    parser.add_argument("--episodes", type=int, default=250, help="Number of training episodes")
    parser.add_argument("--months", type=int, default=24, help="Months per simulation episode")
    parser.add_argument("--batch-size", type=int, default=64, help="Mini-batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    args = parser.parse_args()

    train_rl_agent(
        episodes=args.episodes,
        max_months_per_episode=args.months,
        batch_size=args.batch_size,
        lr=args.lr,
    )
