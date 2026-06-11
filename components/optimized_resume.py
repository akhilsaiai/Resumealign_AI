"""
components/optimized_resume.py
LaTeX-style resume display with 5 ATS-friendly templates.
Download as PDF or DOCX.
"""
import streamlit as st
import re
from utils.export import text_to_pdf_bytes, text_to_docx_bytes, resume_to_txt_bytes, clean_and_check_header, is_bullet, clean_bullet_text, strip_markdown
from utils.ai_engine import optimize_resume

# ── Template definitions ──────────────────────────────────────────────────────
TEMPLATES = {
    "Classic Professional": {
        "desc": "Clean serif Georgia font, navy accents — classic business layout",
        "icon": "🏛️",
        "css": """
            body{font-family:'Georgia',serif;color:#1e293b;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:25px 35px;background:#fff}
            .name{font-size:22px;font-weight:700;color:#0d1b4b;letter-spacing:0.5px;margin-bottom:3px}
            .contact{font-size:10px;color:#475569;margin-bottom:12px;line-height:1.5}
            .section-title{font-size:10.5px;font-weight:700;text-transform:uppercase;
                letter-spacing:1.5px;color:#0d1b4b;border-bottom:1px solid #0d1b4b;
                padding-bottom:2px;margin:12px 0 6px}
            .job-header{font-size:11.5px;font-weight:700;color:#1e293b;margin-bottom:1px}
            .job-meta{font-size:10px;color:#475569;margin-bottom:4px}
            .bullet{font-size:10px;line-height:1.4;color:#334155;margin:2px 0 2px 14px;
                text-indent:-10px;padding-left:10px}
            .bullet::before{content:"•";color:#0d1b4b;margin-right:6px}
            .body-text{font-size:10px;line-height:1.45;color:#334155}
            .skill-group{font-size:10px;color:#334155;margin:2px 0;line-height:1.4}
        """,
    },
    "Modern Minimal": {
        "desc": "Clean sans-serif Arial, sidebar accent line — modern tech layout",
        "icon": "⚡",
        "css": """
            body{font-family:'Arial',sans-serif;color:#1e293b;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:25px 35px;background:#fff;
                border-left:3px solid #2563eb}
            .name{font-size:24px;font-weight:700;color:#1e3a8a;letter-spacing:-0.5px;margin-bottom:2px}
            .contact{font-size:9.5px;color:#64748b;margin-bottom:12px;line-height:1.5}
            .section-title{font-size:9.5px;font-weight:700;text-transform:uppercase;
                letter-spacing:2px;color:#2563eb;margin:12px 0 6px;
                padding-left:6px;border-left:2px solid #2563eb}
            .job-header{font-size:11.5px;font-weight:700;color:#0f172a;margin-bottom:1px}
            .job-meta{font-size:9.5px;color:#64748b;margin-bottom:4px}
            .bullet{font-size:10px;line-height:1.4;color:#334155;margin:2px 0 2px 12px;
                text-indent:-8px;padding-left:8px}
            .bullet::before{content:"▸";color:#2563eb;margin-right:5px;font-size:9px}
            .body-text{font-size:10px;line-height:1.45;color:#334155}
            .skill-group{font-size:10px;color:#334155;margin:2px 0;line-height:1.4}
        """,
    },
    "Executive Elite": {
        "desc": "Compact top header block, gold rule dividers — premium executive style",
        "icon": "👑",
        "css": """
            body{font-family:'Georgia',serif;color:#1e293b;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:0;background:#fff}
            .header-block{background:#1e293b;padding:20px 35px 15px;margin-bottom:0}
            .name{font-size:24px;font-weight:700;color:#fff;letter-spacing:0.5px;margin-bottom:2px}
            .contact{font-size:10px;color:#c9a96e;line-height:1.6}
            .gold-rule{height:2px;background:linear-gradient(90deg,#c9a96e,#e8c98a,#c9a96e);margin:0}
            .body-section{padding:15px 35px}
            .section-title{font-size:9.5px;font-weight:700;text-transform:uppercase;
                letter-spacing:1.5px;color:#c9a96e;border-bottom:1px solid #c9a96e44;
                padding-bottom:2px;margin:12px 0 6px}
            .job-header{font-size:11.5px;font-weight:700;color:#1e293b;margin-bottom:1px}
            .job-meta{font-size:9.5px;color:#6b5f4e;margin-bottom:4px}
            .bullet{font-size:10px;line-height:1.4;color:#334155;margin:2px 0 2px 14px;
                text-indent:-10px;padding-left:10px}
            .bullet::before{content:"◆";color:#c9a96e;margin-right:6px;font-size:7px}
            .body-text{font-size:10px;line-height:1.45;color:#334155}
            .skill-group{font-size:10px;color:#334155;margin:2px 0;line-height:1.4}
        """,
    },
    "Tech Focused": {
        "desc": "Monospace elements, green accents — ideal for tech and developers",
        "icon": "💻",
        "css": """
            body{font-family:'Arial',sans-serif;color:#0f172a;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:25px 35px;background:#fff}
            .name{font-size:22px;font-weight:700;color:#0f172a;font-family:'Courier New',monospace;margin-bottom:2px}
            .name-accent{color:#059669}
            .contact{font-size:9.5px;color:#64748b;font-family:'Courier New',monospace;margin-bottom:12px;line-height:1.6}
            .section-title{font-size:9.5px;font-weight:700;text-transform:uppercase;
                letter-spacing:1.5px;color:#059669;margin:12px 0 6px;
                font-family:'Courier New',monospace}
            .section-rule{height:1px;background:#d1fae5;margin-bottom:6px}
            .job-header{font-size:11.5px;font-weight:700;color:#0f172a;margin-bottom:1px}
            .job-meta{font-size:9.5px;color:#64748b;margin-bottom:4px;font-family:'Courier New',monospace}
            .bullet{font-size:10px;line-height:1.4;color:#1e293b;margin:2px 0 2px 12px;
                text-indent:-8px;padding-left:8px}
            .bullet::before{content:"→";color:#059669;margin-right:5px}
            .body-text{font-size:10px;line-height:1.45;color:#1e293b}
            .skill-group{font-size:10px;color:#1e293b;margin:2px 0;line-height:1.4}
            .skill-tag-inline{background:#d1fae5;color:#065f46;padding:1px 5px;
                border-radius:3px;font-size:9.5px;margin:1px;display:inline-block}
        """,
    },
    "Creative Clean": {
        "desc": "Purple highlights, gradient header borders — clean creative layout",
        "icon": "🎨",
        "css": """
            body{font-family:'Arial',sans-serif;color:#1f1f2e;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:25px 35px;background:#fff}
            .name{font-size:24px;font-weight:700;color:#4c1d95;letter-spacing:-0.3px;margin-bottom:2px}
            .contact{font-size:9.5px;color:#6b7280;margin-bottom:12px;line-height:1.6}
            .section-title{font-size:9.5px;font-weight:700;text-transform:uppercase;
                letter-spacing:1.5px;color:#7c3aed;margin:12px 0 6px;
                background:linear-gradient(90deg,#ede9fe,transparent);
                padding:2px 6px;border-radius:2px}
            .job-header{font-size:11.5px;font-weight:700;color:#1f1f2e;margin-bottom:1px}
            .job-meta{font-size:9.5px;color:#6b7280;margin-bottom:4px}
            .bullet{font-size:10px;line-height:1.4;color:#374151;margin:2px 0 2px 12px;
                text-indent:-8px;padding-left:8px}
            .bullet::before{content:"◉";color:#7c3aed;margin-right:5px;font-size:8px}
            .body-text{font-size:10px;line-height:1.45;color:#374151}
            .skill-group{font-size:10px;color:#374151;margin:2px 0;line-height:1.4}
        """,
    },
    "Sleek Harvard": {
        "desc": "Academic Times New Roman, centered header — traditional elite formatting",
        "icon": "🎓",
        "css": """
            body{font-family:'Times New Roman',Times,serif;color:#111111;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:25px 35px;background:#fff}
            .name{font-size:22px;font-weight:700;text-align:center;color:#000;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px}
            .contact{font-size:9.5px;text-align:center;color:#333;margin-bottom:12px;line-height:1.5}
            .section-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#000;border-bottom:1px solid #000;padding-bottom:2px;margin:12px 0 6px}
            .job-header{font-size:11px;font-weight:700;color:#111;margin-bottom:1px}
            .job-meta{font-size:9.5px;color:#333;margin-bottom:4px}
            .bullet{font-size:10px;line-height:1.4;color:#222;margin:2px 0 2px 14px;text-indent:-10px;padding-left:10px}
            .bullet::before{content:"•";color:#000;margin-right:6px}
            .body-text{font-size:10px;line-height:1.45;color:#222}
            .skill-group{font-size:10px;color:#222;margin:2px 0;line-height:1.4}
        """,
    },
    "Silicon Valley": {
        "desc": "Clean sans-serif, sky blue details — high density tech layout",
        "icon": "🌐",
        "css": """
            body{font-family:'Arial',sans-serif;color:#1e293b;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:25px 35px;background:#fff}
            .name{font-size:24px;font-weight:800;color:#0f172a;letter-spacing:-0.5px;margin-bottom:2px}
            .contact{font-size:9.5px;color:#64748b;margin-bottom:12px;line-height:1.5}
            .section-title{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#0284c7;border-bottom:1px solid #e2e8f0;padding-bottom:2px;margin:12px 0 6px}
            .job-header{font-size:11.5px;font-weight:700;color:#0f172a;margin-bottom:1px}
            .job-meta{font-size:9.5px;color:#64748b;margin-bottom:4px}
            .bullet{font-size:10px;line-height:1.4;color:#334155;margin:2px 0 2px 12px;text-indent:-8px;padding-left:8px}
            .bullet::before{content:"▪";color:#0284c7;margin-right:5px;font-size:7px}
            .body-text{font-size:10px;line-height:1.45;color:#334155}
            .skill-group{font-size:10px;color:#334155;margin:2px 0;line-height:1.4}
        """,
    },
    "Corporate Executive": {
        "desc": "Premium Georgia, slate accents — elegant business single-page format",
        "icon": "💼",
        "css": """
            body{font-family:'Georgia',serif;color:#222;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:25px 35px;background:#fff}
            .name{font-size:22px;font-weight:700;color:#1e293b;letter-spacing:0.5px;margin-bottom:2px}
            .contact{font-size:9.5px;color:#475569;margin-bottom:12px;line-height:1.5}
            .section-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#1e293b;border-bottom:1.5px solid #475569;padding-bottom:2px;margin:12px 0 6px}
            .job-header{font-size:11.5px;font-weight:700;color:#1e293b;margin-bottom:1px}
            .job-meta{font-size:9.5px;color:#475569;margin-bottom:4px}
            .bullet{font-size:10px;line-height:1.4;color:#334155;margin:2px 0 2px 14px;text-indent:-10px;padding-left:10px}
            .bullet::before{content:"•";color:#1e293b;margin-right:6px}
            .body-text{font-size:10px;line-height:1.45;color:#334155}
            .skill-group{font-size:10px;color:#334155;margin:2px 0;line-height:1.4}
        """,
    },
},
}


