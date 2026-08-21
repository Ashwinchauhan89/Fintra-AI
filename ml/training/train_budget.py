"""
Training Pipeline for Budget Recommendation & Allocation Models (Phase 5).

Trains and evaluates multi-output regression models (Ridge, Random Forest, XGBoost)
to predict optimal category-wise budget allocations and savings amounts.
"""

import json
import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.budget_rules import ROADMAP_CATEGORIES  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TRAIN_FILE = os.path.join(PROCESSED_DIR, "budget_train.csv")


def get_feature_and_target_columns():
    num_features = ["monthly_income", "savings_target_pct", "debt_to_income_ratio"]
    hist_features = [f"hist_ratio_{cat}" for cat in ROADMAP_CATEGORIES]
    cat_features = ["lifestyle"]
    
    target_columns = [f"target_budget_{cat}" for cat in ROADMAP_CATEGORIES] + ["target_budget_savings"]
    return num_features + hist_features, cat_features, target_columns


def build_preprocessor(num_cols, cat_cols):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ]
    )
    return preprocessor


def evaluate_cv(pipeline, X, y, n_splits=5):
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    mae_scores = []
    r2_scores = []

    for train_idx, val_idx in kf.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_val)

        mae_scores.append(mean_absolute_error(y_val, preds))
        r2_scores.append(r2_score(y_val, preds, multioutput="uniform_average"))

    return float(np.mean(mae_scores)), float(np.mean(r2_scores))


def train_models():
    print("=" * 60)
    print("Training Pipeline: Phase 5 Budget Recommendation Engine")
    print("=" * 60)

    if not os.path.exists(TRAIN_FILE):
        raise FileNotFoundError(f"Training dataset not found at {TRAIN_FILE}. Run preprocessing/preprocess_budget.py first.")

    df = pd.read_csv(TRAIN_FILE)
    num_cols, cat_cols, target_cols = get_feature_and_target_columns()

    X = df[num_cols + cat_cols]
    y = df[target_cols]

    preprocessor = build_preprocessor(num_cols, cat_cols)

    candidate_models = {
        "ridge": MultiOutputRegressor(Ridge(alpha=1.0)),
        "random_forest": MultiOutputRegressor(
            RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
        ),
        "xgboost": MultiOutputRegressor(
            XGBRegressor(n_estimators=120, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
        ),
    }

    results = {}
    fitted_pipelines = {}

    for name, model in candidate_models.items():
        print(f"[cv] Training & Cross-Validating {name}...")
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", model),
        ])
        mae, r2 = evaluate_cv(pipeline, X, y, n_splits=5)
        results[name] = {"cv_mae": mae, "cv_r2": r2}
        print(f"     -> CV Mean MAE: INR {mae:,.2f} | CV R2: {r2:.4f}")

        # Fit on entire train dataset
        pipeline.fit(X, y)
        fitted_pipelines[name] = pipeline

    # Select best model by CV R2
    best_name = max(results, key=lambda k: results[k]["cv_r2"])
    best_pipeline = fitted_pipelines[best_name]
    print("-" * 60)
    print(f"[result] Best Model: {best_name.upper()} (R2: {results[best_name]['cv_r2']:.4f}, MAE: INR {results[best_name]['cv_mae']:,.2f})")

    os.makedirs(MODEL_DIR, exist_ok=True)
    best_model_path = os.path.join(MODEL_DIR, "budget_recommender.pkl")
    joblib.dump(best_pipeline, best_model_path)
    print(f"[done] Saved best model artifact -> {best_model_path}")

    # Save metadata
    meta = {
        "best_model": best_name,
        "feature_cols": num_cols + cat_cols,
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "target_cols": target_cols,
        "metrics": results,
    }
    meta_path = os.path.join(MODEL_DIR, "budget_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[done] Saved training metadata -> {meta_path}")
    print("=" * 60)


if __name__ == "__main__":
    train_models()
