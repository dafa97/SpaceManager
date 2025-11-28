from typing import Any
from pydantic import field_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "SpaceManager"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Redis
    REDIS_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    # DigitalOcean Spaces
    SPACES_REGION: str = "nyc3"
    SPACES_ENDPOINT: str = ""
    SPACES_KEY: str = ""
    SPACES_SECRET: str = ""
    SPACES_BUCKET: str = ""


settings = Settings()
