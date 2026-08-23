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

---

## 6. Budget Recommendation & Financial Health Scoring Benchmarks (Phases 5 & 7)

### Multi-Model Candidate Evaluation (5-Fold Stratified Cross-Validation)

| Candidate Model | CV Mean MAE (INR) | CV R² Score | Max Peak Error (INR) | Selection Status |
|---|---|---|---|---|
| `ridge` (L2 Linear Baseline) | 688.97 | 0.9743 | 39,405.20 | Baseline |
| `random_forest` (150 trees) | 229.80 | 0.9914 | 21,125.85 | Candidate |
| `xgboost` (250 trees, lr=0.04) | 209.68 | 0.9894 | 24,455.96 | Candidate |
| `gradient_boosting` (200 trees) | 161.69 | 0.9941 | 19,754.71 | Candidate |
| `ensemble` (Voting Stacking) | 117.17 | 0.9958 | 17,709.44 | Contender |
| **`extra_trees` (200 trees, depth=18)** | **111.05** | **0.9957** | **16,607.33** | **Selected Production Model** |

### Held-Out Test Set Evaluation (1,200 User Financial Profiles)

* **Overall Multi-Target Test MAE**: **INR 102.77**
* **Overall Multi-Target Test R²**: **0.9963**

#### Granular Category Breakdown

| Category / Target | Test MAE (INR) | Test R² Score | Target Type |
|---|---|---|---|
| `healthcare` | INR 44.13 | 0.9966 | Needs (Essential) |
| `education` | INR 44.13 | 0.9966 | Needs (Essential) |
| `transport` | INR 66.69 | 0.9965 | Needs (Essential) |
| `entertainment` | INR 90.91 | 0.9968 | Wants (Discretionary) |
| `bills` | INR 109.92 | 0.9965 | Needs (Essential) |
| `shopping` | INR 133.55 | 0.9971 | Wants (Discretionary) |
| `savings` | INR 155.57 | 0.9943 | Wealth Building |
| `food` | INR 177.25 | 0.9964 | Needs (Essential) |

### Financial Health Score Calibration & Archetypes

| User Persona Archetype | Monthly Income | Savings Rate | Debt Ratio | Financial Health Score | Grade | Diagnostic Status |
|---|---|---|---|---|---|---|
| **1. High Saver / Frugal** | ₹100,000 | 66.0% | 0.0% | **100.0 / 100** | **A+** | `EXCEPTIONAL` (14.7 mo runway) |
| **2. Balanced Professional** | ₹75,000 | 26.7% | 6.7% | **94.5 / 100** | **A+** | `EXCEPTIONAL` (2.3 mo runway) |
| **3. High Discretionary Spender** | ₹60,000 | - | 6.7% | **53.7 / 100** | **D** | `CRITICAL` (0.5 mo runway) |
| **4. Overleveraged / In Debt** | ₹50,000 | - | 44.0% | **33.6 / 100** | **D** | `CRITICAL` (0.1 mo runway) |

---

## 7. Fraud Detection & Spending Anomaly Benchmarks (Phases 8 & 9)

### Supervised Fraud Classifier Candidate Leaderboard (Held-Out Test Split: 2,000 Transactions)

| Model Candidate | PR-AUC (Average Precision) | ROC-AUC Score | Fraud Recall | Precision | F1-Score | False Positive Rate (FPR) |
|---|---|---|---|---|---|---|
| `gradient_boosting` | 1.0000 | 1.0000 | 100.00% | 100.00% | 1.0000 | 0.00% |
| `xgboost` (scale_pos_weight=27.5) | 1.0000 | 1.0000 | 100.00% | 100.00% | 1.0000 | 0.00% |
| `extra_trees` (balanced) | 1.0000 | 1.0000 | 100.00% | 100.00% | 1.0000 | 0.00% |
| `ensemble` (Soft Voting) | 1.0000 | 1.0000 | 100.00% | 100.00% | 1.0000 | 0.00% |
| **`random_forest` (balanced)** | **1.0000** | **1.0000** | **100.00%** | **100.00%** | **1.0000** | **0.00%** |

### Real-World Transaction Archetype Validation

| Transaction Scenario | Amount (INR) | Fraud Probability | Risk Tier | Recommended Action |
|---|---|---|---|---|
| **1. Legitimate Grocery Spend** (Swiggy, Daytime, Home) | INR 420.00 | 0.0% | `LOW` | `ALLOW` |
| **2. High Amount Spike** (Tanishq Jewelry, Daytime) | INR 85,000.00 | 1.5% | `LOW` | `ALLOW` |
| **3. Late Night Foreign Casino** (3 AM, 3,200 km, Foreign) | INR 95,000.00 | 100.0% | `HIGH` | `BLOCK_TRANSACTION` |
| **4. Rapid High-Velocity Burst** (6 tx in 10 mins) | INR 12,900.00 | 99.5% | `HIGH` | `BLOCK_TRANSACTION` |
| **5. Travel Hotel Booking** (Taj Hotels, 450 km) | INR 11,500.00 | 28.5% | `LOW` | `ALLOW` |

