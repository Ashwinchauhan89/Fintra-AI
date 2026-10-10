# Fintra-AI Automated Data & ETL Pipeline

Modular, production-grade transaction data ingestion, cleaning, and feature engineering pipeline for Fintra-AI.

## 🚀 Architecture

```text
Raw Sources (CSV / JSON / Database)
                 │
                 ▼
      [TransactionIngestor]
  - Schema alias harmonization
  - Null coercion & type checks
                 │
                 ▼
       [TransactionCleaner]
  - Deduplication
  - Zero/negative amount pruning
  - Temporal feature extraction
                 │
                 ▼
       [FeatureEngineer]
  - Rolling category & merchant spend
  - Historical spend baselines
  - Anomaly ratio signals
                 │
                 ▼
        ML Feature Matrix
```

---

## 🛠️ Usage Example

```python
from data_pipeline.pipeline import FinancialDataPipeline

pipeline = FinancialDataPipeline()

raw_records = [
    {"id": "tx_101", "date": "2026-08-25", "amount": 420.0, "vendor": "Swiggy", "category": "Food"},
    {"id": "tx_102", "date": "2026-08-25", "amount": 1499.0, "vendor": "Zara", "category": "Shopping"},
]

feature_df = pipeline.process_records(raw_records)
print(feature_df[["merchant", "amount", "merchant_avg_amount", "amount_to_merchant_ratio"]])
```

---

## 🧪 Testing

```bash
python -m unittest discover -s data_pipeline/tests -p 'test_*.py'
```
