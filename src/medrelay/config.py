from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MedRelay"
    app_env: str = "local"
    app_debug: bool = True
    app_url: str = "http://localhost:8000"
    secret_key: str = "change-me"

    database_url: str = "mysql+pymysql://root@127.0.0.1:3306/medrelay"

    session_lifetime: int = 120
    session_secure_cookie: bool = False

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"


@lru_cache
def get_settings() -> Settings:
    return Settings()
