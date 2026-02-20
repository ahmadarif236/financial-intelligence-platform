from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Database (Supabase)
    DATABASE_URL: str = "postgresql://[user]:[password]@[host]:[port]/[db-name]"

    # JWT
    SECRET_KEY: str = "gcc-cfo-ai-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # AI Service (Cerebras Cloud)
    AI_API_KEY: str = ""
    AI_API_URL: str = "https://api.cerebras.ai/v1/chat/completions"
    AI_MODEL: str = "llama-3.3-70b"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # App
    APP_NAME: str = "GCC CFO AI"
    APP_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
