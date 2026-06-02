from app.routes.incidents.router import router

__all__ = ["router"]

from app.routes.incidents import mutations, views  # noqa: E402, F401
