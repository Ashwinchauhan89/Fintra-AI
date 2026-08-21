"""
Enhanced Multi-Model Training & Benchmark Pipeline for Budget Recommendation (Phase 5).

Trains, cross-validates, and rigorously evaluates multiple candidate models:
1. Ridge Regressor (L2 Linear Baseline)
2. Random Forest Regressor (Bagging Ensemble)
3. Extra Trees Regressor (Extremely Randomized Trees)
4. Gradient Boosting Regressor (Sequential Boosting)
5. XGBoost Regressor (Extreme Gradient Boosting)
6. Voting Ensemble Regressor (Soft Weighted Multi-Model Stacking)

Selects and exports the highest-performing production model based on cross-validated R² and MAE.
"""

import json
import os
import sys
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
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
from utils.budget_rules import ROADMAP_CATEGORIES  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TRAIN_FILE = os.path.join(PROCESSED_DIR, "budget_train.csv")


class MultiOutputVotingRegressor(BaseEstimator, RegressorMixin):
    """
    Weighted ensemble combining predictions of multiple multi-output regressors.
    """
    def __init__(self, estimators=None, weights=None):
        self.estimators = estimators or []
        self.weights = weights

    def fit(self, X, y):
        from sklearn.base import clone
        self.estimators_ = []
        for name, est in self.estimators:
            fitted_est = clone(est)
            fitted_est.fit(X, y)
            self.estimators_.append((name, fitted_est))
        return self

    def predict(self, X):
        preds = [est.predict(X) for name, est in self.estimators_]
        if self.weights is not None:
            norm_weights = np.array(self.weights) / np.sum(self.weights)
            weighted_preds = sum(w * p for w, p in zip(norm_weights, preds))
            return weighted_preds
        return np.mean(preds, axis=0)


def get_feature_and_target_columns() -> Tuple[list, list, list]:
    num_features = ["monthly_income", "savings_target_pct", "debt_to_income_ratio"]
    hist_features = [f"hist_ratio_{cat}" for cat in ROADMAP_CATEGORIES]
    cat_features = ["lifestyle"]
    target_columns = [f"target_budget_{cat}" for cat in ROADMAP_CATEGORIES] + ["target_budget_savings"]
    return num_features + hist_features, cat_features, target_columns


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
    print("=" * 70)
    print("Multi-Model Training & Benchmark Suite: Phase 5 Budget Engine")
    print("=" * 70)

    if not os.path.exists(TRAIN_FILE):
        raise FileNotFoundError(f"Training dataset not found at {TRAIN_FILE}. Run preprocessing/preprocess_budget.py first.")

    df = pd.read_csv(TRAIN_FILE)
    num_cols, cat_cols, target_cols = get_feature_and_target_columns()

    X = df[num_cols + cat_cols]
    y = df[target_cols]

    preprocessor = build_preprocessor(num_cols, cat_cols)

    # 1. Candidate Base Regressors with optimized hyper-parameters
    models_dict = {
        "ridge": MultiOutputRegressor(Ridge(alpha=1.0)),
        "random_forest": MultiOutputRegressor(
            RandomForestRegressor(n_estimators=150, max_depth=16, min_samples_split=3, random_state=42, n_jobs=-1)
        ),
        "extra_trees": MultiOutputRegressor(
            ExtraTreesRegressor(n_estimators=200, max_depth=18, min_samples_split=2, random_state=42, n_jobs=-1)
        ),
        "gradient_boosting": MultiOutputRegressor(
            GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.06, random_state=42)
        ),
        "xgboost": MultiOutputRegressor(
            XGBRegressor(
                n_estimators=250,
                max_depth=6,
                learning_rate=0.04,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=42,
                n_jobs=-1,
            )
        ),
    }

    # 2. Add Stacking Voting Ensemble
    models_dict["ensemble"] = MultiOutputVotingRegressor(
        estimators=[
            ("et", MultiOutputRegressor(ExtraTreesRegressor(n_estimators=200, max_depth=18, min_samples_split=2, random_state=42, n_jobs=-1))),
            ("gb", MultiOutputRegressor(GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.06, random_state=42))),
            ("xgb", MultiOutputRegressor(XGBRegressor(n_estimators=250, max_depth=6, learning_rate=0.04, subsample=0.9, colsample_bytree=0.9, random_state=42, n_jobs=-1))),
        ],
        weights=[0.50, 0.30, 0.20],
    )

    results = {}
    fitted_pipelines = {}

    print(f"{'Model Name':<22} | {'5-Fold CV MAE':<15} | {'5-Fold CV R2':<12} | {'Max Peak Error'}")
    print("-" * 70)

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

        # Fit on whole train dataset and save individual model
        pipeline.fit(X, y)
        fitted_pipelines[name] = pipeline

        os.makedirs(MODEL_DIR, exist_ok=True)
        model_save_path = os.path.join(MODEL_DIR, f"budget_{name}.pkl")
        joblib.dump(pipeline, model_save_path)

    print("-" * 70)

    # 3. Rigorous Selection Strategy: Highest R2 with lowest MAE
    best_name = min(results, key=lambda k: (results[k]["cv_mae"], -results[k]["cv_r2"]))
    best_pipeline = fitted_pipelines[best_name]

    print(f"[selection] Best Selected Production Model: '{best_name.upper()}'")
    print(f"            * CV MAE: INR {results[best_name]['cv_mae']:,.2f}")
    print(f"            * CV R2 : {results[best_name]['cv_r2']:.4f}")

    # Export best model as primary budget_recommender.pkl
    best_model_path = os.path.join(MODEL_DIR, "budget_recommender.pkl")
    joblib.dump(best_pipeline, best_model_path)
    print(f"[done] Saved Best Production Model -> {best_model_path}")

    # Save comprehensive training metrics
    meta = {
        "selected_best_model": best_name,
        "feature_columns": num_cols + cat_cols,
        "target_columns": target_cols,
        "models_benchmarks": results,
    }
    meta_path = os.path.join(MODEL_DIR, "budget_train_metrics.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    # Legacy budget_meta.json sync
    with open(os.path.join(MODEL_DIR, "budget_meta.json"), "w") as f:
        json.dump({
            "best_model": best_name,
            "feature_cols": num_cols + cat_cols,
            "target_cols": target_cols,
            "metrics": results,
        }, f, indent=2)

    print(f"[done] Saved benchmark report -> {meta_path}")
    print("=" * 70)


if __name__ == "__main__":
    train_models()
