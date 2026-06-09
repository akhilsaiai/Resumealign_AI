"""
utils/export.py
Exports resume to PDF (template-aware), DOCX, TXT.
"""
from __future__ import annotations
import io
import re


def resume_to_txt_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def text_to_docx_bytes(text: str) -> bytes:
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()
        for section in doc.sections:
            section.top_margin    = Inches(0.75)
            section.bottom_margin = Inches(0.75)
            section.left_margin   = Inches(0.9)
            section.right_margin  = Inches(0.9)

        style = doc.styles["Normal"]
        style.font.name = "Calibri"
        style.font.size = Pt(10.5)

        name_done = False
        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                doc.add_paragraph()
                continue

            # ALL-CAPS section header
            if re.match(r"^[A-Z][A-Z\s\/&]{3,}$", stripped) and len(stripped) < 50:
                p   = doc.add_paragraph()
                run = p.add_run(stripped)
                run.bold = True
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(0x1a, 0x50, 0xc8)
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after  = Pt(3)
                continue

            # Name
            if not name_done and len(stripped.split()) <= 6 and not any(c in stripped for c in ["@","|","+"]):
                p   = doc.add_paragraph()
                run = p.add_run(stripped)
                run.font.size = Pt(20)
                run.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                name_done = True
                continue

            # Bullet
            if stripped.startswith("•"):
                p = doc.add_paragraph(style="List Bullet")
                p.add_run(stripped.lstrip("• ").strip())
                p.paragraph_format.left_indent = Inches(0.2)
                continue

            doc.add_paragraph(stripped)

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()
    except ImportError:
        return text.encode("utf-8")


def text_to_pdf_bytes(text: str, template_name: str = "Classic Professional") -> bytes:
    """Generate a styled PDF matching the selected template."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        # ── Palette per template ──────────────────────────────────────
        PALETTES = {
            "Classic Professional": {"header": "#0d1b4b", "accent": "#0d1b4b",  "body": "#2d3748", "meta": "#4a5568"},
            "Modern Minimal":       {"header": "#1e3a8a", "accent": "#2563eb",  "body": "#374151", "meta": "#6b7280"},
            "Executive Elite":      {"header": "#1a1a2e", "accent": "#c9a96e",  "body": "#2d3748", "meta": "#6b5f4e"},
            "Tech Focused":         {"header": "#0f172a", "accent": "#059669",  "body": "#1e293b", "meta": "#64748b"},
            "Creative Clean":       {"header": "#4c1d95", "accent": "#7c3aed",  "body": "#374151", "meta": "#6b7280"},
        }
        p = PALETTES.get(template_name, PALETTES["Classic Professional"])
        HDR  = colors.HexColor(p["header"])
        ACC  = colors.HexColor(p["accent"])
        BODY = colors.HexColor(p["body"])
        META = colors.HexColor(p["meta"])

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=2.2*cm, rightMargin=2.2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )

        name_style = ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=22,
            textColor=HDR, alignment=TA_CENTER, spaceAfter=4)
        contact_style = ParagraphStyle("Contact", fontName="Helvetica", fontSize=9.5,
            textColor=META, alignment=TA_CENTER, spaceAfter=6)
        section_style = ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=9.5,
            textColor=ACC, spaceBefore=14, spaceAfter=4, leading=14)
        job_header_style = ParagraphStyle("JobHdr", fontName="Helvetica-Bold", fontSize=11,
            textColor=HDR, spaceAfter=1, leading=14)
        job_meta_style = ParagraphStyle("JobMeta", fontName="Helvetica", fontSize=9.5,
            textColor=META, spaceAfter=4, leading=13)
        body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=10,
            textColor=BODY, leading=15, spaceAfter=2)
        bullet_style = ParagraphStyle("Bullet", fontName="Helvetica", fontSize=10,
            textColor=BODY, leading=15, spaceAfter=2, leftIndent=14, firstLineIndent=-10)

        story = []
        lines = text.split("\n")
        name_done = False
        in_header = True

        for line in lines:
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 4))
                continue

            # ALL-CAPS section
            if re.match(r"^[A-Z][A-Z\s\/&]{3,}$", stripped) and len(stripped) < 50:
                in_header = False
                story.append(Spacer(1, 6))
                story.append(HRFlowable(width="100%", thickness=0.8, color=ACC, spaceAfter=4))
                story.append(Paragraph(stripped, section_style))
                continue

            # Name
            if in_header and not name_done and len(stripped.split()) <= 6 and not any(c in stripped for c in ["@","|","+"]):
                story.append(Paragraph(stripped, name_style))
                name_done = True
                continue

            # Contact header lines
            if in_header:
                story.append(Paragraph(stripped, contact_style))
                continue

            # Bullet
            if stripped.startswith("•") or stripped.startswith("-"):
                clean = re.sub(r'^[•\-]\s*', '', stripped)
                story.append(Paragraph(f"• {clean}", bullet_style))
                continue

            # Job header with |
            if "|" in stripped:
                parts = [p2.strip() for p2 in stripped.split("|")]
                story.append(Paragraph(parts[0], job_header_style))
                if len(parts) > 1:
                    story.append(Paragraph(" · ".join(parts[1:]), job_meta_style))
                continue

            # Date line
            if re.search(r'\d{4}', stripped) and len(stripped) < 60:
                story.append(Paragraph(stripped, job_meta_style))
                continue

            story.append(Paragraph(stripped, body_style))

        doc.build(story)
        return buf.getvalue()

    except ImportError:
        return text.encode("utf-8")
