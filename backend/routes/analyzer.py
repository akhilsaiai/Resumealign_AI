import sys
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError

# Add parent directory to sys.path to allow imports from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.ai_engine import analyze_resume
from backend.schemas.api_models import AnalysisRequest, AnalysisResponse
from backend.config import settings

router = APIRouter(prefix="/api", tags=["Analyzer"])

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume_endpoint(payload: AnalysisRequest):
    """
    Perform ATS score and gap analysis on raw resume text against a job description.
    """
    provider = payload.provider
    
    # Resolve API Key: payload key -> environment variable -> fallback config settings
    api_key = payload.api_key
    if not api_key:
        if "openai" in provider.lower():
            api_key = os.getenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        else:
            api_key = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"API key is missing. Please provide `api_key` in the request or set the appropriate environment variable on the server."
        )

    try:
        # Map provider string to match utils/ai_engine.py expectations
        mapped_provider = "OpenAI GPT-4o" if "openai" in provider.lower() else "Groq (Free)"
        
        result = analyze_resume(
            resume_text=payload.resume_text,
            jd_text=payload.jd_text,
            provider=mapped_provider,
            api_key=api_key
        )
        
        # Validate result dict format matches expected schema
        # If the keys returned from AI aren't exact, we map them or let Pydantic handle validation
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
