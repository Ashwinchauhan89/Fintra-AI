
import argparse
import glob
import os
import sys

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GroupShuffleSplit

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "preprocessing"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "training"))
from utils.text_utils import build_text_feature  # noqa: E402
from utils.amount_bucketizer import AmountBucketizer  # noqa: E402
from preprocessing.source_adapters import load_and_unify  # noqa: E402
from training.train import (  # noqa: E402
    build_baseline_pipeline,
    build_random_forest_pipeline,
    build_xgboost_pipeline,
    HAS_XGBOOST,
)

DEFAULT_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "raw")
DEFAULT_TEST_PATH = os.path.join(
    os.path.dirname(__file__), "..", "datasets", "processed", "test.csv",
)
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

TEXT_COL = "text_feature"
CAT_FEATURE_COLS = ["amount_bucket", "day_of_week"]
TARGET_COL = "category_encoded"


def is_text_only_pipeline(pipeline) -> bool:
    """Baseline pipeline's first step is 'tfidf' and takes raw text;
    feature pipelines' first step is 'features' and take a DataFrame."""
    return list(pipeline.named_steps.keys())[0] == "tfidf"


def evaluate_model(name: str, model_path: str, df: pd.DataFrame,
                    label_encoder) -> dict:
    pipeline = joblib.load(model_path)

    X = df[TEXT_COL] if is_text_only_pipeline(pipeline) else \
        df[[TEXT_COL] + CAT_FEATURE_COLS]
    y_true = df[TARGET_COL]

    y_pred = pipeline.predict(X)

    acc = accuracy_score(y_true, y_pred)
    target_names = label_encoder.classes_
    report = classification_report(
        y_true, y_pred, target_names=target_names,
        zero_division=0, output_dict=True,
    )
    cm = confusion_matrix(y_true, y_pred)

    print(f"\n{'=' * 60}")
    print(f"Model: {name}")
    print(f"{'=' * 60}")
    print(f"Accuracy: {acc:.3f}")
    print()
    print(classification_report(
        y_true, y_pred, target_names=target_names, zero_division=0,
    ))
    print("Confusion matrix (rows=actual, cols=predicted):")
    cm_df = pd.DataFrame(cm, index=target_names, columns=target_names)
    print(cm_df)

    return {"accuracy": acc, "macro_f1": report["macro avg"]["f1-score"]}


def run_grouped_generalization_check(raw_dir: str) -> pd.DataFrame:
    """
    Re-splits the raw data by MERCHANT (not by row) so no merchant in
    the test set was ever seen during training, then trains fresh
    models on that split and evaluates them. This measures actual
    generalization to unfamiliar transactions, which the standard
    random split does not — see module docstring.

    Trains temporary models for this check only; does not touch or
    overwrite the production models saved by training/train.py.
    """
    print("\n" + "=" * 60)
    print("GROUPED-SPLIT GENERALIZATION CHECK (merchant-level holdout)")
    print("=" * 60)

    df = load_and_unify(raw_dir)
    df = df.dropna(subset=["category", "merchant", "amount"])
    df["merchant"] = df["merchant"].astype(str)
    df["description"] = df["description"].astype(str)
    df["text_feature"] = df.apply(
        lambda r: build_text_feature(r["merchant"], r["description"]), axis=1
    )
    if "date" in df.columns:
        parsed = pd.to_datetime(df["date"], errors="coerce")
        df["day_of_week"] = parsed.dt.dayofweek.fillna(-1).astype(int)
    else:
        df["day_of_week"] = -1

    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(
        gss.split(df, groups=df["merchant"].str.lower())
    )
    train_g, test_g = df.iloc[train_idx].copy(), df.iloc[test_idx].copy()

    overlap = set(train_g["merchant"].str.lower()) & set(test_g["merchant"].str.lower())
    assert len(overlap) == 0, "Merchant leaked across the grouped split"
    print(f"[info] Train: {len(train_g)} rows, {train_g['merchant'].nunique()} merchants")
    print(f"[info] Test:  {len(test_g)} rows, {test_g['merchant'].nunique()} merchants "
          f"— NONE overlap with train")

    bucketizer = AmountBucketizer(n_bins=5)
    train_g["amount_bucket"] = bucketizer.fit_transform(train_g["amount"])
    test_g["amount_bucket"] = bucketizer.transform(test_g["amount"])

    # xgboost requires numeric labels; encode here (baseline/RF work
    # fine with either, so this keeps all three consistent).
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_train = le.fit_transform(train_g["category"])
    y_test = le.transform(test_g["category"])

    candidates = {
        "baseline": build_baseline_pipeline(),
        "random_forest": build_random_forest_pipeline(),
    }
    if HAS_XGBOOST:
        candidates["xgboost"] = build_xgboost_pipeline()

    results = {}
    for name, pipeline in candidates.items():
        is_text_only = name == "baseline"
        X_train = train_g["text_feature"] if is_text_only else \
            train_g[["text_feature", "amount_bucket", "day_of_week"]]
        X_test = test_g["text_feature"] if is_text_only else \
            test_g[["text_feature", "amount_bucket", "day_of_week"]]

        pipeline.fit(X_train, y_train)
        pred = pipeline.predict(X_test)

        acc = accuracy_score(y_test, pred)
        macro_f1 = f1_score(y_test, pred, average="macro")
        results[name] = {"accuracy": acc, "macro_f1": macro_f1}
        print(f"[result] {name:15s} unseen-merchant accuracy={acc:.3f}  "
              f"macro_f1={macro_f1:.3f}")

    return pd.DataFrame(results).T


