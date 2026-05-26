from enum import StrEnum


class ResourceType(StrEnum):
    AMBULANCE = "AMBULANCE"
    PATROL = "PATROL"
    TEAM_LEAD = "TEAM_LEAD"
    BUGGY = "BUGGY"
    OTHER = "OTHER"

    def label(self) -> str:
        return {
            ResourceType.AMBULANCE: "Ambulance",
            ResourceType.PATROL: "Patrol",
            ResourceType.TEAM_LEAD: "Team Lead",
            ResourceType.BUGGY: "Buggy",
            ResourceType.OTHER: "Other",
        }[self]
