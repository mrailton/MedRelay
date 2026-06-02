from __future__ import annotations

from typing import Annotated

from fastapi import Form
from pydantic import Field, field_validator

from app.enums import IncidentStatus
from app.schemas.forms.base import CsrfForm, normalize_int_list


class IncidentCreateForm(CsrfForm):
    location: str = Field(min_length=1, max_length=255)
    priority: str = Field(min_length=1, max_length=50)
    category: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)

    @field_validator("location", "priority", "category", "description", mode="before")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    def to_service_dict(self) -> dict[str, str]:
        return {
            "location": self.location,
            "priority": self.priority,
            "category": self.category,
            "description": self.description,
        }


class IncidentStatusForm(CsrfForm):
    status: IncidentStatus

    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, value: str) -> IncidentStatus:
        return IncidentStatus(value)


class IncidentAssignResourcesForm(CsrfForm):
    resource_ids: list[int] = Field(default_factory=list)

    @field_validator("resource_ids", mode="before")
    @classmethod
    def normalize_ids(cls, value: int | list[int] | None) -> list[int]:
        return normalize_int_list(value)


class IncidentNoteForm(CsrfForm):
    content: str = Field(min_length=1)

    @field_validator("content", mode="before")
    @classmethod
    def strip_content(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


def incident_create_form(
    location: Annotated[str, Form()],
    priority: Annotated[str, Form()],
    category: Annotated[str, Form()],
    description: Annotated[str, Form()],
    csrf_token: Annotated[str | None, Form()] = None,
) -> IncidentCreateForm:
    return IncidentCreateForm(
        location=location,
        priority=priority,
        category=category,
        description=description,
        csrf_token=csrf_token,
    )


def incident_status_form(
    status: Annotated[str, Form()],
    csrf_token: Annotated[str | None, Form()] = None,
) -> IncidentStatusForm:
    return IncidentStatusForm.model_validate({"status": status, "csrf_token": csrf_token})


def incident_assign_resources_form(
    resource_ids: Annotated[list[int], Form()] = [],
    csrf_token: Annotated[str | None, Form()] = None,
) -> IncidentAssignResourcesForm:
    return IncidentAssignResourcesForm(resource_ids=resource_ids, csrf_token=csrf_token)


def incident_note_form(
    content: Annotated[str, Form()],
    csrf_token: Annotated[str | None, Form()] = None,
) -> IncidentNoteForm:
    return IncidentNoteForm(content=content, csrf_token=csrf_token)
