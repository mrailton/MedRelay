from __future__ import annotations

from typing import Annotated

from fastapi import Form
from pydantic import Field, field_validator

from app.schemas.forms.base import CsrfForm, parse_form_datetime


class EventCreateForm(CsrfForm):
    name: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)
    start_time: str = Field(min_length=1)
    end_time: str | None = None
    is_active: bool = False
    notes: str | None = None

    @field_validator("name", "location", mode="before")
    @classmethod
    def strip_required(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("notes", mode="before")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None

    def to_service_dict(self, organisation_id: int) -> dict:
        return {
            "organisation_id": organisation_id,
            "name": self.name,
            "location": self.location,
            "start_time": parse_form_datetime(self.start_time),
            "end_time": parse_form_datetime(self.end_time) if self.end_time else None,
            "is_active": self.is_active,
            "notes": self.notes,
        }


class EventUpdateForm(CsrfForm):
    name: str | None = None
    location: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    is_active: bool = False
    notes: str | None = None

    @field_validator("name", "location", "start_time", "notes", mode="before")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None

    def to_service_dict(self) -> dict[str, object]:
        data: dict[str, object] = {}
        if self.name is not None:
            data["name"] = self.name
        if self.location is not None:
            data["location"] = self.location
        if self.start_time:
            data["start_time"] = parse_form_datetime(self.start_time)
        data["end_time"] = parse_form_datetime(self.end_time) if self.end_time else None
        data["is_active"] = self.is_active
        data["notes"] = self.notes
        return data


def event_create_form(
    name: Annotated[str, Form()],
    location: Annotated[str, Form()],
    start_time: Annotated[str, Form()],
    end_time: Annotated[str | None, Form()] = None,
    is_active: Annotated[bool, Form()] = False,
    notes: Annotated[str | None, Form()] = None,
    csrf_token: Annotated[str | None, Form()] = None,
) -> EventCreateForm:
    return EventCreateForm(
        name=name,
        location=location,
        start_time=start_time,
        end_time=end_time,
        is_active=is_active,
        notes=notes,
        csrf_token=csrf_token,
    )


def event_update_form(
    name: Annotated[str | None, Form()] = None,
    location: Annotated[str | None, Form()] = None,
    start_time: Annotated[str | None, Form()] = None,
    end_time: Annotated[str | None, Form()] = None,
    is_active: Annotated[bool, Form()] = False,
    notes: Annotated[str | None, Form()] = None,
    csrf_token: Annotated[str | None, Form()] = None,
) -> EventUpdateForm:
    return EventUpdateForm(
        name=name,
        location=location,
        start_time=start_time,
        end_time=end_time,
        is_active=is_active,
        notes=notes,
        csrf_token=csrf_token,
    )
