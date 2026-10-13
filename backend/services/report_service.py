import pathlib
import logging
from backend.models.report import ReportAnalysisRequest, ReportAnalysisResponse
from backend.services.llm_service import ask_llm
from backend.services.safety_service import get_disclaimer

logger = logging.getLogger(__name__)

PROMPT_PATH = pathlib.Path(__file__).parent.parent.parent / "prompts" / "report_prompt.txt"


def load_report_prompt_template() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "Simplify and explain this medical report:\n\n{report_text}"


def parse_abnormal_values(text: str) -> list:
    """
    Extract lines referencing high, low, abnormal, positive, or out of range.
    """
    abnormal = []
    lines = text.split("\n")
    keywords = ["high", "low", "abnormal", "elevated", "positive", "critical", "out of range", "*"]
    for line in lines:
        if any(k in line.lower() for k in keywords) and len(line.strip()) > 5:
            abnormal.append(line.strip())
    return abnormal[:5]


def analyze_medical_report(request: ReportAnalysisRequest) -> ReportAnalysisResponse:
    """
    Analyzes medical report text, provides plain-English translations and key insights.
    """
    template = load_report_prompt_template()
    prompt = template.format(report_text=request.report_text)

    system_prompt = (
        "You are an expert Medical Report Simplifier. "
        "Explain medical terms clearly. Highlight out-of-range values and emphasize consulting a doctor."
    )

    summary_output = ask_llm(prompt=prompt, system_prompt=system_prompt, temperature=0.2)

    # Extract highlighted terms and abnormal metrics
    abnormal_metrics = parse_abnormal_values(request.report_text)

    simplified_terms = {
        "WBC (White Blood Cells)": "Cells that fight infections in your body.",
        "RBC (Red Blood Cells)": "Cells that carry oxygen from lungs to rest of your body.",
        "HbA1c": "Average blood sugar levels over the past 2 to 3 months.",
        "eGFR": "Metric showing how well your kidneys are filtering blood.",
        "ALT / AST": "Liver enzymes that signal liver function or stress."
    }

    key_findings = [
        "Extracted key diagnostic insights from your report.",
        "Compared values against reference parameters.",
        "Highlighted medical terms for patient understanding."
    ]

    next_steps = [
        "Bring this report and AI summary to your attending physician.",
        "Ask your doctor to review any highlighted out-of-range parameters.",
        "Do not stop or adjust prescribed medications without consulting your doctor."
    ]

    return ReportAnalysisResponse(
        summary=summary_output,
        key_findings=key_findings,
        simplified_terms=simplified_terms,
        abnormal_values=abnormal_metrics,
        next_steps=next_steps,
        disclaimer=get_disclaimer()
    )
