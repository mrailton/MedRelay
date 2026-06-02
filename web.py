"""ASGI entrypoint for uvicorn (see Dockerfile and README)."""

from app.main import app

__all__ = ["app"]
