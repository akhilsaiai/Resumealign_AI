"""
components/optimized_resume.py
LaTeX-style resume display with 5 ATS-friendly templates.
Download as PDF or DOCX.
"""
import streamlit as st
import re
from utils.export import text_to_pdf_bytes, text_to_docx_bytes, resume_to_txt_bytes
from utils.ai_engine import optimize_resume

# ── Template definitions ──────────────────────────────────────────────────────
TEMPLATES = {
    "Classic Professional": {
        "desc": "Clean serif font, navy accents — ideal for finance, law, consulting",
        "icon": "🏛️",
        "css": """
            body{font-family:'Georgia',serif;color:#1a1a2e;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:48px 52px;background:#fff}
            .name{font-size:26px;font-weight:700;color:#0d1b4b;letter-spacing:0.5px;margin-bottom:3px}
            .contact{font-size:11px;color:#4a5568;margin-bottom:18px;line-height:1.8}
            .section-title{font-size:11px;font-weight:700;text-transform:uppercase;
                letter-spacing:2px;color:#0d1b4b;border-bottom:1.5px solid #0d1b4b;
                padding-bottom:3px;margin:20px 0 10px}
            .job-header{font-size:12.5px;font-weight:700;color:#1a1a2e;margin-bottom:1px}
            .job-meta{font-size:11px;color:#4a5568;margin-bottom:6px}
            .bullet{font-size:11.5px;line-height:1.65;color:#2d3748;margin:2px 0 2px 16px;
                text-indent:-10px;padding-left:10px}
            .bullet::before{content:"•";color:#0d1b4b;margin-right:6px}
            .body-text{font-size:11.5px;line-height:1.7;color:#2d3748}
            .skill-group{font-size:11.5px;color:#2d3748;margin:3px 0;line-height:1.6}
        """,
    },
    "Modern Minimal": {
        "desc": "Clean sans-serif, sidebar accent line — great for tech, startups",
        "icon": "⚡",
        "css": """
            body{font-family:'Arial',sans-serif;color:#111;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:44px 52px;background:#fff;
                border-left:4px solid #2563eb}
            .name{font-size:28px;font-weight:700;color:#1e3a8a;letter-spacing:-0.5px;margin-bottom:2px}
            .contact{font-size:11px;color:#6b7280;margin-bottom:20px;line-height:1.9}
            .section-title{font-size:10px;font-weight:700;text-transform:uppercase;
                letter-spacing:2.5px;color:#2563eb;margin:22px 0 8px;
                padding-left:8px;border-left:3px solid #2563eb}
            .job-header{font-size:13px;font-weight:700;color:#111;margin-bottom:1px}
            .job-meta{font-size:11px;color:#6b7280;margin-bottom:6px}
            .bullet{font-size:11.5px;line-height:1.65;color:#374151;margin:2px 0 2px 14px;
                text-indent:-8px;padding-left:8px}
            .bullet::before{content:"▸";color:#2563eb;margin-right:5px;font-size:10px}
            .body-text{font-size:11.5px;line-height:1.7;color:#374151}
            .skill-group{font-size:11.5px;color:#374151;margin:3px 0;line-height:1.6}
        """,
    },
    "Executive Elite": {
        "desc": "Two-tone header, gold rule — perfect for senior roles and executives",
        "icon": "👑",
        "css": """
            body{font-family:'Georgia',serif;color:#1a1a2e;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:0;background:#fff}
            .header-block{background:#1a1a2e;padding:32px 52px 24px;margin-bottom:0}
            .name{font-size:28px;font-weight:700;color:#fff;letter-spacing:1px;margin-bottom:3px}
            .contact{font-size:11px;color:#c9a96e;line-height:2}
            .gold-rule{height:3px;background:linear-gradient(90deg,#c9a96e,#e8c98a,#c9a96e);margin:0}
            .body-section{padding:24px 52px}
            .section-title{font-size:10px;font-weight:700;text-transform:uppercase;
                letter-spacing:2px;color:#c9a96e;border-bottom:1px solid #c9a96e33;
                padding-bottom:4px;margin:18px 0 10px}
            .job-header{font-size:13px;font-weight:700;color:#1a1a2e;margin-bottom:1px}
            .job-meta{font-size:11px;color:#6b5f4e;margin-bottom:6px}
            .bullet{font-size:11.5px;line-height:1.65;color:#2d3748;margin:2px 0 2px 16px;
                text-indent:-10px;padding-left:10px}
            .bullet::before{content:"◆";color:#c9a96e;margin-right:6px;font-size:8px}
            .body-text{font-size:11.5px;line-height:1.7;color:#2d3748}
            .skill-group{font-size:11.5px;color:#2d3748;margin:3px 0;line-height:1.6}
        """,
    },
    "Tech Focused": {
        "desc": "Monospace accents, green highlights — tailored for software engineers",
        "icon": "💻",
        "css": """
            body{font-family:'Arial',sans-serif;color:#0f172a;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:40px 52px;background:#fff}
            .name{font-size:24px;font-weight:700;color:#0f172a;font-family:'Courier New',monospace;margin-bottom:2px}
            .name-accent{color:#059669}
            .contact{font-size:11px;color:#64748b;font-family:'Courier New',monospace;margin-bottom:18px;line-height:1.9}
            .section-title{font-size:11px;font-weight:700;text-transform:uppercase;
                letter-spacing:1.5px;color:#059669;margin:20px 0 8px;
                font-family:'Courier New',monospace}
            .section-rule{height:1px;background:#d1fae5;margin-bottom:10px}
            .job-header{font-size:13px;font-weight:700;color:#0f172a;margin-bottom:1px}
            .job-meta{font-size:11px;color:#64748b;margin-bottom:6px;font-family:'Courier New',monospace}
            .bullet{font-size:11.5px;line-height:1.65;color:#1e293b;margin:2px 0 2px 14px;
                text-indent:-8px;padding-left:8px}
            .bullet::before{content:"→";color:#059669;margin-right:5px}
            .body-text{font-size:11.5px;line-height:1.7;color:#1e293b}
            .skill-group{font-size:11.5px;color:#1e293b;margin:3px 0;line-height:1.6}
            .skill-tag-inline{background:#d1fae5;color:#065f46;padding:1px 7px;
                border-radius:3px;font-size:10.5px;margin:2px;display:inline-block}
        """,
    },
    "Creative Clean": {
        "desc": "Purple accents, modern layout — for design, marketing, creative roles",
        "icon": "🎨",
        "css": """
            body{font-family:'Arial',sans-serif;color:#1f1f2e;background:#fff;margin:0;padding:0}
            .resume{max-width:760px;margin:0 auto;padding:44px 52px;background:#fff}
            .name{font-size:27px;font-weight:700;color:#4c1d95;letter-spacing:-0.3px;margin-bottom:2px}
            .contact{font-size:11px;color:#6b7280;margin-bottom:18px;line-height:1.9}
            .section-title{font-size:10.5px;font-weight:700;text-transform:uppercase;
                letter-spacing:2px;color:#7c3aed;margin:20px 0 8px;
                background:linear-gradient(90deg,#ede9fe,transparent);
                padding:4px 8px;border-radius:3px}
            .job-header{font-size:13px;font-weight:700;color:#1f1f2e;margin-bottom:1px}
            .job-meta{font-size:11px;color:#6b7280;margin-bottom:6px}
            .bullet{font-size:11.5px;line-height:1.65;color:#374151;margin:2px 0 2px 14px;
                text-indent:-8px;padding-left:8px}
            .bullet::before{content:"◉";color:#7c3aed;margin-right:5px;font-size:9px}
            .body-text{font-size:11.5px;line-height:1.7;color:#374151}
            .skill-group{font-size:11.5px;color:#374151;margin:3px 0;line-height:1.6}
        """,
    },
}


