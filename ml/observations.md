
# Processed Of Data 

category
food             2545
shopping         2536
transport        1913
entertainment    1007
bills             996
healthcare        898
education          20
Name: count, dtype: int64
[info] Rows per source:
source
finance_8000    8000
household       1815
toy              100
Name: count, dtype: int64
[info] Dropped 464 exact-duplicate row(s)
[done] Train: 7560 rows -> E:\tmp\Fintra AI\ml\preprocessing\..\datasets\processed\train.csv
[done] Test:  1891 rows -> E:\tmp\Fintra AI\ml\preprocessing\..\datasets\processed\test.csv
[done] Label encoder -> E:\tmp\Fintra AI\ml\preprocessing\..\models\label_encoder.pkl
[done] Amount bucketizer -> E:\tmp\Fintra AI\ml\preprocessing\..\models\amount_bucketizer.json
[info] Classes: ['bills', 'education', 'entertainment', 'food', 'healthcare', 'shopping', 'transport']
[info] Amount bucket edges: [np.float64(2.0), np.float64(413.74), np.float64(1224.82), np.float64(3865.45), np.float64(12190.88), np.float64(149836.1)]




# Training of the Data 

[info] Loading training data from E:\tmp\Fintra AI\ml\training\..\datasets\processed\train.csv
[cv] baseline: macro F1 = 0.918 (folds=5, scores=[np.float64(0.921), np.float64(0.926), np.float64(0.925), np.float64(0.969), np.float64(0.85)])
[cv] random_forest: macro F1 = 0.977 (folds=5, scores=[np.float64(0.988), np.float64(0.967), np.float64(0.994), np.float64(0.966), np.float64(0.971)])
[cv] xgboost: macro F1 = 0.982 (folds=5, scores=[np.float64(0.987), np.float64(0.969), np.float64(0.994), np.float64(0.966), np.float64(0.992)])
[done] Saved baseline -> E:\tmp\Fintra AI\ml\training\..\models\baseline.pkl
[done] Saved random_forest -> E:\tmp\Fintra AI\ml\training\..\models\random_forest.pkl
[done] Saved xgboost -> E:\tmp\Fintra AI\ml\training\..\models\xgboost.pkl

[result] Best model by CV macro F1: 'xgboost' (0.982) -> saved as best_model.pkl
[note] Run evaluate.py next to check performance on the held-out test set, not just cross-validation.




# Evaluation of Model 


E:\tmp\Fintra AI\ml>python evaluation/evaluate.py --mode random
[info] Loading test data from E:\tmp\Fintra AI\ml\evaluation\..\datasets\processed\test.csv
[info] 1891 test rows

============================================================
Model: baseline
============================================================
Accuracy: 0.997

               precision    recall  f1-score   support

        bills       1.00      0.99      0.99       196
    education       1.00      0.50      0.67         4
entertainment       0.99      0.99      0.99       186
         food       1.00      1.00      1.00       455
   healthcare       1.00      1.00      1.00       179
     shopping       1.00      1.00      1.00       505
    transport       1.00      1.00      1.00       366

     accuracy                           1.00      1891
    macro avg       1.00      0.93      0.95      1891
 weighted avg       1.00      1.00      1.00      1891

Confusion matrix (rows=actual, cols=predicted):
               bills  education  entertainment  food  healthcare  shopping  transport
bills            194          0              1     1           0         0          0
education          0          2              1     0           0         0          1
entertainment      0          0            185     0           0         1          0
food               0          0              0   455           0         0          0
healthcare         0          0              0     0         179         0          0
shopping           0          0              0     0           0       505          0
transport          0          0              0     0           0         0        366

============================================================
Model: random_forest
============================================================
Accuracy: 0.996

               precision    recall  f1-score   support

        bills       0.99      0.99      0.99       196
    education       1.00      0.75      0.86         4
entertainment       0.98      0.99      0.99       186
         food       1.00      1.00      1.00       455
   healthcare       1.00      1.00      1.00       179
     shopping       1.00      1.00      1.00       505
    transport       1.00      1.00      1.00       366

     accuracy                           1.00      1891
    macro avg       1.00      0.96      0.98      1891
 weighted avg       1.00      1.00      1.00      1891

