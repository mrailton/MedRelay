from app.routes.resources.router import router

__all__ = ["router"]

from app.routes.resources import mutations, views  # noqa: E402, F401