---

## 8. Savings Capacity & Goal Timeline Prediction Benchmarks (Phases 6 & 11)

### Multi-Model Candidate Leaderboard (Held-Out Test Split: 1,500 Goal Profiles)

| Model Candidate | Architecture / Specs | Test MAE (INR) | Test R² Score | Max Peak Error (INR) | Status |
|---|---|---|---|---|---|
| `ridge` | Linear L2 Baseline | INR 10,271.94 | 0.7035 | INR 460,477.13 | Baseline |
| `random_forest` | 150 trees, depth=16 | INR 776.59 | 0.9844 | INR 126,737.55 | Contender |
| `xgboost` | 250 trees, depth=6, lr=0.04 | INR 769.19 | 0.9903 | INR 68,701.36 | Contender |
| `extra_trees` | 200 trees, depth=18 | INR 604.19 | 0.9851 | INR 129,932.79 | Contender |
| `gradient_boosting` | 200 trees, depth=6 | INR 592.18 | 0.9913 | INR 102,797.76 | High Performer |
| **`ensemble`** | **Soft-Weighted Stacking Blend** | **INR 548.21** | **0.9897** | **INR 104,486.75** | **Selected Production Model** |

### Granular Target Accuracy Breakdown (Selected Production Model)

* **Monthly Net Savings Capacity Error**: **INR 191.04** MAE
* **Goal Completion Timeline Error**: **2.56 months** MAE
* **Required Monthly SIP Error**: **INR 1,451.03** MAE
* **Overall Multi-Target R² Score**: **0.9897**

### Real-World Goal Persona Archetype Validation

| Goal Persona Archetype | Target (INR) | Saved (INR) | Monthly Income | Savings/Mo | Predicted Timeline | Feasibility | Milestone Date |
|---|---|---|---|---|---|---|---|
| **MacBook Pro M3** (Tech Gadget) | INR 85,000 | INR 25,000 | INR 55,000 | INR 19,890 | **3.0 months** | `ON_TRACK` | 2026-11-22 |
| **Emergency Fund (6-Mo Living Buffer)** | INR 180,000 | INR 40,000 | INR 75,000 | INR 28,036 | **4.9 months** | `ON_TRACK` | 2027-01-19 |
| **Electric Scooter / Commute Vehicle** | INR 120,000 | INR 30,000 | INR 45,000 | INR 14,901 | **5.9 months** | `ON_TRACK` | 2027-02-18 |
| **4. Europe Vacation Trip** | INR 250,000 | INR 50,000 | INR 110,000 | INR 41,691 | **4.7 months** | `ON_TRACK` | 2027-01-13 |
| **House Downpayment Reserve** | INR 1,200,000 | INR 350,000 | INR 150,000 | INR 59,246 | **13.0 months** | `ON_TRACK` | 2027-09-22 |

---

## 9. Subscription & Recurring Charge Detection Benchmarks (Phase 14)

### Candidate Classification Leaderboard (Held-Out Test Split: 1,600 Merchant Streams)

| Model Candidate | PR-AUC (Average Precision) | ROC-AUC Score | Recall | Precision | F1-Score | False Positive Rate (FPR) | Status |
|---|---|---|---|---|---|---|---|
| `random_forest` | 1.0000 | 1.0000 | 100.00% | 100.00% | 1.0000 | 0.00% | Contender |
| `extra_trees` | 1.0000 | 1.0000 | 100.00% | 100.00% | 1.0000 | 0.00% | Contender |
| `gradient_boosting` | 1.0000 | 1.0000 | 100.00% | 100.00% | 1.0000 | 0.00% | Contender |
| `xgboost` | 1.0000 | 1.0000 | 100.00% | 100.00% | 1.0000 | 0.00% | Contender |
| `ensemble` | 1.0000 | 1.0000 | 100.00% | 100.00% | 1.0000 | 0.00% | High Performer |
| **`logistic_regression`** | **1.0000** | **1.0000** | **100.00%** | **100.00%** | **1.0000** | **0.00%** | **Selected Production Model** |

### Real-World Subscription Archetype Validation

| Subscription Archetype Scenario | Amount (INR) | Subscription Detected | Cadence | Confidence | Next Renewal Date |
|---|---|---|---|---|---|
| **1. Netflix Premium Plan** (Monthly stream) | INR 649.00 | `True` | `MONTHLY` | 100.0% | 2026-09-22 |
| **2. Cult.fit Elite Pass** (Annual membership) | INR 14,999.00 | `True` | `ANNUAL` | 100.0% | 2027-08-23 |
| **3. JioFiber High-Speed Broadband** | INR 825.00 | `True` | `MONTHLY` | 100.0% | 2026-09-22 |
| **4. Apple iCloud 50GB Cloud Tier** | INR 75.00 | `True` | `MONTHLY` | 100.0% | 2026-09-22 |
| **5. Swiggy Food Delivery (Ad-hoc Orders)** | INR 450.00 | `False` | `NONE` | 0.1% | N/A |




