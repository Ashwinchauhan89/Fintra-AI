"""
Multi-Model Training & Advanced Benchmark Pipeline for Phase 10: Investment Recommendation.

Features:
- High-signal financial domain feature engineering (ratios, interaction indices, log magnitudes)
- Multi-architecture benchmark:
  1. Multi-Output Ridge (L2 Linear Baseline)
  2. Multi-Output Random Forest (Tuned)
  3. Multi-Output Extra Trees (Deep randomized ensemble)
  4. Multi-Output Gradient Boosting
  5. Multi-Output XGBoost (Colsample & Subsample regularized)
  6. Multi-Output SLSQP Constrained Stacking Ensemble
- Multi-metric composite scoring (Mean MAE, Median AE, R², Max Peak Error)
- Strict Simplex projection constraint verification
"""

import json
import os
import sys
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, median_absolute_error, r2_score
from sklearn.model_selection import KFold
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler, StandardScaler
from xgboost import XGBRegressor

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.investment_rules import (  # noqa: E402
    ENGINEERED_CATEGORICAL_FEATURES,
    ENGINEERED_NUMERICAL_FEATURES,
    FEATURE_COLUMNS_INVESTMENT,
    TARGET_COLUMNS_INVESTMENT,
    ConstrainedMultiOutputVotingRegressor,
    engineer_investment_features,
    normalize_to_simplex,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TRAIN_FILE = os.path.join(PROCESSED_DIR, "investment_train.csv")


def build_preprocessor(num_cols: list, cat_cols: list) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", RobustScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ]
    )


