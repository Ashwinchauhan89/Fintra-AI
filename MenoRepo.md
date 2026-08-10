                         ┌─────────────────────────┐
                         │       USER / CLIENT     │
                         │  Desktop / Mobile Web  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────┐
                  │          NEXT.JS FRONTEND          │
                  │                                    │
                  │ Dashboard │ Transactions │ Budget  │
                  │ Analytics │ Goals │ AI Assistant   │
                  └────────────────┬───────────────────┘
                                   │ HTTPS
                                   ▼
                  ┌────────────────────────────────────┐
                  │          FASTAPI BACKEND            │
                  │                                    │
                  │ Auth │ Validation │ Rate Limiting │
                  │ Transactions │ Budgets │ Reports   │
                  └───────┬──────────────┬─────────────┘
                          │              │
             ┌────────────▼─────┐   ┌───▼────────────────┐
             │   PostgreSQL     │   │    AI SERVICES     │
             │                  │   │                    │
             │ Users            │   │ Gemini             │
             │ Transactions     │   │ Categorization     │
             │ Budgets          │   │ Forecasting        │
             │ Goals            │   │ Anomaly Detection  │
             │ AI Insights      │   │ Financial Assistant│
             └──────────────────┘   └─────────┬──────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │    ML PIPELINE     │
                                    │                    │
                                    │ Feature Engineering│
                                    │ Model Training     │
                                    │ Evaluation         │
                                    │ Model Registry     │
                                    └─────────┬──────────┘
                                              │
                         ┌────────────────────▼────────────┐
                         │         MLOps / Storage         │
                         │                                │
                         │ MLflow │ DVC │ Object Storage │
                         │ Docker │ GitHub Actions        │
                         └─────────────────────────────────┘


Fintra AI/
│
├── ai-finance-platform/                         # Next.js application
│   ├── app/
│   ├── actions/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── public/
│   ├── emails/
│   ├── middleware.js
│   ├── next.config.mjs
│   ├── package.json
│   └── ...
│
├── backend/                          # NEW — FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── transactions.py
│   │   │       ├── budgets.py
│   │   │       ├── analytics.py
│   │   │       ├── predictions.py
│   │   │       ├── ai.py
│   │   │       └── reports.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── transaction_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── prediction_service.py
│   │   │   └── ai_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── ml/                               # NEW — Machine Learning
│   ├── datasets/
│   ├── preprocessing/
│   ├── features/
│   ├── training/
│   │   ├── train_categorization.py
│   │   ├── train_forecasting.py
│   │   └── train_anomaly.py
│   ├── inference/
│   ├── evaluation/
│   └── models/
│
├── data_pipeline/                    # NEW
│   ├── ingestion/
│   ├── preprocessing/
│   └── jobs/
│
├── notebooks/                        # NEW
│   ├── 01_eda.ipynb
│   ├── 02_categorization.ipynb
│   └── 03_forecasting.ipynb
│
├── infrastructure/                   # NEW — deployment
│   ├── docker/
│   ├── monitoring/
│   └── terraform/
│
├── .github/
│   └── workflows/
│       ├── frontend-ci.yml
│       ├── backend-ci.yml
│       └── ml-ci.yml
│
├── docs/
├── Screenshots/
├── docker-compose.yml
├── .gitignore
└── README.md