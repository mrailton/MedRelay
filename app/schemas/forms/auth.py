from __future__ import annotations

from typing import Annotated

from fastapi import Form
from pydantic import field_validator

from app.schemas.forms.base import CsrfForm


class LoginForm(CsrfForm):
    organisation_code: str | None = None
    email: str | None = None
    password: str | None = None
    remember: bool = False

    @field_validator("organisation_code", "email", mode="before")
    @classmethod
    def strip_fields(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        return value.strip() or None

    @property
    def organisation_code_normalized(self) -> str:
        return (self.organisation_code or "").strip()


class LogoutForm(CsrfForm):
    pass


def login_form(
    organisation_code: Annotated[str | None, Form()] = None,
    email: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    remember: Annotated[bool, Form()] = False,
    csrf_token: Annotated[str | None, Form()] = None,
) -> LoginForm:
    return LoginForm(
        organisation_code=organisation_code,
        email=email,
        password=password,
        remember=remember,
        csrf_token=csrf_token,
    )


def logout_form(
    csrf_token: Annotated[str | None, Form()] = None,
) -> LogoutForm:
    return LogoutForm(csrf_token=csrf_token)
