from __future__ import annotations

from typing import Annotated

from fastapi import Form
from pydantic import Field, field_validator

from app.enums import ClinicalLevel
from app.schemas.forms.base import CsrfForm


class StaffCreateForm(CsrfForm):
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    clinical_level: ClinicalLevel
    notes: str | None = None

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_names(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("clinical_level", mode="before")
    @classmethod
    def parse_level(cls, value: str) -> ClinicalLevel:
        return ClinicalLevel(value)

    @field_validator("notes", mode="before")
    @classmethod
    def strip_notes(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None

    def to_service_dict(self, organisation_id: int) -> dict:
        return {
            "organisation_id": organisation_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "clinical_level": self.clinical_level.value,
            "notes": self.notes,
        }


def staff_create_form(
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    clinical_level: Annotated[str, Form()],
    notes: Annotated[str | None, Form()] = None,
    csrf_token: Annotated[str | None, Form()] = None,
) -> StaffCreateForm:
    return StaffCreateForm.model_validate(
        {
            "first_name": first_name,
            "last_name": last_name,
            "clinical_level": clinical_level,
            "notes": notes,
            "csrf_token": csrf_token,
        }
    )
