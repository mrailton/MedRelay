from __future__ import annotations

from sqlalchemy.orm import Session

from app.enums import ClinicalLevel
from app.repositories import Resource


def recalculate_resource_capability(db: Session, resource: Resource) -> None:
    db.refresh(resource, attribute_names=["staff"])
    if not resource.staff:
        resource.highest_clinical_level = None
        resource.is_deployable = False
        return

    highest = max(ClinicalLevel(s.clinical_level).rank for s in resource.staff)
    resource.highest_clinical_level = {
        1: ClinicalLevel.FAR,
        2: ClinicalLevel.EFR,
        3: ClinicalLevel.EMT,
        4: ClinicalLevel.PARAMEDIC,
        5: ClinicalLevel.ADVANCED_PARAMEDIC,
    }[highest].value
    resource.is_deployable = True
    db.flush()
