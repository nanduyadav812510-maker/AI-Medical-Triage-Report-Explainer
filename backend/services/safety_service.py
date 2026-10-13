import re
from typing import List, Tuple

RED_FLAG_KEYWORDS = [
    r"chest pain",
    r"pressure in chest",
    r"shortness of breath",
    r"difficulty breathing",
    r"unable to breathe",
    r"sudden numbness",
    r"face drooping",
    r"slurred speech",
    r"arm weakness",
    r"unconscious",
    r"fainted",
    r"severe head injury",
    r"uncontrolled bleeding",
    r"coughing up blood",
    r"severe allergic reaction",
    r"anaphylaxis",
    r"suicidal thoughts",
    r"overdose"
]

STANDARD_DISCLAIMER = (
    "IMPORTANT NOTICE: AI Medical Triage is an informational decision-support tool powered by Gemma 3:1B. "
    "It DOES NOT provide professional medical diagnoses, prescriptions, or treatment plans. "
    "If you believe you are experiencing a medical emergency, immediately call 911 (or your local emergency services) "
    "or go to the nearest emergency room."
)


def evaluate_safety_red_flags(symptoms_text: str) -> Tuple[bool, List[str]]:
    """
    Evaluates text for high-risk emergency red flag keywords.
    Returns (is_emergency_flagged, list_of_detected_red_flags).
    """
    detected_flags = []
    text_lower = symptoms_text.lower()

    for pattern in RED_FLAG_KEYWORDS:
        if re.search(pattern, text_lower):
            flag_name = pattern.replace("\\", "").title()
            detected_flags.append(flag_name)

    is_emergency = len(detected_flags) > 0
    return is_emergency, detected_flags


def get_disclaimer() -> str:
    """Returns standard medical disclaimer."""
    return STANDARD_DISCLAIMER
