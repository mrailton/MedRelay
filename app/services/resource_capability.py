from sqlalchemy.orm import Session

from app.db.models.resource import Resource
from app.enums import ClinicalLevel


def recalculate_resource_capability(db: Session, resource: Resource) -> None:
    db.refresh(resource, attribute_names=["staff"])
    if not resource.staff:
        resource.highest_clinical_level = None
        resource.is_deployable = False
        return

    highest = max(ClinicalLevel(s.clinical_level).rank for s in resource.staff)
    resource.highest_clinical_level = {
        1: ClinicalLevel.EFR,
        2: ClinicalLevel.EMT,
        3: ClinicalLevel.PARAMEDIC,
        4: ClinicalLevel.ADVANCED_PARAMEDIC,
    }[highest].value
    resource.is_deployable = True
    db.flush()
