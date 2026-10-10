"""
Transaction Data Ingestion Module.
Ingests raw transaction records from tabular sources (CSV, JSON, Python dicts)
and normalizes them into canonical schema formats for downstream pipelines.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd


CANONICAL_COLUMNS = [
    "transaction_id",
    "date",
    "amount",
    "type",
    "category",
    "merchant",
    "account_id",
    "user_id",
]


class TransactionIngestor:
    """Ingests and validates financial transaction feeds."""

    def __init__(self, default_currency: str = "INR"):
        self.default_currency = default_currency

    def ingest_records(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Normalizes a list of raw transaction dicts into a canonical DataFrame."""
        if not records:
            return pd.DataFrame(columns=CANONICAL_COLUMNS)

        df = pd.DataFrame(records)
        return self._standardize_schema(df)

    def ingest_csv(self, file_path_or_buffer: Any) -> pd.DataFrame:
        """Reads a CSV file and normalizes columns."""
        df = pd.read_csv(file_path_or_buffer)
        return self._standardize_schema(df)

    def _standardize_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Maps common aliases to canonical column names and validates required types."""
        column_mapping = {
            "id": "transaction_id",
            "txn_id": "transaction_id",
            "txn_date": "date",
            "timestamp": "date",
            "cost": "amount",
            "value": "amount",
            "transaction_type": "type",
            "vendor": "merchant",
            "store": "merchant",
            "description": "merchant",
        }

        # Rename columns if aliases are present
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns and v not in df.columns})

        # Ensure essential columns exist
        if "transaction_id" not in df.columns:
            df["transaction_id"] = [f"tx_{i}" for i in range(len(df))]
        if "merchant" not in df.columns:
            df["merchant"] = "General Merchant"
        if "category" not in df.columns:
            df["category"] = "other-expense"
        if "type" not in df.columns:
            df["type"] = "EXPENSE"

        # Coerce numeric amounts
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).abs()

        # Coerce dates
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").fillna(datetime.now())

        return df
