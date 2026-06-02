from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories import Organisation
from app.repositories.organisation import OrganisationRepository
from app.services.types import OrganisationWriteOutcome


def list_organisations(db: Session) -> list[Organisation]:
    return OrganisationRepository(db).list_all()


def get_organisation(db: Session, organisation_id: int) -> Organisation | None:
    return OrganisationRepository(db).get(organisation_id)


def create_organisation(db: Session, code: str, name: str) -> OrganisationWriteOutcome:
    repo = OrganisationRepository(db)
    if repo.get_by_code(code):
        return OrganisationWriteOutcome(
            success=False,
            errors={"code": "Organisation with this code already exists."},
        )
    organisation = repo.create(code=code, name=name)
    return OrganisationWriteOutcome(success=True, organisation=organisation)


def update_organisation(
    db: Session,
    organisation_id: int,
    code: str,
    name: str,
) -> OrganisationWriteOutcome:
    repo = OrganisationRepository(db)
    existing = repo.get_by_code(code)
    if existing and existing.id != organisation_id:
        return OrganisationWriteOutcome(
            success=False,
            errors={"code": "Organisation with this code already exists."},
            organisation=repo.get(organisation_id),
        )

    organisation = repo.update(organisation_id, code=code, name=name)
    if not organisation:
        return OrganisationWriteOutcome(success=False, not_found=True)

    return OrganisationWriteOutcome(success=True, organisation=organisation)
