"""
Multi-Model Training & Benchmark Pipeline for Fraud Detection & Spending Anomaly Engine (Phases 8 & 9).

Trains and compares:
1. Unsupervised Outlier Suite: Isolation Forest, One-Class SVM, Elliptic Envelope.
2. Supervised Fraud Classifiers: Balanced Random Forest, Extra Trees, Gradient Boosting, XGBoost, and Stacking Soft-Voting Ensemble.

Optimizes for PR-AUC (Precision-Recall AUC), ROC-AUC, and High-Recall (>=92%) with Low False Positive Rate (<1.5%).
"""

import json
import os
import sys
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    IsolationForest,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import OneClassSVM
from xgboost import XGBClassifier

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.anomaly_features import FEATURE_COLUMNS, ROADMAP_CATEGORIES  # noqa: E402

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TRAIN_FILE = os.path.join(PROCESSED_DIR, "anomaly_train.csv")


def build_preprocessor() -> ColumnTransformer:
    num_cols = [c for c in FEATURE_COLUMNS if c != "category"]
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["category"]),
        ]
    )


def evaluate_supervised_cv(pipeline, X: pd.DataFrame, y: pd.Series, n_splits: int = 5) -> Dict[str, float]:
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
    print("Multi-Model Training & Benchmark Suite: Phase 8 & 9 Fraud & Anomaly Engine")
    print("=" * 80)

    if not os.path.exists(TRAIN_FILE):
        raise FileNotFoundError(f"Training dataset not found at {TRAIN_FILE}. Run preprocessing/preprocess_anomaly.py first.")

    df = pd.read_csv(TRAIN_FILE)
    feature_cols = FEATURE_COLUMNS + ["category"]
    X = df[feature_cols]
    y = df["is_fraud"]

    preprocessor = build_preprocessor()
    os.makedirs(MODEL_DIR, exist_ok=True)

    # -------------------------------------------------------------
    # 1. Unsupervised Anomaly Suite (Phase 9)
    # -------------------------------------------------------------
    print("\n--- Part 1: Unsupervised Outlier Suite (Spending Anomaly - Phase 9) ---")
    X_proc = preprocessor.fit_transform(X)
    contamination = float(y.mean())  # ~0.035

    unsupervised_models = {
        "isolation_forest": IsolationForest(n_estimators=200, max_samples=0.8, contamination=contamination, random_state=42, n_jobs=-1),
        "one_class_svm": OneClassSVM(nu=contamination, kernel="rbf", gamma="scale"),
    }

    for name, model in unsupervised_models.items():
        print(f"[unsupervised] Fitting {name} (contamination={contamination:.3f})...")
        model.fit(X_proc)
        save_path = os.path.join(MODEL_DIR, f"anomaly_{name}.pkl")
        joblib.dump((preprocessor, model), save_path)
        print(f"               -> Saved artifact: {save_path}")

    # -------------------------------------------------------------
    # 2. Supervised Fraud Classifiers (Phase 8)
    # -------------------------------------------------------------
    print("\n--- Part 2: Supervised Fraud Probability Classifiers (Phase 8) ---")
    pos_weight = float((len(y) - y.sum()) / max(1, y.sum()))

    supervised_candidates = {
        "random_forest": RandomForestClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=42, n_jobs=-1),
        "extra_trees": ExtraTreesClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=200, max_depth=5, learning_rate=0.06, random_state=42),
        "xgboost": XGBClassifier(
            n_estimators=250,
            max_depth=5,
            learning_rate=0.04,
            scale_pos_weight=pos_weight,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
        ),
    }

    # Stacking Soft-Voting Ensemble
    supervised_candidates["ensemble"] = VotingClassifier(
        estimators=[
            ("xgb", supervised_candidates["xgboost"]),
            ("rf", supervised_candidates["random_forest"]),
            ("et", supervised_candidates["extra_trees"]),
        ],
        voting="soft",
        weights=[0.45, 0.30, 0.25],
    )

    results = {}
    fitted_pipelines = {}

    print(f"{'Model Candidate':<22} | {'PR-AUC (Avg Prec)':<18} | {'ROC-AUC':<10} | {'Recall':<8} | {'Precision':<10} | {'F1-Score'}")
    print("-" * 80)

    for name, clf in supervised_candidates.items():
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", clf),
        ])
        cv_metrics = evaluate_supervised_cv(pipeline, X, y, n_splits=5)
        results[name] = cv_metrics

        print(
            f"{name:<22} | {cv_metrics['pr_auc']:>16.4f} | {cv_metrics['roc_auc']:>8.4f} | "
            f"{cv_metrics['recall']:>6.2%} | {cv_metrics['precision']:>8.2%} | {cv_metrics['f1']:>8.4f}"
        )

        # Fit on whole train set and save individual candidate artifact
        pipeline.fit(X, y)
        fitted_pipelines[name] = pipeline

        save_path = os.path.join(MODEL_DIR, f"fraud_{name}.pkl")
        joblib.dump(pipeline, save_path)

    print("-" * 80)

    # 3. Select Best Model by PR-AUC & F1
    best_name = max(results, key=lambda k: (results[k]["pr_auc"] * 0.6 + results[k]["f1"] * 0.4))
    best_pipeline = fitted_pipelines[best_name]

    print(f"[selection] Best Selected Production Model: '{best_name.upper()}'")
    print(f"            * 5-Fold PR-AUC : {results[best_name]['pr_auc']:.4f}")
    print(f"            * 5-Fold ROC-AUC: {results[best_name]['roc_auc']:.4f}")
    print(f"            * 5-Fold Recall : {results[best_name]['recall']:.2%}")
    print(f"            * 5-Fold F1     : {results[best_name]['f1']:.4f}")

    best_model_path = os.path.join(MODEL_DIR, "fraud_best_model.pkl")
    joblib.dump(best_pipeline, best_model_path)
    print(f"[done] Saved Best Production Model -> {best_model_path}")

    # Save training metadata
    meta = {
        "selected_best_model": best_name,
        "feature_columns": feature_cols,
        "prevalence": float(y.mean()),
        "models_benchmarks": results,
    }
    meta_path = os.path.join(MODEL_DIR, "fraud_train_metrics.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    with open(os.path.join(MODEL_DIR, "anomaly_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"[done] Saved benchmark report -> {meta_path}")
    print("=" * 80)


if __name__ == "__main__":
    train_models()
