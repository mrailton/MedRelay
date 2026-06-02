from __future__ import annotations

from typing import TypeVar, overload

from app.web.responses import ActionResult, redirect_to

T = TypeVar("T")


def redirect_if_missing(entity: T | None, url: str = "/") -> ActionResult | T:
    if entity is None:
        return redirect_to(url)
    return entity


@overload
def split_entity(entity: None, url: str = "/") -> tuple[ActionResult, None]: ...


@overload
def split_entity(entity: T, url: str = "/") -> tuple[None, T]: ...


def split_entity(entity: T | None, url: str = "/") -> tuple[ActionResult | None, T | None]:
    """Return ``(redirect, entity)`` — exactly one of the pair is non-None."""
    if entity is None:
        return redirect_to(url), None
    return None, entity


def resolved_entity(miss: ActionResult | None, entity: T | None) -> T:
    """Narrow types after a ``split_entity`` redirect check."""
    assert miss is None and entity is not None
    return entity