Confusion matrix (rows=actual, cols=predicted):
               bills  education  entertainment  food  healthcare  shopping  transport
bills            195          0              1     0           0         0          0
education          1          3              0     0           0         0          0
entertainment      0          0            185     1           0         0          0
food               0          0              2   453           0         0          0
healthcare         0          0              0     0         179         0          0
shopping           1          0              0     0           0       504          0
transport          0          0              0     1           0         0        365

============================================================
Model: xgboost
============================================================
Accuracy: 0.996

               precision    recall  f1-score   support

        bills       0.99      0.99      0.99       196
    education       0.75      0.75      0.75         4
entertainment       1.00      0.99      0.99       186
         food       0.99      1.00      0.99       455
   healthcare       1.00      1.00      1.00       179
     shopping       1.00      1.00      1.00       505
    transport       1.00      1.00      1.00       366

     accuracy                           1.00      1891
    macro avg       0.96      0.96      0.96      1891
 weighted avg       1.00      1.00      1.00      1891

Confusion matrix (rows=actual, cols=predicted):
               bills  education  entertainment  food  healthcare  shopping  transport
bills            195          0              0     1           0         0          0
education          1          3              0     0           0         0          0
entertainment      0          0            184     1           0         1          0
food               0          1              0   454           0         0          0
healthcare         0          0              0     0         179         0          0
shopping           0          0              0     2           0       503          0
transport          0          0              0     1           0         0        365

============================================================
Summary (random split — includes merchants seen in training)
============================================================
               accuracy  macro_f1
random_forest  0.996298  0.976008
xgboost        0.995769  0.961227
baseline       0.997356  0.950006







# python evaluation/evaluate.py --mode grouped

============================================================
GROUPED-SPLIT GENERALIZATION CHECK (merchant-level holdout)
============================================================
[info] Daily_Household_Transactions.csv (household): 2176 rows -> 1815 kept, 361 dropped (unmapped/invalid category)
[info] personal_expense_classification.csv (toy): 100 rows -> 100 kept, 0 dropped (unmapped/invalid category)
[info] personal_finance_dataset_8000_extended.csv (finance_8000): 8000 rows -> 8000 kept, 0 dropped (unmapped/invalid category)
[info] Combined total: 9915 rows from 3 source(s)
[info] Category counts:
category
food             2545
shopping         2536
transport        1913
entertainment    1007
bills             996
healthcare        898
education          20
Name: count, dtype: int64
[info] Rows per source:
source
finance_8000    8000
household       1815
toy              100
Name: count, dtype: int64
[info] Train: 7745 rows, 157 merchants
[info] Test:  2170 rows, 41 merchants — NONE overlap with train
[result] baseline        unseen-merchant accuracy=0.671  macro_f1=0.499
[result] random_forest   unseen-merchant accuracy=0.635  macro_f1=0.475
[result] xgboost         unseen-merchant accuracy=0.585  macro_f1=0.384

============================================================
Summary (grouped split — merchants NEVER seen in training)
============================================================
               accuracy  macro_f1
baseline       0.670968  0.498660
random_forest  0.635023  0.474663
xgboost        0.584793  0.384073




# python evaluation/evaluate.py --mode both

E:\tmp\Fintra AI\ml>python evaluation/evaluate.py --mode both
[info] Loading test data from E:\tmp\Fintra AI\ml\evaluation\..\datasets\processed\test.csv
[info] 1891 test rows

============================================================
Model: baseline
============================================================
Accuracy: 0.997

               precision    recall  f1-score   support

        bills       1.00      0.99      0.99       196
    education       1.00      0.50      0.67         4
entertainment       0.99      0.99      0.99       186
         food       1.00      1.00      1.00       455
   healthcare       1.00      1.00      1.00       179
     shopping       1.00      1.00      1.00       505
    transport       1.00      1.00      1.00       366

     accuracy                           1.00      1891
    macro avg       1.00      0.93      0.95      1891
 weighted avg       1.00      1.00      1.00      1891

Confusion matrix (rows=actual, cols=predicted):
               bills  education  entertainment  food  healthcare  shopping  transport
bills            194          0              1     1           0         0          0
education          0          2              1     0           0         0          1
entertainment      0          0            185     0           0         1          0
food               0          0              0   455           0         0          0
healthcare         0          0              0     0         179         0          0
shopping           0          0              0     0           0       505          0
transport          0          0              0     0           0         0        366

