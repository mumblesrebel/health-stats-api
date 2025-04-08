from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import json
import os

class Settings(BaseSettings):
    MONGODB_URL: str
    MONGODB_NAME: str = "health_stats"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Local development
        "https://health-stats-tracker.netlify.app",  # Production frontend
        "https://health-stats-tracker.windsurf.build"  # Alternative production URL
    ]
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS from string if it's provided as an environment variable
        cors_origins = os.getenv("CORS_ORIGINS")
        if cors_origins:
            try:
                self.CORS_ORIGINS = json.loads(cors_origins)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse CORS_ORIGINS: {cors_origins}")
                self.CORS_ORIGINS = ["*"]

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# Print configuration for debugging (excluding sensitive values)
print("Current configuration:")
print(f"MONGODB_NAME: {settings.MONGODB_NAME}")
print(f"ALGORITHM: {settings.ALGORITHM}")
print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
print(f"CORS_ORIGINS: {settings.CORS_ORIGINS}")
