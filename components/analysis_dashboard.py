"""
components/analysis_dashboard.py
Shared dashboard renderer used for both Original and Optimized tabs.
"""
import streamlit as st


def _score_color(s: int) -> str:
    if s >= 80: return "#4ade80"
    if s >= 60: return "#c9a96e"
    if s >= 40: return "#fbbf24"
    return "#f87171"


def _grade_color(g: str) -> str:
    return {"Excellent":"#4ade80","Good":"#c9a96e","Fair":"#fbbf24","Poor":"#f87171"}.get(g,"#6b7589")


def _ring(score: int, label: str = "ATS SCORE"):
    color = _score_color(score)
    r = 72
    circ = 2 * 3.14159 * r
    dash = (score / 100) * circ
    grade_map = {range(80,101):"Excellent", range(60,80):"Good",
                 range(40,60):"Fair", range(0,40):"Poor"}
    grade = next((v for k,v in grade_map.items() if score in k), "Poor")
    gc = _grade_color(grade)
    st.markdown(f"""
    <div class="score-ring-container">
        <div class="score-ring">
            <svg width="170" height="170" viewBox="0 0 170 170">
                <circle cx="85" cy="85" r="{r}" fill="none"
                    stroke="rgba(255,255,255,0.05)" stroke-width="10"/>
                <circle cx="85" cy="85" r="{r}" fill="none"
                    stroke="{color}" stroke-width="10"
                    stroke-dasharray="{dash:.1f} {circ:.1f}"
                    stroke-linecap="round"/>
            </svg>
            <div class="score-value">
                <span class="score-number" style="color:{color}">{score}</span>
                <span class="score-label">{label}</span>
            </div>
        </div>
        <span class="score-grade" style="color:{gc}">{grade}</span>
    </div>
    """, unsafe_allow_html=True)


