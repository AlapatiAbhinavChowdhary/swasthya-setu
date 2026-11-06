from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, loaded from environment variables or the .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = Field(min_length=1)
    gemini_model: str = Field(min_length=1)
    gemini_max_retries: int = Field(default=2, ge=0, le=5)
    retrieval_min_relevance: float = Field(default=0.25, ge=0, le=1)
    retrieval_skip_relevance_gate_score: float = Field(default=0.84, ge=0, le=1)
    cors_origins: str = "*"
    max_input_chars: int = Field(default=2000, ge=100, le=10000)
    rate_limit_per_minute: int = Field(default=30, ge=1, le=1000)
    feedback_database: str = "data/swasthya_setu.db"
    vectorstore_backend: str = "chroma"


settings = Settings()