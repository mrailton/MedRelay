"""Model dict serialization for audit logs and realtime payloads."""

from app.repositories import Incident, Resource


def incident_to_dict(incident: Incident) -> dict:
    return {
        "id": incident.id,
        "event_id": incident.event_id,
        "reference": incident.reference,
        "location": incident.location,
        "priority": incident.priority,
        "category": incident.category,
        "description": incident.description,
        "status": incident.status,
        "created_at": incident.created_at.isoformat() if incident.created_at else None,
        "updated_at": incident.updated_at.isoformat() if incident.updated_at else None,
        "resources": [resource_to_dict(r) for r in incident.resources],
        "notes": [
            {
                "id": n.id,
                "incident_id": n.incident_id,
                "user_id": n.user_id,
                "content": n.content,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "updated_at": n.updated_at.isoformat() if n.updated_at else None,
                "user": (
                    {
                        "id": n.user.id,
                        "name": n.user.name,
                        "email": n.user.email,
                    }
                    if n.user
                    else None
                ),
            }
            for n in sorted(incident.notes, key=lambda x: x.created_at or "", reverse=True)
        ],
    }


def resource_to_dict(resource: Resource) -> dict:
    return {
        "id": resource.id,
        "event_id": resource.event_id,
        "name": resource.name,
        "resource_type": resource.resource_type,
        "status": resource.status,
        "availability": resource.availability,
        "highest_clinical_level": resource.highest_clinical_level,
        "is_deployable": resource.is_deployable,
        "created_at": resource.created_at.isoformat() if resource.created_at else None,
        "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
        "staff": [
            {
                "id": s.id,
                "first_name": s.first_name,
                "last_name": s.last_name,
                "clinical_level": s.clinical_level,
                "full_name": s.full_name,
            }
            for s in resource.staff
        ],
    }
