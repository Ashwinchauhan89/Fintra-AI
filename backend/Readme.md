# Fintra-AI Backend & Prediction Service

A modular, production-ready **FastAPI** backend service that exposes RESTful endpoints for Fintra-AI's Machine Learning and Financial Intelligence engines.

## 🚀 Features

- **Expense Category Classification**: Fast ML-driven categorization with confidence scoring.
- **Spending Anomaly & Duplicate Detection**: Real-time statistical spike detection and out-of-pattern spending warnings.
- **Multi-Factor Fraud Risk Scoring**: Supervised fraud probability (0–100%) and actionable risk tiering.
- **50/30/20 Budget Allocations**: Optimal demographic budget recommendations and overspending diagnostics.
- **Financial Health Scoring**: 5-pillar composite 0–100 scoring with letter grades (`A+` to `D`).
- **Goal Completion Forecasting**: Non-linear timeline solving and required monthly SIP projections.
- **Investment Portfolio Allocator**: Multi-asset recommendations across Equity, Debt, Gold, REITs, and Cash.
- **Interactive Documentation**: Auto-generated Swagger UI (`/api/v1/docs`) and ReDoc (`/api/v1/redoc`).

---

## 🛠️ Local Development

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
```

### 2. Run the Development Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```

Open your browser at `http://localhost:8000/api/v1/docs` to test endpoints interactively.

---

## 🐳 Docker Deployment

```bash
docker build -t fintra-ai-backend -f backend/Dockerfile .
docker run -p 8000:8000 fintra-ai-backend
```

---

## 🧪 Testing

Run backend contract and schema tests:
```bash
python -m unittest discover -s backend/tests -p 'test_*.py'
```
