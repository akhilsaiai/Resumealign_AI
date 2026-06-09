import streamlit as st
from utils.file_parser import parse_uploaded_file
from utils.ai_engine import analyze_resume, optimize_resume


def render_upload_section():
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">📄 Your Resume</div>
        </div>
        """, unsafe_allow_html=True)

        upload_tab, paste_tab = st.tabs(["Upload File", "Paste Text"])

        with upload_tab:
            uploaded = st.file_uploader(
                "Drop your resume here",
                type=["pdf", "docx", "txt"],
                label_visibility="collapsed",
            )
            if uploaded:
                try:
                    text = parse_uploaded_file(uploaded)
                    st.session_state.resume_text = text
                    st.success(f"✅ Parsed **{uploaded.name}** — {len(text.split())} words")
                    with st.expander("Preview extracted text"):
                        st.text(text[:1200] + ("…" if len(text) > 1200 else ""))
                except Exception as e:
                    st.error(f"❌ {e}")

        with paste_tab:
            pasted = st.text_area(
                "Paste resume text",
                height=260,
                placeholder="Paste your full resume content here…",
                label_visibility="collapsed",
            )
            if pasted.strip():
                st.session_state.resume_text = pasted.strip()

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">💼 Job Description</div>
        </div>
        """, unsafe_allow_html=True)

        jd_text = st.text_area(
            "Paste the job description",
            height=320,
            placeholder="Paste the complete job description here — include responsibilities, requirements, and desired qualifications…",
            label_visibility="collapsed",
            key="jd_input",
        )
        if jd_text.strip():
            st.session_state.jd_text = jd_text.strip()

    st.markdown("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([2, 1.5, 2])

    with btn_col:
        ready = bool(
            st.session_state.resume_text
            and st.session_state.jd_text
            and st.session_state.api_key
        )
        if not ready:
            missing = []
            if not st.session_state.resume_text:  missing.append("resume")
            if not st.session_state.jd_text:       missing.append("job description")
            if not st.session_state.api_key:        missing.append("API key")
            st.info(f"Please provide: {', '.join(missing)}")

        if st.button("🚀 Analyze Resume", disabled=not ready, use_container_width=True):
            _run_analysis()


def _run_analysis():
    resume   = st.session_state.resume_text
    jd       = st.session_state.jd_text
    provider = st.session_state.model_provider
    api_key  = st.session_state.api_key

    progress = st.progress(0, text="🔍 Analyzing original resume…")
    try:
        progress.progress(15, text="📊 Calculating ATS score for original resume…")
        original_result = analyze_resume(resume, jd, provider, api_key)

        progress.progress(40, text="✍️ Generating optimized resume…")
        optimized = optimize_resume(
            resume, jd,
            original_result.get("missing_skills", []),
            provider, api_key,
        )

        progress.progress(70, text="📈 Analyzing optimized resume ATS score…")
        optimized_result = analyze_resume(optimized, jd, provider, api_key)

        progress.progress(95, text="✅ Finalising results…")

        st.session_state.analysis_result           = original_result
        st.session_state.optimized_analysis_result = optimized_result
        st.session_state.optimized_resume          = optimized
        st.session_state.analysis_complete         = True

        progress.progress(100, text="Done!")
        st.rerun()

    except Exception as e:
        progress.empty()
        st.error(f"❌ Analysis failed: {e}")
