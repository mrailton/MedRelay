from enum import StrEnum


class ClinicalLevel(StrEnum):
    FAR = "FAR"
    EFR = "EFR"
    EMT = "EMT"
    PARAMEDIC = "PARAMEDIC"
    ADVANCED_PARAMEDIC = "ADVANCED_PARAMEDIC"

    def label(self) -> str:
        return {
            ClinicalLevel.FAR: "FAR",
            ClinicalLevel.EFR: "EFR",
            ClinicalLevel.EMT: "EMT",
            ClinicalLevel.PARAMEDIC: "Paramedic",
            ClinicalLevel.ADVANCED_PARAMEDIC: "Advanced Paramedic",
        }[self]

    @property
    def rank(self) -> int:
        return {
            ClinicalLevel.FAR: 1,
            ClinicalLevel.EFR: 2,
            ClinicalLevel.EMT: 3,
            ClinicalLevel.PARAMEDIC: 4,
            ClinicalLevel.ADVANCED_PARAMEDIC: 5,
        }[self]
