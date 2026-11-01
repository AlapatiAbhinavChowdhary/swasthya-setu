from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, loaded from environment variables or the .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = Field(min_length=1)
    gemini_model: str = Field(min_length=1)
    retrieval_min_relevance: float = Field(default=0.25, ge=0, le=1)


settings = Settings()