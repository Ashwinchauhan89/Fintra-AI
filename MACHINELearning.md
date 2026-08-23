# 🧠 Machine Learning Roadmap - Fintra-AI

> **Version:** 1.0.0  
> **Status:** Planned 🚧  
> **Maintainers:** Fintra-AI Core Team

---

# 📖 Overview

The **Machine Learning Module** is the intelligence layer of **Fintra-AI**. It enables predictive analytics, fraud detection, financial recommendations, and personalized insights by leveraging supervised, unsupervised, and deep learning models.

## 🎯 Vision

Build an intelligent financial ecosystem that doesn't just record transactions—it **understands**, **predicts**, and **recommends**.

---

# 🏗️ Architecture

```text
                    User
                     │
                     ▼
              Next.js Frontend
                     │
                     ▼
             Next.js API Routes
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
 Google Gemini API      ML Service (FastAPI)
                                 │
       ┌─────────────────────────┼────────────────────────┐
       ▼                         ▼                        ▼
  TensorFlow              Scikit-Learn             PyTorch
       │                         │                        │
       └─────────────────────────┼────────────────────────┘
                                 ▼
                        PostgreSQL + Prisma
```

---

# 📂 ML Project Structure

```
ml/
│
├── datasets/
├── preprocessing/
├── notebooks/
├── models/
├── training/
├── evaluation/
├── inference/
├── api/
├── utils/
├── requirements.txt
└── README.md
```

---

# 🚀 ML Roadmap

## Phase 1 — Data Collection

### Goals

- Collect transaction data
- Expense history
- Income history
- User demographics
- Merchant information

### Deliverables

- Dataset Schema
- Data Validation
- Data Cleaning Pipeline

---

## Phase 2 — Data Preprocessing

Modules

- Missing Value Handling
- Feature Engineering
- Label Encoding
- Normalization
- One-Hot Encoding
- Outlier Detection

Libraries

- Pandas
- NumPy
- Scikit-Learn

---

## Phase 3 — Expense Classification

### Objective

Automatically classify expenses.

Input

- Merchant Name
- Description
- Amount
- Date

Output

- Food
- Bills
- Shopping
- Transport
- Healthcare
- Education
- Entertainment

Models

- Naive Bayes
- Random Forest
- XGBoost
- BERT

Difficulty

🟢 Beginner → Intermediate

---

## Phase 4 — Expense Prediction ✅ (Implemented)

### Objective

Predict future expenses.

Models

- Seasonal Baseline Regressor
- Ridge Regressor
- Random Forest Regressor
- XGBoost Regressor

Predictions

- 7-Day / Weekly Expenses
- 30-Day / Monthly Expenses
- 90-Day / Quarterly Expenses
- Category-wise Expense Proportions

Implementation: `ml/preprocessing/preprocess_forecasting.py`, `ml/training/train_forecasting.py`, `ml/inference/predict_forecasting.py`

---

## Phase 5 — Budget Recommendation ✅ (Implemented)

Predict optimal budgets & 50/30/20 category allocations.

Input

- Salary / Monthly Income
- Expenses / Category-wise historical spending
- Savings Target / Desired Savings Rate
- Lifestyle (Conservative, Balanced, Growth-Oriented, Flexible)

Output

Recommended budgets for:

- Food
- Travel / Transport
- Bills
- Entertainment
- Shopping
- Healthcare
- Education
- Savings
- Category variance diagnostics & overspending optimization recommendations

Models

- Multi-Output Random Forest & XGBoost Regressors
- 50/30/20 Constrained Allocation Solver

Implementation: `ml/preprocessing/preprocess_budget.py`, `ml/training/train_budget.py`, `ml/evaluation/evaluate_budget.py`, `ml/inference/predict_budget.py`

---

## Phase 6 — Savings Prediction ✅ (Implemented)

### Objective

Predict forward-looking monthly savings capacity, discretionary cut potential, and multi-horizon (1/3/5-year) compounding wealth growth.

Features

- Monthly Income & Disposable Margin
- Essential (Needs) vs Discretionary (Wants) Breakdown
- Debt Obligations & Baseline Savings Rate
- Liquid Buffer Multiples

Models

- Multi-Output Stacking Ensemble Regressor
- Gradient Boosting & Extra Trees Regressors
- Compounding Wealth Growth Projector

Output

```
Monthly Savings Capacity: INR 24,747.21 (33.0% Savings Rate)
Discretionary Cut Potential: INR 4,725.00/month
5-Year Compounded Wealth: INR 1,842,605.83
```

Implementation: `ml/preprocessing/preprocess_goals.py`, `ml/training/train_goals.py`, `ml/evaluation/evaluate_goals.py`, `ml/inference/predict_goals.py` (`predict_savings_growth`)

---

## Phase 7 — Financial Health Score ✅ (Implemented)

Generate explainable 0–100 composite Financial Health Score and letter grade (`A+` to `D`).

```
Financial Health

92.4 / 100  (Grade A+ - EXCEPTIONAL)
```

5 Calibrated Health Pillars:

