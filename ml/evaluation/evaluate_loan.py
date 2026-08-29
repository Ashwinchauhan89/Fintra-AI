"""
Held-Out Test Set Evaluation Pipeline for Phase 12: Loan Eligibility & Credit Risk.

Evaluates trained production model on 1,199 held-out applications:
- Computes ROC-AUC, PR-AUC, Confusion Matrix, Precision, Recall, and Macro F1
- Analyzes False Positive Rate (Bad loans approved) vs False Negative Rate
- Evaluates Brier Score and Probability Calibration
- Evaluates Risk Tier classification performance
"""

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.loan_rules import (  # noqa: E402
    ENGINEERED_CATEGORICAL_FEATURES_LOAN,
    ENGINEERED_NUMERICAL_FEATURES_LOAN,
    RAW_FEATURE_COLUMNS_LOAN,
    TARGET_COLUMN_LOAN,
    engineer_loan_features,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "loan_test.csv")


def main():
    print("=" * 80)
    print("Phase 12: Loan Eligibility & Credit Risk — Held-Out Test Evaluation")
    print("=" * 80)

    if not os.path.exists(TEST_FILE):
        print(f"[error] Test file not found: {TEST_FILE}")
        sys.exit(1)

    model_path = os.path.join(MODEL_DIR, "best_loan_model.pkl")
    preprocessor_path = os.path.join(MODEL_DIR, "loan_preprocessor.pkl")
    metadata_path = os.path.join(MODEL_DIR, "loan_metadata.json")

    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        print("[error] Model artifacts not found. Run train_loan.py first.")
        sys.exit(1)

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    with open(metadata_path, "r") as f:
        meta = json.load(f)

    raw_test_df = pd.read_csv(TEST_FILE)
    print(f"[info] Evaluating model '{meta['best_model_name']}' on {len(raw_test_df)} held-out applications\n")

    test_df = engineer_loan_features(raw_test_df)

    num_cols = meta.get("engineered_numerical_features", ENGINEERED_NUMERICAL_FEATURES_LOAN)
    cat_cols = meta.get("engineered_categorical_features", ENGINEERED_CATEGORICAL_FEATURES_LOAN)
    optimal_thresh = meta.get("optimal_threshold", 0.50)

    X_test = test_df[num_cols + cat_cols]
    y_true = test_df[TARGET_COLUMN_LOAN].values

    X_proc = preprocessor.transform(X_test)

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_proc)[:, 1]
    else:
        probs = model.decision_function(X_proc)

    y_pred = (probs >= optimal_thresh).astype(int)

    # Core Metrics
    roc_auc = roc_auc_score(y_true, probs)
    pr_auc = average_precision_score(y_true, probs)
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro")
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    brier = brier_score_loss(y_true, probs)

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    fpr = float(fp / max(1, fp + tn))  # False Positive Rate (Risky loans wrongly approved)

    print("=================================================================")
    print(f"ROC-AUC Score:                 {roc_auc:6.4f}")
    print(f"PR-AUC (Average Precision):    {pr_auc:6.4f}")
    print(f"Macro F1-Score:                {macro_f1:6.4f}")
    print(f"Accuracy:                      {acc*100:6.2f}%")
    print(f"Precision (Approval Safety):   {precision*100:6.2f}%")
    print(f"Recall (Eligible Capture):     {recall*100:6.2f}%")
    print(f"False Positive Rate (Bad Appr):{fpr*100:6.2f}%")
    print(f"Brier Calibration Loss:        {brier:6.4f}")
    print(f"Applied Decision Threshold:    {optimal_thresh:6.3f}")
    print("=================================================================\n")

    print("Confusion Matrix:")
    print(f"  True Negatives (Correctly Declined):  {tn}")
    print(f"  False Positives (Risky Bad Approved): {fp} (FPR: {fpr*100:.2f}%)")
    print(f"  False Negatives (Missed Eligible):    {fn}")
    print(f"  True Positives (Correctly Approved):  {tp}\n")

    print("Classification Report:")
    print(classification_report(y_true, y_pred, target_names=["DECLINED", "APPROVED"], digits=4))


if __name__ == "__main__":
    main()
