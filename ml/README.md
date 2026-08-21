# Expense Category Prediction — ML Module

Implements Phase 3 of `MACHINELEARNING.md`: predicts an expense
category (Food, Bills, Shopping, Transport, Healthcare, Education,
Entertainment) from `merchant`, `description`, `amount`, and
optionally `date`.

## Setup

```bash
cd ml
pip install -r requirements.txt --break-system-packages
```

## Pipeline

```bash
# 1. Preprocess: join all raw sources, clean, engineer features, stratified split
python preprocessing/preprocess.py

# 2. Train: fits baseline (TF-IDF + Naive Bayes) and improved
#    (TF-IDF + amount bucket + day-of-week + Random Forest / XGBoost)
#    models, picks the best by cross-validated macro F1
python training/train.py

# 3. Evaluate: scores every saved model on the held-out test set
python evaluation/evaluate.py --mode random

# 3b. Evaluate generalization to merchants the model has NEVER seen
#     (see "Two evaluation modes" below — this is the honest number)
python evaluation/evaluate.py --mode grouped

# 3c. Both side by side
python evaluation/evaluate.py --mode both

# 4. Predict: use the trained model
python inference/predict.py --merchant Swiggy --description "dinner order" --amount 450
```

## Two evaluation modes — read this before trusting the accuracy number

`--mode random` (default) reports **99.6–99.7% accuracy**. That
number is real but misleading: it comes from a row-level train/test
split, and 99.8% of test rows use a merchant the model already saw
during training. Since merchant name nearly determines category in
this data, that mode mostly measures memorization, not
classification ability.

`--mode grouped` re-splits by merchant — a merchant in the test set
is **guaranteed never to have appeared in training** — then trains
fresh models on that split. This is the honest measure of how the
model will perform on real transactions from merchants it hasn't
seen:

| Model | Known-merchant F1 (random split) | Unseen-merchant F1 (grouped split) | Gap |
|---|---|---|---|
| baseline (Naive Bayes) | 0.950 | **0.499** | 0.451 |
| random_forest | 0.976 | 0.475 | 0.501 |
| xgboost | 0.961 | 0.384 | 0.577 |

Takeaway: the tree models look best on the random split but
generalize *worse* to new merchants — they're leaning harder on
merchant identity, which doesn't transfer. The simple Naive Bayes
baseline, which relies more on the actual text tokens, generalizes
best despite scoring lower on the misleading metric. This should
factor into which model is "best" for production, not just the
random-split leaderboard.


## Dataset

Three raw sources in `datasets/raw/`, each with a different native
schema, unified by `preprocessing/source_adapters.py`:

| File | Rows kept | Notes |
|---|---|---|
| `personal_expense_classification.csv` | 100 | Toy set — 7 merchants, useful only as a smoke test |
| `personal_finance_dataset_8000_extended.csv` | 8,000 | 108 merchants, amount genuinely separates categories |
| `Daily_Household_Transactions.csv` | 1,815 (of 2,176 expense rows) | Real ledger data — messy free-text `Note` field, 50 raw categories remapped to the roadmap's 7 |

Combined: **9,915 rows → 9,451 after de-duplication**, covering all
7 roadmap categories (no single source covers all 7 alone).

**Known gap:** `education` has only 20 rows (vs 2,500+ for
food/shopping) — almost all from the household dataset. Test-set
precision/recall for this class is noisy (~0.75) and unseen
education merchants get misclassified in practice. Needs a larger
education-labeled sample before this class can be trusted; flagged
in the PR rather than hidden.

To add another raw file: drop the CSV into `datasets/raw/` and, if
it's a new schema, add one `adapt_x(df)` function + its column
signature to `source_adapters.py`. Nothing else changes.

## Design notes

- `preprocessing/source_adapters.py` unifies differently-shaped raw
  files into one common schema
  (`merchant, description, amount, category, date, source`) via
  column-signature detection, so new sources plug in without
  touching the rest of the pipeline.
- `utils/text_utils.py` centralizes text cleaning and feature
  building so preprocessing (train time) and `inference/predict.py`
  (serving time) can never drift apart.
- `utils/amount_bucketizer.py` fits quantile bin edges on the
  **training set only** (amounts range from ~₹2 to ~₹150,000 across
  sources, so fixed thresholds broke) and saves them for reuse at
  eval/inference time — never fit on test data, to avoid leakage.
- Each trained model is saved as a single self-contained
  `sklearn.Pipeline` (vectorizer + classifier together), so
  inference only needs one `joblib.load()` call.
- `predict_category()` returns a confidence score and flags
  low-confidence predictions, so the app can ask the user to
  confirm instead of silently auto-filling when the model is
  unsure — this matters most for the weak `education` class above.
- `evaluation/evaluate.py --mode grouped` trains temporary,
  throwaway models on a merchant-level holdout purely to measure
  generalization; it never overwrites the production models saved
  by `training/train.py`.

---

# Expense & Cash Flow Forecasting — ML Module (Phases 4 & 18)

Implements Phase 4 (Expense Forecasting) and Phase 18 (Cash Flow Trajectory Simulation) of `MACHINELEARNING.md`: predicts future daily spending trajectories, category breakdowns, and net account balance projections across 7-day, 30-day, and 90-day horizons.

## Forecasting Pipeline

