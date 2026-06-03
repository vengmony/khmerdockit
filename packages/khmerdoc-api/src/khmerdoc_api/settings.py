"""Runtime settings for the API server.

Loaded from environment variables (and an optional ``.env`` file at the
repo root). All values are exposed as a typed Pydantic v2 model so the rest
of the code can rely on validation.
"""

from __future__ import annotations

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KHMERDOC_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- core ----
    log_level: str = "INFO"
    ocr_backend: str = "mock"
    ocr_lang: str = "en"
    extractor_backend: str = "rules"
    document_type_hint: str = "auto"

    # ---- API ----
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    api_max_upload_mb: int = 10
    api_allowed_mime: List[str] = Field(
        default_factory=lambda: [
            "image/jpeg",
            "image/png",
            "image/webp",
            "application/pdf",
            "text/plain",
        ]
    )

    # ---- LLM (optional) ----
    llm_enabled: bool = False
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    @field_validator("api_cors_origins", "api_allowed_mime", mode="before")
    @classmethod
    def _split_csv(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("api_max_upload_mb")
    @classmethod
    def _positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("api_max_upload_mb must be > 0")
        return v


_settings: Settings | None = None


def get_settings() -> Settings:
    """Lazily load and cache the global :class:`Settings` instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
