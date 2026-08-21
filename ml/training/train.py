import argparse
import json
import os
import sys

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import OneHotEncoder

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

DEFAULT_TRAIN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "datasets", "processed", "train.csv",
)
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

TEXT_COL = "text_feature"
CAT_FEATURE_COLS = ["amount_bucket", "day_of_week"]
FEATURE_COLS = [TEXT_COL] + CAT_FEATURE_COLS
TARGET_COL = "category_encoded"

CV_FOLDS = 5


def build_feature_pipeline() -> ColumnTransformer:
    """
    Combined Word + Subword/Character N-Gram TF-IDF with categorical features.
    Provides high accuracy on exact merchant matches as well as strong
    generalization to unseen merchants via character-level tokenization.
    """
    text_union = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True, min_df=1)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True, min_df=2)),
    ])
    return ColumnTransformer(transformers=[
        ("text", text_union, TEXT_COL),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_FEATURE_COLS),
    ])


def build_candidate_pipelines() -> dict:
    candidates = {
        "baseline": Pipeline([
            ("features", build_feature_pipeline()),
            ("clf", ComplementNB(norm=True)),
        ]),
        "logistic_regression": Pipeline([
            ("features", build_feature_pipeline()),
            ("clf", LogisticRegression(max_iter=1000, C=3.0, class_weight="balanced", random_state=42)),
        ]),
        "random_forest": Pipeline([
            ("features", build_feature_pipeline()),
            ("clf", RandomForestClassifier(
                n_estimators=200, max_depth=None, random_state=42,
                class_weight="balanced",
            )),
        ]),
    }

    if HAS_XGBOOST:
        candidates["xgboost"] = Pipeline([
            ("features", build_feature_pipeline()),
            ("clf", XGBClassifier(
                n_estimators=200, max_depth=6, learning_rate=0.1,
                eval_metric="mlogloss", random_state=42,
            )),
        ])

    candidates["ensemble"] = Pipeline([
        ("features", build_feature_pipeline()),
        ("clf", VotingClassifier(
            estimators=[
                ("lr", LogisticRegression(max_iter=1000, C=3.0, class_weight="balanced", random_state=42)),
                ("nb", ComplementNB(norm=True)),
                ("rf", RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")),
            ],
            voting="soft",
        )),
    ])

    return candidates


def safe_cv_folds(y, requested: int) -> int:
    """Cross-val needs at least `folds` samples in the smallest class."""
    min_class_count = pd.Series(y).value_counts().min()
    return max(2, min(requested, min_class_count))


def evaluate_cv(name: str, pipeline: Pipeline, X: pd.DataFrame, y: pd.Series) -> float:
    folds = safe_cv_folds(y, CV_FOLDS)
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, X, y, cv=cv, scoring="f1_macro")
    mean_score = scores.mean()
    print(f"[cv] {name:20s}: macro F1 = {mean_score:.4f} "
          f"(folds={folds}, scores={[round(s, 4) for s in scores]})")
    return mean_score


def main():
    parser = argparse.ArgumentParser(description="Train expense classifiers")
    parser.add_argument("--train", default=DEFAULT_TRAIN_PATH)
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()

    os.makedirs(args.model_dir, exist_ok=True)

    print(f"[info] Loading training data from {args.train}")
    df = pd.read_csv(args.train)
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    candidates = build_candidate_pipelines()

    scores = {}
    print("\n--- Cross-Validation Benchmarks (5-Fold Stratified Macro F1) ---")
    for name, pipeline in candidates.items():
        scores[name] = evaluate_cv(name, pipeline, X, y)

    # Fit every candidate on the FULL training set and save it
    print("\n--- Training and Saving Production Candidate Models ---")
    for name, pipeline in candidates.items():
        pipeline.fit(X, y)
        model_path = os.path.join(args.model_dir, f"{name}.pkl")
        joblib.dump(pipeline, model_path)
        print(f"[done] Saved {name} -> {model_path}")

    # Select best model based on cross-validation macro F1
    best_name = max(scores, key=scores.get)
    best_path = os.path.join(args.model_dir, f"{best_name}.pkl")
    best_dest = os.path.join(args.model_dir, "best_model.pkl")
    joblib.dump(joblib.load(best_path), best_dest)

    metrics_path = os.path.join(args.model_dir, "training_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump({
            "cv_macro_f1": scores,
            "best_model": best_name,
            "feature_columns": FEATURE_COLS,
        }, f, indent=2)

    print(f"\n[result] Best model by CV macro F1: '{best_name}' "
          f"({scores[best_name]:.4f}) -> saved as best_model.pkl")
    print(f"[done] Metrics saved to {metrics_path}")
    print("[note] Run evaluate.py next to check performance on the held-out test set.")


if __name__ == "__main__":
    main()

