from enum import StrEnum


class ResourceStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    TRANSPORTING = "TRANSPORTING"
    RETURNING = "RETURNING"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

    def label(self) -> str:
        return {
            ResourceStatus.AVAILABLE: "Available",
            ResourceStatus.ASSIGNED: "Assigned",
            ResourceStatus.EN_ROUTE: "En Route",
            ResourceStatus.ON_SCENE: "On Scene",
            ResourceStatus.TRANSPORTING: "Transporting",
            ResourceStatus.RETURNING: "Returning",
            ResourceStatus.OUT_OF_SERVICE: "Out of Service",
        }[self]
