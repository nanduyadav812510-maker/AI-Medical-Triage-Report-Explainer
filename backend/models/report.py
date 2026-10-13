from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ReportAnalysisRequest(BaseModel):
    report_text: str = Field(..., description="Extracted raw text from medical PDF report")
    report_type: Optional[str] = Field(default="General Lab Report", description="Type of medical document")
    language: Optional[str] = Field(default="English", description="Target response language")


class ReportAnalysisResponse(BaseModel):
    summary: str = Field(..., description="Executive plain-language summary of report")
    key_findings: List[str] = Field(default_factory=list, description="Primary clinical findings")
    simplified_terms: Dict[str, str] = Field(default_factory=dict, description="Medical jargon translated to simple terms")
    abnormal_values: List[str] = Field(default_factory=list, description="Highlighted abnormal/out-of-range metrics")
    next_steps: List[str] = Field(default_factory=list, description="Suggested questions/actions for doctor consultation")
    disclaimer: str = Field(..., description="Standard medical disclaimer")