def main():
    parser = argparse.ArgumentParser(description="Evaluate expense classifiers")
    parser.add_argument("--test", default=DEFAULT_TEST_PATH)
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    parser.add_argument("--raw-dir", default=DEFAULT_RAW_DIR,
                         help="Used only by --mode grouped/both")
    parser.add_argument("--mode", choices=["random", "grouped", "both"],
                         default="random",
                         help="'random': evaluate saved models on the standard "
                              "test split. 'grouped': train+evaluate fresh "
                              "models on a merchant-level holdout (no shared "
                              "merchants between train/test) to check real "
                              "generalization. 'both' runs both and prints "
                              "them side by side.")
    args = parser.parse_args()

    random_summary = None
    if args.mode in ("random", "both"):
        print(f"[info] Loading test data from {args.test}")
        df = pd.read_csv(args.test)
        print(f"[info] {len(df)} test rows")

        label_encoder = joblib.load(
            os.path.join(args.model_dir, "label_encoder.pkl")
        )

        model_paths = sorted(glob.glob(os.path.join(args.model_dir, "*.pkl")))
        model_paths = [
            p for p in model_paths
            if os.path.basename(p) not in ("label_encoder.pkl", "best_model.pkl")
        ]

        if not model_paths:
            print("[error] No trained models found. Run train.py first.")
        else:
            results = {}
            for path in model_paths:
                name = os.path.splitext(os.path.basename(path))[0]
                results[name] = evaluate_model(name, path, df, label_encoder)

            print(f"\n{'=' * 60}")
            print("Summary (random split — includes merchants seen in training)")
            print(f"{'=' * 60}")
            random_summary = pd.DataFrame(results).T.sort_values(
                "macro_f1", ascending=False
            )
            print(random_summary)

    grouped_summary = None
    if args.mode in ("grouped", "both"):
        grouped_summary = run_grouped_generalization_check(args.raw_dir)
        print(f"\n{'=' * 60}")
        print("Summary (grouped split — merchants NEVER seen in training)")
        print(f"{'=' * 60}")
        print(grouped_summary.sort_values("macro_f1", ascending=False))

    if args.mode == "both" and random_summary is not None and grouped_summary is not None:
        print(f"\n{'=' * 60}")
        print("Side by side (macro F1): known merchants vs unseen merchants")
        print(f"{'=' * 60}")
        combined = pd.DataFrame({
            "random_split_f1": random_summary["macro_f1"],
            "grouped_split_f1": grouped_summary["macro_f1"],
        })
        combined["gap"] = combined["random_split_f1"] - combined["grouped_split_f1"]
        print(combined.sort_values("gap", ascending=False))


if __name__ == "__main__":
    main()
