import pytest

from app.config import Settings


def test_testing_env_allows_weak_secret():
    settings = Settings(app_env="testing", secret_key="test-secret-key")
    assert settings.is_testing


def test_production_rejects_weak_secret():
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(app_env="production", secret_key="change-me")


def test_production_accepts_strong_secret():
    settings = Settings(app_env="production", secret_key="x" * 32)
    assert settings.is_production
