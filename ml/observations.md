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

---

## 10. Investment Recommendation & Portfolio Allocation Benchmarks (Phase 10)

### Multi-Model Candidate Leaderboard (5-Fold Stratified Cross-Validation)

| Candidate Architecture | CV Mean MAE (%) | CV Median AE (%) | CV R² Score | Max Peak Error (%) | Composite Selection Score | Status |
|---|---|---|---|---|---|---|
| `ridge` (L2 Linear Baseline) | 1.5691% | 1.2548% | 0.9423 | 13.79% | 2.2586 | Baseline |
| `xgboost` (300 trees, subsample=0.9) | 0.4476% | 0.3664% | 0.9910 | 6.21% | 0.7581 | High Performer |
| `random_forest` (200 trees, depth=18) | 0.4431% | 0.3640% | 0.9911 | 6.01% | 0.7435 | Contender |
| `extra_trees` (250 trees, depth=20) | 0.4545% | 0.3747% | 0.9908 | 4.73% | 0.6909 | High Performer |
| `slsqp_stacking_ensemble` (ET+XGB+RF+GB) | 0.4524% | 0.3717% | 0.9909 | 4.75% | 0.6898 | Contender |
| **`gradient_boosting` (250 trees, lr=0.05)** | **0.4447%** | **0.3657%** | **0.9910** | **4.74%** | **0.6816** | **Selected Production Model** |

### Held-Out Test Set Evaluation (1,199 User Investment Profiles)

* **Overall Multi-Target Allocation MAE**: **0.4498%**
* **Overall Multi-Target Allocation Median AE**: **0.3801%**
* **Overall Multi-Target Allocation RMSE**: **0.6167%**
* **Overall Multi-Target Allocation R²**: **0.9912**
* **Overall Max Single-Target Peak Error**: **6.36%** (Cut down by >33% from raw trees)
* **Simplex Constraint Violation**: **0.000000% (Strictly sums to 100.00%)**

#### Granular Asset Class Breakdown

| Asset Class Target | Test MAE (%) | Test Median AE (%) | Test R² Score | Max Error (%) | Mean Allocation (%) |
|---|---|---|---|---|---|
| `EQUITY` | 0.654% | 0.555% | 0.9982 | 5.82% | 47.78% |
| `DEBT` | 0.656% | 0.550% | 0.9980 | 6.36% | 32.05% |
| `GOLD` | 0.319% | 0.276% | 0.9829 | 1.21% | 9.51% |
| `REIT` | 0.302% | 0.250% | 0.9859 | 1.53% | 5.06% |
| `CASH` | 0.319% | 0.270% | 0.9910 | 1.44% | 5.60% |

### Real-World Investor Archetype Validation

| User Scenario | Age | Income | Surplus | Risk Profile | Equity % | Debt % | Gold % | REIT % | Cash % | Expected CAGR | Projected Wealth (Horizon) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **1. Young Tech Aggressive** | 24 | ₹100,000 | ₹45,000 | `AGGRESSIVE` | **71.7%** | 4.3% | 4.1% | 8.0% | 12.0% | **11.76%** | **₹58.55 Lakhs** (7 yrs) |
| **2. Balanced Mid-Career Family** | 38 | ₹150,000 | ₹35,000 | `BALANCED` | **51.8%** | 27.2% | 8.9% | 7.1% | 5.0% | **10.82%** | **₹29.98 Lakhs** (5 yrs) |
| **3. Conservative Pre-Retirement** | 56 | ₹90,000 | ₹25,000 | `CONSERVATIVE` | **9.9%** | **69.9%** | 15.0% | 0.1% | 5.0% | **8.03%** | **₹10.79 Lakhs** (3 yrs) |

---

## 11. Loan Eligibility & Credit Risk Underwriting Benchmarks (Phase 12)

### Multi-Model Candidate Leaderboard (5-Fold Stratified Cross-Validation)

| Candidate Classifier | PR-AUC (Average Precision) | ROC-AUC Score | Macro F1-Score | Accuracy | Brier Calibration Loss | Optimal Decision Threshold | Composite Score | Status |
|---|---|---|---|---|---|---|---|---|
| `logistic_regression` (Balanced) | 0.8805 | 0.9248 | 0.8551 | 85.86% | 0.1086 | 0.509 | 0.7898 | Baseline |
| `extra_trees` (250 trees, depth=18) | 0.9280 | 0.9555 | 0.9174 | 92.02% | 0.0800 | 0.498 | 0.8333 | Candidate |
| `random_forest` (Balanced Subsample) | 0.9453 | 0.9625 | 0.9426 | 94.50% | 0.0528 | 0.502 | 0.8501 | Contender |
| `soft_voting_ensemble` | 0.9474 | 0.9653 | 0.9509 | 95.29% | 0.0487 | 0.505 | 0.8538 | High Performer |
| `gradient_boosting` (250 trees) | 0.9498 | 0.9645 | 0.9509 | 95.29% | 0.0430 | 0.508 | 0.8551 | Contender |
| **`xgboost` (scale_pos_weight=1.5)** | **0.9499** | **0.9642** | **0.9527** | **95.46%** | **0.0426** | **0.506** | **0.8555** | **Selected Production Model** |

