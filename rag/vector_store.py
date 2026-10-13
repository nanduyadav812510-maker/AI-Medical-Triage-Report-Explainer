import pathlib
from typing import List, Dict
from rag.embeddings import cosine_similarity_tf

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"

SAMPLE_MEDICAL_DOCS = [
    "Chest Pain Guidelines: Severe chest pain radiating to left arm or neck is a classic red flag for myocardial infarction. Immediate emergency room triage required.",
    "Fever Assessment: Body temperature above 103°F (39.4°C) lasting over 3 days warrants urgent medical evaluation to rule out acute bacterial infection.",
    "Hypertension Lab Ranges: Blood pressure exceeding 180/120 mmHg indicates hypertensive crisis requiring urgent emergency care.",
    "Diabetes & HbA1c: Normal HbA1c is under 5.7%. 5.7-6.4% indicates prediabetes. 6.5% or higher on two separate tests indicates diabetes.",
    "Respiratory Distress: Shortness of breath at rest, cyanosis (bluish lips/fingers), or inability to speak full sentences indicates acute respiratory emergency."
]


class LocalVectorStore:
    def __init__(self):
        self.documents: List[str] = []
        self.load_documents()

    def load_documents(self):
        """Loads documents from data/ directory or populates standard guidelines."""
        self.documents = list(SAMPLE_MEDICAL_DOCS)
        if DATA_DIR.exists():
            for file in DATA_DIR.glob("*.txt"):
                try:
                    content = file.read_text(encoding="utf-8")
                    if content.strip():
                        self.documents.append(content.strip())
                except Exception:
                    pass

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Search documents ordered by similarity score."""
        scored_docs = []
        for doc in self.documents:
            score = cosine_similarity_tf(query, doc)
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k] if score > 0.05] or [SAMPLE_MEDICAL_DOCS[0]]


vector_store = LocalVectorStore()
