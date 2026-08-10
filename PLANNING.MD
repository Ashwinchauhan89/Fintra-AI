<div align="center">

# 💸 Fintra-AI

### 🚀 AI-Powered Personal Finance Management Platform

Manage your finances smarter with Artificial Intelligence, Machine Learning, and Modern Cloud Technologies.

[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)]()
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)]()
[![Prisma](https://img.shields.io/badge/Prisma-ORM-2D3748?logo=prisma)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql)]()
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38BDF8?logo=tailwindcss)]()
[![Clerk](https://img.shields.io/badge/Auth-Clerk-6C47FF)]()
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4)]()
[![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Enabled-orange)]()
[![Open Source](https://img.shields.io/badge/Open%20Source-Welcome-success)]()

⭐ Star this repository if you find it useful!

</div>

---

# 📖 Overview

Fintra-AI is an **AI-powered Personal Finance Management Platform** built with **Next.js**, **Prisma**, **PostgreSQL**, **Google Gemini AI**, and **Machine Learning**.

The platform helps users manage expenses, track income, create budgets, monitor financial health, receive AI-powered recommendations, and leverage predictive analytics for smarter financial decisions.

---

# ✨ Key Features

## 💰 Finance Management

- Expense Tracking
- Income Tracking
- Budget Planning
- Savings Goals
- Financial Dashboard
- Monthly Reports
- Cash Flow Analysis
- Multi-Category Expenses

---

## 🤖 Artificial Intelligence

- AI Financial Advisor
- AI Budget Suggestions
- AI Expense Insights
- AI Goal Planner
- AI Spending Analysis
- AI Chat Assistant
- Personalized Financial Recommendations

---

## 🧠 Machine Learning

- Expense Category Prediction
- Spending Forecasting
- Budget Prediction
- Fraud Detection
- Financial Health Score
- Goal Completion Prediction
- Investment Recommendation
- Smart Recommendation Engine

---

## 📊 Analytics

- Expense Analytics
- Income Analytics
- Spending Trends
- Financial Reports
- Interactive Charts
- Cash Flow Dashboard

---

## 🔐 Security

- Clerk Authentication
- Arcjet Security
- Protected APIs
- Session Management
- Secure Database
- Role-Based Access Control

---

## 📧 Notifications

- Email Notifications
- Budget Alerts
- Goal Reminders
- Monthly Financial Reports

---

# 🏗 Tech Stack

## Frontend

- Next.js
- React
- Tailwind CSS
- Shadcn UI

## Backend

- Next.js Server Actions
- Prisma ORM
- PostgreSQL

## AI

- Google Gemini API

## Machine Learning

- Scikit-Learn
- TensorFlow
- PyTorch
- XGBoost
- Prophet

## Authentication

- Clerk

## Email

- Resend

## Security

- Arcjet

## Deployment

- Vercel

---

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


---

# 🚀 Quick Start

### Clone Repository

```bash
git clone https://github.com/Ashwinchauhan89/Fintra-AI.git

cd Fintra-AI
```

### Install Dependencies

```bash
npm install
```

### Configure Environment

Create a `.env` file.

```env
DATABASE_URL=
DIRECT_URL=

NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=

NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/onboarding
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

GEMINI_API_KEY=

RESEND_API_KEY=

ARCJET_KEY=
```

### Setup Database

```bash
npx prisma generate

npx prisma db push
```

### Run Development Server

```bash
npm run dev
```

Open

```
http://localhost:3000
```

---

# 📚 Documentation

| Document | Description |
|-----------|-------------|
| `README.md` | Project Overview |
| `PLANNING.md` | Complete Development Roadmap |
| `MACHINELEARNING.md` | Machine Learning Pipeline |
| `CONTRIBUTING.md` | Contribution Guidelines |
| `ARCHITECTURE.md` | System Design |
| `SECURITY.md` | Security Policies |

---

# 🛣 Roadmap

### Phase 1

- Authentication
- Dashboard
- Expense Management
- Income Management

### Phase 2

- Budget Planner
- Reports
- Analytics

### Phase 3

- AI Financial Advisor
- Gemini Integration
- Smart Recommendations

### Phase 4

- Machine Learning
- Fraud Detection
- Expense Prediction
- Financial Health Score

### Phase 5

- OCR Receipt Scanner
- Investment Tracker
- Family Wallet
- PWA Support

📄 See **PLANNING.md** for the complete roadmap.

---

# 🤝 Contributing

We welcome developers, designers, AI engineers, and machine learning enthusiasts.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push your branch.
5. Open a Pull Request.

Please read **CONTRIBUTING.md** before contributing.

---

# 🎯 IEEE Summer of Code 2026

This repository is designed for open-source collaboration.

Contribution levels:

- 🟢 Beginner — Documentation, UI, Bug Fixes
- 🟡 Intermediate — APIs, Database, Analytics
- 🔴 Advanced — AI, Machine Learning, Fraud Detection, OCR

---

# 🌟 Future Goals

- AI Financial Copilot
- Machine Learning Engine
- Fraud Detection System
- Open Banking Integration
- Voice Finance Assistant
- Smart Receipt OCR
- Investment Portfolio Manager
- Multi-Currency Support
- Explainable AI
- MLOps Pipeline

---

# 📄 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Maintainer

**Ashwin Chauhan**

Project Lead — Fintra-AI

GitHub: https://github.com/Ashwinchauhan89

---

<div align="center">

### ⭐ If you like this project, please Star the repository!

Made with ❤️ using Next.js, Prisma, Gemini AI & Machine Learning.

**Happy Coding! 🚀**

</div>