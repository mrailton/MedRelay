import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.dependencies import LoginRequired
from app.handlers.validation import request_validation_exception_handler
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.session import RememberSessionMiddleware
from app.routes import api_router
from app.templating import register_route_names, setup_template_globals

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.realtime.hub import realtime_hub

    register_route_names(list(app.routes))
    realtime_hub.bind_loop(asyncio.get_running_loop())
    await realtime_hub.start()
    try:
        yield
    finally:
        await realtime_hub.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RememberSessionMiddleware,
    remember_max_age_seconds=settings.session_remember_lifetime * 60,
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=settings.session_lifetime * 60,
    https_only=settings.session_secure_cookie,
)

static_dir = Path(__file__).resolve().parent.parent / "static" / "dist"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

setup_template_globals()
app.include_router(api_router)

app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore[arg-type]


@app.exception_handler(LoginRequired)
async def login_required_handler(request: Request, exc: LoginRequired):
    return RedirectResponse(url="/login", status_code=303)
