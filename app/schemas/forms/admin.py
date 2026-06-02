from __future__ import annotations

from typing import Annotated

from fastapi import Form
from pydantic import Field, field_validator

from app.enums import UserRole
from app.schemas.forms.base import CsrfForm, normalize_int_list, normalize_str_list


class AdminUserCreateForm(CsrfForm):
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1)
    password_confirmation: str
    role: str = UserRole.CONTROLLER.value
    organisation_ids: list[int] = Field(default_factory=list)
    org_role: list[str] = Field(default_factory=list)

    @field_validator("name", "email", mode="before")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("organisation_ids", mode="before")
    @classmethod
    def normalize_org_ids(cls, value: int | list[int] | None) -> list[int]:
        return normalize_int_list(value)

    @field_validator("org_role", mode="before")
    @classmethod
    def normalize_org_role(cls, value: str | list[str] | None) -> list[str]:
        return normalize_str_list(value)

    def filtered_organisation_ids(self, organisation_id: int) -> list[int]:
        return [oid for oid in self.organisation_ids if oid == organisation_id]

    def org_roles_dict(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for entry in self.org_role:
            parts = entry.split(":", 1)
            if len(parts) == 2:
                result[parts[0]] = parts[1]
        return result

    def to_service_dict(self, organisation_ids: list[int]) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "organisation_ids": organisation_ids,
            "org_roles": self.org_roles_dict(),
        }


def admin_user_create_form(
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    password_confirmation: Annotated[str, Form()],
    role: Annotated[str, Form()] = UserRole.CONTROLLER.value,
    organisation_ids: Annotated[list[int], Form()] = [],
    org_role: Annotated[list[str], Form()] = [],
    csrf_token: Annotated[str | None, Form()] = None,
) -> AdminUserCreateForm:
    return AdminUserCreateForm(
        name=name,
        email=email,
        password=password,
        password_confirmation=password_confirmation,
        role=role,
        organisation_ids=organisation_ids,
        org_role=org_role,
        csrf_token=csrf_token,
    )
