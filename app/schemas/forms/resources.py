from __future__ import annotations

from typing import Annotated

from fastapi import Form
from pydantic import Field, field_validator

from app.enums import ResourceStatus, ResourceType
from app.schemas.forms.base import CsrfForm, normalize_int_list


class ResourceCreateForm(CsrfForm):
    name: str = Field(min_length=1, max_length=255)
    resource_type: ResourceType
    staff_ids: list[int] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("resource_type", mode="before")
    @classmethod
    def parse_type(cls, value: str) -> ResourceType:
        return ResourceType(value)

    @field_validator("staff_ids", mode="before")
    @classmethod
    def normalize_staff_ids(cls, value: int | list[int] | None) -> list[int]:
        return normalize_int_list(value)

    def to_service_dict(self) -> dict:
        return {
            "name": self.name,
            "resource_type": self.resource_type.value,
            "staff_ids": self.staff_ids,
        }


class ResourceStatusForm(CsrfForm):
    status: ResourceStatus

    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, value: str) -> ResourceStatus:
        return ResourceStatus(value)


class ResourceAssignStaffForm(CsrfForm):
    staff_id: int = Field(gt=0)


def resource_create_form(
    name: Annotated[str, Form()],
    resource_type: Annotated[str, Form()],
    staff_ids: Annotated[list[int], Form()] = [],
    csrf_token: Annotated[str | None, Form()] = None,
) -> ResourceCreateForm:
    return ResourceCreateForm.model_validate(
        {
            "name": name,
            "resource_type": resource_type,
            "staff_ids": staff_ids,
            "csrf_token": csrf_token,
        }
    )


def resource_status_form(
    status: Annotated[str, Form()],
    csrf_token: Annotated[str | None, Form()] = None,
) -> ResourceStatusForm:
    return ResourceStatusForm.model_validate({"status": status, "csrf_token": csrf_token})


def resource_assign_staff_form(
    staff_id: Annotated[int, Form()],
    csrf_token: Annotated[str | None, Form()] = None,
) -> ResourceAssignStaffForm:
    return ResourceAssignStaffForm(staff_id=staff_id, csrf_token=csrf_token)