def _parse_resume_to_html(text: str, template_name: str) -> str:
    """Convert plain resume text to styled HTML using selected template."""
    css = TEMPLATES[template_name]["css"]
    lines = [l for l in text.split("\n")]

    is_executive = template_name == "Executive Elite"
    is_tech      = template_name == "Tech Focused"

    body_html = ""
    in_header_block = True
    name_done = False
    contact_lines = []

    def flush_contacts():
        nonlocal contact_lines
        if contact_lines:
            html = '<div class="contact">' + " &nbsp;|&nbsp; ".join(contact_lines) + '</div>'
            contact_lines = []
            return html
        return ""

    sections_html = ""
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # ALL-CAPS section header
        if re.match(r"^[A-Z][A-Z\s\/&]{3,}$", stripped) and len(stripped) < 50:
            in_header_block = False
            sections_html += flush_contacts()
            rule = '<div class="section-rule"></div>' if is_tech else ''
            sections_html += f'<div class="section-title">{stripped}</div>{rule}'
            current_section = stripped
            continue

        # Name (first short non-contact line)
        if in_header_block and not name_done and len(stripped.split()) <= 6 and not any(c in stripped for c in ["@",":","|","+"]):
            name_display = stripped
            if is_tech:
                # Split name and add accent to last word
                parts = stripped.split()
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
        if stripped.startswith("•") or stripped.startswith("-"):
            clean = stripped.lstrip("•- ").strip()
            sections_html += f'<div class="bullet">{clean}</div>'
            continue

        # Job header: line with | separating company/title/date
        if "|" in stripped and len(stripped.split("|")) >= 2:
            parts = [p.strip() for p in stripped.split("|")]
            sections_html += f'<div class="job-header">{parts[0]}</div>'
            if len(parts) > 1:
                sections_html += f'<div class="job-meta">{" · ".join(parts[1:])}</div>'
            continue

        # Date ranges as job meta
        if re.search(r'\d{4}', stripped) and ("–" in stripped or "-" in stripped or "Present" in stripped) and len(stripped) < 60:
            sections_html += f'<div class="job-meta">{stripped}</div>'
            continue

        # Skills line with colon
        if ":" in stripped and current_section and "SKILL" in current_section.upper():
            sections_html += f'<div class="skill-group"><strong>{stripped.split(":")[0]}:</strong> {":".join(stripped.split(":")[1:])}</div>'
            continue

        # Generic body text
        sections_html += f'<div class="body-text">{stripped}</div>'

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

    cols = st.columns(5, gap="small")
    for i, (tname, tmeta) in enumerate(TEMPLATES.items()):
        with cols[i]:
            selected = st.session_state.get("selected_template") == tname
            border   = "2px solid #c9a96e" if selected else "1px solid rgba(201,169,110,0.15)"
            bg       = "rgba(201,169,110,0.08)" if selected else "#12121a"
            st.markdown(f"""
            <div style="background:{bg};border:{border};border-radius:10px;
                        padding:0.8rem 0.5rem;text-align:center;cursor:pointer">
                <div style="font-size:1.4rem;margin-bottom:0.3rem">{tmeta['icon']}</div>
                <div style="font-size:0.72rem;font-weight:600;color:#f0f2f6;
                            margin-bottom:0.2rem">{tname}</div>
                <div style="font-size:0.62rem;color:#6b7589;line-height:1.4">{tmeta['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select", key=f"tpl_{i}", use_container_width=True):
                st.session_state.selected_template = tname
                st.rerun()

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
