import json
from functools import lru_cache
from urllib.parse import parse_qsl, quote_plus, urlencode, urlparse, urlunparse

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "AI Lead Qualification System"
    APP_ENV: str = "development"

    API_V1_PREFIX: str = "/api/v1"
    API_BASE_URL: str = "http://localhost"
    FRONTEND_BASE_URL: str = "http://localhost"

    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/lead_qualification"
    PGHOST: str = ""
    PGPORT: int = 5432
    PGUSER: str = ""
    PGPASSWORD: str = ""
    PGDATABASE: str = ""
    DATABASE_SSLMODE: str = "require"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    USE_QDRANT: bool = False
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_API_KEY: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = Field(default="", validation_alias=AliasChoices("SMTP_USER", "SMTP_USERNAME"))
    SMTP_PASS: str = Field(default="", validation_alias=AliasChoices("SMTP_PASS", "SMTP_PASSWORD"))
    SMTP_FROM_EMAIL: str = "noreply@example.com"
    SMTP_USE_TLS: bool = True

    BACKEND_CORS_ORIGINS: str = "*"

    @staticmethod
    def _normalize_origin(value: str) -> str:
        cleaned = value.strip().rstrip("/")
        if not cleaned:
            return ""

        candidate = cleaned if "://" in cleaned else f"https://{cleaned}"
        parsed = urlparse(candidate)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
        return ""

    @staticmethod
    def _normalize_postgres_scheme(database_url: str) -> str:
        if database_url.startswith("postgres://"):
            return "postgresql+psycopg2://" + database_url[len("postgres://") :]
        if database_url.startswith("postgresql://"):
            return "postgresql+psycopg2://" + database_url[len("postgresql://") :]
        return database_url

    def _build_database_url_from_pg_parts(self) -> str:
        if not all([self.PGHOST, self.PGUSER, self.PGPASSWORD, self.PGDATABASE]):
            return ""

        user = quote_plus(self.PGUSER)
        password = quote_plus(self.PGPASSWORD)
        database = quote_plus(self.PGDATABASE)
        return f"postgresql+psycopg2://{user}:{password}@{self.PGHOST}:{self.PGPORT}/{database}"

    def sqlalchemy_database_url(self) -> str:
        raw_database_url = self.DATABASE_URL.strip() or self._build_database_url_from_pg_parts()

        if not raw_database_url:
            raw_database_url = "postgresql+psycopg2://postgres:postgres@db:5432/lead_qualification"

        normalized_url = self._normalize_postgres_scheme(raw_database_url)
        parsed = urlparse(normalized_url)

        if not parsed.scheme.startswith("postgresql"):
            return normalized_url

        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        sslmode = self.DATABASE_SSLMODE.strip().lower()
        if sslmode and "sslmode" not in query:
            query["sslmode"] = sslmode

        updated = parsed._replace(query=urlencode(query))
        return urlunparse(updated)

    def cors_origins_list(self) -> list[str]:
        raw_value = self.BACKEND_CORS_ORIGINS.strip()

        if raw_value and raw_value != "*":
            if raw_value.startswith("["):
                try:
                    parsed = json.loads(raw_value)
                    if isinstance(parsed, list):
                        origins = [self._normalize_origin(str(origin)) for origin in parsed]
                        filtered = [origin for origin in origins if origin]
                        if filtered:
                            return filtered
                except json.JSONDecodeError:
                    pass

            origins = [self._normalize_origin(origin) for origin in raw_value.split(",")]
            filtered = [origin for origin in origins if origin]
            if filtered:
                return filtered

        # Widget must work on ANY client website, so always allow all origins.
        return ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
