import streamlit as st
import os
from dotenv import load_dotenv
from utils.session_state import reset_analysis

load_dotenv()

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:0.5rem 0 1.4rem;border-bottom:1px solid rgba(201,169,110,0.12);margin-bottom:1.2rem">
            <div style="font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:700;
                        color:#f0f2f6;letter-spacing:-0.01em;">ResumeAlign <span style="color:#c9a96e">AI</span></div>
            <div style="font-size:0.68rem;color:#6b7589;margin-top:0.3rem;letter-spacing:0.1em;text-transform:uppercase">
                Intelligent Resume Optimization
            </div>
        </div>
        """, unsafe_allow_html=True)

        key_name = "GROQ_API_KEY"
        env_key = os.getenv(key_name, "")
        if not env_key:
            try:
                if key_name in st.secrets:
                    env_key = st.secrets[key_name]
            except Exception:
                pass
        st.session_state.api_key = env_key

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.7rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;color:#c9a96e;margin-bottom:0.6rem'>📋 &nbsp; How it works</div>", unsafe_allow_html=True)

        steps = [
            ("1", "Upload resume (PDF, DOCX, or TXT)"),
            ("2", "Paste the target job description"),
            ("3", "Click Analyze — AI scores your resume"),
            ("4", "View gaps, keywords & ATS score"),
            ("5", "See Before & After comparison"),
            ("6", "Download PDF / DOCX of optimized resume"),
        ]
        html = '<div class="step-list">'
        for num, text in steps:
            html += f'<div class="step-item"><div class="step-num">{num}</div><div class="step-text">{text}</div></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.get("analysis_complete"):
            if st.button("🔄 New Analysis", use_container_width=True):
                reset_analysis()
                st.rerun()

        st.markdown("""
        <div style="margin-top:2rem;text-align:center;padding-top:1.5rem;border-top:1px solid rgba(201,169,110,0.1)">
            <div style="font-size:0.65rem;color:#6b7589;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.3rem">
                Intelligent Engine
            </div>
            <div style="font-size:0.8rem;color:#f0f2f6;font-family:'Playfair Display', serif;font-style:italic">
                Designed by <span style="color:#c9a96e;font-weight:600;font-style:normal">Akhil</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
