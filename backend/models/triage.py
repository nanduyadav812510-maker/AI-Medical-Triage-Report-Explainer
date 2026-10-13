from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class UrgencyLevel(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    ROUTINE = "ROUTINE"
    SELF_CARE = "SELF_CARE"


class SymptomInput(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: str = Field(..., description="Gender (e.g. Male, Female, Other)")
    symptoms: str = Field(..., description="Detailed description of current symptoms")
    duration: str = Field(..., description="Duration of symptoms (e.g., '2 days', '3 hours')")
    severity_score: int = Field(..., ge=1, le=10, description="Self-reported pain/severity score 1-10")
    existing_conditions: Optional[str] = Field(default="None", description="Pre-existing medical conditions")
    language: Optional[str] = Field(default="English", description="Target response language")
    user_id: Optional[str] = Field(default=None, description="Optional user ID for tracking history")


class TriageResponse(BaseModel):
    urgency_level: UrgencyLevel
    summary: str
    recommended_action: str
    red_flags_detected: List[str] = Field(default_factory=list)
    questions_for_doctor: List[str] = Field(default_factory=list)
    disclaimer: str
