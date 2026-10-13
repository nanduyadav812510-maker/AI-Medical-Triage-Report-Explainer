import logging
from typing import List
from rag.retriever import query_medical_knowledge_base

logger = logging.getLogger(__name__)


def retrieve_relevant_medical_context(query: str, top_k: int = 3) -> str:
    """
    Retrieves context passages from local medical vector/knowledge index.
    """
    results: List[str] = query_medical_knowledge_base(query=query, top_k=top_k)
    if not results:
        return "No specific local knowledge documents retrieved."

    context_str = "\n\n".join([f"[Reference {i+1}]: {res}" for i, res in enumerate(results)])
    return context_str
