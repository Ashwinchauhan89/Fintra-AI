"""
End-to-End Data Pipeline Orchestrator.
Chains Ingestion -> Cleaning -> Feature Engineering.
"""

from typing import Any, Dict, List
import pandas as pd

from data_pipeline.ingestion.ingestor import TransactionIngestor
from data_pipeline.preprocessing.cleaner import TransactionCleaner
from data_pipeline.feature_engineering.features import FeatureEngineer


class FinancialDataPipeline:
    """Orchestrates end-to-end data processing for financial transactions."""

    def __init__(self):
        self.ingestor = TransactionIngestor()
        self.cleaner = TransactionCleaner()
        self.feature_engineer = FeatureEngineer()

    def process_records(self, raw_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Processes raw JSON/dict records into an ML-ready feature matrix."""
        df_raw = self.ingestor.ingest_records(raw_records)
        df_clean = self.cleaner.clean(df_raw)
        df_features = self.feature_engineer.compute_features(df_clean)
        return df_features

    def process_csv(self, csv_source: Any) -> pd.DataFrame:
        """Processes a raw CSV file into an ML-ready feature matrix."""
        df_raw = self.ingestor.ingest_csv(csv_source)
        df_clean = self.cleaner.clean(df_raw)
        df_features = self.feature_engineer.compute_features(df_clean)
        return df_features
