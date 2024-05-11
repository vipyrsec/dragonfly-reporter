from os import getenv

from pydantic_settings import BaseSettings, SettingsConfigDict

# Git SHA for Sentry
GIT_SHA = getenv("GIT_SHA", "development")


class EnvConfig(BaseSettings):
    """Our default configuration for models that should load from .env files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


class _Sentry(EnvConfig, env_prefix="sentry_"):  # pyright: ignore
    dsn: str = ""
    environment: str = "production"
    release_prefix: str = "dragonfly-reporter"


Sentry = _Sentry()  # pyright: ignore


class _PyPI(EnvConfig, env_prefix="pypi_"):  # pyright: ignore
    """Environment variables for PyPI."""

    base_url: str = "https://pypi.org/danger-api"
    api_token: str = ""


PyPI = _PyPI()
