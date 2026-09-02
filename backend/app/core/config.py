"""
Application Configuration for Fintra-AI Backend Service.
"""

import os
from typing import List


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


settings = Settings()
