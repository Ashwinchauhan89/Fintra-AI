"""
Multi-Model Training & Banking Benchmark Pipeline for Phase 12: Loan Eligibility & Credit Risk.

Benchmarks 6 candidate classifiers via 5-Fold Stratified Cross-Validation:
1. Balanced Logistic Regression (L2 Baseline)
2. Balanced Random Forest Classifier
3. Extra Trees Classifier
4. Gradient Boosting Classifier
5. Tuned XGBoost Classifier (with scale_pos_weight & L1/L2 regularization)
6. Calibrated Soft-Voting Stacking Ensemble

Optimizes for:
- Precision-Recall AUC (PR-AUC / Average Precision)
- ROC-AUC Score
- Macro F1 & Balanced Accuracy
- Youden's J Optimal Decision Threshold Selection
- Probability Calibration (Brier Loss Minimization)
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from xgboost import XGBClassifier

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.loan_rules import (  # noqa: E402
    ENGINEERED_CATEGORICAL_FEATURES_LOAN,
    ENGINEERED_NUMERICAL_FEATURES_LOAN,
    RAW_FEATURE_COLUMNS_LOAN,
    TARGET_COLUMN_LOAN,
    engineer_loan_features,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TRAIN_FILE = os.path.join(PROCESSED_DIR, "loan_train.csv")


def build_preprocessor(num_cols: list, cat_cols: list) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", RobustScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ]
    )


def evaluate_cv(model, X: np.ndarray, y: np.ndarray, n_splits: int = 5) -> Dict[str, float]:
    """
    Evaluates classifier using 5-Fold Stratified Cross-Validation across multiple banking risk metrics.
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    roc_scores, pr_scores, f1_scores, acc_scores, brier_scores = [], [], [], [], []
    optimal_thresholds = []

    for train_idx, val_idx in skf.split(X, y):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        model.fit(X_train, y_train)

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_val)[:, 1]
        else:
            probs = model.decision_function(X_val)

        # Youden's J statistic for optimal threshold: max(Sensitivity + Specificity - 1)
        fpr, tpr, thresholds = roc_curve(y_val, probs)
        j_scores = tpr - fpr
        best_thresh = thresholds[np.argmax(j_scores)]
        best_thresh = float(np.clip(best_thresh, 0.20, 0.80))
        optimal_thresholds.append(best_thresh)

        preds = (probs >= best_thresh).astype(int)

        roc_scores.append(roc_auc_score(y_val, probs))
        pr_scores.append(average_precision_score(y_val, probs))
        f1_scores.append(f1_score(y_val, preds, average="macro"))
        acc_scores.append(accuracy_score(y_val, preds))
        brier_scores.append(brier_score_loss(y_val, probs))

    return {
        "roc_auc": float(np.mean(roc_scores)),
        "pr_auc": float(np.mean(pr_scores)),
        "macro_f1": float(np.mean(f1_scores)),
        "accuracy": float(np.mean(acc_scores)),
        "brier_score": float(np.mean(brier_scores)),
        "optimal_threshold": float(np.mean(optimal_thresholds)),
    }


