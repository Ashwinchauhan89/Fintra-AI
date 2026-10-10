"""
FastAPI Production REST Microservice for Fintra-AI (Phase 19).

Serves all 15 Machine Learning intelligence engines and AI Copilot:
- Automatic interactive documentation via Swagger UI (/docs) and ReDoc (/redoc)
- CORS middleware for Next.js web application frontend integration
- Sub-millisecond synchronous & asynchronous inference endpoints
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from api.routes import budget, copilot, expenses, health, persona, risk, wealth  # noqa: E402

app = FastAPI(
    title="Fintra-AI ML Production REST Microservice",
    description="High-performance machine learning inference API and AI financial copilot service powering the Fintra-AI platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Next.js local development & production staging
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All Sub-Routers
app.include_router(health.router)
app.include_router(expenses.router)
app.include_router(budget.router)
app.include_router(risk.router)
app.include_router(wealth.router)
app.include_router(persona.router)
app.include_router(copilot.router)


@app.get("/")
def root():
    return {
        "service": "Fintra-AI ML Production REST Microservice",
        "status": "running",
        "documentation": "/docs",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
