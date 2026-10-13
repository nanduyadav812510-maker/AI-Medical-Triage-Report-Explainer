import logging
from backend.services.llm_service import ask_llm

logger = logging.getLogger(__name__)


def translate_text(text: str, target_language: str) -> str:
    """
    Translates medical advice/summaries into the requested target language.
    """
    if not target_language or target_language.lower() == "english":
        return text

    prompt = f"""
Translate the following medical summary accurately into {target_language}.
Maintain clear, compassionate language and ensure all safety instructions remain intact.

Text:
{text}
"""
    system_prompt = f"You are a professional medical translator into {target_language}."

    translated = ask_llm(prompt=prompt, system_prompt=system_prompt, temperature=0.1)
    return translated
