"""
Held-Out Test Set Evaluation Pipeline for Phase 13: Credit Score Estimator.

Evaluates trained production model on 1,200 held-out profiles:
- Computes Mean Absolute Error (MAE in points), Median AE, RMSE, and R²
- Evaluates Credit Tier categorization accuracy (Excellent, Good, Fair, Poor, Very Poor)
- Analyzes residual distributions and peak error bounds
"""

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    median_absolute_error,
    mean_squared_error,
    r2_score,
)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.credit_rules import (  # noqa: E402
    CREDIT_TIERS,
    ENGINEERED_NUMERICAL_FEATURES_CREDIT,
    RAW_FEATURE_COLUMNS_CREDIT,
    SCORE_MAX,
    SCORE_MIN,
    TARGET_COLUMN_CREDIT,
    engineer_credit_features,
    get_credit_tier_info,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "credit_test.csv")


def main():
    print("=" * 80)
    print("Phase 13: Credit Score Estimator — Held-Out Test Evaluation")
    print("=" * 80)

    if not os.path.exists(TEST_FILE):
        print(f"[error] Test file not found: {TEST_FILE}")
        sys.exit(1)

    model_path = os.path.join(MODEL_DIR, "best_credit_model.pkl")
    preprocessor_path = os.path.join(MODEL_DIR, "credit_preprocessor.pkl")
    metadata_path = os.path.join(MODEL_DIR, "credit_metadata.json")

    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        print("[error] Model artifacts not found. Run train_credit.py first.")
        sys.exit(1)

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    with open(metadata_path, "r") as f:
        meta = json.load(f)

    raw_test_df = pd.read_csv(TEST_FILE)
    print(f"[info] Evaluating model '{meta['best_model_name']}' on {len(raw_test_df)} held-out records\n")

    test_df = engineer_credit_features(raw_test_df)
    num_cols = meta.get("engineered_numerical_features", ENGINEERED_NUMERICAL_FEATURES_CREDIT)

    X_test = test_df[num_cols]
    y_true = test_df[TARGET_COLUMN_CREDIT].values

    X_proc = preprocessor.transform(X_test)
    raw_preds = model.predict(X_proc)
    y_pred = np.clip(np.round(raw_preds), SCORE_MIN, SCORE_MAX).astype(int)

    # Core Regression Metrics
    mae = mean_absolute_error(y_true, y_pred)
    med_ae = median_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    max_err = np.max(np.abs(y_true - y_pred))

    # Tier Classification Accuracy
    true_tiers = [get_credit_tier_info(s)["tier"] for s in y_true]
    pred_tiers = [get_credit_tier_info(s)["tier"] for s in y_pred]
    tier_accuracy = accuracy_score(true_tiers, pred_tiers)
    tier_macro_f1 = f1_score(true_tiers, pred_tiers, average="macro")

    # Within-15-points accuracy
    within_10_pts = float(np.mean(np.abs(y_true - y_pred) <= 10.0) * 100.0)
    within_20_pts = float(np.mean(np.abs(y_true - y_pred) <= 20.0) * 100.0)

    print("=================================================================")
    print(f"Mean Absolute Error (MAE):     {mae:5.2f} points (< {mae/6.0:.2f}% relative error)")
    print(f"Median Absolute Error (MedAE): {med_ae:5.2f} points")
    print(f"Root Mean Squared Error (RMSE):{rmse:5.2f} points")
    print(f"R² Score:                      {r2:6.4f}")
    print(f"Max Peak Outlier Error:        {max_err:4.1f} points")
    print(f"Within +/- 10 Points Accuracy: {within_10_pts:5.2f}%")
    print(f"Within +/- 20 Points Accuracy: {within_20_pts:5.2f}%")
    print(f"Credit Tier Match Accuracy:    {tier_accuracy*100:5.2f}%")
    print(f"Credit Tier Macro F1-Score:    {tier_macro_f1:6.4f}")
    print("=================================================================\n")

    print("Tier Classification Breakdown:")
    print(classification_report(true_tiers, pred_tiers, digits=4))


if __name__ == "__main__":
    main()