- **Savings Ratio (25%)**: Savings vs 20%+ target benchmark
- **Debt & Fixed Obligation Ratio (25%)**: Debt + bills vs safe threshold
- **Discretionary Spending Control (20%)**: Ratio of wants (shopping, entertainment) to total spend
- **Emergency Runway & Liquidity (15%)**: Months of living expenses covered by current liquid balance
- **Spending Buffer & Solvency (15%)**: Net cash cushion ratio

Engine:
- Multi-Pillar Composite Scoring & Diagnostic Engine with Explainable AI Insights

Implementation: `ml/inference/predict_budget.py` (`calculate_financial_health_score`), `ml/evaluation/evaluate_budget.py`

---

## Phase 8 — Fraud Detection ✅ (Implemented)

### Objective

Detect unauthorized or high-risk fraudulent transactions with probability scoring (0–100%) and tiering (`LOW`, `MEDIUM`, `HIGH`).

Features

- Large / Disproportionate Amount (Relative to category baseline)
- Unknown / Untrusted Device
- Geo-Distance Deviation (km)
- Off-hours / Night-time Activity (11 PM - 5 AM)
- Merchant Risk Index & Foreign Currency Flag
- 1-Hour Transaction Velocity Burst

Models

- Balanced Random Forest Classifier
- Tuned XGBoost Classifier (with `scale_pos_weight`)
- Extra Trees & Gradient Boosting Classifiers
- Soft-Voting Stacking Ensemble

Output

```
Fraud Probability: 100.0%  (Risk Tier: HIGH - Action: BLOCK_TRANSACTION)
```

Implementation: `ml/preprocessing/preprocess_anomaly.py`, `ml/training/train_anomaly.py`, `ml/evaluation/evaluate_anomaly.py`, `ml/inference/predict_anomaly.py` (`predict_fraud_risk`)

---

## Phase 9 — Spending Anomaly Detection ✅ (Implemented)

### Objective

Identify real-time out-of-pattern spending anomalies, duplicate payments, and sudden category spikes.

Detect

- Abnormal Expense Spikes (Z-Score & Isolation Outlier Scoring)
- Potential Duplicate Charges (Same Merchant & Exact Amount within short intervals)
- Unprecedented Category Drift & Night-time Bursts

Models

- Isolation Forest (Unsupervised partition isolation)
- One-Class SVM (RBF kernel boundary estimation)

Output

```
Anomaly Status: Flagged (Severity: CRITICAL)
Reasons: ["Potential duplicate payment", "Amount is 12.5x higher than category median"]
```

Implementation: `ml/inference/predict_anomaly.py` (`detect_transaction_anomaly`), `ml/training/train_anomaly.py`

---

## Phase 10 — Investment Recommendation

Recommend

- SIP
- Stocks
- ETFs
- Mutual Funds
- Gold

Input

- Salary
- Risk
- Age
- Goals

Models

- Gradient Boosting
- Recommendation System

---

## Phase 11 — Goal Prediction ✅ (Implemented)

### Objective

Predict exact fractional goal completion timeline, target milestone completion date, required monthly SIP contribution, and feasibility tiering (`ON_TRACK`, `FEASIBLE`, `STRETCH`, `AT_RISK`).

Features

- Target Goal Amount & Current Saved Balance
- Disposable Savings Capacity
- User Intended Horizon Months
- Expected Compounding Return (%)
- Goal Archetype Preset (`emergency_fund`, `tech_gadget`, `vehicle`, `travel_vacation`, `home_downpayment`, `education_fund`)

Models

- Multi-Output Stacking Ensemble Regressor
- Non-Linear Future Value Logarithmic Timeline Solver
- Discretionary Acceleration Optimization Engine

Output

```
Goal: MacBook Pro M3 (Target: INR 85,000 | Saved: INR 25,000)
Predicted Completion: 2.6 months (Milestone Date: 2026-11-10)
Feasibility Status: ON_TRACK
Required Monthly SIP: INR 9,709.32
Acceleration Tip: Reallocating INR 2,500/mo from discretionary spend achieves goal 0.4 months earlier.
```

Implementation: `ml/preprocessing/preprocess_goals.py`, `ml/training/train_goals.py`, `ml/evaluation/evaluate_goals.py`, `ml/inference/predict_goals.py` (`predict_goal_timeline`)

---

## Phase 12 — Loan Eligibility Prediction

Models

- Logistic Regression
- XGBoost

Output

- Eligible
- High Risk
- Medium Risk

---

## Phase 13 — Credit Score Estimator

Predict credit score using

- Income
- Savings
- Loans
- Expenses
- Debt

---

## Phase 14 — Subscription Detection ✅ (Implemented)

### Objective

Automatically identify recurring charges, predict billing cadence (`MONTHLY`, `ANNUAL`, `WEEKLY`, `QUARTERLY`), calculate next renewal dates, and flag silent price hikes.

Features

- Subword Character n-grams & TF-IDF Merchant Representation
- Recurring Interval Mean & Standard Deviation (Periodic consistency)
- Charge Amount Variance & Fixed Flag
- Historical Cycle Frequency Count
- Base Transaction Category

