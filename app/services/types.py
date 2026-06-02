from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldErrors:
    """Validation or business-rule failures keyed by form field."""

    errors: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class AuthenticatedUser:
    user_id: int
    organisation_id: int
    organisation_code: str
    remember: bool = False


@dataclass
class LoginFailure:
    errors: dict[str, str]
    email: str | None = None
    organisation_code: str | None = None


@dataclass
class CreateUserOutcome:
    success: bool
    errors: dict[str, str] = field(default_factory=dict)
    user: Any = None


@dataclass
class OrganisationWriteOutcome:
    success: bool
    errors: dict[str, str] = field(default_factory=dict)
    organisation: Any = None
    not_found: bool = False
