from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CsrfForm(BaseModel):
    csrf_token: str | None = None


def parse_form_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized) if "T" in normalized else datetime.fromisoformat(value)


def normalize_int_list(value: int | list[int] | None) -> list[int]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_str_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
