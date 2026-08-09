# 💸 Fintra-AI

### 🚀 AI-Powered Personal Finance Management Platform

> **Track. Understand. Predict. Improve.**
> Fintra-AI combines modern web technologies, Artificial Intelligence, Machine Learning, and secure cloud infrastructure to help users make smarter financial decisions.

![Fintra-AI](https://img.shields.io/badge/Fintra--AI-AI%20Finance-6366F1?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge\&logo=next.js)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge\&logo=react)
![Prisma](https://img.shields.io/badge/Prisma-ORM-2D3748?style=for-the-badge\&logo=prisma)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge\&logo=postgresql)
![Gemini](https://img.shields.io/badge/Google%20Gemini-AI-4285F4?style=for-the-badge\&logo=google)
![Vercel](https://img.shields.io/badge/Vercel-Deployment-black?style=for-the-badge\&logo=vercel)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📌 Table of Contents

* [Overview](#-overview)
* [Why Fintra-AI?](#-why-fintra-ai)
* [Key Features](#-key-features)
* [AI & Machine Learning](#-ai--machine-learning)
* [Analytics](#-analytics)
* [Security](#-security)
* [Technology Stack](#-technology-stack)
* [System Architecture](#-system-architecture)
* [Project Structure](#-project-structure)
* [Getting Started](#-getting-started)
* [Environment Variables](#-environment-variables)
* [Database Setup](#-database-setup)
* [Development Workflow](#-development-workflow)
* [Documentation](#-documentation)
* [Roadmap](#-roadmap)
* [IEEE Summer of Code 2026](#-ieee-summer-of-code-2026)
* [Contributing](#-contributing)
* [Future Vision](#-future-vision)
* [License](#-license)
* [Maintainer](#-maintainer)

---

# 📖 Overview

**Fintra-AI** is an AI-powered personal finance management platform designed to transform raw financial data into actionable insights.

Instead of simply recording transactions, Fintra-AI aims to help users understand **where their money goes, why they spend it, what may happen next, and how they can improve their financial health.**

The platform combines:

* 💰 Personal finance management
* 🤖 Generative AI
* 🧠 Machine Learning
* 📊 Financial analytics
* 🔐 Secure authentication
* ☁️ Cloud-native infrastructure
* 📈 Predictive financial insights

### 🎯 Core Objective

> **Turn financial data into intelligent, personalized, and actionable financial decisions.**

---

# 💡 Why Fintra-AI?

Traditional expense trackers primarily answer:

> **"Where did my money go?"**

Fintra-AI aims to answer much more:

* Where am I spending the most?
* What spending patterns are emerging?
* Am I likely to exceed my budget?
* How healthy is my financial behavior?
* What can I do to improve my savings?
* Which financial goals are achievable?
* Can AI help me plan my next month?
* Can machine learning identify unusual financial activity?

This creates a shift from:

**Expense Tracking → Financial Intelligence**

---

# ✨ Key Features

## 💰 Personal Finance Management

* Expense Tracking
* Income Tracking
* Budget Management
* Savings Goals
* Financial Dashboard
* Monthly Reports
* Cash Flow Analysis
* Category-Based Expenses
* Transaction Management
* Financial Summary

---

## 🤖 AI Financial Intelligence

Powered by **Google Gemini AI**, Fintra-AI can provide intelligent financial assistance such as:

* AI Financial Advisor
* AI Budget Suggestions
* AI Expense Insights
* AI Goal Planning
* AI Spending Analysis
* AI Financial Chat Assistant
* Personalized Recommendations
* Financial Data Summarization
* Smart Budget Recommendations

---

## 🧠 Machine Learning

The planned ML engine focuses on transforming historical financial data into predictive insights.

### ML Capabilities

| Capability                | Purpose                                     |
| ------------------------- | ------------------------------------------- |
| 📂 Expense Classification | Predict appropriate expense categories      |
| 📈 Spending Forecasting   | Estimate future spending                    |
| 💰 Budget Prediction      | Predict potential budget overruns           |
| 🚨 Fraud Detection        | Identify suspicious financial patterns      |
| ❤️ Financial Health Score | Estimate overall financial behavior         |
| 🎯 Goal Prediction        | Estimate goal completion probability        |
| 💡 Recommendation Engine  | Generate personalized financial suggestions |
| 📊 Trend Detection        | Identify changes in spending behavior       |

---

# 📊 Analytics

Fintra-AI provides a data-driven view of personal finances.

### Analytics Modules

* Expense Analytics
* Income Analytics
* Category Distribution
* Monthly Spending Trends
* Cash Flow Analysis
* Budget Utilization
* Savings Analysis
* Financial Reports
* Interactive Charts
* Historical Comparisons

### Example Financial Intelligence Flow

```text
Financial Transactions
        │
        ▼
   Data Processing
        │
        ▼
 ┌───────────────────┐
 │ Feature Extraction│
 └─────────┬─────────┘
           │
           ▼
    ML / AI Engine
           │
     ┌─────┴─────┐
     ▼           ▼
Prediction    Insights
     │           │
     └─────┬─────┘
           ▼
 Personalized
 Recommendations
```

---

# 🔐 Security

Security is a core component of Fintra-AI because financial data is highly sensitive.

### Security Stack

* 🔑 Clerk Authentication
* 🛡️ Arcjet Security
* 🔒 Protected APIs
* 👤 Session Management
* 🗄️ Secure Database Access
* 🎭 Role-Based Access Control
* 🔐 Environment-Based Secrets
* 🚫 No sensitive credentials committed to source control

> **Never commit `.env`, API keys, database credentials, or authentication secrets to Git.**

---

# 📧 Notifications

Fintra-AI can provide timely financial notifications including:

* 📩 Email Notifications
* ⚠️ Budget Alerts
* 🎯 Savings Goal Reminders
* 📊 Monthly Financial Reports
* 🔔 Financial Activity Notifications

Email infrastructure is powered by **Resend**.

---

# 🏗️ Technology Stack

## Frontend

* Next.js
* React
* Tailwind CSS
* Shadcn UI

## Backend

* Next.js Server Actions
* Prisma ORM
* PostgreSQL

## Artificial Intelligence

* Google Gemini API

## Machine Learning

* Scikit-Learn
* TensorFlow
* PyTorch
* XGBoost
* Prophet

## Authentication

* Clerk

## Email

* Resend

## Application Security

* Arcjet

## Deployment

* Vercel

---

# 🧩 System Architecture

```text
                        ┌──────────────────────┐
                        │      User / Client   │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │      Next.js App     │
                        │   UI + Server Logic  │
                        └──────────┬───────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
             ┌───────────┐  ┌───────────┐  ┌────────────┐
             │   Clerk   │  │  Arcjet   │  │  Resend    │
             │   Auth    │  │ Security  │  │   Email    │
             └───────────┘  └───────────┘  └────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │      Prisma      │
                         │       ORM        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   PostgreSQL     │
                         │    Database      │
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │       AI / ML Layer     │
                    ├─────────────────────────┤
                    │ Google Gemini           │
                    │ ML Prediction Models    │
                    │ Recommendation Engine   │
                    │ Financial Analytics     │
                    └─────────────────────────┘
```

---

# 📂 Project Structure

```text
Fintra-AI/
│
├── app/                       # Next.js application routes
│
├── components/                # Reusable UI components
│
├── data/                      # Application and financial data
│
├── emails/                    # Email templates
│
├── hooks/                     # Custom React hooks
│
├── lib/                       # Utilities and services
│
├── prisma/                    # Prisma schema and database configuration
│
├── public/                    # Static assets
│
├── docs/                      # Project documentation
│   ├── PLANNING.md
│   ├── MACHINELEARNING.md
│   ├── CONTRIBUTING.md
│   ├── ARCHITECTURE.md
│   └── SECURITY.md
│
├── .env.example               # Environment variable template
├── package.json
├── README.md
└── LICENSE
```

---

# 🚀 Getting Started

Follow these steps to run Fintra-AI locally.

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Ashwinchauhan89/Fintra-AI.git

cd Fintra-AI
```

## 2️⃣ Install Dependencies

```bash
npm install
```

## 3️⃣ Configure Environment Variables

Create a `.env` file in the project root.

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

> ⚠️ Keep all secrets private and never commit `.env` to Git.

## 4️⃣ Generate Prisma Client

```bash
npx prisma generate
```

## 5️⃣ Initialize Database

```bash
npx prisma db push
```

## 6️⃣ Start Development Server

```bash
npm run dev
```

The application will be available at:

```text
http://localhost:3000
```

---

# 🗄️ Database Workflow

Fintra-AI uses **Prisma ORM** with **PostgreSQL**.

### Generate Prisma Client

```bash
npx prisma generate
```

### Push Schema Changes

```bash
npx prisma db push
```

### Open Prisma Studio

```bash
npx prisma studio
```

Prisma Studio can be used to inspect and manage development database records.

---

# 🧪 Development Workflow

Recommended development flow:

```text
Create Issue
     │
     ▼
Create Feature Branch
     │
     ▼
Implement Feature
     │
     ▼
Run Tests / Checks
     │
     ▼
Review Changes
     │
     ▼
Commit
     │
     ▼
Push Branch
     │
     ▼
Open Pull Request
     │
     ▼
Code Review
     │
     ▼
Merge
```

### Branch Naming

Recommended naming convention:

```text
feature/expense-analytics
feature/ai-budget-advisor
feature/ml-spending-prediction

fix/authentication-error
fix/dashboard-loading

docs/update-readme
docs/ml-documentation
```

---

# 📚 Documentation

| Document             | Description                          |
| -------------------- | ------------------------------------ |
| `README.md`          | Project overview and setup           |
| `PLANNING.md`        | Development roadmap and milestones   |
| `MACHINELEARNING.md` | ML architecture and pipeline         |
| `ARCHITECTURE.md`    | System architecture and design       |
| `CONTRIBUTING.md`    | Contribution guidelines              |
| `SECURITY.md`        | Security policies and best practices |

---

# 🛣️ Roadmap

## 🟢 Phase 1 — Core Finance

* [x] Authentication
* [x] Dashboard
* [x] Expense Management
* [x] Income Management
* [ ] Advanced Transaction Management

## 🟡 Phase 2 — Financial Analytics

* [x] Budget Planning
* [x] Reports
* [x] Analytics
* [ ] Advanced Cash Flow Analytics
* [ ] Financial Trend Detection

## 🔵 Phase 3 — AI Financial Assistant

* [ ] AI Financial Advisor
* [ ] Gemini Integration
* [ ] AI Budget Recommendations
* [ ] Personalized Financial Insights
* [ ] AI Financial Copilot

## 🟣 Phase 4 — Machine Learning

* [ ] Expense Classification
* [ ] Spending Prediction
* [ ] Budget Forecasting
* [ ] Fraud Detection
* [ ] Financial Health Score
* [ ] Goal Completion Prediction
* [ ] Recommendation Engine

## 🔴 Phase 5 — Advanced Platform

* [ ] OCR Receipt Scanner
* [ ] Investment Tracker
* [ ] Family Wallet
* [ ] Voice Finance Assistant
* [ ] PWA Support
* [ ] Multi-Currency Support
* [ ] Open Banking Integration
* [ ] Explainable AI
* [ ] MLOps Pipeline

📄 See `docs/PLANNING.md` for the detailed roadmap.

---

# 🎓 IEEE Summer of Code 2026

Fintra-AI is designed as an **open-source collaboration project** and welcomes contributors interested in software engineering, Artificial Intelligence, Machine Learning, cybersecurity, data analytics, and product development.

### Contribution Levels

| Level           | Suitable Contributions                              |
| --------------- | --------------------------------------------------- |
| 🟢 Beginner     | Documentation, UI improvements, testing, bug fixes  |
| 🟡 Intermediate | APIs, database features, analytics, backend modules |
| 🔴 Advanced     | AI, ML, fraud detection, predictive analytics, OCR  |

### Potential Contribution Areas

```text
Frontend
   ├── Dashboard
   ├── Charts
   └── UI/UX

Backend
   ├── APIs
   ├── Database
   └── Server Actions

AI
   ├── Gemini Integration
   ├── Financial Advisor
   └── Recommendations

ML
   ├── Classification
   ├── Forecasting
   ├── Fraud Detection
   └── Financial Health

DevOps
   ├── CI/CD
   ├── Testing
   └── Deployment
```

---

# 🤝 Contributing

Contributions are welcome from:

* 👨‍💻 Software Developers
* 🎨 UI/UX Designers
* 🤖 AI Engineers
* 🧠 Machine Learning Engineers
* 📊 Data Scientists
* 🔐 Cybersecurity Developers
* 🧪 QA/Test Engineers
* 📝 Technical Writers

### Contribution Steps

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Test your changes locally.
5. Commit your changes.
6. Push your branch.
7. Open a Pull Request.
8. Participate in code review.

Before contributing, please read:

```text
docs/CONTRIBUTING.md
```

---

# 🌟 Future Vision

Fintra-AI aims to evolve from a traditional finance tracker into a complete **AI Financial Intelligence Platform**.

### Long-Term Vision

```text
                 ┌──────────────────────┐
                 │      FINTRA-AI       │
                 │ Financial Intelligence│
                 └──────────┬───────────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
   AI Advisor          ML Prediction        Analytics
       │                    │                    │
       ▼                    ▼                    ▼
  Personalized       Future Spending      Financial
  Recommendations      Forecasting         Insights
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                  Smarter Financial Decisions
```

### 🔮 Future Capabilities

* 🤖 AI Financial Copilot
* 🧠 Advanced ML Prediction Engine
* 🚨 Real-Time Fraud Detection
* 🏦 Open Banking Integration
* 🎙️ Voice Finance Assistant
* 📷 Smart Receipt OCR
* 📈 Investment Portfolio Management
* 🌍 Multi-Currency Support
* 🔍 Explainable AI
* ⚙️ Production MLOps Pipeline
* 👨‍👩‍👧 Family Finance Management
* 📱 Progressive Web Application

---

# 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for complete license information.

---

# 👨‍💻 Maintainer

### Ashwin Chauhan

**Project Lead — Fintra-AI**

GitHub: **@Ashwinchauhan89**

---

# ⭐ Support the Project

If you find **Fintra-AI** useful, interesting, or valuable for learning:

### ⭐ Star the repository

### 🍴 Fork the project

### 🐛 Report bugs

### 💡 Suggest features

### 🤝 Contribute

Every contribution helps improve the project and grow the open-source community around Fintra-AI.

---

<div align="center">

## 💸 Fintra-AI

### **From Financial Data → Financial Intelligence**

Built with ❤️ using **Next.js · Prisma · PostgreSQL · Gemini AI · Machine Learning**

**Happy Coding! 🚀**

</div>
