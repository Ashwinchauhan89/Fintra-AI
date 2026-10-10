# Reinforcement Learning Financial Decision Engine

## 1. Overview & Objective

The **Reinforcement Learning (RL) Financial Decision Engine** (implemented for [Issue #54](https://github.com/Ashwinchauhan89/Fintra-AI/issues/54)) enables **Fintra-AI** to simulate complex multi-month financial trajectories and recommend personalized strategies for improving long-term financial health.

Rather than relying on static 50/30/20 heuristics or one-size-fits-all budgets, this RL system models a dynamic financial environment where actions directly influence future states (e.g. debt interest compounding, investment portfolio growth, emergency buffer stability, and goal attainment).

> [!IMPORTANT]
> **Non-Custodial Design**: The engine is strictly a decision-support and predictive simulation tool. No real financial accounts are accessed or executed upon.

---

## 2. Mathematical RL Formulation

The decision problem is modeled as a Markov Decision Process (MDP) over discrete monthly intervals: $\langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma \rangle$.

### State Representation $\mathcal{S} \in [0, 1]^9$
The state vector encodes the user's financial posture across 9 normalized dimensions:

| Index | Feature | Normalization Function | Description |
|---|---|---|---|
| 0 | `income_norm` | $\text{clip}(\text{income} / 200000, 0, 1)$ | Monthly disposable income |
| 1 | `expenses_ratio` | $\text{clip}(\text{expenses} / \text{income}, 0, 1)$ | Monthly expenditure pressure |
| 2 | `savings_ratio` | $\text{clip}(\text{savings} / (6 \cdot \text{expenses}), 0, 1)$ | Liquid cash reserves coverage |
| 3 | `debt_ratio` | $\text{clip}(\text{debt} / (12 \cdot \text{income}), 0, 1)$ | Overall debt burden |
| 4 | `investment_ratio` | $\text{clip}(\text{investment} / (10 \cdot \text{income}), 0, 1)$ | Market asset accumulation |
| 5 | `emergency_runway` | $\text{clip}(\text{emergency} / (6 \cdot \text{expenses}), 0, 1)$ | Liquid safety buffer |
| 6 | `risk_tolerance` | $\text{clip}(\text{risk\_tol}, 0, 1)$ | Investor risk appetite |
| 7 | `goal_ratio` | $\text{clip}(\text{goal} / (10 \cdot \text{income}), 0, 1)$ | Target milestone size |
| 8 | `goal_progress` | $\text{clip}(\text{net\_worth} / \text{goal}, 0, 1)$ | Progress ratio toward milestone |

### Action Space $\mathcal{A} \in \{0, 1, 2, 3, 4, 5\}$
The agent selects one high-level capital allocation strategy each month:

1. **`0: MAINTAIN_CURRENT_STRATEGY`**: Baseline balanced allocation (40% savings, 35% investments, 25% debt/emergency).
2. **`1: INCREASE_SAVINGS`**: Channels 70% of monthly surplus into high-yield liquid savings.
3. **`2: REDUCE_DISCRETIONARY_SPENDING`**: Curtails monthly expenses by 18%, enlarging investable/saveable cash flow.
4. **`3: PAY_DOWN_DEBT`**: Aggressive debt elimination (75% surplus toward debt principal, avoiding compounding interest).
5. **`4: INCREASE_EMERGENCY_FUND`**: Prioritizes building a 3 to 6-month liquid runway before taking market risk.
6. **`5: ADJUST_INVESTMENT_ALLOCATION`**: Channels 75% of surplus into diversified compounding market assets.

### Multi-Objective Sustainable Health Reward Function $\mathcal{R}(s, a, s')$

$$R = 1.5 \cdot R_{\text{savings}} + 2.0 \cdot R_{\text{debt}} + 1.0 \cdot R_{\text{goal}} + 1.2 \cdot R_{\text{emergency}} + 1.0 \cdot \Delta \text{Health} + B_{\text{cut}} - P_{\text{risk}}$$

- **$R_{\text{savings}}$**: Rewards net wealth growth normalized by income.
- **$R_{\text{debt}}$**: Heavily rewards liability reduction ($3.5 \times$ ratio) and provides a $+2.0$ bonus when full debt freedom is achieved.
- **$R_{\text{emergency}}$**: Rewards maintaining 3–6 months of liquid expenses ($+2.0$); imposes severe penalty ($-2.0$) if buffer $< 1$ month.
- **$P_{\text{risk}}$**: Penalizes aggressive market investing when debt is high ($> 2 \times$ monthly income) or emergency buffer is nonexistent ($< 2$ months).

---

## 3. Deep Q-Network (Double-DQN) Architecture

Implemented in **PyTorch** (`ml/rl/agent.py`):
- **Q-Network**: Fully connected MLP with Layer Normalization:
  $$\text{Input}(9) \to \text{Dense}(128) + \text{LayerNorm} + \text{ReLU} \to \text{Dense}(128) + \text{LayerNorm} + \text{ReLU} \to \text{Dense}(64) \to \text{Output}(6)$$
- **Double DQN**: Decouples action selection from target value evaluation:
  $$Y_t^{\text{DoubleQ}} = R_{t+1} + \gamma Q\left(S_{t+1}, \arg\max_a Q(S_{t+1}, a; \theta_t); \theta_t^{-}\right)$$
- **Experience Replay Buffer**: 50,000 transition capacity.
- **Loss Function**: Smooth L1 (Huber) Loss with gradient norm clipping at $1.0$.

---

## 4. REST API Endpoints

### 1. `POST /api/v1/rl/simulate` (also aliased at `/api/rl/simulate`)

#### Request:
```json
{
  "income": 60000,
  "expenses": 35000,
  "savings": 150000,
  "debt": 50000,
  "investment": 100000,
  "risk_tolerance": 0.6,
  "goal_progress": 0.45,
  "simulation_period_months": 24
}
```

#### Response:
```json
{
  "status": "success",
  "recommended_strategy": "Accelerate debt repayment to become completely debt-free by Month 7, and reallocate freed cash flow into compounding diversified market investments",
  "projected_savings": 195000,
  "projected_debt": 0,
  "projected_investments": 345000,
  "projected_net_worth": 540000,
  "goal_progress": 1.0,
  "simulation_period_months": 24,
  "monthly_trajectory": [
    {
      "month": 0,
      "income": 60000,
      "expenses": 35000,
      "savings": 150000,
      "debt": 50000,
      "investment": 100000,
      "net_worth": 200000,
      "action_name": "Starting Baseline",
      "health_score": 78.5
    }
  ],
  "action_breakdown": {
    "Pay Down Debt": 7,
    "Adjust Investment Allocation": 17
  },
  "risk_indicators": {
    "initial_emergency_runway_months": 1.4,
    "final_emergency_runway_months": 4.8,
    "initial_debt_to_income_ratio": 0.069,
    "final_debt_to_income_ratio": 0.0,
    "initial_health_score": 78.5,
    "final_health_score": 96.2,
    "debt_free_month": 7
  }
}
```

### 2. `GET /api/v1/rl/info`
Returns framework details, state dimensionality, and the discrete action dictionary.

### 3. `POST /api/v1/rl/train`
Triggers retraining of the Double-DQN agent on synthetic financial profiles.

---

## 5. Frontend Dashboard Integration

Located at `ai-finance-platform/app/(main)/dashboard/_components/rl-decision-simulator.jsx`:
- **Archetype Presets**: 1-click loading for *Debt Elimination*, *Balanced Builder*, *Wealth Accelerator*, and the official *Issue #54 Benchmark*.
- **Interactive Sliders**: Real-time adjustment of income, liabilities, savings, investments, and risk appetite.
- **KPI Summary Cards**: Projected Savings, Debt-Free Milestones, Net Worth Accumulation, and Goal Gauge.
- **Multi-Asset Recharts Trajectory**: Displays Net Worth, Savings, Investments, and Debt Amortization curves.
- **Decision Distribution**: Badges showing the exact distribution of RL policy actions across the simulated horizon.

---

## 6. Verification & Automated Tests

Run the complete test suite:
```bash
python -m unittest backend/tests/test_rl_engine.py
```

Run benchmark evaluation against heuristic baselines:
```bash
python ml/evaluation/evaluate_rl.py
```
