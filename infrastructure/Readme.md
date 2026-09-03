# Fintra-AI Infrastructure & Container Orchestration

This directory details containerization, local development orchestration, and multi-service deployment for the Fintra-AI platform.

## 🐳 Architecture

Fintra-AI uses a multi-container Docker Compose architecture:

1. **`postgres` (Database)**: PostgreSQL 15 on port `5432` with automated health checks and persistent volume storage.
2. **`backend` (FastAPI ML Service)**: Python 3.11 service on port `8000` exposing REST endpoints for financial intelligence, fraud detection, budget optimization, and OCR receipt scanning.
3. **`frontend` (Next.js 15 Platform)**: Full-stack web application on port `3000` interfacing with PostgreSQL via Prisma and communicating with the ML backend via internal networking.

---

## 🚀 Quickstart

### Prerequisites
- Docker Engine `>=24.0.0`
- Docker Compose `>=v2.20.0`

### 1. Launch All Services
From the root repository directory:
```bash
docker compose up --build
```

### 2. Verify Running Services
- **Web App**: Open [http://localhost:3000](http://localhost:3000)
- **ML API Swagger UI**: Open [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **PostgreSQL**: Connect at `localhost:5432` (User: `fintra_user`, Database: `fintra_db`)

### 3. Stop Services
```bash
docker compose down
```

To remove persistent volumes as well:
```bash
docker compose down -v
```