```bash
# 1. Preprocess time-series: aggregate continuous daily spend, extract cyclical & lag features
python preprocessing/preprocess_forecasting.py

# 2. Train: 5-fold expanding-window TimeSeriesSplit CV on Seasonal Baseline, Ridge, Random Forest, XGBoost
python training/train_forecasting.py

# 3. Evaluate: Out-of-time chronological test evaluation (MAE, RMSE, MAPE, Directional Accuracy)
python evaluation/evaluate_forecasting.py

# 4. Inference: Multi-day forecast & cash flow simulation
python inference/predict_forecasting.py --horizon 30 --income 60000 --balance 25000
```

## Out-of-Time Held-Out Evaluation (796 Days Test Period)

| Model | MAE (INR) | RMSE (INR) | R² | MAPE % | Directional Acc % |
|---|---|---|---|---|---|
| **baseline_seasonal** | **66,615.28** | **122,446.88** | **0.473** | **72.4%** | **75.5%** |
| random_forest | 123,135.02 | 206,696.06 | -0.502 | 96.7% | 72.7% |
| xgboost | 122,760.86 | 206,447.01 | -0.498 | 96.2% | 63.8% |
| ridge | 125,706.99 | 209,877.25 | -0.549 | 100.8% | 16.4% |

## Python API Usage

```python
from ml.inference.predict_forecasting import predict_expense_forecast, predict_cash_flow

# 1. Predict 30-day future expense trajectory & category breakdown
forecast = predict_expense_forecast(horizon_days=30)
print("Total Projected Expense:", forecast["total_predicted_expense"])
print("Weekly Summary:", forecast["weekly_summary"])
print("Category Breakdown:", forecast["category_breakdown"])

# 2. Simulate Net Cash Flow & Balance Trajectory
cash_flow = predict_cash_flow(
    monthly_income=65000.0,
    current_balance=30000.0,
    horizon_days=30,
    payday_of_month=1
)
print("Projected Net Savings:", cash_flow["projected_net_savings"])
print("Savings Rate:", cash_flow["savings_rate_pct"], "%")
print("AI Health Status:", cash_flow["health_status"])
print("Recommendation:", cash_flow["recommendation"])
```

---

# Budget Recommendation & Financial Health Scoring — ML Module (Phases 5 & 7)

Implements Phase 5 (Budget Recommendation) and Phase 7 (Financial Health Score) of `MACHINELEARNING.md`: calculates optimal 50/30/20 category budget allocations, variance diagnostics, cost-cutting recommendations, and 5-pillar 0–100 composite Financial Health Scores.

## Budget & Health Pipeline

```bash
# 1. Preprocess: Generate demographic profiles and compute baseline distributions
python preprocessing/preprocess_budget.py

# 2. Train: 5-Fold cross-validation on multi-output Ridge, Random Forest, and XGBoost models
python training/train_budget.py

# 3. Evaluate: Out-of-sample evaluation, category MAE/R2, and archetype validation
python evaluation/evaluate_budget.py

# 4. Live CLI Inference:
# Recommend optimal budget allocations
python inference/predict_budget.py --mode budget --income 75000 --savings-target 0.20 --lifestyle balanced

# Calculate 0-100 Financial Health Score
python inference/predict_budget.py --mode health --income 75000 --balance 150000 --expenses 45000 --debt 10000
```

## Multi-Model Candidate Leaderboard (Held-Out Test Split)

| Model Candidate | Test MAE (INR) | Test R² Score | Max Peak Error (INR) | Selection Status |
|---|---|---|---|---|
| `ridge` | 696.22 | 0.9766 | 42,690.68 | Baseline |
| `random_forest` | 211.38 | 0.9926 | 41,505.80 | Contender |
| `xgboost` | 214.50 | 0.9872 | 46,742.96 | Contender |
| `gradient_boosting` | 148.49 | 0.9949 | 46,390.60 | Contender |
| `ensemble` (Voting Stacking) | 107.70 | 0.9965 | 39,968.11 | High Performer |
| **`extra_trees`** | **102.77** | **0.9963** | **33,404.69** | **Selected Production Model** |

### Category-wise Breakdown (Selected Production Model)

| Category / Target | MAE (INR) | R² Score | Target Type |
|---|---|---|---|
| Healthcare | INR 44.13 | 0.9966 | Needs (Essential) |
| Education | INR 44.13 | 0.9966 | Needs (Essential) |
| Transport | INR 66.69 | 0.9965 | Needs (Essential) |
| Entertainment | INR 90.91 | 0.9968 | Wants (Discretionary) |
| Bills | INR 109.92 | 0.9965 | Needs (Essential) |
| Shopping | INR 133.55 | 0.9971 | Wants (Discretionary) |
| Savings | INR 155.57 | 0.9943 | Wealth Building |
| Food | INR 177.25 | 0.9964 | Needs (Essential) |

## Python API Usage

```python
from ml.inference.predict_budget import recommend_budget, calculate_financial_health_score

# 1. Recommend optimal budget allocations & analyze overspending
budget = recommend_budget(
    monthly_income=75000.0,
    historical_expenses={"food": 18000, "shopping": 22000, "bills": 9000, "entertainment": 6000, "transport": 5000},
    savings_target_pct=0.20,
    lifestyle="balanced"
)
print("Allocations:", budget["recommended_allocations"])
print("50/30/20 Rule:", budget["rule_50_30_20"])
print("AI Optimizations:", budget["optimization_insights"])

# 2. Calculate 0-100 Financial Health Score with diagnostic recommendations
health = calculate_financial_health_score(
    monthly_income=75000.0,
    current_balance=150000.0,
    monthly_expenses=45000.0,
    debt_obligations=10000.0
)
print("Score:", health["financial_health_score"], "/ 100")
print("Grade:", health["grade"], "-", health["status"])
print("Pillars:", health["pillars"])
print("Recommendations:", health["recommendations"])
```

