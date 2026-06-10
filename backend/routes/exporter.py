import sys
import os
import io
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional

# Add parent directory to sys.path to allow imports from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.export import resume_to_txt_bytes, text_to_docx_bytes, text_to_pdf_bytes

router = APIRouter(prefix="/api/export", tags=["Exporter"])

class ExportRequest(BaseModel):
    text: str = Field(..., description="The plain text of the optimized resume to export")

class PDFExportRequest(ExportRequest):
    template_name: str = Field(
        "Classic Professional", 
        description="The template style to use. Choices: 'Classic Professional', 'Modern Minimal', 'Executive Elite', 'Tech Focused', 'Creative Clean'"
    )

@router.post("/docx")
async def export_docx(payload: ExportRequest):
    """
    Export the optimized resume text as a formatted DOCX Word Document.
    """
    try:
        docx_bytes = text_to_docx_bytes(payload.text)
        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=optimized_resume.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")

@router.post("/pdf")
async def export_pdf(payload: PDFExportRequest):
    """
    Export the optimized resume text as a beautifully styled PDF matching the selected template.
    """
    try:
        pdf_bytes = text_to_pdf_bytes(payload.text, template_name=payload.template_name)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=optimized_resume.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.post("/txt")
async def export_txt(payload: ExportRequest):
    """
    Export the optimized resume text as a plain text (.txt) file.
    """
    try:
        txt_bytes = resume_to_txt_bytes(payload.text)
        return StreamingResponse(
            io.BytesIO(txt_bytes),
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=optimized_resume.txt"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate TXT: {str(e)}")
