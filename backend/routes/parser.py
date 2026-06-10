import io
import sys
import os
from fastapi import APIRouter, UploadFile, File, HTTPException

# Add parent directory to sys.path to allow imports from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_parser import parse_uploaded_file

router = APIRouter(prefix="/api", tags=["Parser"])

class MockUploadedFile:
    def __init__(self, filename: str, content: bytes):
        self.name = filename
        self.content = content
        self._io = io.BytesIO(content)

    def read(self):
        return self._io.read()

@router.post("/parse", response_model=dict)
async def parse_resume_file(file: UploadFile = File(..., description="PDF, DOCX, or TXT resume file")):
    """
    Extract plain text from an uploaded resume file (.pdf, .docx, .txt).
    """
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format: {ext}. Only PDF, DOCX, and TXT are supported."
        )
        
    try:
        content = await file.read()
        mock_file = MockUploadedFile(filename, content)
        extracted_text = parse_uploaded_file(mock_file)
        
        return {
            "filename": filename,
            "text": extracted_text,
            "word_count": len(extracted_text.split())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")
