from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    CONTROLLER = "CONTROLLER"
    READ_ONLY = "READ_ONLY"

    def label(self) -> str:
        return {
            UserRole.ADMIN: "Admin",
            UserRole.CONTROLLER: "Controller",
            UserRole.READ_ONLY: "Read Only",
        }[self]