### Held-Out Test Set Evaluation (1,199 Loan Applications)

* **ROC-AUC Score**: **0.9695**
* **PR-AUC (Average Precision)**: **0.9505**
* **Macro F1-Score**: **0.9541**
* **Overall Accuracy**: **95.58%**
* **Approval Safety (Precision)**: **93.65%**
* **Eligible Capture (Recall)**: **95.41%**
* **False Positive Rate on Bad Loans (FPR)**: **4.31%**
* **Brier Score Calibration Loss**: **0.0404** (Well-calibrated credit risk probabilities)

### Real-World Underwriting Archetype Validation

| Borrower Scenario | Monthly Income | Requested Loan | Purpose | Credit Score | Existing EMI | Verdict | Risk Tier | Default Prob | Max Safe Borrowing Limit | Actionable Tip |
|---|---|---|---|---|---|---|---|---|---|---|
| **1. Prime Salaried Homebuyer** | ₹125,000 | ₹3,500,000 (15 yrs) | `HOME_LOAN` | 780 | ₹0 | **APPROVED** | `LOW_RISK` | **1.91%** | **₹73.04 Lakhs** | 26.36% FOIR (Healthy); Prime 7.75% preferential rate |
| **2. Overleveraged Unsecured Applicant** | ₹35,000 | ₹800,000 (3 yrs) | `PERSONAL_LOAN` | 590 | ₹12,000 | **DECLINED** | `HIGH_RISK` | **98.21%** | **₹1.08 Lakhs** | FOIR 113.5% exceeds 45% ceiling; negative cashflow (₹-20.4k) |
| **3. Moderate Near-Prime Auto Buyer** | ₹75,000 | ₹900,000 (5 yrs) | `AUTO_LOAN` | 695 | ₹8,000 | **APPROVED** | `MODERATE_RISK` | **14.20%** | **₹14.80 Lakhs** | FOIR 35.8%; Auto collateral verified |

---

## 12. Credit Score Estimator & 5-Pillar Diagnostics Benchmarks (Phase 13)

### Multi-Model Candidate Leaderboard (5-Fold Stratified Cross-Validation)

| Candidate Architecture | CV Mean MAE (pts) | CV Median AE (pts) | CV R² Score | Max Peak Error (pts) | Training Latency | Status |
|---|---|---|---|---|---|---|
| `random_forest` (180 trees) | 7.26 pts | 5.20 pts | 0.9855 | 55.0 pts | 1.8s | Contender |
| `ridge` (L2 Baseline) | 7.84 pts | 6.80 pts | 0.9855 | 39.0 pts | 0.1s | Baseline |
| `extra_trees` (200 trees) | 5.66 pts | 4.20 pts | 0.9911 | 50.0 pts | 1.6s | High Performer |
| `xgboost_hist` (350 trees) | 4.45 pts | 3.40 pts | 0.9949 | 36.0 pts | 0.8s | High Performer |
| **`hist_gradient_boosting`** | **4.32 pts** | **3.40 pts** | **0.9953** | **31.0 pts** | **0.6s** | **Selected Production Model** |

### Held-Out Test Set Evaluation (1,200 Credit Records)

* **Mean Absolute Error (MAE)**: **3.89 points** (Relative error only **0.65%** on 600-pt scale)
* **Median Absolute Error (MedAE)**: **3.00 points**
* **Root Mean Squared Error (RMSE)**: **5.03 points**
* **R² Score**: **0.9962**
* **Max Outlier Error**: **21.0 points**
* **Within $\pm 10$ Points Accuracy**: **95.67%**
* **Within $\pm 20$ Points Accuracy**: **99.92%**
* **Credit Tier Categorization Accuracy**: **95.50%** (Macro F1: **0.9519**)

### Real-World Persona Validation

| Persona Scenario | Limit / Used | Utilization | On-Time | Missed | Credit Age | Inquiries | Estimated Score | Tier | Risk Grade | Simulated Gain Action |
|---|---|---|---|---|---|---|---|---|---|---|
### Extreme Stress-Testing & Corner-Case Boundary Validation

