import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.triage import router as triage_router
from backend.routes.reports import router as reports_router
from backend.routes.chat import router as chat_router
from backend.services.llm_service import check_model, OLLAMA_MODEL


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI-Medical-Triage-Backend")


# ---------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------

app = FastAPI(
    title="AI Medical Triage & Report Explainer API",
    description=(
        "FastAPI backend providing AI medical triage, "
        "medical report analysis, and health chat."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5501",
        "http://127.0.0.1:5501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Include API Routers
# ---------------------------------------------------------

app.include_router(triage_router)
app.include_router(reports_router)
app.include_router(chat_router)


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get("/")
async def root_status():
    return {
        "status": "online",
        "service": "AI Medical Triage & Report Explainer API",
        "model_configured": OLLAMA_MODEL,
    }


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/api/health")
async def health_check():
    ollama_ready = check_model()

    return {
        "status": "healthy" if ollama_ready else "degraded",
        "ollama_connected": ollama_ready,
        "configured_model": OLLAMA_MODEL,
    }


# ---------------------------------------------------------
# Run Application
# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )