from __future__ import annotations

from typing import Annotated

from fastapi import Form
from pydantic import Field, field_validator

from app.schemas.forms.base import CsrfForm


class OrganisationForm(CsrfForm):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)

    @field_validator("code", "name", mode="before")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


def organisation_form(
    code: Annotated[str, Form()],
    name: Annotated[str, Form()],
    csrf_token: Annotated[str | None, Form()] = None,
) -> OrganisationForm:
    return OrganisationForm(code=code, name=name, csrf_token=csrf_token)
