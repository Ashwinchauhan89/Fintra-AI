# Fintra-AI Production Deployment Architecture

Comprehensive guide for deploying Fintra-AI across cloud platforms and containerized production environments.

---

## 🏗️ Production Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Ingress / CDN                      │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
     [Next.js 15 Web App]            [FastAPI ML Backend]
     - Vercel / Docker Container      - Railway / Render / AWS ECS
     - SSR & Client Rendering         - ML Inference Endpoints
     - Server Actions & Arcjet Edge   - Token-bucket Rate Limiter
               │                               │
               ▼                               ▼
    ┌──────────────────────┐         ┌──────────────────────┐
    │  PostgreSQL Database │         │   Clerk Auth JWKS    │
    │  (Neon / Supabase)   │         │   (Token Validation) │
    └──────────────────────┘         └──────────────────────┘
```

---

## 🚀 Deployment Options

### Option 1: Vercel + Railway / Render (Recommended Cloud Setup)

1. **Frontend (Next.js)**:
   - Deploy `ai-finance-platform` directly to **Vercel**.
   - Configure Environment Variables in Vercel Dashboard:
     - `DATABASE_URL` and `DIRECT_URL` (from Supabase/Neon PostgreSQL)
     - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY`
     - `ARCJET_KEY`, `RESEND_API_KEY`, `GEMINI_API_KEY`
     - `NEXT_PUBLIC_ML_SERVICE_URL` (Points to the deployed FastAPI service URL)

2. **Backend (FastAPI ML Service)**:
   - Deploy `backend/` as a Docker container on **Railway**, **Render**, or **AWS App Runner**.
   - Root Directory: Repository root `.`
   - Dockerfile: `backend/Dockerfile`
   - Port: `8000`
   - Environment Variables:
     - `DEBUG=False`
     - `CLERK_JWKS_URL` or `CLERK_SECRET_KEY`

---

### Option 2: Full-Stack Docker Compose Deployment (Self-Hosted VPS)

Deploy the entire platform on any Ubuntu / Debian VPS with Docker and Docker Compose installed:

```bash
# 1. Clone repository
git clone https://github.com/Ashwinchauhan89/Fintra-AI.git
cd Fintra-AI

# 2. Configure environment
cp ai-finance-platform/.env.example ai-finance-platform/.env

# 3. Build and launch all services in detached mode
docker compose up --build -d
```

#### Build Arguments Note
Next.js compiles `NEXT_PUBLIC_*` variables at *build time*. Ensure your `.env` contains valid values before executing `docker compose up --build` so that Clerk authentication and client features bundle properly.

---

## 🛡️ CI/CD Deployment Pipeline

The repository includes automated GitHub Actions:
- **`quality.yml`**: Triggers on PRs and pushes to `main` for linting, type-checking, building, and ML unit tests.
- **`deploy.yml`**: Triggers on pushes to `main` or manual dispatch (`workflow_dispatch`), building production container images for both the frontend and backend services.
