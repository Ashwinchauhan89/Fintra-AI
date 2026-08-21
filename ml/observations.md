# 📊 Fintra-AI ML Observations & Benchmark Report

This document records the exact training logs, cross-validation scores, held-out test evaluation benchmarks, generalization analysis on unseen merchants, and inference results.

---

## 1. Data Preprocessing & Unification

```text
[info] Scanning datasets/raw for source files
[info] Daily_Household_Transactions.csv (household): 2176 rows -> 1815 kept, 361 dropped (unmapped/invalid category)
[info] personal_expense_classification.csv (toy): 100 rows -> 100 kept, 0 dropped (unmapped/invalid category)
[info] personal_finance_dataset_8000_extended.csv (finance_8000): 8000 rows -> 8000 kept, 0 dropped (unmapped/invalid category)
[info] Combined total: 9915 rows from 3 source(s)

Category Distribution:
  - food             : 2545
  - shopping         : 2536
  - transport        : 1913
  - entertainment    : 1007
  - bills            : 996
  - healthcare       : 898
  - education        : 20

[info] Dropped 464 exact-duplicate row(s)
[done] Train: 7560 rows -> datasets/processed/train.csv
[done] Test:  1891 rows -> datasets/processed/test.csv
[done] Label encoder -> models/label_encoder.pkl
[done] Amount bucketizer -> models/amount_bucketizer.json
[info] Classes: ['bills', 'education', 'entertainment', 'food', 'healthcare', 'shopping', 'transport']
[info] Amount bucket edges: [2.0, 413.74, 1224.82, 3865.45, 12190.88, 149836.1]
```

---

## 2. Feature Engineering & Multi-Model Training

We employ a dual-granularity feature representation:
1. **Word-level TF-IDF (1 to 3 n-grams)** with sublinear TF scaling.
2. **Character-level Subword TF-IDF (`char_wb` 2 to 5 n-grams)** to capture merchant prefixes, sub-brands, and spelling variations.
3. **Categorical Features**: Quantile Amount Bucket + Day of Week.

### Cross-Validation Results (5-Fold Stratified Macro F1)

```text
[cv] baseline (Complement NB): macro F1 = 0.9853 (scores=[0.9674, 0.9926, 0.9976, 0.9921, 0.9770])
[cv] logistic_regression     : macro F1 = 0.9867 (scores=[0.9689, 0.9949, 0.9990, 0.9952, 0.9757])
[cv] random_forest           : macro F1 = 0.9863 (scores=[0.9683, 0.9929, 0.9985, 0.9947, 0.9769])
[cv] xgboost                 : macro F1 = 0.9853 (scores=[0.9671, 0.9929, 0.9989, 0.9920, 0.9756])
[cv] ensemble (Soft Voting)  : macro F1 = 0.9871 (scores=[0.9692, 0.9949, 0.9990, 0.9955, 0.9769])

[result] Best model by CV macro F1: 'ensemble' (0.9871) -> saved as best_model.pkl
```

---

## 3. Held-out Test Set Evaluation (`--mode random`)

Evaluated on **1,891 held-out test transactions**:

```text
============================================================
Model: ensemble (Best Selected Production Model)
============================================================
Accuracy: 0.9979 (99.79%)

               precision    recall  f1-score   support

        bills       1.00      0.99      1.00       196
    education       1.00      1.00      1.00         4
entertainment       1.00      0.99      1.00       186
         food       0.99      1.00      1.00       455
   healthcare       1.00      1.00      1.00       179
     shopping       1.00      1.00      1.00       505
    transport       1.00      1.00      1.00       366

     accuracy                           1.00      1891
    macro avg       1.00      1.00      1.00      1891
 weighted avg       1.00      1.00      1.00      1891

============================================================
Summary Table (Random Held-Out Split)
============================================================
                     Accuracy   Macro F1
ensemble             0.9979     0.9983
logistic_regression  0.9979     0.9983
baseline (NB)        0.9984     0.9982
xgboost              0.9974     0.9976
random_forest        0.9968     0.9973
```

---

## 4. Unseen Merchants Generalization Check (`--mode grouped`)

To prevent merchant data leakage and evaluate real-world performance on completely new/unfamiliar merchants:
* **Train set**: 7,745 transactions across 157 merchants.
* **Test set**: 2,170 transactions across 41 merchants (**0% merchant overlap with train**).

```text
============================================================
Summary (Grouped Split — Merchants NEVER seen in training)
============================================================
                     Accuracy   Macro F1
baseline (NB)        0.7576     0.5781
logistic_regression  0.7023     0.5289
ensemble             0.6825     0.5081
random_forest        0.6590     0.4991
xgboost              0.5290     0.4042

============================================================
Generalization Gap Analysis (Known vs Unseen Merchants)
============================================================
                     Random F1  Unseen F1  Generalization Gap
baseline             0.9982     0.5781     0.4201  (Best generalizing)
logistic_regression  0.9983     0.5289     0.4694
ensemble             0.9983     0.5081     0.4902
random_forest        0.9973     0.4991     0.4982
xgboost              0.9976     0.4042     0.5934  (Highest overfitting)
```

---

## 5. Live Inference Verification

```bash
python ml/inference/predict.py --merchant Swiggy --description "dinner order" --amount 450
```

**Output:**
```json
{"category": "food", "confidence": 0.5782}
```

```bash
python ml/inference/predict.py --merchant Netflix --description "monthly subscription" --amount 649
```

**Output:**
```json
{"category": "entertainment", "confidence": 0.9854}
```
