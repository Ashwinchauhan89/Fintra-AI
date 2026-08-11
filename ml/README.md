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
