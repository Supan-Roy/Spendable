from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    APP_NAME: str = "Spendable API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server settings (Railway dynamic PORT binding compatibility)
    PORT: int = Field(default=8000, alias="PORT")
    HOST: str = "0.0.0.0"

    # CORS settings
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    # Database settings
    DATABASE_URL: str = "sqlite:///./spendable.db"
    DATA_PROVIDER: str = "database"

    # AI Service settings (Gemini API integration)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # JWT Authentication settings
    JWT_SECRET: str = "spendable-demo-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(ROOT_DIR, ".env"),
            os.path.join(BASE_DIR, ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )



settings = Settings()
