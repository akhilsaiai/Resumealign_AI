import streamlit as st


def initialize_session_state():
    defaults = {
        "resume_text": "",
        "jd_text": "",
        "analysis_complete": False,
        "analysis_result": None,        # original resume analysis
        "optimized_analysis_result": None,  # optimized resume analysis
        "optimized_resume": "",
        "selected_template": "Classic Professional",
        "api_key": "",
        "model_provider": "Groq (Free)",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_analysis():
    st.session_state.analysis_complete = False
    st.session_state.analysis_result = None
    st.session_state.optimized_analysis_result = None
    st.session_state.optimized_resume = ""
    st.session_state.selected_template = "Classic Professional"
