from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from fastapi import Depends, Request

from app.dependencies import verify_csrf
from app.schemas.forms.base import CsrfForm

F = TypeVar("F", bound=CsrfForm)


def verified_form[F: CsrfForm](form_dependency: Callable[..., F]) -> Callable[..., F]:
    """Wrap a form dependency so CSRF is checked before the route body runs."""

    def _verified(request: Request, form: F = Depends(form_dependency)) -> F:
        verify_csrf(request, form.csrf_token)
        return form

    return _verified