def evaluate_cv(model, X: np.ndarray, y: np.ndarray, n_splits: int = 5) -> Tuple[float, float, float, float]:
    """
    Evaluates multi-output model using 5-Fold cross-validation.
    Returns: (mean_mae, median_ae, mean_r2, max_error)
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    mae_scores = []
    med_scores = []
    r2_scores = []
    max_err_scores = []

    for train_idx, val_idx in kf.split(X, y):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        # Fit model on training fold
        model.fit(X_train, y_train)
        preds = model.predict(X_val)

        # Ensure simplex projection on predictions
        preds = normalize_to_simplex(preds) * 100.0

        fold_mae = mean_absolute_error(y_val, preds)
        fold_med = median_absolute_error(y_val, preds)
        fold_r2 = r2_score(y_val, preds)
        fold_max_err = np.max(np.abs(y_val - preds))

        mae_scores.append(fold_mae)
        med_scores.append(fold_med)
        r2_scores.append(fold_r2)
        max_err_scores.append(fold_max_err)

    return (
        float(np.mean(mae_scores)),
        float(np.mean(med_scores)),
        float(np.mean(r2_scores)),
        float(np.max(max_err_scores)),
    )


def main():
    print("=" * 75)
    print("Phase 10: Advanced Multi-Model Investment Recommendation Benchmark")
    print("=" * 75)

    if not os.path.exists(TRAIN_FILE):
        print(f"[error] Train file not found: {TRAIN_FILE}. Run preprocess_investment.py first.")
        sys.exit(1)

    raw_df = pd.read_csv(TRAIN_FILE)
    print(f"[info] Loaded {len(raw_df)} training records. Engineering financial domain features...")

    df = engineer_investment_features(raw_df)

    cat_cols = ENGINEERED_CATEGORICAL_FEATURES
    num_cols = ENGINEERED_NUMERICAL_FEATURES

    X = df[num_cols + cat_cols]
    y = df[TARGET_COLUMNS_INVESTMENT].values

    # Preprocessor fit & transform
    preprocessor = build_preprocessor(num_cols, cat_cols)
    X_proc = preprocessor.fit_transform(X)

    # Define High-Capacity Tuned Candidate Models
    candidates = {
        "ridge": MultiOutputRegressor(Ridge(alpha=0.5)),
        "random_forest": MultiOutputRegressor(
            RandomForestRegressor(n_estimators=200, max_depth=18, min_samples_split=3, random_state=42, n_jobs=-1)
        ),
        "extra_trees": MultiOutputRegressor(
            ExtraTreesRegressor(n_estimators=250, max_depth=20, min_samples_split=2, random_state=42, n_jobs=-1)
        ),
        "gradient_boosting": MultiOutputRegressor(
            GradientBoostingRegressor(n_estimators=250, max_depth=6, learning_rate=0.05, random_state=42)
        ),
        "xgboost": MultiOutputRegressor(
            XGBRegressor(
                n_estimators=300,
                max_depth=7,
                learning_rate=0.03,
                subsample=0.90,
                colsample_bytree=0.85,
                reg_alpha=0.05,
                reg_lambda=0.80,
                random_state=42,
                n_jobs=-1,
            )
        ),
    }

    # SLSQP-Optimized Stacking Ensemble
    ensemble_base = [
        ("et", MultiOutputRegressor(ExtraTreesRegressor(n_estimators=200, max_depth=18, random_state=42, n_jobs=-1))),
        ("xgb", MultiOutputRegressor(XGBRegressor(n_estimators=250, max_depth=6, learning_rate=0.04, random_state=42, n_jobs=-1))),
        ("rf", MultiOutputRegressor(RandomForestRegressor(n_estimators=180, max_depth=16, random_state=42, n_jobs=-1))),
        ("gb", MultiOutputRegressor(GradientBoostingRegressor(n_estimators=180, max_depth=5, random_state=42))),
    ]
    candidates["slsqp_stacking_ensemble"] = ConstrainedMultiOutputVotingRegressor(
        estimators=ensemble_base, optimize_weights=True
    )

    print("\n[info] Running 5-Fold Stratified Cross-Validation on all Candidates...")
    leaderboard = []

    for name, model in candidates.items():
        mae, med_ae, r2, max_err = evaluate_cv(model, X_proc, y, n_splits=5)
        
        # Composite score penalizing both mean error and extreme peak deviations
        composite_score = mae + 0.05 * max_err
        
        leaderboard.append({
            "model": name,
            "cv_mae_pct": round(mae, 4),
            "cv_median_ae_pct": round(med_ae, 4),
            "cv_r2": round(r2, 4),
            "max_peak_error_pct": round(max_err, 2),
            "composite_score": round(composite_score, 4),
        })
        print(f"  [{name:24s}] MAE: {mae:6.4f}% | MedAE: {med_ae:6.4f}% | R²: {r2:6.4f} | MaxErr: {max_err:5.2f}% | Score: {composite_score:6.4f}")

    leaderboard_df = pd.DataFrame(leaderboard).sort_values("composite_score")
    best_row = leaderboard_df.iloc[0]
    best_name = best_row["model"]

    print("\n" + "=" * 75)
    print(f"[result] Optimal Selected Production Model: '{best_name}'")
    print(f"         CV Mean MAE:     {best_row['cv_mae_pct']}%")
    print(f"         CV Median AE:    {best_row['cv_median_ae_pct']}%")
    print(f"         CV R² Score:     {best_row['cv_r2']}")
    print(f"         Max Peak Error:  {best_row['max_peak_error_pct']}%")
    print("=" * 75)

    # Train winning architecture on complete training set
    best_model = candidates[best_name]
    best_model.fit(X_proc, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    model_save_path = os.path.join(MODEL_DIR, "best_investment_model.pkl")
    preprocessor_save_path = os.path.join(MODEL_DIR, "investment_preprocessor.pkl")
    metadata_save_path = os.path.join(MODEL_DIR, "investment_metadata.json")

    joblib.dump(best_model, model_save_path)
    joblib.dump(preprocessor, preprocessor_save_path)

    metadata = {
        "best_model_name": best_name,
        "raw_feature_columns": FEATURE_COLUMNS_INVESTMENT,
        "engineered_numerical_features": num_cols,
        "engineered_categorical_features": cat_cols,
        "target_columns": TARGET_COLUMNS_INVESTMENT,
        "cv_leaderboard": leaderboard,
        "num_training_samples": len(df),
        "best_model_metrics": best_row.to_dict(),
    }
    with open(metadata_save_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[done] Serialized production model -> {model_save_path}")
    print(f"[done] Serialized preprocessor      -> {preprocessor_save_path}")
    print(f"[done] Serialized metadata          -> {metadata_save_path}")


if __name__ == "__main__":
    main()
