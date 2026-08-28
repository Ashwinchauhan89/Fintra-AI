"""
Held-Out Test Set Evaluation Pipeline for Phase 10: Investment Recommendation.

Evaluates the trained production model on 1,199 held-out user profiles:
- Applies domain feature engineering pipeline
- Computes Mean Absolute Error (MAE), Median AE, RMSE, and R² for each asset class
- Validates Simplex constraint adherence (sum of weights = 100.00%)
- Analyzes peak error distributions and outlier bounds
"""

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, median_absolute_error, mean_squared_error, r2_score

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.investment_rules import (  # noqa: E402
    ENGINEERED_CATEGORICAL_FEATURES,
    ENGINEERED_NUMERICAL_FEATURES,
    TARGET_COLUMNS_INVESTMENT,
    engineer_investment_features,
    normalize_to_simplex,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "investment_test.csv")


def main():
    print("=" * 75)
    print("Phase 10: Investment Recommendation — Held-Out Test Evaluation")
    print("=" * 75)

    if not os.path.exists(TEST_FILE):
        print(f"[error] Test file not found: {TEST_FILE}")
        sys.exit(1)

    model_path = os.path.join(MODEL_DIR, "best_investment_model.pkl")
    preprocessor_path = os.path.join(MODEL_DIR, "investment_preprocessor.pkl")
    metadata_path = os.path.join(MODEL_DIR, "investment_metadata.json")

    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        print("[error] Trained model or preprocessor not found. Run train_investment.py first.")
        sys.exit(1)

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    with open(metadata_path, "r") as f:
        meta = json.load(f)

    raw_test_df = pd.read_csv(TEST_FILE)
    print(f"[info] Evaluating model '{meta['best_model_name']}' on {len(raw_test_df)} held-out profiles\n")

    test_df = engineer_investment_features(raw_test_df)

    num_cols = meta.get("engineered_numerical_features", ENGINEERED_NUMERICAL_FEATURES)
    cat_cols = meta.get("engineered_categorical_features", ENGINEERED_CATEGORICAL_FEATURES)

    X_test = test_df[num_cols + cat_cols]
    y_true = test_df[TARGET_COLUMNS_INVESTMENT].values

    X_proc = preprocessor.transform(X_test)
    y_pred_raw = model.predict(X_proc)

    # Simplex normalization to guarantee sum = 100.0%
    y_pred = normalize_to_simplex(y_pred_raw) * 100.0

    # Overall multi-output metrics
    overall_mae = mean_absolute_error(y_true, y_pred)
    overall_med_ae = median_absolute_error(y_true, y_pred)
    overall_rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    overall_r2 = r2_score(y_true, y_pred)
    max_peak_error = np.max(np.abs(y_true - y_pred))

    print("=" * 65)
    print(f"Overall Multi-Target Allocation MAE:       {overall_mae:6.4f}%")
    print(f"Overall Multi-Target Allocation Median AE: {overall_med_ae:6.4f}%")
    print(f"Overall Multi-Target Allocation RMSE:      {overall_rmse:6.4f}%")
    print(f"Overall Multi-Target Allocation R²:        {overall_r2:6.4f}")
    print(f"Overall Max Single-Target Peak Error:      {max_peak_error:6.2f}%")
    print("=" * 65 + "\n")

    # Granular breakdown by asset class
    breakdown = []
    for idx, target in enumerate(TARGET_COLUMNS_INVESTMENT):
        t_true = y_true[:, idx]
        t_pred = y_pred[:, idx]
        t_mae = mean_absolute_error(t_true, t_pred)
        t_med = median_absolute_error(t_true, t_pred)
        t_r2 = r2_score(t_true, t_pred)
        t_max = np.max(np.abs(t_true - t_pred))
        breakdown.append({
            "Asset Class": target.replace("_pct", "").upper(),
            "MAE (%)": f"{t_mae:.3f}%",
            "Median AE (%)": f"{t_med:.3f}%",
            "R² Score": f"{t_r2:.4f}",
            "Max Error (%)": f"{t_max:.2f}%",
            "Mean Target (%)": f"{np.mean(t_pred):.2f}%",
        })

    breakdown_df = pd.DataFrame(breakdown)
    print("Asset Class Granular Breakdown:")
    print(breakdown_df.to_string(index=False))

    # Constraint Check: Sum of allocations
    row_sums = np.sum(y_pred, axis=1)
    sum_violation = np.max(np.abs(row_sums - 100.0))
    print(f"\n[constraint check] Max allocation sum deviation from 100.0%: {sum_violation:.6f}%")
    if sum_violation < 1e-4:
        print("  -> PASSED: All test predictions sum strictly to 100.00%")
    else:
        print("  -> WARNING: Non-zero simplex violation detected.")


if __name__ == "__main__":
    main()
