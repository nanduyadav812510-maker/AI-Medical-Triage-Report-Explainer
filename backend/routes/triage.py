from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.models.triage import SymptomInput, TriageResponse
from backend.services.triage_service import perform_triage_assessment
from backend.services.translation_service import translate_text
from backend.services.storage_service import (
    save_assessment, get_user_assessments, get_statistics, 
    save_user_profile, get_user_profile
)
from backend.services.pdf_export_service import generate_triage_report_pdf
import tempfile
import os

router = APIRouter(prefix="/api/triage", tags=["Symptom Triage"])


@router.post("/assess", response_model=TriageResponse)
async def assess_symptoms(payload: SymptomInput):
    """
    Evaluates symptoms, computes urgency level (EMERGENCY/URGENT/ROUTINE/SELF_CARE),
    scans for red flags, and returns recommendations.
    """
    try:
        response = perform_triage_assessment(payload)

        # Handle translation if language specified and not English
        if payload.language and payload.language.lower() != "english":
            response.summary = translate_text(response.summary, payload.language)
            response.recommended_action = translate_text(response.recommended_action, payload.language)

        # Save assessment if user_id is provided
        if payload.user_id:
            assessment_data = {
                "age": payload.age,
                "gender": payload.gender,
                "symptoms": payload.symptoms,
                "duration": payload.duration,
                "severity_score": payload.severity_score,
                "existing_conditions": payload.existing_conditions,
                "language": payload.language,
                "urgency_level": response.urgency_level,
                "summary": response.summary,
                "recommended_action": response.recommended_action,
                "red_flags_detected": response.red_flags_detected
            }
            save_assessment(payload.user_id, assessment_data)

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage assessment failed: {str(e)}")


@router.get("/history/{user_id}")
async def get_assessment_history(user_id: str):
    """
    Retrieves assessment history for a specific user.
    """
    try:
        assessments = get_user_assessments(user_id)
        return {
            "user_id": user_id,
            "total_assessments": len(assessments),
            "assessments": assessments[-10:]  # Return last 10
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@router.get("/export/{user_id}/{assessment_id}")
async def export_assessment_as_pdf(user_id: str, assessment_id: str):
    """
    Exports a specific assessment as PDF.
    """
    try:
        assessments = get_user_assessments(user_id)
        assessment = next((a for a in assessments if a.get("id") == assessment_id), None)
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        pdf_bytes = generate_triage_report_pdf(assessment)
        
        # Return PDF as file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        return FileResponse(tmp_path, media_type="application/pdf", filename=f"triage_report_{assessment_id}.pdf")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting PDF: {str(e)}")


@router.get("/statistics")
async def get_triage_statistics():
    """
    Returns overall triage statistics and analytics.
    """
    try:
        stats = get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")


@router.post("/profile/{user_id}")
async def save_profile(user_id: str, profile_data: dict):
    """
    Saves or updates user profile information.
    """
    try:
        success = save_user_profile(user_id, profile_data)
        if success:
            return {"message": "Profile saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save profile")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving profile: {str(e)}")


@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """
    Retrieves user profile.
    """
    try:
        profile = get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")
