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


# 📁 Fintra-AI — Project Structure

```text
Fintra-AI/
│
├── ai-finance-platform/                    # Next.js Frontend Application
│   ├── app/                                # App Router & Pages
│   ├── actions/                            # Server Actions
│   ├── components/                         # Reusable UI Components
│   ├── hooks/                              # Custom React Hooks
│   ├── lib/                                # Utilities & Configurations
│   ├── public/                             # Static Assets
│   ├── emails/                             # Email Templates
│   ├── middleware.js                       # Authentication & Middleware
│   ├── next.config.mjs                     # Next.js Configuration
│   ├── package.json
│   └── ...
│
├── backend/                                # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/                         # Versioned REST API
│   │   │       ├── transactions.py        # Transaction Management
│   │   │       ├── budgets.py              # Budget Management
│   │   │       ├── analytics.py            # Financial Analytics
│   │   │       ├── predictions.py          # ML Predictions
│   │   │       ├── ai.py                   # AI-powered Features
│   │   │       └── reports.py              # Financial Reports
│   │   │
│   │   ├── core/                            # Core Backend Configuration
│   │   │   ├── config.py                   # Application Configuration
│   │   │   ├── database.py                 # Database Configuration
│   │   │   └── security.py                 # Authentication & Security
│   │   │
│   │   ├── models/                          # Database Models
│   │   ├── schemas/                         # Pydantic Schemas
│   │   │
│   │   ├── services/                        # Business Logic Layer
│   │   │   ├── transaction_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── prediction_service.py
│   │   │   └── ai_service.py
│   │   │
│   │   └── main.py                          # FastAPI Application Entry Point
│   │
│   ├── tests/                               # Backend Tests
│   ├── requirements.txt                     # Python Dependencies
│   └── Dockerfile                           # Backend Container
│
├── ml/                                      # Machine Learning Pipeline
│   ├── datasets/                            # ML Datasets
│   ├── preprocessing/                       # Data Preprocessing
│   ├── features/                            # Feature Engineering
│   ├── training/                            # Model Training
│   │   ├── train_categorization.py         # Expense Categorization
│   │   ├── train_forecasting.py            # Financial Forecasting
│   │   └── train_anomaly.py                # Anomaly Detection
│   │
│   ├── inference/                           # Model Inference
│   ├── evaluation/                          # Model Evaluation
│   └── models/                              # Trained ML Models
│
├── data_pipeline/                           # Data Engineering Pipeline
│   ├── ingestion/                           # Data Ingestion
│   ├── preprocessing/                       # Data Cleaning & Processing
│   └── jobs/                                # Automated Data Jobs
│
├── notebooks/                               # Jupyter Notebooks
│   ├── 01_eda.ipynb                         # Exploratory Data Analysis
│   ├── 02_categorization.ipynb              # Expense Categorization
│   └── 03_forecasting.ipynb                 # Financial Forecasting
│
├── infrastructure/                         # DevOps & Cloud Infrastructure
│   ├── docker/                              # Docker Configuration
│   ├── monitoring/                          # Monitoring & Observability
│   └── terraform/                           # Infrastructure as Code
│
├── .github/
│   └── workflows/                           # CI/CD Pipelines
│       ├── frontend-ci.yml                  # Frontend CI
│       ├── backend-ci.yml                   # Backend CI
│       └── ml-ci.yml                        # ML CI
│
├── docs/                                    # Project Documentation
├── Screenshots/                             # Application Screenshots
│
├── docker-compose.yml                       # Multi-Service Docker Setup
├── .gitignore                               # Git Ignore Rules
└── README.md                                # Project Documentation
```

## 🏗️ Architecture Overview

Fintra-AI follows a **Full-Stack AI/ML Microservice Architecture**, separating the frontend, backend APIs, machine-learning workloads, data pipelines, and infrastructure into independently maintainable layers.

```text
                         ┌─────────────────────────┐
                         │       User / Client     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   Next.js Frontend      │
                         │  ai-finance-platform/   │
                         └────────────┬────────────┘
                                      │ REST API
                                      ▼
                         ┌─────────────────────────┐
                         │     FastAPI Backend     │
                         │       backend/          │
                         └───────┬─────────┬───────┘
                                 │         │
                    ┌────────────┘         └─────────────┐
                    ▼                                    ▼
          ┌──────────────────┐                 ┌──────────────────┐
          │   ML Services    │                 │  Data Pipeline   │
          │       ml/        │                 │ data_pipeline/   │
          └────────┬─────────┘                 └────────┬─────────┘
                   │                                    │
                   ▼                                    ▼
          ┌──────────────────┐                 ┌──────────────────┐
          │ Trained Models   │                 │ Data Processing  │
          │ Forecasting      │                 │ Ingestion        │
          │ Categorization   │                 │ ETL Jobs         │
          │ Anomaly Detection│                 └──────────────────┘
          └──────────────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Database / Data  │
          │      Layer       │
          └──────────────────┘
```

### 🔑 Core Layers

| Layer                | Directory              | Responsibility                                     |
| -------------------- | ---------------------- | -------------------------------------------------- |
| **Frontend**         | `ai-finance-platform/` | User interface, dashboards and client interactions |
| **Backend**          | `backend/`             | REST APIs, authentication and business logic       |
| **AI/ML**            | `ml/`                  | Training, inference and financial intelligence     |
| **Data Engineering** | `data_pipeline/`       | Data ingestion, preprocessing and automation       |
| **Research**         | `notebooks/`           | EDA, experimentation and model research            |
| **Infrastructure**   | `infrastructure/`      | Docker, monitoring and cloud deployment            |
| **CI/CD**            | `.github/workflows/`   | Automated testing and deployment                   |
| **Documentation**    | `docs/`                | Technical and project documentation                |

### 🤖 AI/ML Capabilities

Fintra-AI's ML layer is designed around three primary intelligence modules:

* **Expense Categorization** — Automatically classifies financial transactions.
* **Financial Forecasting** — Predicts future spending and financial trends.
* **Anomaly Detection** — Identifies unusual or potentially suspicious transactions.

This separation keeps **model development and experimentation independent from the production FastAPI services**, making the platform easier to scale, test, deploy, and maintain.

```
```