def _progress(label, value):
    c = _score_color(value)
    st.markdown(f"""
    <div class="progress-item">
        <div class="progress-header">
            <span>{label}</span>
            <span style="color:{c};font-weight:600">{value}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:{value}%;background:{c}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _tags(skills, style):
    if not skills:
        st.markdown("<span style='color:#6b7589;font-size:0.78rem'>None identified</span>", unsafe_allow_html=True)
        return
    tags = "".join(f'<span class="skill-tag {style}">{s}</span>' for s in skills)
    st.markdown(f'<div class="skill-tags">{tags}</div>', unsafe_allow_html=True)


def _improvements(items):
    for item in items:
        p    = item.get("priority","medium").lower()
        icon = {"high":"🔴","medium":"🟡","low":"🟢"}.get(p,"🔵")
        st.markdown(f"""
        <div class="improvement-item {p}">
            <div class="improvement-icon">{icon}</div>
            <div class="improvement-text">
                <strong>{item.get('section','')}: {item.get('issue','')}</strong><br>
                <span>{item.get('suggestion','')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_dashboard(result: dict, label: str = "ATS SCORE", badge_color: str = "#f87171", badge_text: str = "ORIGINAL"):
    """Reusable dashboard renderer for any analysis result dict."""
    if not result:
        st.warning("No analysis data available.")
        return

    ats         = result.get("ats_score", 0)
    match       = result.get("match_percentage", 0)
    grade       = result.get("grade", "N/A")
    summary     = result.get("summary", "")
    matched     = result.get("matched_skills", [])
    missing     = result.get("missing_skills", [])
    suggested   = result.get("suggested_skills", [])
    kw_found    = result.get("keywords_found", [])
    kw_missing  = result.get("keywords_missing", [])
    sections    = result.get("section_scores", {})
    improvements= result.get("improvements", [])
    strengths   = result.get("strengths", [])
    weaknesses  = result.get("weaknesses", [])

    # Badge
    st.markdown(f"""
    <div style="display:inline-flex;align-items:center;gap:0.5rem;
                background:rgba(0,0,0,0.3);border:1px solid {badge_color}33;
                padding:0.3rem 1rem;border-radius:100px;margin-bottom:1rem">
        <span style="width:7px;height:7px;border-radius:50%;background:{badge_color};display:inline-block"></span>
        <span style="font-size:0.65rem;font-weight:700;letter-spacing:0.2em;
                     text-transform:uppercase;color:{badge_color}">{badge_text} RESUME ANALYSIS</span>
    </div>
    """, unsafe_allow_html=True)

    # KPI strip
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-box">
            <div class="stat-num" style="color:{_score_color(ats)}">{ats}</div>
            <div class="stat-desc">ATS Score</div>
        </div>
        <div class="stat-box">
            <div class="stat-num" style="color:{_score_color(match)}">{match}%</div>
            <div class="stat-desc">Job Match</div>
        </div>
        <div class="stat-box">
            <div class="stat-num" style="color:{_grade_color(grade)}">{grade}</div>
            <div class="stat-desc">Overall Grade</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Score ring + sections
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        st.markdown('<div class="card"><div class="card-title">🎯 ATS Score</div>', unsafe_allow_html=True)
        _ring(ats, label)
        if summary:
            st.markdown(f"<p style='font-size:0.8rem;color:#6b7589;margin-top:0.8rem;line-height:1.65'>{summary}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card"><div class="card-title">📋 Section Breakdown</div>', unsafe_allow_html=True)
        for sec, val in sections.items():
            _progress(sec, val)
        st.markdown('</div>', unsafe_allow_html=True)

    # Skills
    s1, s2, s3 = st.columns(3, gap="medium")
    with s1:
        st.markdown(f'<div class="card"><div class="card-title">✅ Matched Skills ({len(matched)})</div>', unsafe_allow_html=True)
        _tags(matched, "matched"); st.markdown('</div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="card"><div class="card-title">❌ Missing Skills ({len(missing)})</div>', unsafe_allow_html=True)
        _tags(missing, "missing"); st.markdown('</div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="card"><div class="card-title">💡 Suggested ({len(suggested)})</div>', unsafe_allow_html=True)
        _tags(suggested, "suggested"); st.markdown('</div>', unsafe_allow_html=True)

    # Keywords
    k1, k2 = st.columns(2, gap="medium")
    with k1:
        st.markdown(f'<div class="card"><div class="card-title">🔑 Keywords Found ({len(kw_found)})</div>', unsafe_allow_html=True)
        _tags(kw_found, "keyword"); st.markdown('</div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="card"><div class="card-title">🔍 Keywords Missing ({len(kw_missing)})</div>', unsafe_allow_html=True)
        _tags(kw_missing, "missing"); st.markdown('</div>', unsafe_allow_html=True)

    # Strengths & Weaknesses
    sw1, sw2 = st.columns(2, gap="medium")
    with sw1:
        st.markdown('<div class="card"><div class="card-title">💪 Strengths</div>', unsafe_allow_html=True)
        for s in strengths:
            st.markdown(f"<div style='padding:0.35rem 0;font-size:0.82rem;color:#c8d0de;border-bottom:1px solid rgba(255,255,255,0.04)'>✦ &nbsp;{s}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with sw2:
        st.markdown('<div class="card"><div class="card-title">⚠️ Weaknesses</div>', unsafe_allow_html=True)
        for w in weaknesses:
            st.markdown(f"<div style='padding:0.35rem 0;font-size:0.82rem;color:#c8d0de;border-bottom:1px solid rgba(255,255,255,0.04)'>✦ &nbsp;{w}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Improvements
    if improvements:
        st.markdown('<div class="card"><div class="card-title">🛠️ Prioritized Improvements</div>', unsafe_allow_html=True)
        high   = [i for i in improvements if i.get("priority","").lower()=="high"]
        medium = [i for i in improvements if i.get("priority","").lower()=="medium"]
        low    = [i for i in improvements if i.get("priority","").lower()=="low"]
        for group in [high, medium, low]:
            _improvements(group)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Tab-level renderers ───────────────────────────────────────────────────────

def render_analysis_dashboard():
    """Tab 1 — Original resume analysis."""
    render_dashboard(
        st.session_state.get("analysis_result", {}),
        label="ATS SCORE",
        badge_color="#f87171",
        badge_text="ORIGINAL",
    )


def render_optimized_analysis_dashboard():
    """Tab 2 — Optimized resume analysis."""
    render_dashboard(
        st.session_state.get("optimized_analysis_result", {}),
        label="ATS SCORE",
        badge_color="#4ade80",
        badge_text="OPTIMIZED",
    )
