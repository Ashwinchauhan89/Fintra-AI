"""
Multi-Model Training & Benchmark Pipeline for Subscription & Recurring Charge Detection Engine (Phase 14).

Trains and compares 6 classification architectures:
1. Logistic Regression (L2 Linear Baseline)
2. Balanced Random Forest Classifier
3. Extra Trees Classifier
4. Gradient Boosting Classifier
5. Tuned XGBoost Classifier
6. Soft-Voting Stacking Ensemble

Optimizes for PR-AUC, ROC-AUC, and F1-Score to eliminate false positives on one-off purchases.
"""

import json
import os
import sys
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.subscription_rules import FEATURE_COLUMNS_SUBSCRIPTION  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TRAIN_FILE = os.path.join(PROCESSED_DIR, "subscriptions_train.csv")


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("text", TfidfVectorizer(ngram_range=(2, 4), analyzer="char_wb", min_df=2), "merchant_name"),
            ("num", StandardScaler(), FEATURE_COLUMNS_SUBSCRIPTION),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["category"]),
        ]
    )


def evaluate_cv(pipeline, X: pd.DataFrame, y: pd.Series, n_splits: int = 5) -> Dict[str, float]:
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    roc_aucs = []
    pr_aucs = []
    recalls = []
    precisions = []
    f1s = []

    for train_idx, val_idx in skf.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipeline.fit(X_train, y_train)
        probs = pipeline.predict_proba(X_val)[:, 1]
        preds = (probs >= 0.50).astype(int)

        roc_aucs.append(roc_auc_score(y_val, probs))
        pr_aucs.append(average_precision_score(y_val, probs))
        recalls.append(recall_score(y_val, preds, zero_division=0))
        precisions.append(precision_score(y_val, preds, zero_division=0))
        f1s.append(f1_score(y_val, preds, zero_division=0))

    return {
        "pr_auc": float(np.mean(pr_aucs)),
        "roc_auc": float(np.mean(roc_aucs)),
        "recall": float(np.mean(recalls)),
        "precision": float(np.mean(precisions)),
        "f1": float(np.mean(f1s)),
    }


def train_models():
    print("=" * 80)
    print("Multi-Model Training & Benchmark Suite: Phase 14 Subscription Engine")
    print("=" * 80)

    if not os.path.exists(TRAIN_FILE):
        raise FileNotFoundError(f"Training dataset not found at {TRAIN_FILE}. Run preprocessing/preprocess_subscriptions.py first.")

    df = pd.read_csv(TRAIN_FILE)
    features = ["merchant_name", "category"] + FEATURE_COLUMNS_SUBSCRIPTION
    X = df[features]
    y = df["is_subscription"]

    preprocessor = build_preprocessor()
    os.makedirs(MODEL_DIR, exist_ok=True)

    pos_weight = float((len(y) - y.sum()) / max(1, y.sum()))

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, C=2.0, random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=150, max_depth=16, class_weight="balanced", random_state=42, n_jobs=-1),
        "extra_trees": ExtraTreesClassifier(n_estimators=200, max_depth=16, class_weight="balanced", random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42),
        "xgboost": XGBClassifier(
            n_estimators=250,
            max_depth=5,
            learning_rate=0.04,
            scale_pos_weight=pos_weight,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
        ),
    }

    # Stacking Soft-Voting Ensemble
    candidates["ensemble"] = VotingClassifier(
        estimators=[
            ("et", candidates["extra_trees"]),
            ("xgb", candidates["xgboost"]),
            ("rf", candidates["random_forest"]),
        ],
        voting="soft",
        weights=[0.45, 0.35, 0.20],
    )

    results = {}
    fitted_pipelines = {}

    print(f"{'Model Candidate':<22} | {'5-Fold PR-AUC':<14} | {'5-Fold ROC-AUC':<14} | {'Recall':<8} | {'Precision':<10} | {'F1-Score'}")
    print("-" * 80)

    for name, clf in candidates.items():
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", clf),
        ])
        cv_metrics = evaluate_cv(pipeline, X, y, n_splits=5)
        results[name] = cv_metrics

        print(
            f"{name:<22} | {cv_metrics['pr_auc']:>12.4f} | {cv_metrics['roc_auc']:>12.4f} | "
            f"{cv_metrics['recall']:>6.2%} | {cv_metrics['precision']:>8.2%} | {cv_metrics['f1']:>8.4f}"
        )

        # Fit on whole train set and save individual candidate artifact
        pipeline.fit(X, y)
        fitted_pipelines[name] = pipeline

        save_path = os.path.join(MODEL_DIR, f"subscriptions_{name}.pkl")
        joblib.dump(pipeline, save_path)

    print("-" * 80)

    # Select Best Production Model by PR-AUC and F1
    best_name = max(results, key=lambda k: (results[k]["pr_auc"] * 0.5 + results[k]["f1"] * 0.5))
    best_pipeline = fitted_pipelines[best_name]

    print(f"[selection] Best Selected Production Model: '{best_name.upper()}'")
    print(f"            * 5-Fold PR-AUC : {results[best_name]['pr_auc']:.4f}")
    print(f"            * 5-Fold ROC-AUC: {results[best_name]['roc_auc']:.4f}")
    print(f"            * 5-Fold F1     : {results[best_name]['f1']:.4f}")

    best_model_path = os.path.join(MODEL_DIR, "subscription_best_model.pkl")
    joblib.dump(best_pipeline, best_model_path)
    print(f"[done] Saved Best Production Model -> {best_model_path}")

    # Save training metadata
    meta = {
        "selected_best_model": best_name,
        "feature_columns": features,
        "prevalence": float(y.mean()),
        "models_benchmarks": results,
    }
    meta_path = os.path.join(MODEL_DIR, "subscriptions_train_metrics.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    with open(os.path.join(MODEL_DIR, "subscriptions_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"[done] Saved benchmark report -> {meta_path}")
    print("=" * 80)


if __name__ == "__main__":
    train_models()
