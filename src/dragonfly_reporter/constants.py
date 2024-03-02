from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    """Our default configuration for models that should load from .env files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


class _PyPI(EnvConfig, env_prefix="pypi_"):  # pyright: ignore
    base_url: str = "https://pypi.org/danger-api"
    api_token: str = ""


PyPI = _PyPI()


class _Mail(EnvConfig, env_prefix="mail_"):  # pyright: ignore
    """Environment variables that are core to the app itself."""

    sender: str = "system@vipyrsec.com"


Mail = _Mail()


class _Microsoft(EnvConfig, env_prefix="microsoft_"):  # pyright: ignore
    """Environment variables for Microsoft."""

    tenant_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    scopes: list[str] = ["https://graph.microsoft.com/.default"]


Microsoft = _Microsoft()
