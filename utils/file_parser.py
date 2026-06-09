"""
utils/file_parser.py
Handles text extraction from PDF (.pdf) and Word (.docx) files.
"""
from __future__ import annotations
import io


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract plain text from a PDF file object."""
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except ImportError:
        # Fallback to pypdf if PyPDF2 not installed
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages).strip()
        except ImportError:
            raise ImportError(
                "PDF parsing requires PyPDF2 or pypdf. "
                "Install with: pip install PyPDF2"
            )


def extract_text_from_docx(uploaded_file) -> str:
    """Extract plain text from a .docx file object."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs).strip()
    except ImportError:
        raise ImportError(
            "DOCX parsing requires python-docx. "
            "Install with: pip install python-docx"
        )


def parse_uploaded_file(uploaded_file) -> str:
    """
    Auto-detect file type and return extracted text.
    Supports: .pdf, .docx, .txt
    """
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    elif name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore").strip()
    else:
        raise ValueError(
            f"Unsupported file type: {uploaded_file.name}. "
            "Please upload a .pdf, .docx, or .txt file."
        )
