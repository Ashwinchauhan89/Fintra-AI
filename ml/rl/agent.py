"""
PyTorch Deep Q-Network (DQN) Agent for Financial Decision Optimization.
Features Experience Replay, Double DQN Target Separation, and Layer-Normalized Policy Networks.
"""

import os
import random
from collections import deque
from typing import Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


class FinancialQNetwork(nn.Module):
    """
    Multi-layer Perceptron estimating state-action values Q(s, a).
    Equipped with LayerNorm for stable numerical convergence across diverse financial scales.
    """

    def __init__(self, state_dim: int = 9, action_dim: int = 6, hidden_dim: int = 128):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class ReplayBuffer:
    """Experience Replay Buffer for off-policy transition storage."""

    def __init__(self, capacity: int = 50000):
        self.buffer = deque(maxlen=capacity)

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(
        self, batch_size: int, device: torch.device
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states_t = torch.as_tensor(np.array(states), dtype=torch.float32, device=device)
        actions_t = torch.as_tensor(actions, dtype=torch.int64, device=device).unsqueeze(1)
        rewards_t = torch.as_tensor(rewards, dtype=torch.float32, device=device).unsqueeze(1)
        next_states_t = torch.as_tensor(np.array(next_states), dtype=torch.float32, device=device)
        dones_t = torch.as_tensor(dones, dtype=torch.float32, device=device).unsqueeze(1)

        return states_t, actions_t, rewards_t, next_states_t, dones_t

    def __len__(self) -> int:
        return len(self.buffer)


class DQNAgent:
    """
    Reinforcement Learning Agent implementing Double-DQN for financial action selection.
    """

    def __init__(
        self,
        state_dim: int = 9,
        action_dim: int = 6,
        gamma: float = 0.98,
        lr: float = 1e-3,
        batch_size: int = 64,
        replay_capacity: int = 50000,
        tau: float = 0.005,
        device: Optional[Union[str, torch.device]] = None,
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.batch_size = batch_size
        self.tau = tau

        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        # Policy and Target Networks
        self.policy_net = FinancialQNetwork(state_dim, action_dim).to(self.device)
        self.target_net = FinancialQNetwork(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.criterion = nn.SmoothL1Loss()  # Huber loss
        self.memory = ReplayBuffer(capacity=replay_capacity)

    def select_action(
        self,
        state: np.ndarray,
        epsilon: float = 0.0,
    ) -> Tuple[int, np.ndarray]:
        """
        Chooses an action using epsilon-greedy exploration.
        Returns the chosen action integer and the vector of Q-values.
        """
        if random.random() < epsilon:
            action = random.randrange(self.action_dim)
            # Dummy Q-values during pure random exploration
            q_vals = np.zeros(self.action_dim, dtype=np.float32)
            return action, q_vals

        self.policy_net.eval()
        with torch.no_grad():
            state_t = torch.as_tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
            q_values = self.policy_net(state_t).squeeze(0).cpu().numpy()
            action = int(np.argmax(q_values))

        return action, q_values

    def step(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> Optional[float]:
        """Adds experience to buffer and executes a training gradient update if ready."""
        self.memory.push(state, action, reward, next_state, done)

        if len(self.memory) >= self.batch_size:
            return self.train_step()
        return None

    def train_step(self) -> float:
        """Executes a single Double-DQN optimization step."""
        self.policy_net.train()

        states, actions, rewards, next_states, dones = self.memory.sample(
            self.batch_size, self.device
        )

        # Current Q-values
        current_q = self.policy_net(states).gather(1, actions)

        # Double DQN target computation:
        # 1. Action selection using Policy Network
        with torch.no_grad():
            next_state_actions = self.policy_net(next_states).argmax(dim=1, keepdim=True)
            # 2. Value evaluation using Target Network
            next_q = self.target_net(next_states).gather(1, next_state_actions)
            target_q = rewards + (1.0 - dones) * self.gamma * next_q

        loss = self.criterion(current_q, target_q)

        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping for training stability
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=1.0)
        self.optimizer.step()

        # Soft target network update
        self._soft_update()

        return float(loss.item())

    def _soft_update(self):
        """Polyak soft update: theta_target = tau * theta_policy + (1 - tau) * theta_target"""
        for target_param, policy_param in zip(
            self.target_net.parameters(), self.policy_net.parameters()
        ):
            target_param.data.copy_(
                self.tau * policy_param.data + (1.0 - self.tau) * target_param.data
            )

    def save(self, filepath: str):
        """Saves policy network weights."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        torch.save(
            {
                "policy_state_dict": self.policy_net.state_dict(),
                "target_state_dict": self.target_net.state_dict(),
                "state_dim": self.state_dim,
                "action_dim": self.action_dim,
            },
            filepath,
        )

    def load(self, filepath: str, map_location: Optional[Union[str, torch.device]] = None):
        """Loads policy network weights."""
        loc = map_location or self.device
        checkpoint = torch.load(filepath, map_location=loc)
        self.policy_net.load_state_dict(checkpoint["policy_state_dict"])
        self.target_net.load_state_dict(checkpoint.get("target_state_dict", checkpoint["policy_state_dict"]))
        self.policy_net.eval()
        self.target_net.eval()
