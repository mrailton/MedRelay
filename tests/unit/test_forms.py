from datetime import datetime

import pytest
from pydantic import ValidationError

from app.enums import ClinicalLevel, IncidentStatus, ResourceStatus, ResourceType
from app.schemas.forms.admin import AdminUserCreateForm
from app.schemas.forms.base import parse_form_datetime
from app.schemas.forms.events import EventCreateForm, EventUpdateForm
from app.schemas.forms.incidents import IncidentCreateForm, IncidentStatusForm
from app.schemas.forms.resources import ResourceCreateForm, ResourceStatusForm


def test_parse_form_datetime_iso_with_t():
    dt = parse_form_datetime("2026-06-01T12:00:00Z")
    assert isinstance(dt, datetime)


def test_parse_form_datetime_date_only():
    dt = parse_form_datetime("2026-06-01")
    assert dt.year == 2026


def test_event_create_form_to_service_dict():
    form = EventCreateForm(
        name=" Marathon ",
        location=" Central Park ",
        start_time="2026-06-01T10:00:00",
        is_active=True,
    )
    data = form.to_service_dict(organisation_id=1)
    assert data["name"] == "Marathon"
    assert data["organisation_id"] == 1
    assert data["is_active"] is True


def test_event_update_form_partial():
    form = EventUpdateForm(name="Updated", is_active=False)
    data = form.to_service_dict()
    assert data["name"] == "Updated"
    assert data["is_active"] is False


def test_incident_create_strips_fields():
    form = IncidentCreateForm(
        location="  Site  ",
        priority="P1",
        category="medical",
        description="  help  ",
    )
    payload = form.to_service_dict()
    assert payload["location"] == "Site"
    assert payload["description"] == "help"


def test_incident_status_parses_enum():
    form = IncidentStatusForm(status="DISPATCHED")
    assert form.status == IncidentStatus.DISPATCHED


def test_resource_create_normalizes_single_staff_id():
    form = ResourceCreateForm(name="Unit 1", resource_type="AMBULANCE", staff_ids=5)
    assert form.staff_ids == [5]
    assert form.resource_type == ResourceType.AMBULANCE


def test_resource_create_invalid_type_raises():
    with pytest.raises(ValidationError):
        ResourceCreateForm(name="X", resource_type="INVALID")


def test_resource_status_parses_enum():
    form = ResourceStatusForm(status="EN_ROUTE")
    assert form.status == ResourceStatus.EN_ROUTE


def test_staff_create_clinical_level():
    from app.schemas.forms.staff import StaffCreateForm

    form = StaffCreateForm(first_name="Jane", last_name="Doe", clinical_level="EMT")
    data = form.to_service_dict(organisation_id=3)
    assert data["clinical_level"] == ClinicalLevel.EMT.value


def test_admin_user_create_filters_org_ids():
    form = AdminUserCreateForm(
        name="Admin",
        email="a@example.com",
        password="password1",
        password_confirmation="password1",
        organisation_ids=[1, 2, 3],
    )
    assert form.filtered_organisation_ids(2) == [2]


def test_admin_user_create_org_roles_dict():
    form = AdminUserCreateForm(
        name="Admin",
        email="a@example.com",
        password="password1",
        password_confirmation="password1",
        org_role=["2:ADMIN", "3:CONTROLLER"],
    )
    assert form.org_roles_dict() == {"2": "ADMIN", "3": "CONTROLLER"}
