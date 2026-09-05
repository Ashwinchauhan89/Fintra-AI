"""
Transaction Preprocessing & Data Cleaning Module.
Cleans raw ingested data, handles missing values, deduplicates, and validates bounds.
"""

from typing import Optional
import pandas as pd


class TransactionCleaner:
    """Cleans and validates transaction datasets."""

    def __init__(self, drop_duplicates: bool = True, remove_zero_amounts: bool = True):
        self.drop_duplicates = drop_duplicates
        self.remove_zero_amounts = remove_zero_amounts

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Executes full cleaning pipeline on a transaction DataFrame."""
        if df.empty:
            return df

        df = df.copy()

        # 1. Clean strings
        for col in ["merchant", "category", "type"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        if "category" in df.columns:
            df["category"] = df["category"].str.lower()

        if "type" in df.columns:
            df["type"] = df["type"].str.upper()

        # 2. Filter zero or invalid amounts
        if self.remove_zero_amounts and "amount" in df.columns:
            df = df[df["amount"] > 0.0]

        # 3. Deduplicate
        if self.drop_duplicates:
            subset = [c for c in ["date", "merchant", "amount"] if c in df.columns]
            if subset:
                df = df.drop_duplicates(subset=subset, keep="first")

        # 4. Temporal Features Extraction
        if "date" in df.columns:
            df["year"] = df["date"].dt.year
            df["month"] = df["date"].dt.month
            df["day"] = df["date"].dt.day
            df["day_of_week"] = df["date"].dt.dayofweek
            df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

        df = df.reset_index(drop=True)
        return df
