from app.routes.staff.router import router

__all__ = ["router"]

from app.routes.staff import mutations, views  # noqa: E402, F401
