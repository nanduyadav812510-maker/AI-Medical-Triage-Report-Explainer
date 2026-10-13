import os
import logging
from typing import List, Dict, Optional
import ollama
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def ask_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,
    messages_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Send prompt or message history to local Ollama model.
    """
    try:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if messages_history:
            messages.extend(messages_history)
        else:
            messages.append({"role": "user", "content": prompt})

        client = ollama.Client(host=OLLAMA_HOST)
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={"temperature": temperature}
        )

        # Handle SDK response format variants
        if isinstance(response, dict):
            return response.get("message", {}).get("content", "").strip()
        elif hasattr(response, "message"):
            return getattr(response.message, "content", "").strip()
        return str(response).strip()

    except Exception as e:
        logger.error(f"Error calling Ollama LLM service: {e}")
        return f"AI Service error: Unable to connect to local Ollama instance ({e}). Ensure Ollama is running."


def check_model() -> bool:
    """
    Check if configured Ollama model is downloaded and accessible.
    Handles both dict and object return formats from ollama.list().
    """
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        response = client.list()

        models_list = []
        if isinstance(response, dict) and "models" in response:
            models_list = response["models"]
        elif hasattr(response, "models"):
            models_list = response.models

        for item in models_list:
            name = ""
            if isinstance(item, dict):
                name = item.get("model") or item.get("name") or ""
            else:
                name = getattr(item, "model", None) or getattr(item, "name", "") or ""

            if OLLAMA_MODEL.split(":")[0] in name:
                return True

        return False
    except Exception as e:
        logger.warning(f"Ollama model check failed: {e}")
        return False
