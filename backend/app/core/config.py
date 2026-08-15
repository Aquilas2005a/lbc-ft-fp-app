from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import quote

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "lbc-ft-fp-app"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    postgres_db: str = "lbc_db"
    postgres_user: str = "lbc_user"
    postgres_password: str = "lbc_password"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str | None = None
    default_match_threshold: float = Field(default=85.0, ge=0.0, le=100.0)
    high_transaction_amount: float = Field(default=1_000_000.0, gt=0.0)
    transaction_frequency_count: int = Field(default=3, ge=2, le=100)
    transaction_frequency_window_hours: int = Field(default=24, ge=1, le=168)
    high_risk_countries: Annotated[list[str], NoDecode] = []
    screening_mode: Literal["mock", "opensanctions", "auto"] = "mock"
    open_sanctions_api_url: str = "https://api.opensanctions.org"
    open_sanctions_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENSANCTIONS_API_KEY", "OPEN_SANCTIONS_API_KEY"),
    )
    open_sanctions_timeout_seconds: float = Field(default=10.0, gt=0.0, le=30.0)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("high_risk_countries", mode="before")
    @classmethod
    def normalize_high_risk_countries(cls, value: str | list[str]) -> list[str]:
        values = value.split(",") if isinstance(value, str) else value
        return sorted({item.strip().upper() for item in values if item.strip()})

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        return (
            "postgresql+psycopg://"
            f"{quote(self.postgres_user, safe='')}:"
            f"{quote(self.postgres_password, safe='')}@"
            f"{self.postgres_host}:{self.postgres_port}/"
            f"{quote(self.postgres_db, safe='')}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