def md_to_html(text: str) -> str:
    # Replace **text** with <strong>text</strong>
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    # Replace *text* with <em>text</em>
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    # Replace __text__ with <strong>text</strong>
    text = re.sub(r"__(.*?)__", r"<strong>\1</strong>", text)
    # Replace _text_ with <em>text</em>
    text = re.sub(r"_(.*?)_", r"<em>\1</em>", text)
    return text


def _parse_resume_to_html(text: str, template_name: str) -> str:
    """Convert plain resume text to styled HTML using selected template."""
    css = TEMPLATES[template_name]["css"]
    lines = [l for l in text.split("\n")]

    is_executive = template_name == "Executive Elite"
    is_tech      = template_name == "Tech Focused"

    sections_html = ""
    in_header_block = True
    name_done = False
    contact_lines = []

    def flush_contacts():
        nonlocal contact_lines
        if contact_lines:
            cleaned_contacts = [md_to_html(strip_markdown(l)) for l in contact_lines]
            html = '<div class="contact">' + " &nbsp;|&nbsp; ".join(cleaned_contacts) + '</div>'
            contact_lines = []
            return html
        return ""

    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for section header
        is_hdr, hdr_title = clean_and_check_header(stripped)
        if is_hdr:
            in_header_block = False
            sections_html += flush_contacts()
            rule = '<div class="section-rule"></div>' if is_tech else ''
            sections_html += f'<div class="section-title">{hdr_title}</div>{rule}'
            current_section = hdr_title
            continue

        # Name (first short non-contact line)
        if in_header_block and not name_done:
            name_candidate = strip_markdown(stripped).strip()
            if len(name_candidate.split()) <= 6 and not any(c in name_candidate for c in ["@", ":", "|", "+"]):
                name_display = name_candidate
                if is_tech:
                    # Split name and add accent to last word
                    parts = name_candidate.split()
                    if len(parts) > 1:
                        name_display = " ".join(parts[:-1]) + f' <span class="name-accent">{parts[-1]}</span>'
                sections_html += f'<div class="name">{name_display}</div>'
                name_done = True
                continue

        # Contact info lines
        if in_header_block:
            contact_lines.append(stripped)
            continue

        # Bullet point
        if is_bullet(stripped):
            clean = clean_bullet_text(stripped)
            sections_html += f'<div class="bullet">{md_to_html(clean)}</div>'
            continue

        # Job header: line with | separating company/title/date
        if "|" in stripped and len(stripped.split("|")) >= 2:
            parts = [p.strip() for p in stripped.split("|")]
            company = md_to_html(strip_markdown(parts[0]))
            sections_html += f'<div class="job-header">{company}</div>'
            if len(parts) > 1:
                meta = " · ".join(md_to_html(strip_markdown(p)) for p in parts[1:])
                sections_html += f'<div class="job-meta">{meta}</div>'
            continue

        # Date ranges as job meta
        if re.search(r'\d{4}', stripped) and ("–" in stripped or "-" in stripped or "Present" in stripped) and len(stripped) < 60:
            sections_html += f'<div class="job-meta">{md_to_html(strip_markdown(stripped))}</div>'
            continue

        # Skills line with colon
        if ":" in stripped and current_section and "SKILL" in current_section.upper():
            parts = stripped.split(":")
            category = md_to_html(strip_markdown(parts[0]))
            val = md_to_html(strip_markdown(":".join(parts[1:])))
            sections_html += f'<div class="skill-group"><strong>{category}:</strong> {val}</div>'
            continue

        # Generic body text
        sections_html += f'<div class="body-text">{md_to_html(stripped)}</div>'

    sections_html += flush_contacts()

    if is_executive:
        header_html = f"""
        <div class="header-block">
            {sections_html.split('<div class="section-title">')[0] if '<div class="section-title">' in sections_html else ""}
        </div>
        <div class="gold-rule"></div>
        <div class="body-section">
            {"".join(sections_html.split('<div class="section-title">')[1:]).replace('</div>', '</div>', 1) if '<div class="section-title">' in sections_html else sections_html}
        </div>
        """
        # Simpler approach for executive
        all_lines_html = sections_html
        final_html = f"""
        <!DOCTYPE html><html><head>
        <meta charset="UTF-8">
        <style>
            {css}
            @media print {{ body{{margin:0}} .resume{{padding:32px 44px}} }}
        </style>
        </head><body>
        <div class="resume">
            {all_lines_html}
        </div>
        </body></html>
        """
    else:
        final_html = f"""
        <!DOCTYPE html><html><head>
        <meta charset="UTF-8">
        <style>
            {css}
            @media print {{ body{{margin:0}} .resume{{padding:32px 44px}} }}
        </style>
        </head><body>
        <div class="resume">
            {sections_html}
        </div>
        </body></html>
        """
    return final_html


