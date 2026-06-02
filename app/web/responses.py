from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ActionResult:
    """Maps to HTML via ``handle()`` — routes should not build responses by hand."""

    redirect_url: str | None = None
    status_code: int = 303
    template: str | None = None
    context: dict[str, Any] | None = None
    errors: dict[str, str] | None = None
    flash: tuple[str, str] | None = None
    commit: bool = False
    empty_response: bool = False
    user: Any = None


def redirect_to(
    url: str,
    *,
    commit: bool = False,
    flash: tuple[str, str] | None = None,
    status_code: int = 303,
) -> ActionResult:
    return ActionResult(
        redirect_url=url,
        commit=commit,
        flash=flash,
        status_code=status_code,
    )


def render_page(
    template: str,
    context: dict[str, Any] | None = None,
    *,
    errors: dict[str, str] | None = None,
    user: Any = None,
    status_code: int = 200,
) -> ActionResult:
    return ActionResult(
        template=template,
        context=context or {},
        errors=errors,
        user=user,
        status_code=status_code,
    )


def referer_or(request: object, fallback: str) -> str:
    headers = getattr(request, "headers", None)
    if headers is None:
        return fallback
    return headers.get("referer", fallback) or fallback
