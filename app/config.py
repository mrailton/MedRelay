from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_WEAK_SECRET_KEYS = frozenset({"change-me", "change-me-to-a-random-secret-key", "test-secret-key", "secret"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MedRelay"
    app_env: str = "local"
    app_debug: bool = True
    app_url: str = "http://localhost:8000"
    secret_key: str = "change-me"

    database_url: str = "mysql+pymysql://root@127.0.0.1:3306/medrelay"

    session_lifetime: int = 120
    session_remember_lifetime: int = 43200  # minutes (30 days)
    session_secure_cookie: bool = False

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"

    @property
    def is_production(self) -> bool:
        return self.app_env in ("production", "prod")

    @field_validator("secret_key")
    @classmethod
    def secret_key_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("SECRET_KEY must not be empty.")
        return value

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Settings:
        if self.is_testing:
            return self
        if self.is_production and self.secret_key.strip().lower() in _WEAK_SECRET_KEYS:
            raise ValueError("SECRET_KEY must be set to a strong random value in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