def render_optimized_resume():
    optimized = st.session_state.get("optimized_resume", "")
    if not optimized:
        st.info("No optimized resume yet. Please run an analysis first.")
        return

    # ── Header ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom:1.5rem">
        <div style="font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;
                    color:#f0f2f6;margin-bottom:0.3rem">
            ✨ Optimized Resume
        </div>
        <div style="font-size:0.75rem;color:#6b7589;letter-spacing:0.06em">
            Select a template · Preview · Download as PDF or DOCX
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Template selector ───────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.15em;
                text-transform:uppercase;color:#c9a96e;margin-bottom:0.8rem">
        ✦ Choose a Template
    </div>
    """, unsafe_allow_html=True)

    t_items = list(TEMPLATES.items())
    for row_idx in [0, 4]:
        cols = st.columns(4, gap="small")
        for col_idx in range(4):
            idx = row_idx + col_idx
            if idx >= len(t_items):
                break
            tname, tmeta = t_items[idx]
            with cols[col_idx]:
                selected = st.session_state.get("selected_template") == tname
                border   = "2px solid #c9a96e" if selected else "1px solid rgba(201,169,110,0.15)"
                bg       = "rgba(201,169,110,0.08)" if selected else "#12121a"
                st.markdown(f"""
                <div style="background:{bg};border:{border};border-radius:10px;
                            padding:0.6rem 0.4rem;text-align:center;cursor:pointer;min-height:115px">
                    <div style="font-size:1.2rem;margin-bottom:0.2rem">{tmeta['icon']}</div>
                    <div style="font-size:0.68rem;font-weight:600;color:#f0f2f6;
                                margin-bottom:0.2rem">{tname}</div>
                    <div style="font-size:0.58rem;color:#6b7589;line-height:1.3">{tmeta['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Select", key=f"tpl_{idx}", use_container_width=True):
                    st.session_state.selected_template = tname
                    st.rerun()
        st.markdown("<div style='margin-bottom:0.4rem'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    selected_template = st.session_state.get("selected_template", "Classic Professional")

    # ── Download buttons ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:1rem">
        <span style="font-size:0.7rem;font-weight:600;letter-spacing:0.15em;
                     text-transform:uppercase;color:#c9a96e">✦ Download As</span>
    </div>
    """, unsafe_allow_html=True)

    dl1, dl2, dl3, regen_col = st.columns([1,1,1,1], gap="small")

    with dl1:
        try:
            pdf_bytes = text_to_pdf_bytes(optimized, selected_template)
            st.download_button(
                "⬇ PDF",
                data=pdf_bytes,
                file_name=f"resume_{selected_template.lower().replace(' ','_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as ex:
            st.caption(f"PDF error: {ex}")

    with dl2:
        try:
            docx_bytes = text_to_docx_bytes(optimized)
            st.download_button(
                "⬇ DOCX",
                data=docx_bytes,
                file_name="optimized_resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception:
            st.caption("DOCX unavailable")

    with dl3:
        st.download_button(
            "⬇ TXT",
            data=resume_to_txt_bytes(optimized),
            file_name="optimized_resume.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with regen_col:
        if st.button("🔁 Regenerate", use_container_width=True):
            _regenerate()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Live preview ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.15em;
                text-transform:uppercase;color:#c9a96e;margin-bottom:0.8rem">
        ✦ Live Preview — {selected_template}
    </div>
    """, unsafe_allow_html=True)

    html_preview = _parse_resume_to_html(optimized, selected_template)
    st.components.v1.html(html_preview, height=900, scrolling=True)

    # ── Edit raw text ─────────────────────────────────────────────────
    with st.expander("✏️ Edit resume text (advanced)"):
        edited = st.text_area("Edit content", value=optimized, height=500, label_visibility="collapsed", key="editable_resume")
        if edited != optimized:
            st.session_state.optimized_resume = edited
            st.caption("Changes saved — preview and downloads will update.")


def _regenerate():
    resume   = st.session_state.resume_text
    jd       = st.session_state.jd_text
    provider = st.session_state.model_provider
    api_key  = st.session_state.api_key
    missing  = (st.session_state.analysis_result or {}).get("missing_skills", [])
    with st.spinner("🔄 Regenerating optimized resume…"):
        try:
            new_resume = optimize_resume(resume, jd, missing, provider, api_key)
            st.session_state.optimized_resume = new_resume
            st.success("✅ Regenerated!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ {e}")
