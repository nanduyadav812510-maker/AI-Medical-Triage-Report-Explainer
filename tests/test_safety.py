from backend.services.safety_service import evaluate_safety_red_flags, get_disclaimer


def test_red_flag_detection():
    is_emergency, flags = evaluate_safety_red_flags("Patient reports severe chest pain and shortness of breath.")
    assert is_emergency is True
    assert len(flags) >= 2


def test_routine_symptoms_no_red_flag():
    is_emergency, flags = evaluate_safety_red_flags("Mild runny nose and sneezing for 1 day.")
    assert is_emergency is False
    assert len(flags) == 0


def test_disclaimer_content():
    disclaimer = get_disclaimer()
    assert "DOES NOT provide professional medical diagnoses" in disclaimer
