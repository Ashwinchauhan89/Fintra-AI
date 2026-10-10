"""
Application Configuration for Fintra-AI Backend Service.
"""

import os
from typing import List, Optional


class Settings:
    PROJECT_NAME: str = "Fintra-AI Backend & Prediction Service"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")

    # Allowed CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://fintra-ai.vercel.app",
    ]

    # Clerk Authentication
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")
    CLERK_PUBLISHABLE_KEY: str = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", os.getenv("CLERK_PUBLISHABLE_KEY", ""))
    CLERK_PEM_PUBLIC_KEY: Optional[str] = os.getenv("CLERK_PEM_PUBLIC_KEY", os.getenv("CLERK_JWT_KEY", None))
    CLERK_JWKS_URL: Optional[str] = os.getenv("CLERK_JWKS_URL", None)
    CLERK_ISSUER: Optional[str] = os.getenv("CLERK_ISSUER", None)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "RS256")

    # Inter-Service API Key Authentication
    BACKEND_API_KEY: str = os.getenv("BACKEND_API_KEY", "fintra_secret_key_default")
    INTERNAL_API_KEYS: List[str] = (
        [k.strip() for k in os.getenv("INTERNAL_API_KEYS", "").split(",") if k.strip()]
        if os.getenv("INTERNAL_API_KEYS")
        else []
    )

    # Rate Limiting (Arcjet Parity & In-Memory Token Bucket)
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() in ("true", "1")
    RATE_LIMIT_DEFAULT_RATE: int = int(os.getenv("RATE_LIMIT_DEFAULT_RATE", "60"))  # Requests
    RATE_LIMIT_DEFAULT_WINDOW: int = int(os.getenv("RATE_LIMIT_DEFAULT_WINDOW", "60"))  # Seconds
    RATE_LIMIT_BURST_CAPACITY: int = int(os.getenv("RATE_LIMIT_BURST_CAPACITY", "20"))


settings = Settings()
