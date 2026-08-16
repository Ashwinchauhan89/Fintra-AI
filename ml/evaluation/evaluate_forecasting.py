"""
Evaluation Pipeline for Financial Time-Series Forecasting (Phases 4 & 18).

Evaluates all trained forecasting models on the held-out out-of-time test set,
computes MAE, RMSE, MAPE, R2, directional accuracy, and category-level errors.
"""

import argparse
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.timeseries_features import (  # noqa: E402
    ROADMAP_CATEGORIES,
    extract_forecasting_feature_names,
)
from models.baseline_forecaster import SeasonalBaselineRegressor  # noqa: F401, E402

DEFAULT_TEST_PATH = os.path.join(
    os.path.dirname(__file__), "..", "datasets", "processed", "forecasting_test.csv",
)
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def compute_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Computes MAPE ignoring zero actual values to avoid division by zero."""
    mask = y_true > 1.0
    if not np.any(mask):
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)


def compute_directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Percentage of times the model correctly predicts the direction of spend change."""
    if len(y_true) < 2:
        return 0.0
    actual_diff = np.diff(y_true)
    pred_diff = np.diff(y_pred)
    correct_direction = np.sign(actual_diff) == np.sign(pred_diff)
    return float(np.mean(correct_direction) * 100.0)


def evaluate_model(name: str, pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    preds = np.maximum(0.0, pipeline.predict(X_test))
    y_true = y_test.values

    mae = mean_absolute_error(y_true, preds)
    rmse = np.sqrt(mean_squared_error(y_true, preds))
    r2 = r2_score(y_true, preds)
    mape = compute_mape(y_true, preds)
    dir_acc = compute_directional_accuracy(y_true, preds)

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "mape_pct": float(mape),
        "directional_accuracy_pct": float(dir_acc),
        "mean_actual": float(np.mean(y_true)),
        "mean_predicted": float(np.mean(preds)),
    }


def evaluate_categories(category_models: dict, X_test: pd.DataFrame, test_df: pd.DataFrame) -> dict:
    cat_results = {}
    for cat, model in category_models.items():
        cat_col = f"{cat}_spend"
        if cat_col in test_df.columns:
            y_cat = test_df[cat_col].values
            cat_preds = np.maximum(0.0, model.predict(X_test))
            mae = mean_absolute_error(y_cat, cat_preds)
            rmse = np.sqrt(mean_squared_error(y_cat, cat_preds))
            cat_results[cat] = {
                "mae": float(mae),
                "rmse": float(rmse),
                "mean_actual": float(np.mean(y_cat)),
                "mean_predicted": float(np.mean(cat_preds)),
            }
    return cat_results


def main():
    parser = argparse.ArgumentParser(description="Evaluate forecasting models on held-out test set")
    parser.add_argument("--test", default=DEFAULT_TEST_PATH)
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()

    print(f"[info] Loading test set from {args.test}...")
    test_df = pd.read_csv(args.test)
    print(f"[info] Held-out test period: {len(test_df)} days ({test_df['date'].min()} to {test_df['date'].max()})")

    feature_cols = extract_forecasting_feature_names()
    available_features = [c for c in feature_cols if c in test_df.columns]
    X_test = test_df[available_features]
    y_test = test_df["total_spend"]

    model_names = ["baseline_seasonal", "ridge", "random_forest", "xgboost"]
    results = {}

    print("\n" + "=" * 80)
    print(f"{'Model':<20} | {'MAE (INR)':<12} | {'RMSE (INR)':<12} | {'R2':<8} | {'MAPE %':<10} | {'Dir Acc %':<10}")
    print("=" * 80)

    for name in model_names:
        model_path = os.path.join(args.model_dir, f"forecasting_{name}.pkl")
        if not os.path.exists(model_path):
            continue
        pipeline = joblib.load(model_path)
        metrics = evaluate_model(name, pipeline, X_test, y_test)
        results[name] = metrics
        print(f"{name:<20} | {metrics['mae']:>12.2f} | {metrics['rmse']:>12.2f} | {metrics['r2']:>8.3f} | {metrics['mape_pct']:>9.1f}% | {metrics['directional_accuracy_pct']:>9.1f}%")

    print("=" * 80)

    # Category evaluation
    cat_models_path = os.path.join(args.model_dir, "forecasting_categories.pkl")
    cat_results = {}
    if os.path.exists(cat_models_path):
        category_models = joblib.load(cat_models_path)
        cat_results = evaluate_categories(category_models, X_test, test_df)

        print("\n" + "=" * 65)
        print("CATEGORY-WISE FORECAST PERFORMANCE ON HELD-OUT TEST DATA")
        print("=" * 65)
        print(f"{'Category':<16} | {'MAE (INR)':<12} | {'RMSE (INR)':<12} | {'Mean Actual':<12}")
        print("-" * 65)
        for cat, m in cat_results.items():
            print(f"{cat:<16} | {m['mae']:>12.2f} | {m['rmse']:>12.2f} | {m['mean_actual']:>12.2f}")
        print("=" * 65)

    # Save complete evaluation output
    out_file = os.path.join(args.model_dir, "forecasting_evaluation_metrics.json")
    with open(out_file, "w") as f:
        json.dump({
            "models": results,
            "category_models": cat_results,
            "test_samples": len(test_df),
        }, f, indent=2)

    print(f"\n[done] Evaluation report saved -> {out_file}")


if __name__ == "__main__":
    main()
