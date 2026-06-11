import streamlit as st
from components.sidebar import render_sidebar
from components.upload_section import render_upload_section
from components.analysis_dashboard import render_analysis_dashboard, render_optimized_analysis_dashboard
from components.optimized_resume import render_optimized_resume
from utils.session_state import initialize_session_state

st.set_page_config(
    page_title="ResumeAlign AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(current_dir, "assets", "styles.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

initialize_session_state()

st.markdown("""
<div class="main-header">
    <div class="header-eyebrow">✦ &nbsp; AI-Powered Resume Intelligence</div>
    <h1 class="header-title">ResumeAlign <span class="gold-text">AI</span></h1>
    <div class="header-divider"></div>
    <p class="header-subtitle">ATS Scoring · Skill Gap Analysis · Intelligent Optimization</p>
</div>
""", unsafe_allow_html=True)

render_sidebar()

if st.session_state.get("analysis_complete"):
    tab1, tab2, tab3 = st.tabs([
        "📋  Original Resume Score",
        "📈  Optimized Resume Score",
        "🎨  Resume Builder",
    ])
    with tab1:
        render_analysis_dashboard()
    with tab2:
        render_optimized_analysis_dashboard()
    with tab3:
        render_optimized_resume()
else:
    render_upload_section()
