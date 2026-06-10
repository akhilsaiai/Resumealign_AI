import sys
import os
from fastapi import APIRouter, HTTPException
from typing import List

# Add parent directory to sys.path to allow imports from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.ai_engine import optimize_resume
from backend.schemas.api_models import OptimizationRequest, OptimizationResponse
from backend.config import settings

router = APIRouter(prefix="/api", tags=["Optimizer"])

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_resume_endpoint(payload: OptimizationRequest):
    """
    Optimize and rewrite a resume for a target job description, incorporating identified missing skills.
    """
    provider = payload.provider
    
    # Resolve API Key
    api_key = payload.api_key
    if not api_key:
        if "openai" in provider.lower():
            api_key = os.getenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        else:
            api_key = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="API key is missing. Please provide `api_key` in the request or set the appropriate environment variable on the server."
        )

    try:
        mapped_provider = "OpenAI GPT-4o" if "openai" in provider.lower() else "Groq (Free)"
        
        optimized_text = optimize_resume(
            resume_text=payload.resume_text,
            jd_text=payload.jd_text,
            missing_skills=payload.missing_skills,
            provider=mapped_provider,
            api_key=api_key
        )
        
        return {"optimized_resume": optimized_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
