import pathlib
import logging
from backend.models.triage import SymptomInput, TriageResponse, UrgencyLevel
from backend.services.llm_service import ask_llm
from backend.services.safety_service import evaluate_safety_red_flags, get_disclaimer

logger = logging.getLogger(__name__)

PROMPT_PATH = pathlib.Path(__file__).parent.parent.parent / "prompts" / "triage_prompt.txt"


def load_triage_prompt_template() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return (
        "Analyze symptoms for Patient (Age {age}, Gender {gender}).\n"
        "Symptoms: {symptoms}, Duration: {duration}, Severity: {severity_score}/10.\n"
        "Provide urgency assessment and guidance."
    )


def perform_triage_assessment(input_data: SymptomInput) -> TriageResponse:
    """
    Evaluates patient symptoms, computes safety flags, queries LLM, and formats response.
    """
    # Step 1: Safety rule check for immediate red flags
    is_emergency, detected_red_flags = evaluate_safety_red_flags(input_data.symptoms)

    # Step 2: Build LLM Prompt
    template = load_triage_prompt_template()
    formatted_prompt = template.format(
        age=input_data.age,
        gender=input_data.gender,
        symptoms=input_data.symptoms,
        duration=input_data.duration,
        severity_score=input_data.severity_score,
        existing_conditions=input_data.existing_conditions or "None"
    )

    system_prompt = (
        "You are an AI Medical Triage assistant. "
        "Strictly adhere to medical disclaimers. Do not give specific drug prescriptions or definitive diagnoses."
    )

    llm_output = ask_llm(prompt=formatted_prompt, system_prompt=system_prompt, temperature=0.2)

    # Step 3: Determine Urgency Level
    if is_emergency or input_data.severity_score >= 9:
        urgency = UrgencyLevel.EMERGENCY
    elif input_data.severity_score >= 7 or "URGENT" in llm_output.upper():
        urgency = UrgencyLevel.URGENT
    elif input_data.severity_score >= 4 or "ROUTINE" in llm_output.upper():
        urgency = UrgencyLevel.ROUTINE
    else:
        urgency = UrgencyLevel.SELF_CARE

    # Step 4: Recommended Action based on Urgency
    action_map = {
        UrgencyLevel.EMERGENCY: "Seek immediate emergency medical attention (Call 911 or go to nearest ER).",
        UrgencyLevel.URGENT: "Schedule an urgent doctor appointment or visit an urgent care clinic within 24-48 hours.",
        UrgencyLevel.ROUTINE: "Schedule a routine consultation with your primary healthcare provider.",
        UrgencyLevel.SELF_CARE: "Monitor symptoms at home with adequate rest and hydration. Consult doctor if symptoms worsen."
    }

    questions_for_doctor = [
        "What potential underlying causes could explain these symptoms?",
        "Are there any specific warning signs I should monitor closely?",
        "Should I undergo diagnostic tests or lab work?"
    ]

    return TriageResponse(
        urgency_level=urgency,
        summary=llm_output,
        recommended_action=action_map[urgency],
        red_flags_detected=detected_red_flags,
        questions_for_doctor=questions_for_doctor,
        disclaimer=get_disclaimer()
    )
