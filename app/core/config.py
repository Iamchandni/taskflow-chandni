"""
app/core/config.py
──────────────────
Application configuration loaded from environment variables via pydantic-settings.
This is the single source of truth for all configurable values (DB credentials,
JWT parameters, bcrypt cost). No other file reads os.environ directly.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── PostgreSQL ──────────────────────────────────────────────
    POSTGRES_USER: str = "taskflow"
    POSTGRES_PASSWORD: str = "taskflow_secret"
    POSTGRES_DB: str = "taskflow"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # ── JWT ─────────────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production-use-a-long-random-string"
    JWT_EXPIRY_HOURS: int = 24
    JWT_ALGORITHM: str = "HS256"

    # ── Bcrypt ──────────────────────────────────────────────────
    BCRYPT_ROUNDS: int = Field(default=12, ge=12)

    @property
    def database_url(self) -> str:
        """Async PostgreSQL connection string for SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync PostgreSQL connection string (used by Alembic)."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
