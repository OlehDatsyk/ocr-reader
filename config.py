"""
config.py
=========
Centralised application configuration.

All runtime configuration is supplied through environment variables (see
``.env.example``). Values are loaded with ``python-dotenv`` and validated
through a Pydantic v2 model so that a misconfigured deployment fails fast,
with a clear error message, instead of failing deep inside a request.

This module is imported exactly once; the module-level ``settings`` object
is the single source of truth for configuration throughout the codebase.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load the .env file (if present) into process environment variables before
# anything else reads them. This must happen at import time, before the
# Settings model below reads os.environ.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)


class Settings(BaseModel):
    """Strongly typed, validated application settings.

    Every field is populated from an environment variable of the same
    name (upper-cased). Sensible defaults are provided for everything
    except the OpenAI API key, which is mandatory in production but is
    allowed to be empty for local static analysis / test collection.
    """

    # --- Application metadata -------------------------------------------------
    app_name: str = Field(default="OCR Reader")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    # --- Server -----------------------------------------------------------------
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)

    # --- OpenAI -------------------------------------------------------------------
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4.1-mini")
    openai_timeout_seconds: float = Field(default=60.0)
    openai_max_output_tokens: int = Field(default=4000)

    # --- Storage ------------------------------------------------------------------
    database_path: Path = Field(default=BASE_DIR / "ocr_reader.db")
    log_dir: Path = Field(default=BASE_DIR / "logs")
    log_level: str = Field(default="INFO")

    # --- Upload constraints ---------------------------------------------------
    max_upload_size_mb: float = Field(default=8.0)
    allowed_mime_types: tuple[str, ...] = Field(
        default=(
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
            "image/bmp",
        )
    )

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, value: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = value.upper()
        if upper not in valid:
            raise ValueError(f"log_level must be one of {sorted(valid)}, got {value!r}")
        return upper

    @property
    def max_upload_size_bytes(self) -> int:
        return int(self.max_upload_size_mb * 1024 * 1024)

    @property
    def has_valid_api_key(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())


def _bool_env(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Build (and cache) the settings object from the current environment.

    Using ``lru_cache`` means the environment is only parsed once per
    process, while still allowing tests to call ``get_settings.cache_clear()``
    to force a reload after mutating ``os.environ``.
    """
    return Settings(
        app_name=os.environ.get("APP_NAME", "OCR Reader"),
        app_version=os.environ.get("APP_VERSION", "1.0.0"),
        environment=os.environ.get("ENVIRONMENT", "development"),
        debug=_bool_env("DEBUG", False),
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        openai_model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        openai_timeout_seconds=float(os.environ.get("OPENAI_TIMEOUT_SECONDS", "60")),
        openai_max_output_tokens=int(os.environ.get("OPENAI_MAX_OUTPUT_TOKENS", "4000")),
        database_path=Path(os.environ.get("DATABASE_PATH", str(BASE_DIR / "ocr_reader.db"))),
        log_dir=Path(os.environ.get("LOG_DIR", str(BASE_DIR / "logs"))),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
        max_upload_size_mb=float(os.environ.get("MAX_UPLOAD_SIZE_MB", "8")),
    )


settings = get_settings()