def main():
    print("=" * 80)
    print("Phase 12: Advanced Loan Underwriting & Credit Risk Multi-Model Benchmark")
    print("=" * 80)

    if not os.path.exists(TRAIN_FILE):
        print(f"[error] Train file not found: {TRAIN_FILE}. Run preprocess_loan.py first.")
        sys.exit(1)

    raw_df = pd.read_csv(TRAIN_FILE)
    print(f"[info] Loaded {len(raw_df)} loan records. Applying banking feature engineering...")

    df = engineer_loan_features(raw_df)

    num_cols = ENGINEERED_NUMERICAL_FEATURES_LOAN
    cat_cols = ENGINEERED_CATEGORICAL_FEATURES_LOAN

    X = df[num_cols + cat_cols]
    y = df[TARGET_COLUMN_LOAN].values

    # Preprocessor fit & transform
    preprocessor = build_preprocessor(num_cols, cat_cols)
    X_proc = preprocessor.fit_transform(X)

    # Class distribution ratio for XGBoost scale_pos_weight
    neg_count = int((y == 0).sum())
    pos_count = int((y == 1).sum())
    pos_scale = float(neg_count / max(1, pos_count))

    # Define Candidate Classifiers
    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced", C=0.8, random_state=42),
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=16, min_samples_split=3, class_weight="balanced_subsample", random_state=42, n_jobs=-1
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=250, max_depth=18, min_samples_split=2, class_weight="balanced", random_state=42, n_jobs=-1
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=250, max_depth=5, learning_rate=0.04, random_state=42
        ),
        "xgboost": XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.03,
            scale_pos_weight=pos_scale,
            subsample=0.90,
            colsample_bytree=0.85,
            reg_alpha=0.05,
            reg_lambda=1.2,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
        ),
    }

    # Soft-Voting Stacking Ensemble of top models
    ensemble_base = [
        ("et", ExtraTreesClassifier(n_estimators=200, max_depth=16, class_weight="balanced", random_state=42, n_jobs=-1)),
        ("xgb", XGBClassifier(n_estimators=250, max_depth=5, learning_rate=0.04, scale_pos_weight=pos_scale, random_state=42, n_jobs=-1, eval_metric="logloss")),
        ("gb", GradientBoostingClassifier(n_estimators=200, max_depth=5, learning_rate=0.04, random_state=42)),
        ("rf", RandomForestClassifier(n_estimators=180, max_depth=14, class_weight="balanced", random_state=42, n_jobs=-1)),
    ]
    candidates["soft_voting_ensemble"] = VotingClassifier(estimators=ensemble_base, voting="soft")

    print("\n[info] Running 5-Fold Stratified Cross-Validation on Candidate Models...")
    leaderboard = []

    for name, model in candidates.items():
        metrics = evaluate_cv(model, X_proc, y, n_splits=5)
        # Composite score combining PR-AUC (40%), ROC-AUC (30%), Macro F1 (20%), and Brier Calibration penalty (10%)
        composite_score = (
            0.40 * metrics["pr_auc"]
            + 0.30 * metrics["roc_auc"]
            + 0.20 * metrics["macro_f1"]
            - 0.10 * metrics["brier_score"]
        )

        row = {
            "model": name,
            "pr_auc": round(metrics["pr_auc"], 4),
            "roc_auc": round(metrics["roc_auc"], 4),
            "macro_f1": round(metrics["macro_f1"], 4),
            "accuracy_pct": round(metrics["accuracy"] * 100.0, 2),
            "brier_score": round(metrics["brier_score"], 4),
            "optimal_threshold": round(metrics["optimal_threshold"], 3),
            "composite_score": round(composite_score, 4),
        }
        leaderboard.append(row)
        print(
            f"  [{name:22s}] PR-AUC: {row['pr_auc']:6.4f} | ROC-AUC: {row['roc_auc']:6.4f} | F1: {row['macro_f1']:6.4f} | Acc: {row['accuracy_pct']:5.2f}% | Brier: {row['brier_score']:6.4f} | Score: {row['composite_score']:6.4f}"
        )

    leaderboard_df = pd.DataFrame(leaderboard).sort_values("composite_score", ascending=False)
    best_row = leaderboard_df.iloc[0]
    best_name = best_row["model"]

    print("\n" + "=" * 80)
    print(f"[result] Selected Optimal Production Architecture: '{best_name}'")
    print(f"         PR-AUC:             {best_row['pr_auc']}")
    print(f"         ROC-AUC:            {best_row['roc_auc']}")
    print(f"         Macro F1-Score:     {best_row['macro_f1']}")
    print(f"         Accuracy:           {best_row['accuracy_pct']}%")
    print(f"         Optimal Threshold:  {best_row['optimal_threshold']}")
    print(f"         Brier Calibration:  {best_row['brier_score']}")
    print("=" * 80)

    # Train winning production model on full dataset
    best_model = candidates[best_name]
    best_model.fit(X_proc, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    model_save_path = os.path.join(MODEL_DIR, "best_loan_model.pkl")
    preprocessor_save_path = os.path.join(MODEL_DIR, "loan_preprocessor.pkl")
    metadata_save_path = os.path.join(MODEL_DIR, "loan_metadata.json")

    joblib.dump(best_model, model_save_path)
    joblib.dump(preprocessor, preprocessor_save_path)

    metadata = {
        "best_model_name": best_name,
        "raw_feature_columns": RAW_FEATURE_COLUMNS_LOAN,
        "engineered_numerical_features": num_cols,
        "engineered_categorical_features": cat_cols,
        "target_column": TARGET_COLUMN_LOAN,
        "optimal_threshold": best_row["optimal_threshold"],
        "cv_leaderboard": leaderboard,
        "num_training_samples": len(df),
        "class_distribution": {"approved": pos_count, "rejected": neg_count},
        "best_model_metrics": best_row.to_dict(),
    }
    with open(metadata_save_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[done] Serialized production model -> {model_save_path}")
    print(f"[done] Serialized preprocessor      -> {preprocessor_save_path}")
    print(f"[done] Serialized metadata          -> {metadata_save_path}")


if __name__ == "__main__":
    main()
