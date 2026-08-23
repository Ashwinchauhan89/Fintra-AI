"""
Multi-Model Training & Benchmark Pipeline for Savings & Goal Prediction (Phases 6 & 11).

Trains, cross-validates, and compares 6 regression architectures:
1. Ridge (L2 Linear Baseline)
2. Random Forest Regressor
3. Extra Trees Regressor
4. Gradient Boosting Regressor
5. XGBoost Regressor
6. Soft-Weighted Stacking Ensemble

Selects and exports the highest-performing model based on cross-validated R² and MAE.
"""

import json
import os
import sys
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.goal_rules import FEATURE_COLUMNS_SAVINGS, GOAL_PRESETS, MultiOutputVotingRegressor  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TRAIN_FILE = os.path.join(PROCESSED_DIR, "goals_train.csv")


def build_preprocessor(num_cols: list, cat_cols: list) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ]
    )


def evaluate_cv(pipeline, X: pd.DataFrame, y: pd.DataFrame, n_splits: int = 5) -> Tuple[float, float, float]:
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    mae_scores = []
    r2_scores = []
    max_err_scores = []

    for train_idx, val_idx in kf.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_val)

        mae_scores.append(mean_absolute_error(y_val, preds))
        r2_scores.append(r2_score(y_val, preds, multioutput="uniform_average"))
        max_err_scores.append(np.max(np.abs(y_val.values - preds)))

    return float(np.mean(mae_scores)), float(np.mean(r2_scores)), float(np.mean(max_err_scores))


def train_models():
    print("=" * 75)
    print("Multi-Model Training & Benchmark Suite: Phase 6 Savings & Phase 11 Goal Engine")
    print("=" * 75)

    if not os.path.exists(TRAIN_FILE):
        raise FileNotFoundError(f"Training dataset not found at {TRAIN_FILE}. Run preprocessing/preprocess_goals.py first.")

    df = pd.read_csv(TRAIN_FILE)
    num_cols = FEATURE_COLUMNS_SAVINGS + ["target_amount", "current_saved", "intended_months", "annual_return_pct"]
    cat_cols = ["goal_type"]
    target_cols = ["target_monthly_savings", "target_completion_months", "target_required_savings"]

    X = df[num_cols + cat_cols]
    y = df[target_cols]

    preprocessor = build_preprocessor(num_cols, cat_cols)
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 1. Candidate Multi-Output Regressors
    models_dict = {
        "ridge": MultiOutputRegressor(Ridge(alpha=1.0)),
        "random_forest": MultiOutputRegressor(
            RandomForestRegressor(n_estimators=150, max_depth=16, min_samples_split=3, random_state=42, n_jobs=-1)
        ),
        "extra_trees": MultiOutputRegressor(
            ExtraTreesRegressor(n_estimators=200, max_depth=18, min_samples_split=2, random_state=42, n_jobs=-1)
        ),
        "gradient_boosting": MultiOutputRegressor(
            GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.05, random_state=42)
        ),
        "xgboost": MultiOutputRegressor(
            XGBRegressor(n_estimators=250, max_depth=6, learning_rate=0.04, subsample=0.9, colsample_bytree=0.9, random_state=42, n_jobs=-1)
        ),
    }

    # Stacking Soft-Voting Ensemble
    models_dict["ensemble"] = MultiOutputVotingRegressor(
        estimators=[
            ("et", MultiOutputRegressor(ExtraTreesRegressor(n_estimators=200, max_depth=18, min_samples_split=2, random_state=42, n_jobs=-1))),
            ("xgb", MultiOutputRegressor(XGBRegressor(n_estimators=250, max_depth=6, learning_rate=0.04, subsample=0.9, colsample_bytree=0.9, random_state=42, n_jobs=-1))),
            ("gb", MultiOutputRegressor(GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.05, random_state=42))),
        ],
        weights=[0.50, 0.30, 0.20],
    )

    results = {}
    fitted_pipelines = {}

    print(f"{'Model Candidate':<22} | {'5-Fold CV MAE':<15} | {'5-Fold CV R2':<12} | {'Max Peak Error'}")
    print("-" * 75)

    for name, model in models_dict.items():
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", model),
        ])
        mae, r2, max_err = evaluate_cv(pipeline, X, y, n_splits=5)
        results[name] = {
            "cv_mae": round(mae, 2),
            "cv_r2": round(r2, 4),
            "cv_max_error": round(max_err, 2),
        }
        print(f"{name:<22} | INR {mae:>8,.2f} | {r2:>10.4f} | INR {max_err:>10,.2f}")

        # Fit on whole train dataset and save individual candidate artifact
        pipeline.fit(X, y)
        fitted_pipelines[name] = pipeline

        save_path = os.path.join(MODEL_DIR, f"goals_{name}.pkl")
        joblib.dump(pipeline, save_path)

    print("-" * 75)

    # 2. Select Best Production Model
    best_name = min(results, key=lambda k: (results[k]["cv_mae"], -results[k]["cv_r2"]))
    best_pipeline = fitted_pipelines[best_name]

    print(f"[selection] Best Selected Production Model: '{best_name.upper()}'")
    print(f"            * CV MAE: INR {results[best_name]['cv_mae']:,.2f}")
    print(f"            * CV R2 : {results[best_name]['cv_r2']:.4f}")

    best_model_path = os.path.join(MODEL_DIR, "savings_best_model.pkl")
    joblib.dump(best_pipeline, best_model_path)
    print(f"[done] Saved Best Production Model -> {best_model_path}")

    # Save training metadata
    meta = {
        "selected_best_model": best_name,
        "num_columns": num_cols,
        "cat_columns": cat_cols,
        "target_columns": target_cols,
        "models_benchmarks": results,
    }
    meta_path = os.path.join(MODEL_DIR, "goals_train_metrics.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    with open(os.path.join(MODEL_DIR, "goals_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"[done] Saved benchmark report -> {meta_path}")
    print("=" * 75)


if __name__ == "__main__":
    train_models()
