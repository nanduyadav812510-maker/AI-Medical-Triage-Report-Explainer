from typing import List
from rag.vector_store import vector_store


def query_medical_knowledge_base(query: str, top_k: int = 3) -> List[str]:
    """
    Public entry point to retrieve relevant documents from vector store.
    """
    return vector_store.search(query=query, top_k=top_k)
