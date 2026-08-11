import argparse
import json
import os

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
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
TARGET_COL = "category_encoded"

CV_FOLDS = 5


def build_baseline_pipeline() -> Pipeline:
    """TF-IDF (text only) + Multinomial Naive Bayes."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(min_df=2, ngram_range=(1, 2))),
        ("clf", MultinomialNB()),
    ])


def build_feature_pipeline() -> ColumnTransformer:
    """Text + amount bucket + day-of-week, combined for tree models."""
    return ColumnTransformer(transformers=[
        ("text", TfidfVectorizer(min_df=2, ngram_range=(1, 2)), TEXT_COL),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_FEATURE_COLS),
    ])


def build_random_forest_pipeline() -> Pipeline:
    return Pipeline([
        ("features", build_feature_pipeline()),
        ("clf", RandomForestClassifier(
            n_estimators=200, max_depth=None, random_state=42,
            class_weight="balanced",
        )),
    ])


def build_xgboost_pipeline():
    if not HAS_XGBOOST:
        return None
    return Pipeline([
        ("features", build_feature_pipeline()),
        ("clf", XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            eval_metric="mlogloss", random_state=42,
        )),
    ])


def safe_cv_folds(y, requested: int) -> int:
    """Cross-val needs at least `folds` samples in the smallest class."""
    min_class_count = pd.Series(y).value_counts().min()
    return max(2, min(requested, min_class_count))


def evaluate_cv(name: str, pipeline: Pipeline, X, y) -> float:
    folds = safe_cv_folds(y, CV_FOLDS)
    scores = cross_val_score(pipeline, X, y, cv=folds, scoring="f1_macro")
    mean_score = scores.mean()
    print(f"[cv] {name}: macro F1 = {mean_score:.3f} "
          f"(folds={folds}, scores={[round(s, 3) for s in scores]})")
    return mean_score


def main():
    parser = argparse.ArgumentParser(description="Train expense classifiers")
    parser.add_argument("--train", default=DEFAULT_TRAIN_PATH)
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()

    os.makedirs(args.model_dir, exist_ok=True)

    print(f"[info] Loading training data from {args.train}")
    df = pd.read_csv(args.train)
    X = df[[TEXT_COL] + CAT_FEATURE_COLS]
    y = df[TARGET_COL]

    candidates = {
        "baseline": build_baseline_pipeline(),
        "random_forest": build_random_forest_pipeline(),
    }
    if HAS_XGBOOST:
        candidates["xgboost"] = build_xgboost_pipeline()
    else:
        print("[warn] xgboost not installed — skipping. "
              "Install with: pip install xgboost --break-system-packages")

    scores = {}
    for name, pipeline in candidates.items():
        # Baseline only uses the text column; feed it a 1D series.
        X_input = X[TEXT_COL] if name == "baseline" else X
        scores[name] = evaluate_cv(name, pipeline, X_input, y)

    # Fit every candidate on the FULL training set and save it, so
    # evaluate.py can compare all of them on the held-out test set.
    for name, pipeline in candidates.items():
        X_input = X[TEXT_COL] if name == "baseline" else X
        pipeline.fit(X_input, y)
        model_path = os.path.join(args.model_dir, f"{name}.pkl")
        joblib.dump(pipeline, model_path)
        print(f"[done] Saved {name} -> {model_path}")

    best_name = max(scores, key=scores.get)
    best_path = os.path.join(args.model_dir, f"{best_name}.pkl")
    best_dest = os.path.join(args.model_dir, "best_model.pkl")
    joblib.dump(joblib.load(best_path), best_dest)

    with open(os.path.join(args.model_dir, "training_metrics.json"), "w") as f:
        json.dump({
            "cv_macro_f1": scores,
            "best_model": best_name,
            "uses_text_only": best_name == "baseline",
        }, f, indent=2)

    print(f"\n[result] Best model by CV macro F1: '{best_name}' "
          f"({scores[best_name]:.3f}) -> saved as best_model.pkl")
    print("[note] Run evaluate.py next to check performance on the "
          "held-out test set, not just cross-validation.")


if __name__ == "__main__":
    main()
