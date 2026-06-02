from app.enums import ClinicalLevel


def test_clinical_level_labels():
    assert ClinicalLevel.PARAMEDIC.label() == "Paramedic"
    assert ClinicalLevel.FAR.rank == 1
    assert ClinicalLevel.ADVANCED_PARAMEDIC.rank == 5
