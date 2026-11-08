from functools import cache
import os
from typing import Any

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

DUMMY_VALUES = {
    "ci-dummy-key",
    "ci-dummy-model",
    "dummy",
    "placeholder",
    "your_api_key_here",
    "test-key",
}


def is_dummy_or_missing(val: str | None) -> bool:
    if not val:
        return True
    s = val.strip().lower()
    return not s or s in DUMMY_VALUES or "dummy" in s or "placeholder" in s


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
    enable_ocr: bool = Field(default=False)
    enable_overpass: bool = Field(default=False)
    admin_token: str | None = Field(default=None)
    enable_frontend: bool = Field(default=False)


@cache
def get_settings() -> Settings:
    return Settings()


def check_llm_configured() -> tuple[bool, str | None]:
    """Check whether Gemini LLM settings are configured with valid values."""
    try:
        s = get_settings()
    except ValidationError as err:
        locs = [str(e["loc"][0]) for e in err.errors() if e.get("loc")]
        if "gemini_api_key" in locs:
            return False, "GEMINI_API_KEY"
        if "gemini_model" in locs:
            return False, "GEMINI_MODEL"
        return False, "GEMINI_API_KEY"
    except Exception:
        return False, "GEMINI_API_KEY"

    if is_dummy_or_missing(s.gemini_api_key):
        return False, "GEMINI_API_KEY"
    if is_dummy_or_missing(s.gemini_model):
        return False, "GEMINI_MODEL"
    return True, None


class _SettingsProxy:
    """Lazy proxy for settings to allow importing modules without requiring GEMINI_API_KEY."""

    def __init__(self) -> None:
        self.__dict__["cors_origins"] = "*"
        self.__dict__["feedback_database"] = "data/swasthya_setu.db"
        self.__dict__["rate_limit_per_minute"] = 30
        self.__dict__["max_input_chars"] = 2000
        self.__dict__["gemini_max_retries"] = 2
        self.__dict__["retrieval_min_relevance"] = 0.25
        self.__dict__["retrieval_skip_relevance_gate_score"] = 0.84
        self.__dict__["vectorstore_backend"] = "chroma"
        self.__dict__["enable_ocr"] = False
        self.__dict__["_overrides"] = set()

    def __getattribute__(self, name: str) -> Any:
        if name in ("__dict__", "_overrides") or name.startswith("__"):
            return super().__getattribute__(name)
        if name in self.__dict__.get("_overrides", set()):
            return self.__dict__[name]
        try:
            return getattr(get_settings(), name)
        except Exception:
            if name in self.__dict__:
                return self.__dict__[name]
            raise

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value
        self.__dict__["_overrides"].add(name)
        try:
            setattr(get_settings(), name, value)
        except Exception:
            pass

    def __delattr__(self, name: str) -> None:
        if name in self.__dict__.get("_overrides", set()):
            self.__dict__["_overrides"].discard(name)
        if name in self.__dict__:
            del self.__dict__[name]
        else:
            super().__delattr__(name)


settings = _SettingsProxy()