============================================================
Model: random_forest
============================================================
Accuracy: 0.996

               precision    recall  f1-score   support

        bills       0.99      0.99      0.99       196
    education       1.00      0.75      0.86         4
entertainment       0.98      0.99      0.99       186
         food       1.00      1.00      1.00       455
   healthcare       1.00      1.00      1.00       179
     shopping       1.00      1.00      1.00       505
    transport       1.00      1.00      1.00       366

     accuracy                           1.00      1891
    macro avg       1.00      0.96      0.98      1891
 weighted avg       1.00      1.00      1.00      1891

Confusion matrix (rows=actual, cols=predicted):
               bills  education  entertainment  food  healthcare  shopping  transport
bills            195          0              1     0           0         0          0
education          1          3              0     0           0         0          0
entertainment      0          0            185     1           0         0          0
food               0          0              2   453           0         0          0
healthcare         0          0              0     0         179         0          0
shopping           1          0              0     0           0       504          0
transport          0          0              0     1           0         0        365

============================================================
Model: xgboost
============================================================
Accuracy: 0.996

               precision    recall  f1-score   support

        bills       0.99      0.99      0.99       196
    education       0.75      0.75      0.75         4
entertainment       1.00      0.99      0.99       186
         food       0.99      1.00      0.99       455
   healthcare       1.00      1.00      1.00       179
     shopping       1.00      1.00      1.00       505
    transport       1.00      1.00      1.00       366

     accuracy                           1.00      1891
    macro avg       0.96      0.96      0.96      1891
 weighted avg       1.00      1.00      1.00      1891

Confusion matrix (rows=actual, cols=predicted):
               bills  education  entertainment  food  healthcare  shopping  transport
bills            195          0              0     1           0         0          0
education          1          3              0     0           0         0          0
entertainment      0          0            184     1           0         1          0
food               0          1              0   454           0         0          0
healthcare         0          0              0     0         179         0          0
shopping           0          0              0     2           0       503          0
transport          0          0              0     1           0         0        365

============================================================
Summary (random split — includes merchants seen in training)
============================================================
               accuracy  macro_f1
random_forest  0.996298  0.976008
xgboost        0.995769  0.961227
baseline       0.997356  0.950006

============================================================
GROUPED-SPLIT GENERALIZATION CHECK (merchant-level holdout)
============================================================
[info] Daily_Household_Transactions.csv (household): 2176 rows -> 1815 kept, 361 dropped (unmapped/invalid category)
[info] personal_expense_classification.csv (toy): 100 rows -> 100 kept, 0 dropped (unmapped/invalid category)
[info] personal_finance_dataset_8000_extended.csv (finance_8000): 8000 rows -> 8000 kept, 0 dropped (unmapped/invalid category)
[info] Combined total: 9915 rows from 3 source(s)
[info] Category counts:
category
food             2545
shopping         2536
transport        1913
entertainment    1007
bills             996
healthcare        898
education          20
Name: count, dtype: int64
[info] Rows per source:
source
finance_8000    8000
household       1815
toy              100
Name: count, dtype: int64
[info] Train: 7745 rows, 157 merchants
[info] Test:  2170 rows, 41 merchants — NONE overlap with train
[result] baseline        unseen-merchant accuracy=0.671  macro_f1=0.499
[result] random_forest   unseen-merchant accuracy=0.635  macro_f1=0.475
[result] xgboost         unseen-merchant accuracy=0.585  macro_f1=0.384

============================================================
Summary (grouped split — merchants NEVER seen in training)
============================================================
               accuracy  macro_f1
baseline       0.670968  0.498660
random_forest  0.635023  0.474663
xgboost        0.584793  0.384073

============================================================
Side by side (macro F1): known merchants vs unseen merchants
============================================================
               random_split_f1  grouped_split_f1       gap
xgboost               0.961227          0.384073  0.577154
random_forest         0.976008          0.474663  0.501345
baseline              0.950006          0.498660  0.451346








# python inference/predict.py --merchant Swiggy --description "dinner order" --amount 450



{'category': 'food', 'confidence': 0.9725386500358582}


