# 🩺 AI Medical Triage & Report Explainer       

An intelligent, local-first medical symptom triage, PDF lab report explainer, and health Q&A assistant powered by **Gemma 3:1B**, **Ollama**, **FastAPI**, **Streamlit**, and **PyMuPDF**.

---

## 🌟 Key Features

1. **🩺 Intelligent Symptom Triage**:
   - Analyzes symptoms, age, duration, and self-reported severity.
   - Computes urgency level: `EMERGENCY`, `URGENT`, `ROUTINE`, or `SELF_CARE`.
   - Built-in Safety Engine automatically detects emergency red flags (e.g., chest pain, shortness of breath, sudden weakness) prior to LLM evaluation.

2. **📄 Medical PDF Report Explainer**:
   - Parses complex PDF lab reports using PyMuPDF (`fitz`).
   - Translates medical jargon (WBC, eGFR, HbA1c, ALT/AST) into everyday plain English.
   - Highlights out-of-reference-range abnormal values and suggests doctor consultation questions.

3. **💬 AI Health Assistant**:
   - Conversational health Q&A with RAG (Retrieval-Augmented Generation) context from local medical guidelines.

4. **🌍 Multi-Language Support**:
   - Generates triage explanations and report summaries in English, Hindi, Telugu, Tamil, Spanish, French, and Kannada.

---

## 🏗 Project Architecture

```
AI-Medical-Triage/
├── frontend/
│   └── app.py                     # Streamlit frontend application
├── backend/
│   ├── main.py                    # FastAPI server entrypoint
│   ├── routes/
│   │   ├── triage.py              # Symptom assessment endpoints
│   │   ├── reports.py             # PDF upload & report explanation endpoints
│   │   └── chat.py                # Health Q&A chat endpoint
│   ├── services/
│   │   ├── llm_service.py         # Ollama API client (Gemma 3:1B)
│   │   ├── triage_service.py      # Urgency rating logic
│   │   ├── safety_service.py      # Red flag emergency detection
│   │   ├── pdf_service.py         # PyMuPDF parser
│   │   ├── report_service.py     # Medical term simplifier
│   │   └── translation_service.py # Multi-lingual engine
│   └── models/
│       ├── triage.py              # Pydantic symptom schemas
│       ├── report.py              # Pydantic report schemas
│       └── user.py                # Chat schemas
├── rag/                           # Local RAG vector store & retriever
├── prompts/                       # Modular prompt text templates
├── tests/                         # Pytest test suite
├── .env                           # Environment variables
├── requirements.txt               # Dependencies
└── README.md                      # Documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
1. Install [Python 3.10+](https://www.python.org/).
2. Install [Ollama](https://ollama.com/) and pull the Gemma model:
   ```bash
   ollama pull gemma3:1b
   ```

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start FastAPI Backend
```bash
python -m backend.main
```
*Backend API will run at `http://localhost:8000` (API Docs at `http://localhost:8000/docs`).*

### 3. Start Streamlit Frontend
```bash
streamlit run frontend/app.py
```
*Frontend UI will open automatically at `http://localhost:8501`.*

---

## 🧪 Running Unit Tests

To run the automated safety and PDF parser test suite:
```bash
pytest tests/
```

---

## ⚠️ Medical Disclaimer
This application is an educational and informational tool powered by AI. It **DOES NOT** provide medical diagnoses, treatment advice, or drug prescriptions. Always seek the advice of a physician or qualified healthcare provider with any medical questions. In case of emergency, call 911 or visit the nearest emergency room immediately.
