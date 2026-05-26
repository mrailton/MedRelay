from enum import StrEnum


class IncidentStatus(StrEnum):
    NEW = "NEW"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    TRANSPORTING = "TRANSPORTING"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"

    def label(self) -> str:
        return {
            IncidentStatus.NEW: "New",
            IncidentStatus.DISPATCHED: "Dispatched",
            IncidentStatus.EN_ROUTE: "En Route",
            IncidentStatus.ON_SCENE: "On Scene",
            IncidentStatus.TRANSPORTING: "Transporting",
            IncidentStatus.COMPLETE: "Complete",
            IncidentStatus.CANCELLED: "Cancelled",
        }[self]
