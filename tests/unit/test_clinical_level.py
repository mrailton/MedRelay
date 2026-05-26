from medrelay.enums import ClinicalLevel


def test_clinical_level_labels():
    assert ClinicalLevel.PARAMEDIC.label() == "Paramedic"
    assert ClinicalLevel.EFR.rank == 1
    assert ClinicalLevel.ADVANCED_PARAMEDIC.rank == 4
