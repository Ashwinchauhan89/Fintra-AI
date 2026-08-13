import argparse
import os
import sys

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.text_utils import build_text_feature  # noqa: E402
from utils.amount_bucketizer import AmountBucketizer  # noqa: E402
from source_adapters import load_and_unify  # noqa: E402

# Roadmap categories (MACHINELEARNING.md, Phase 3). The adapters map
# every source's native categories down to this set (or drop the row).
EXPECTED_CATEGORIES = {
    "food", "bills", "shopping", "transport",
    "healthcare", "education", "entertainment",
}

DEFAULT_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "raw")
DEFAULT_OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def validate_categories(df: pd.DataFrame) -> None:
    seen = set(df["category"].unique())
    unexpected = seen - EXPECTED_CATEGORIES
    missing = EXPECTED_CATEGORIES - seen
    if unexpected:
        print(f"[warn] Unexpected categories after mapping: {sorted(unexpected)}")
    if missing:
        print(f"[warn] Roadmap categories with zero rows: {sorted(missing)}")


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
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

    return df


def main():
    parser = argparse.ArgumentParser(description="Preprocess and join expense data")
    parser.add_argument("--raw-dir", default=DEFAULT_RAW_DIR,
                         help="Directory containing raw CSVs to combine")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                         help="Where to write processed train/test CSVs")
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR,
                         help="Where to save the label encoder / amount bucketizer")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min-class-count", type=int, default=10,
                         help="Warn if a category has fewer rows than this")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.model_dir, exist_ok=True)

    print(f"[info] Scanning {args.raw_dir} for source files")
    df = load_and_unify(args.raw_dir)

    validate_categories(df)
    df = engineer_features(df)

    # Drop exact duplicate transactions (can happen when the same
    # merchant/description/amount repeats verbatim across sources).
    before = len(df)
    df = df.drop_duplicates(subset=["merchant", "description", "amount", "category"])
    if before - len(df):
        print(f"[info] Dropped {before - len(df)} exact-duplicate row(s)")

    class_counts = df["category"].value_counts()
    small_classes = class_counts[class_counts < args.min_class_count]
    if len(small_classes) > 0:
        print(f"[warn] Categories below {args.min_class_count} rows "
              f"(unreliable to evaluate): {small_classes.to_dict()}")

    label_encoder = LabelEncoder()
    df["category_encoded"] = label_encoder.fit_transform(df["category"])

    train_df, test_df = train_test_split(
        df,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=df["category_encoded"],
    )

    # Fit the amount bucketizer on TRAIN only, then apply to both —
    # never fit on test data, that would leak test-set distribution
    # into a "feature" available at training time.
    bucketizer = AmountBucketizer(n_bins=5)
    train_df = train_df.copy()
    test_df = test_df.copy()
    train_df["amount_bucket"] = bucketizer.fit_transform(train_df["amount"])
    test_df["amount_bucket"] = bucketizer.transform(test_df["amount"])

    train_path = os.path.join(args.out_dir, "train.csv")
    test_path = os.path.join(args.out_dir, "test.csv")
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    encoder_path = os.path.join(args.model_dir, "label_encoder.pkl")
    joblib.dump(label_encoder, encoder_path)
    bucketizer_path = os.path.join(args.model_dir, "amount_bucketizer.json")
    bucketizer.save(bucketizer_path)

    print(f"[done] Train: {len(train_df)} rows -> {train_path}")
    print(f"[done] Test:  {len(test_df)} rows -> {test_path}")
    print(f"[done] Label encoder -> {encoder_path}")
    print(f"[done] Amount bucketizer -> {bucketizer_path}")
    print(f"[info] Classes: {list(label_encoder.classes_)}")
    print(f"[info] Amount bucket edges: {[round(e, 2) for e in bucketizer.edges]}")


if __name__ == "__main__":
    main()
