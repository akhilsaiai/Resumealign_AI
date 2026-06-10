import sys
import os
import io
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Optional

# Add parent directory to sys.path to allow imports from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_parser import parse_uploaded_file
from utils.ai_engine import analyze_resume, optimize_resume
from backend.schemas.api_models import PipelineResponse, AnalysisResponse
from backend.config import settings

router = APIRouter(prefix="/api", tags=["Pipeline"])

class MockUploadedFile:
    def __init__(self, filename: str, content: bytes):
        self.name = filename
        self.content = content
        self._io = io.BytesIO(content)

    def read(self):
        return self._io.read()

@router.post("/pipeline", response_model=PipelineResponse)
async def pipeline_endpoint(
    file: Optional[UploadFile] = File(None, description="Optional PDF, DOCX, or TXT resume file"),
    resume_text: Optional[str] = Form(None, description="Optional raw resume text if no file is uploaded"),
    jd_text: str = Form(..., description="Target job description"),
    provider: str = Form("Groq Llama 3.3", description="AI Provider ('OpenAI GPT-4o' or 'Groq Llama 3.3')"),
    api_key: Optional[str] = Form(None, description="Optional API Key")
):
    """
    Consolidated end-to-end pipeline. 
    1. Extracts text from file (if provided) or uses the provided raw text.
    2. Scores the original resume and extracts missing skills.
    3. Rewrites and optimizes the resume for the job description.
    4. Scores the optimized resume to show the improved metrics.
    """
    # 1. Resolve Resume Text
    text_content = ""
    if file:
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".pdf", ".docx", ".txt"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {ext}. Upload PDF, DOCX, or TXT."
            )
        try:
            content = await file.read()
            mock_file = MockUploadedFile(filename, content)
            text_content = parse_uploaded_file(mock_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse resume file: {str(e)}")
    elif resume_text:
        text_content = resume_text.strip()
    
    if not text_content:
        raise HTTPException(
            status_code=400,
            detail="Please provide a resume by uploading a file or passing resume_text."
        )

    # 2. Resolve API Key
    resolved_api_key = api_key
    if not resolved_api_key:
        if "openai" in provider.lower():
            resolved_api_key = os.getenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        else:
            resolved_api_key = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)

    if not resolved_api_key:
        raise HTTPException(
            status_code=400,
            detail="API key is missing. Please provide `api_key` or configure the server environment variables."
        )

    mapped_provider = "OpenAI GPT-4o" if "openai" in provider.lower() else "Groq (Free)"

    try:
        # Step 1: Analyze original resume
        original_analysis = analyze_resume(
            resume_text=text_content,
            jd_text=jd_text,
            provider=mapped_provider,
            api_key=resolved_api_key
        )

        # Step 2: Optimize resume using missing skills
        missing_skills = original_analysis.get("missing_skills", [])
        optimized_text = optimize_resume(
            resume_text=text_content,
            jd_text=jd_text,
            missing_skills=missing_skills,
            provider=mapped_provider,
            api_key=resolved_api_key
        )

        # Step 3: Analyze the optimized resume
        optimized_analysis = analyze_resume(
            resume_text=optimized_text,
            jd_text=jd_text,
            provider=mapped_provider,
            api_key=resolved_api_key
        )

        return {
            "original_analysis": original_analysis,
            "optimized_resume": optimized_text,
            "optimized_analysis": optimized_analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
