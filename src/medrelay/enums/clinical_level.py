from enum import StrEnum


class ClinicalLevel(StrEnum):
    EFR = "EFR"
    EMT = "EMT"
    PARAMEDIC = "PARAMEDIC"
    ADVANCED_PARAMEDIC = "ADVANCED_PARAMEDIC"

    def label(self) -> str:
        return {
            ClinicalLevel.EFR: "EFR",
            ClinicalLevel.EMT: "EMT",
            ClinicalLevel.PARAMEDIC: "Paramedic",
            ClinicalLevel.ADVANCED_PARAMEDIC: "Advanced Paramedic",
        }[self]

    @property
    def rank(self) -> int:
        return {
            ClinicalLevel.EFR: 1,
            ClinicalLevel.EMT: 2,
            ClinicalLevel.PARAMEDIC: 3,
            ClinicalLevel.ADVANCED_PARAMEDIC: 4,
        }[self]