| Extreme Scenario Archetype | Key Risk Signals & Inputs | Ground Truth Constraint | Predicted Score | Result Tier | Risk Grade | Stress-Test Status |
|---|---|---|---|---|---|---|
| **1. Perfect Prime Ceiling** | ₹3.5L income, 1% util, 18 yrs age, 0 inq, 0 missed | $850 \le \text{Score} \le 900$ | **889** | `EXCELLENT` | **A+** | ✅ **PASS** |
| **2. Catastrophic Default Floor** | ₹18k income, 100% util, 6 missed, 7 hard inq | $300 \le \text{Score} \le 520$ | **300** | `VERY_POOR` | **D** | ✅ **PASS** |
| **3. Thin-File Fresh Graduate** | 100% on-time, 15% util, but **only 6 months age** | $660 \le \text{Score} \le 730$ | **708** | `FAIR` | **B** | ✅ **PASS** |
| **4. High-Earner Card Churner** | ₹2.5L income, but **87.5% util + 6 hard inq** | $580 \le \text{Score} \le 680$ | **617** | `POOR` | **C** | ✅ **PASS** |
| **5. Sudden Delinquency Shock** | Prime profile hit by **2 missed payments in 2 yrs** | $550 \le \text{Score} \le 660$ | **598** | `POOR` | **C** | ✅ **PASS** |
| **6. Over-Limit Anomaly** | 110% over-limit utilization, 2 missed payments | $300 \le \text{Score} \le 560$ | **383** | `VERY_POOR` | **D** | ✅ **PASS** |

---

## 13. Customer Financial Persona & Archetype Segmentation Benchmarks (Phase 17)

### Unsupervised Clustering Model Leaderboard (5-Fold Validated)

| Architecture | Silhouette Score (Separation) | Davies-Bouldin Index (Compactness) | Calinski-Harabasz Index | Training Latency | Status |
|---|---|---|---|---|---|
| `gmm_diagonal` (6 Components) | 0.4691 | 1.0020 | 5,208.8 | 12.2 ms | Candidate |
| `minibatch_kmeans` (Batch=256) | 0.5104 | 0.7271 | 5,250.1 | 30.9 ms | Contender |
| `standard_kmeans` (Euclidean) | 0.5104 | 0.7271 | 5,250.1 | 1,935.9 ms | Baseline |
| **`pca_kmeans_plus_plus` (Fast Pipeline)** | **0.5961** | **0.5592** | **7,904.4** | **17.6 ms** | **Selected Production Pipeline** |

### Held-Out Test Set Evaluation (1,200 User Profiles)

* **Silhouette Score (Cluster Separation)**: **0.6025** (Benchmark: $\ge 0.50$)
* **Davies-Bouldin Index (Cluster Overlap)**: **0.5431** (Benchmark: $\le 0.85$)
* **Calinski-Harabasz Variance Ratio**: **2,072.6**
* **Adjusted Rand Index (ARI Ground-Truth Purity)**: **0.9940** (99.40% cluster purity)
* **Adjusted Mutual Information (AMI)**: **0.9927**
* **Homogeneity / V-Measure**: **0.9927**
* **Inference Response Latency**: **`< 0.2 milliseconds`**

### Real-World Persona Archetype Validation

| Archetype Scenario | Monthly Income | Savings Rate | Equity SIP | Debt EMI | Card Util | Primary Persona | Confidence | Secondary Affinity |
|---|---|---|---|---|---|---|---|---|
| **1. Early Starter Student** | ₹20,000 | 25.0% | ₹1,000 | ₹0 | 10.0% | `BUDGET_CONSCIOUS_STUDENT` | **74.7%** | Family Homemaker (16.8%) |
| **2. Young Tech Professional** | ₹160,000 | 41.9% | ₹45,000 | ₹5,000 | 14.2% | `YOUNG_TECH_PROFESSIONAL` | **59.7%** | HNI Investor (24.0%) |
| **3. Balanced Family Homemaker** | ₹95,000 | 29.5% | ₹10,000 | ₹22,000 | 18.0% | `BALANCED_FAMILY_HOMEMAKER` | **67.3%** | Early Student (18.9%) |
| **4. HNI Wealth Accumulator** | ₹450,000 | 57.8% | ₹220,000 | ₹20,000 | 6.0% | `HIGH_NET_WORTH_INVESTOR` | **81.0%** | Young Tech Pro (15.4%) |
| **5. SMB Business Owner** | ₹220,000 (CV 0.58) | 34.1% | ₹30,000 | ₹35,000 | 32.0% | `SMB_BUSINESS_OWNER` | **100.0%** | Young Tech Pro (0.01%) |
| **6. Overleveraged Distressed** | ₹42,000 | -28.6% | ₹0 | ₹22,000 | 87.5% | `DEBT_REHABILITATION_SEEKER` | **91.5%** | Family Homemaker (4.8%) |

### Extreme Stress-Testing & High-Throughput Validation

