"""
Training Pipeline for Financial Time-Series Forecasting (Phases 4 & 18).

Trains baseline, linear, and non-linear ensemble models using expanding-window
TimeSeriesSplit cross-validation, benchmarks candidates on MAE/RMSE/R2, and
serializes the best model and category forecasters.
"""

import argparse
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from models.baseline_forecaster import SeasonalBaselineRegressor  # noqa: E402
from utils.timeseries_features import (  # noqa: E402
    ROADMAP_CATEGORIES,
    extract_forecasting_feature_names,
)

DEFAULT_TRAIN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "datasets", "processed", "forecasting_train.csv",
)
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
CV_FOLDS = 5


def build_ridge_pipeline() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", Ridge(alpha=10.0, random_state=42)),
    ])


def build_random_forest_pipeline() -> Pipeline:
    return Pipeline([
        ("regressor", RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )),
    ])


def build_xgboost_pipeline() -> Pipeline | None:
    if not HAS_XGBOOST:
        return None
    return Pipeline([
        ("regressor", XGBRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )),
    ])


from sklearn.base import BaseEstimator, RegressorMixin, clone

def evaluate_timeseries_cv(name: str, pipeline, X: pd.DataFrame, y: pd.Series) -> dict:
    """
    Evaluates a candidate model using expanding-window TimeSeriesSplit.
    """
    tscv = TimeSeriesSplit(n_splits=CV_FOLDS)
    mae_list, rmse_list, r2_list = [], [], []

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_va, y_va = X.iloc[val_idx], y.iloc[val_idx]

        model = clone(pipeline)
        model.fit(X_tr, y_tr)
        preds = np.maximum(0.0, model.predict(X_va))

        mae_list.append(mean_absolute_error(y_va, preds))
        rmse_list.append(np.sqrt(mean_squared_error(y_va, preds)))
        r2_list.append(r2_score(y_va, preds))

    results = {
        "mae": float(np.mean(mae_list)),
        "rmse": float(np.mean(rmse_list)),
        "r2": float(np.mean(r2_list)),
    }
    print(f"[cv] {name:<18} | MAE: INR {results['mae']:>10.2f} | RMSE: INR {results['rmse']:>10.2f} | R2: {results['r2']:>6.3f}")
    return results


def train_category_forecasters(train_df: pd.DataFrame, feature_cols: list[str]) -> dict:
    """
    Trains specialized regressors for each individual expense category.
    """
    category_models = {}
    X = train_df[feature_cols]

    for cat in ROADMAP_CATEGORIES:
        cat_col = f"{cat}_spend"
        if cat_col in train_df.columns and train_df[cat_col].sum() > 0:
            y_cat = train_df[cat_col]
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                random_state=42,
                n_jobs=-1,
            )
            model.fit(X, y_cat)
            category_models[cat] = model
    return category_models


def main():
    parser = argparse.ArgumentParser(description="Train financial time-series forecasting models")
    parser.add_argument("--train", default=DEFAULT_TRAIN_PATH)
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()

    os.makedirs(args.model_dir, exist_ok=True)

    print(f"[info] Loading training data from {args.train}...")
    df = pd.read_csv(args.train)

    feature_cols = extract_forecasting_feature_names()
    available_features = [c for c in feature_cols if c in df.columns]
    X = df[available_features]
    y = df["total_spend"]

    print(f"[info] Training dataset: {len(df)} samples, {len(available_features)} engineered features")
    print(f"[info] Running {CV_FOLDS}-fold expanding-window TimeSeriesSplit cross-validation...\n")

    candidates = {
        "baseline_seasonal": SeasonalBaselineRegressor(),
        "ridge": build_ridge_pipeline(),
        "random_forest": build_random_forest_pipeline(),
    }
    if HAS_XGBOOST:
        candidates["xgboost"] = build_xgboost_pipeline()

    cv_scores = {}
    for name, pipeline in candidates.items():
        cv_scores[name] = evaluate_timeseries_cv(name, pipeline, X, y)

    # Fit all models on the entire training set and save them
    print("\n[info] Fitting final models on full training data...")
    for name, pipeline in candidates.items():
        pipeline.fit(X, y)
        model_path = os.path.join(args.model_dir, f"forecasting_{name}.pkl")
        joblib.dump(pipeline, model_path)
        print(f"[done] Saved {name} -> {model_path}")

    # Best model selection by lowest CV MAE
    best_name = min(cv_scores, key=lambda k: cv_scores[k]["mae"])
    best_pipeline = candidates[best_name]
    best_model_path = os.path.join(args.model_dir, "forecasting_best_model.pkl")
    joblib.dump(best_pipeline, best_model_path)

    # Fit and save category-level forecasters
    print("[info] Training category-wise forecasters...")
    category_models = train_category_forecasters(df, available_features)
    cat_models_path = os.path.join(args.model_dir, "forecasting_categories.pkl")
    joblib.dump(category_models, cat_models_path)
    print(f"[done] Saved {len(category_models)} category models -> {cat_models_path}")

    # Save training metrics summary
    metrics_path = os.path.join(args.model_dir, "forecasting_train_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump({
            "cv_scores": cv_scores,
            "best_model": best_name,
            "best_cv_mae": cv_scores[best_name]["mae"],
            "features": available_features,
            "trained_samples": len(df),
        }, f, indent=2)

    print(f"\n[result] Best Forecasting Model: '{best_name}' (CV MAE: INR {cv_scores[best_name]['mae']:.2f})")
    print(f"[result] Best model saved as {best_model_path}")


if __name__ == "__main__":
    main()
