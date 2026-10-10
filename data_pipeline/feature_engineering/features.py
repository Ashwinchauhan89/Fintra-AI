"""
Feature Engineering Module.
Extracts ML-ready features such as category aggregates, rolling spend averages,
and transaction velocity.
"""

import pandas as pd


class FeatureEngineer:
    """Computes behavioral and statistical features from cleaned transaction data."""

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enriches cleaned transaction data with statistical and aggregated signals."""
        if df.empty:
            return df

        df = df.copy()

        # Ensure date sorting for temporal aggregates
        if "date" in df.columns:
            df = df.sort_values("date").reset_index(drop=True)

        # 1. Merchant-level aggregates
        if "merchant" in df.columns and "amount" in df.columns:
            merchant_stats = (
                df.groupby("merchant")["amount"]
                .agg(["count", "mean", "std"])
                .rename(columns={"count": "merchant_txn_count", "mean": "merchant_avg_amount", "std": "merchant_std_amount"})
                .fillna(0.0)
            )
            df = df.merge(merchant_stats, on="merchant", how="left")

        # 2. Category-level aggregates
        if "category" in df.columns and "amount" in df.columns:
            cat_stats = (
                df.groupby("category")["amount"]
                .agg(["mean", "sum"])
                .rename(columns={"mean": "category_avg_amount", "sum": "category_total_spend"})
            )
            df = df.merge(cat_stats, on="category", how="left")

        # 3. Deviation ratio from merchant baseline
        if "amount" in df.columns and "merchant_avg_amount" in df.columns:
            df["amount_to_merchant_ratio"] = (df["amount"] / (df["merchant_avg_amount"] + 1e-6)).round(3)

        return df
