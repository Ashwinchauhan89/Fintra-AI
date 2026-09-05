"""
Unit Test Suite for Fintra-AI Data Pipeline.
"""

import unittest
from datetime import datetime
from data_pipeline.ingestion.ingestor import TransactionIngestor
from data_pipeline.preprocessing.cleaner import TransactionCleaner
from data_pipeline.feature_engineering.features import FeatureEngineer
from data_pipeline.pipeline import FinancialDataPipeline


class TestDataPipeline(unittest.TestCase):
    def setUp(self):
        self.raw_data = [
            {"id": "t1", "date": "2026-08-01 10:30:00", "amount": 450.0, "vendor": "Swiggy", "category": "Food"},
            {"id": "t2", "date": "2026-08-01 14:00:00", "amount": 1200.0, "vendor": "Amazon", "category": "Shopping"},
            {"id": "t3", "date": "2026-08-02 09:15:00", "amount": 350.0, "vendor": "Swiggy", "category": "Food"},
            # Duplicate transaction
            {"id": "t4", "date": "2026-08-02 09:15:00", "amount": 350.0, "vendor": "Swiggy", "category": "Food"},
            # Zero-amount transaction
            {"id": "t5", "date": "2026-08-02 12:00:00", "amount": 0.0, "vendor": "Test", "category": "Misc"},
        ]

    def test_ingestion(self):
        ingestor = TransactionIngestor()
        df = ingestor.ingest_records(self.raw_data)
        self.assertEqual(len(df), 5)
        self.assertIn("merchant", df.columns)
        self.assertIn("transaction_id", df.columns)

    def test_cleaning(self):
        ingestor = TransactionIngestor()
        df_raw = ingestor.ingest_records(self.raw_data)
        cleaner = TransactionCleaner()
        df_clean = cleaner.clean(df_raw)
        # 1 duplicate dropped + 1 zero-amount dropped = 3 rows remaining
        self.assertEqual(len(df_clean), 3)
        self.assertIn("day_of_week", df_clean.columns)
        self.assertIn("is_weekend", df_clean.columns)

    def test_feature_engineering(self):
        ingestor = TransactionIngestor()
        cleaner = TransactionCleaner()
        fe = FeatureEngineer()

        df_raw = ingestor.ingest_records(self.raw_data)
        df_clean = cleaner.clean(df_raw)
        df_features = fe.compute_features(df_clean)

        self.assertIn("merchant_avg_amount", df_features.columns)
        self.assertIn("category_avg_amount", df_features.columns)
        self.assertIn("amount_to_merchant_ratio", df_features.columns)

    def test_end_to_end_pipeline(self):
        pipeline = FinancialDataPipeline()
        df_out = pipeline.process_records(self.raw_data)
        self.assertEqual(len(df_out), 3)
        self.assertIn("amount_to_merchant_ratio", df_out.columns)


if __name__ == "__main__":
    unittest.main()
