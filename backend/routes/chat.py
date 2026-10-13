import pathlib
from fastapi import APIRouter, HTTPException
from backend.models.user import ChatRequest, ChatResponse
from backend.services.llm_service import ask_llm
from backend.services.safety_service import get_disclaimer
from backend.services.rag_service import retrieve_relevant_medical_context

router = APIRouter(prefix="/api/chat", tags=["Health Chat"])

PROMPT_PATH = pathlib.Path(__file__).parent.parent.parent / "prompts" / "chat_prompt.txt"


def load_chat_system_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "You are a helpful AI Health Assistant. Provide educational health information."


@router.post("/query", response_model=ChatResponse)
async def health_chat_query(payload: ChatRequest):
    """
    Handles health Q&A queries with local Gemma 3:1B LLM and RAG retrieval context.
    """
    try:
        messages_dict = [{"role": m.role, "content": m.content} for m in payload.messages]
        latest_user_query = payload.messages[-1].content if payload.messages else ""

        # Retrieve RAG Context
        rag_context = retrieve_relevant_medical_context(latest_user_query)

        system_prompt = (
            f"{load_chat_system_prompt()}\n\n"
            f"Relevant Medical Reference Context:\n{rag_context}"
        )

        response_text = ask_llm(
            prompt=latest_user_query,
            system_prompt=system_prompt,
            temperature=0.3,
            messages_history=messages_dict
        )

        return ChatResponse(
            response=response_text,
            disclaimer=get_disclaimer()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation error: {str(e)}")