| Extreme Stress Scenario | Stress Constraints | Ground Truth Expectation | Model Verdict | Confidence | Status |
|---|---|---|---|---|---|
| **1. Acute Unemployment Crisis** | Zero monthly income, 96% card util | `DEBT_REHABILITATION_SEEKER` | `DEBT_REHABILITATION_SEEKER` | **99.8%** | ✅ **PASS** (Zero division immune) |
| **2. Multi-Crore HNI Outlier** | ₹25L/mo income, ₹4.5 Cr savings | `HIGH_NET_WORTH_INVESTOR` | `HIGH_NET_WORTH_INVESTOR` | **98.5%** | ✅ **PASS** (Magnitude invariant) |
| **3. 50/50 Hybrid Borderline** | ₹2.2L income, ₹85k SIP | `YOUNG_TECH_PRO / HNI` | `HIGH_NET_WORTH_INVESTOR` | **59.6%** | ✅ **PASS** (Soft transition verified) |
| **4. Hyper-Volatile Merchant** | CV = 1.15 revenue swings | `SMB_BUSINESS_OWNER` | `SMB_BUSINESS_OWNER` | **100.0%** | ✅ **PASS** (Volatility capture) |
| **5. Frugal Minimum Wage** | ₹14k income, ₹1.5k micro-SIP | `BUDGET_CONSCIOUS_STUDENT` | `BUDGET_CONSCIOUS_STUDENT` | **75.3%** | ✅ **PASS** (Discipline recognized) |
| **6. Luxury Leverage Trap** | ₹1.5L income, 63% EMI, 96% util | `DEBT_REHABILITATION_SEEKER` | `DEBT_REHABILITATION_SEEKER` | **93.8%** | ✅ **PASS** (Debt overrides income) |
| **7. 1,000 Batch Throughput** | 1,000 continuous requests | Latency $< 1.0\text{ms}$ | **555 microseconds / call** | **1,800 req/s** | ✅ **PASS** (Sub-millisecond speed) |

---

## 14. Financial Product Recommendation & Smart Marketplace Benchmarks (Phase 16)

### Recommender Architecture Leaderboard (5-Fold Validated)

| Recommender Architecture | NDCG@5 Score | Precision@3 (%) | Hit Rate@5 (%) | Mean Reciprocal Rank (MRR) | Query Latency | Status |
|---|---|---|---|---|---|---|
| `content_cosine_matcher` | 0.2801 | 36.1% | 41.8% | 0.2986 | 67.2 µs | Baseline |
| `matrix_factorization_svd` | 0.6263 | 69.0% | 94.6% | 0.5296 | 69.0 µs | Candidate |
| `popularity_baseline` | 0.6658 | 79.7% | 94.6% | 0.5808 | 43.3 µs | Baseline |
| **`multi_stage_hybrid_ranker`** | **0.9742** | **99.85%** | **100.0%** | **0.9653** | **31.1 µs** | **Selected Production Pipeline** |

### Held-Out Test Set Evaluation (1,200 User Profiles)

* **NDCG@5 Score**: **0.9737** (Benchmark target: $\ge 0.90$)
* **Top-1 Recommendation Accuracy**: **93.25%**
* **Precision@3 (Top 3 Capture)**: **100.00%**
* **Hit Rate@5 (Top 5 Coverage)**: **100.00%**
* **Mean Reciprocal Rank (MRR)**: **0.9644**
* **Eligibility Safety Violations**: **0 (0.00% Safety Purity)**
* **Average Inference Query Latency**: **`31.1 microseconds (0.031 ms)`**
* **Throughput Capacity**: **`32,204 queries / second`** (Pure CPU)

### Real-World Consumer Persona Matchmaking Validation

| User Scenario | Spending Profile Highlights | Top Recommended Product | Net Annual Benefit (₹) | Value Justification |
|---|---|---|---|---|
| **1. Student Credit Starter** | ₹18k income, zero credit score | `IDFC FIRST WOW Card` | **₹876 / yr** | Lifetime free FD-backed card (7.5% FD interest + CIBIL building) |
| **2. High-Flyer Tech HNI** | ₹3.5L income, ₹85k/mo travel | `HDFC Infinia Metal Card` | **₹2,74,992 / yr** | 16.5% flight/hotel reward rate on SmartBuy + Unlimited global lounge access |
| **3. Heavy Foodie Spender** | ₹85k income, ₹15k dining, ₹20k shopping | `Airtel Axis Card` | **₹42,600 / yr** | 10% on Swiggy/Zomato/BigBasket + 25% on Airtel utility bills |
| **4. Debt-Distressed User** | ₹45k income, ₹1.8L card debt at 38% | `SBI Debt Consolidation Loan` | **₹47,700 / yr** | Saves ₹47.7k interest by replacing 38% card APR with 11.5% fixed loan |
| **5. Family Utility Optimizer** | ₹70k income, ₹12k/mo electricity & DTH | `Airtel Axis Card` | **₹59,880 / yr** | 25% utility bill cashback (₹3k/mo) + 10% groceries on BigBasket |











