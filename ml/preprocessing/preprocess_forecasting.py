"""
Preprocessing Pipeline for Financial Time-Series Forecasting (Phases 4 & 18).

Aggregates raw transaction data into a continuous daily financial time-series,
extracts category-level breakdowns, engineers temporal/lag/rolling features,
and produces chronological train/test splits.
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from preprocessing.source_adapters import load_and_unify  # noqa: E402
from utils.timeseries_features import (  # noqa: E402
    ROADMAP_CATEGORIES,
    add_calendar_features,
    add_lag_features,
    add_rolling_features,
    extract_forecasting_feature_names,
)

DEFAULT_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "raw")
DEFAULT_OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def build_daily_timeseries(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw transaction-level DataFrame into continuous daily time-series.
    Fills zero-spend days to ensure strict temporal continuity.
    """
    df = raw_df.dropna(subset=["date", "amount", "category"]).copy()
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()

    # Aggregate overall daily spending and transaction count
    daily_agg = df.groupby("date").agg(
        total_spend=("amount", "sum"),
        tx_count=("amount", "count"),
    )

    # Aggregate category-level daily spending
    cat_pivot = (
        df.pivot_table(
            index="date",
            columns="category",
            values="amount",
            aggfunc="sum",
            fill_value=0.0,
        )
    )
    # Ensure all 7 canonical categories are present
    for cat in ROADMAP_CATEGORIES:
        col_name = f"{cat}_spend"
        if cat in cat_pivot.columns:
            daily_agg[col_name] = cat_pivot[cat]
        else:
            daily_agg[col_name] = 0.0

    # Sort chronologically and reindex with continuous daily frequency
    daily_agg = daily_agg.sort_index()
    full_date_range = pd.date_range(
        start=daily_agg.index.min(),
        end=daily_agg.index.max(),
        freq="D",
    )
    daily_continuous = daily_agg.reindex(full_date_range).fillna(0.0)
    daily_continuous.index.name = "date"
    daily_continuous = daily_continuous.reset_index()

    return daily_continuous


def preprocess_forecasting_pipeline(
    raw_dir: str = DEFAULT_RAW_DIR,
    out_dir: str = DEFAULT_OUT_DIR,
    model_dir: str = DEFAULT_MODEL_DIR,
    test_ratio: float = 0.20,
):
    """
    End-to-end preprocessing, feature extraction, and chronological split.
    """
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)

    print(f"[info] Loading raw transaction sources from {raw_dir}...")
    raw_df = load_and_unify(raw_dir)

    print("[info] Building continuous daily financial time-series...")
    daily_df = build_daily_timeseries(raw_df)
    print(f"[info] Daily series created: {len(daily_df)} days "
          f"({daily_df['date'].min().strftime('%Y-%m-%d')} to {daily_df['date'].max().strftime('%Y-%m-%d')})")

    print("[info] Engineering temporal, cyclical, lag, and rolling features...")
    df_features = add_calendar_features(daily_df, date_col="date")
    df_features = add_lag_features(df_features, target_col="total_spend")
    df_features = add_rolling_features(df_features, target_col="total_spend")

    # Drop burn-in rows where 30-day lags/windows are not fully populated
    initial_len = len(df_features)
    df_features = df_features.dropna(subset=["lag_30"]).copy().reset_index(drop=True)
    print(f"[info] Burn-in dropped: {initial_len} -> {len(df_features)} valid feature rows")

    # Chronological train/test split (no random shuffling in time-series!)
    split_idx = int(len(df_features) * (1.0 - test_ratio))
    train_df = df_features.iloc[:split_idx].copy()
    test_df = df_features.iloc[split_idx:].copy()

    train_path = os.path.join(out_dir, "forecasting_train.csv")
    test_path = os.path.join(out_dir, "forecasting_test.csv")

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    feature_cols = extract_forecasting_feature_names()

    meta = {
        "start_date": str(df_features["date"].min().date()),
        "end_date": str(df_features["date"].max().date()),
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "train_date_range": [str(train_df["date"].min().date()), str(train_df["date"].max().date())],
        "test_date_range": [str(test_df["date"].min().date()), str(test_df["date"].max().date())],
        "feature_cols": feature_cols,
        "target_col": "total_spend",
        "category_targets": [f"{cat}_spend" for cat in ROADMAP_CATEGORIES],
        "mean_daily_spend_train": float(train_df["total_spend"].mean()),
        "std_daily_spend_train": float(train_df["total_spend"].std()),
    }
    meta_path = os.path.join(model_dir, "forecasting_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"[done] Saved training set: {len(train_df)} days -> {train_path}")
    print(f"[done] Saved test set:     {len(test_df)} days -> {test_path}")
    print(f"[done] Saved metadata:     {meta_path}")

    return train_df, test_df, meta


def main():
    parser = argparse.ArgumentParser(description="Preprocess time-series data for forecasting")
    parser.add_argument("--raw-dir", default=DEFAULT_RAW_DIR)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    parser.add_argument("--test-ratio", type=float, default=0.20)
    args = parser.parse_args()

    preprocess_forecasting_pipeline(
        raw_dir=args.raw_dir,
        out_dir=args.out_dir,
        model_dir=args.model_dir,
        test_ratio=args.test_ratio,
    )


if __name__ == "__main__":
    main()
