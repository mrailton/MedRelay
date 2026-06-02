from app.routes.events.router import router

__all__ = ["router"]

# Register view and mutation routes on the shared router.
from app.routes.events import mutations, views  # noqa: E402, F401
