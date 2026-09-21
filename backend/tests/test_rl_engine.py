"""
Comprehensive Unit and Integration Tests for RL Financial Decision Engine.
Verifies Gymnasium Environment, PyTorch DQNAgent, Simulator rollouts, and FastAPI endpoints.
"""

import os
import sys
import unittest
import numpy as np
import torch
from fastapi.testclient import TestClient

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.rl.environment import FinancialDecisionEnv, FinancialAction
from ml.rl.agent import DQNAgent, FinancialQNetwork, ReplayBuffer
from ml.rl.simulator import FinancialDecisionSimulator
from backend.app.schemas.rl import RLSimulateRequest, RLSimulateResponse
from backend.app.main import app


class TestGymnasiumFinancialEnvironment(unittest.TestCase):
    """Tests the Gymnasium Environment observation space, action execution, and reward formulation."""

    def setUp(self):
        self.initial_state = {
            "income": 60000.0,
            "expenses": 35000.0,
            "savings": 150000.0,
            "debt": 50000.0,
            "investment": 100000.0,
            "emergency_fund": 40000.0,
            "risk_tolerance": 0.6,
            "financial_goal": 500000.0,
            "goal_progress": 0.45,
        }
        self.env = FinancialDecisionEnv(initial_state=self.initial_state, max_months=12)

    def test_environment_spaces(self):
        self.assertEqual(self.env.observation_space.shape, (9,))
        self.assertEqual(self.env.action_space.n, 6)

    def test_reset_returns_valid_observation(self):
        obs, info = self.env.reset()
        self.assertEqual(obs.shape, (9,))
        self.assertTrue(np.all(obs >= 0.0) and np.all(obs <= 1.0))
        self.assertIn("health_score", info)
        self.assertGreater(info["health_score"], 0)

    def test_step_execution_and_debt_paydown(self):
        self.env.reset()
        initial_debt = self.env.state_raw["debt"]
        obs, reward, terminated, truncated, info = self.env.step(int(FinancialAction.PAY_DOWN_DEBT))

        self.assertLess(info["state_raw"]["debt"], initial_debt)
        self.assertIsInstance(reward, float)
        self.assertFalse(terminated)

    def test_multi_month_termination(self):
        self.env.reset()
        for i in range(12):
            _, _, terminated, _, _ = self.env.step(int(FinancialAction.MAINTAIN_CURRENT_STRATEGY))
        self.assertTrue(terminated)


class TestPyTorchDQNAgent(unittest.TestCase):
    """Tests PyTorch QNetwork architecture, experience replay, and double DQN optimization."""

    def setUp(self):
        self.agent = DQNAgent(state_dim=9, action_dim=6, batch_size=16)

    def test_network_forward_pass(self):
        dummy_state = np.random.uniform(0.0, 1.0, size=(9,)).astype(np.float32)
        action, q_values = self.agent.select_action(dummy_state, epsilon=0.0)

        self.assertIn(action, range(6))
        self.assertEqual(len(q_values), 6)

    def test_replay_buffer_and_train_step(self):
        buffer = ReplayBuffer(capacity=100)
        state = np.zeros(9, dtype=np.float32)
        next_state = np.ones(9, dtype=np.float32)

        for _ in range(25):
            buffer.push(state, 1, 1.5, next_state, False)
            self.agent.memory.push(state, 1, 1.5, next_state, False)

        self.assertEqual(len(buffer), 25)
        loss = self.agent.train_step()
        self.assertIsInstance(loss, float)
        self.assertGreaterEqual(loss, 0.0)


class TestFinancialSimulatorRollouts(unittest.TestCase):
    """Verifies end-to-end multi-month rollout simulations across multiple user archetypes."""

    def setUp(self):
        self.simulator = FinancialDecisionSimulator()

    def test_simulation_matching_issue_54(self):
        # Specific test input payload from Issue #54
        result = self.simulator.simulate(
            income=60000.0,
            expenses=35000.0,
            savings=150000.0,
            debt=50000.0,
            investment=100000.0,
            risk_tolerance=0.6,
            goal_progress=0.45,
            simulation_period_months=24,
        )

        self.assertIn("recommended_strategy", result)
        self.assertIsInstance(result["recommended_strategy"], str)
        self.assertGreater(len(result["recommended_strategy"]), 10)

        self.assertIn("projected_savings", result)
        self.assertIn("projected_debt", result)
        self.assertIn("goal_progress", result)
        self.assertEqual(result["simulation_period_months"], 24)

        # Monthly trajectory checks
        trajectory = result["monthly_trajectory"]
        self.assertEqual(len(trajectory), 25)  # Month 0 to 24
        self.assertEqual(trajectory[0]["month"], 0)
        self.assertEqual(trajectory[24]["month"], 24)

        # Action breakdown checks
        self.assertIsInstance(result["action_breakdown"], dict)
        self.assertIn("risk_indicators", result)

    def test_high_debt_archetype(self):
        result = self.simulator.simulate(
            income=45000.0,
            expenses=30000.0,
            savings=15000.0,
            debt=120000.0,
            investment=0.0,
            simulation_period_months=24,
        )
        self.assertLess(result["projected_debt"], 120000.0)
        self.assertGreater(result["risk_indicators"]["health_score_gain"], 0.0)


class TestFastAPIRLEndpoints(unittest.TestCase):
    """Tests the REST endpoints for RL simulation via FastAPI TestClient."""

    def setUp(self):
        self.client = TestClient(app)

    def test_api_v1_rl_simulate_endpoint(self):
        payload = {
            "income": 60000,
            "expenses": 35000,
            "savings": 150000,
            "debt": 50000,
            "investment": 100000,
            "risk_tolerance": 0.6,
            "goal_progress": 0.45,
            "simulation_period_months": 24,
        }

        response = self.client.post("/api/v1/rl/simulate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["status"], "success")
        self.assertIn("recommended_strategy", data)
        self.assertIn("projected_savings", data)
        self.assertIn("projected_debt", data)
        self.assertIn("goal_progress", data)
        self.assertEqual(data["simulation_period_months"], 24)

    def test_api_direct_simulate_endpoint_alias(self):
        # Direct issue route: POST /api/rl/simulate
        payload = {
            "income": 50000,
            "expenses": 25000,
            "savings": 100000,
            "debt": 20000,
            "investment": 50000,
            "risk_tolerance": 0.5,
            "goal_progress": 0.3,
        }

        response = self.client.post("/api/rl/simulate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_api_rl_info_endpoint(self):
        response = self.client.get("/api/v1/rl/info")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["framework"], "PyTorch + Gymnasium")
        self.assertEqual(data["state_dimensions"], 9)
        self.assertEqual(data["action_dimensions"], 6)


if __name__ == "__main__":
    unittest.main()
