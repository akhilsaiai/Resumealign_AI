from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ImprovementItem(BaseModel):
    priority: str = Field(..., description="Priority level: high, medium, low")
    section: str = Field(..., description="Section of the resume the improvement applies to")
    issue: str = Field(..., description="Description of the issue found")
    suggestion: str = Field(..., description="Actionable recommendation to fix the issue")

class SectionScores(BaseModel):
    work_experience: int = Field(..., alias="Work Experience")
    skills: int = Field(..., alias="Skills")
    education: int = Field(..., alias="Education")
    summary_objective: int = Field(..., alias="Summary/Objective")
    formatting: int = Field(..., alias="Formatting")

    class Config:
        populate_by_name = True

class AnalysisResponse(BaseModel):
    ats_score: int
    match_percentage: int
    grade: str
    summary: str
    matched_skills: List[str]
    missing_skills: List[str]
    suggested_skills: List[str]
    keywords_found: List[str]
    keywords_missing: List[str]
    section_scores: Dict[str, int]
    improvements: List[ImprovementItem]
    strengths: List[str]
    weaknesses: List[str]

class AnalysisRequest(BaseModel):
    resume_text: str = Field(..., description="Plain text content of the resume")
    jd_text: str = Field(..., description="Target job description text")
    provider: str = Field("Groq Llama 3.3", description="AI Provider: 'OpenAI GPT-4o' or 'Groq Llama 3.3'")
    api_key: Optional[str] = Field(None, description="Optional API Key for the selected provider. If not provided, the backend will check env variables.")

class OptimizationRequest(BaseModel):
    resume_text: str
    jd_text: str
    missing_skills: List[str] = Field(default_factory=list)
    provider: str = "Groq Llama 3.3"
    api_key: Optional[str] = None

class OptimizationResponse(BaseModel):
    optimized_resume: str

class PipelineResponse(BaseModel):
    original_analysis: AnalysisResponse
    optimized_resume: str
    optimized_analysis: AnalysisResponse

class TextParseResponse(BaseModel):
    filename: str
    text: str