Models

- Regularized Logistic Regression & Soft-Voting Stacking Ensemble Classifiers
- Interval & Cadence Estimators (`estimate_cadence`)
- Silent Price Hike & Anomaly Tracker (`detect_price_hike`)

Output

```
Active Subscriptions: Netflix (INR 649/mo), Spotify (INR 119/mo), JioFiber (INR 825/mo)
Total Monthly Burn: INR 1,593.00
Upcoming Renewals: JioFiber on Aug 31 (7 days remaining), Netflix on Sep 22 (29 days remaining)
Alerts: Spotify increased by 25.2% (+INR 30.00) compared to previous cycle.
```

Implementation: `ml/preprocessing/preprocess_subscriptions.py`, `ml/training/train_subscriptions.py`, `ml/evaluation/evaluate_subscriptions.py`, `ml/inference/predict_subscriptions.py`

---

## Phase 15 — OCR Receipt Intelligence

Pipeline

```
Receipt

↓

OCR

↓

Merchant Detection

↓

Category Prediction

↓

Expense Creation
```

Libraries

- EasyOCR
- PaddleOCR
- Tesseract

---

## Phase 16 — Financial Recommendation Engine

Recommend

- Budgets
- Investments
- Insurance
- Savings Plans
- Credit Cards

Models

- Collaborative Filtering
- Content-Based Recommendation

---

## Phase 17 — Customer Segmentation

Group users

- Students
- Professionals
- Families
- Investors
- Business Owners

Algorithms

- K-Means
- DBSCAN

---

## Phase 18 — Cash Flow Forecasting ✅ (Implemented)

Predict

- Account Balance Trajectory
- Daily / Monthly Net Cash Flow
- Deficit Date Detection & Savings Projections
- AI Financial Health & Recommendations

Models

- Seasonal Moving Average + Multi-Step Autoregression
- Tree Ensemble Regressors & Rolling Window Estimators

Implementation: `ml/inference/predict_forecasting.py` (`predict_cash_flow`)

---

## Phase 19 — AI + ML Hybrid Copilot

Gemini explains.

Machine Learning predicts.

Example

```
User

Can I afford a new laptop?

↓

ML

Savings Prediction

↓

Gemini

Explains the recommendation in natural language.
```

---

## Phase 20 — Reinforcement Learning (Future)

Personal Finance Agent

Learns user behaviour.

Optimizes

- Spending
- Savings
- Investments

---

# 🧪 Datasets

Potential datasets

- Kaggle Personal Finance Dataset
- Bank Marketing Dataset
- Credit Card Fraud Dataset
- UCI ML Repository
- Synthetic Finance Data

---

# 📚 Tech Stack

## Data

- Pandas
- NumPy

## Machine Learning

- Scikit-Learn
- XGBoost
- LightGBM

## Deep Learning

- TensorFlow
- Keras
- PyTorch

## NLP

- Transformers
- Sentence Transformers
- BERT

## Time Series

- Prophet
- ARIMA
- LSTM

## Computer Vision

- OpenCV
- EasyOCR
- PaddleOCR

## Deployment

- FastAPI
- Docker
- Kubernetes (Future)

---

# 📊 Model Evaluation

Metrics

Classification

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC

Regression

- MAE
- RMSE
- R² Score

Clustering

- Silhouette Score
- Davies-Bouldin Index

---

# 📅 Milestones

## Milestone 1

- Data Collection
- Data Cleaning
- Feature Engineering

---

## Milestone 2

- Expense Classification
- Budget Prediction

---

## Milestone 3

- Fraud Detection
- Financial Health Score

---

## Milestone 4

- Recommendation Engine
- Goal Prediction

---

## Milestone 5

- OCR
- AI Copilot
- Production Deployment

---

# 🤝 Contribution Opportunities

### 🟢 Beginner

- Data Cleaning
- Visualization
- Documentation
- Unit Tests

---

### 🟡 Intermediate

- Feature Engineering
- Model Training
- API Integration
- Model Evaluation

---

### 🔴 Advanced

- Deep Learning
- Fraud Detection
- NLP
- OCR
- Recommendation Systems
- Time-Series Forecasting
- MLOps

---

# 🌟 Future Vision

- Real-Time Fraud Detection
- AI Financial Coach
- Voice-Based Expense Tracking
- Personalized Wealth Advisor
- Retirement Planning
- Tax Optimization
- ESG Investment Analysis
- Financial Digital Twin
- Explainable AI (XAI)
- Federated Learning for Privacy

---

# 📈 Success Metrics

- ≥95% Expense Classification Accuracy
- ≥90% Fraud Detection Recall
- ≤5% Budget Prediction Error
- Real-Time Inference (<200 ms)
- Explainable ML Outputs
- Production-Ready MLOps Pipeline

---

# ❤️ Join Us

Whether you're passionate about **Machine Learning, Data Science, AI, MLOps, or Backend Development**, there's a place for you in the Fintra-AI ML team.

Let's build the future of intelligent personal finance together! 🚀