"""
utils/ai_engine.py
Uses Groq (free, fast) with Llama 3.3 70B model.
Supports: resume analysis, optimized resume analysis, resume optimization.
"""
from __future__ import annotations
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

ANALYSIS_PROMPT = """You are an expert ATS resume analyst and career coach. Analyze the resume against the job description and respond ONLY with a valid JSON object — no markdown fences, no extra text.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Return this exact JSON schema:
{{
  "ats_score": <integer 0-100>,
  "match_percentage": <integer 0-100>,
  "grade": "<Excellent|Good|Fair|Poor>",
  "summary": "<2-3 sentence overall assessment>",
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "suggested_skills": ["skill1", "skill2"],
  "keywords_found": ["kw1", "kw2"],
  "keywords_missing": ["kw1", "kw2"],
  "section_scores": {{
    "Work Experience": <0-100>,
    "Skills": <0-100>,
    "Education": <0-100>,
    "Summary/Objective": <0-100>,
    "Formatting": <0-100>
  }},
  "improvements": [
    {{
      "priority": "<high|medium|low>",
      "section": "<section name>",
      "issue": "<short issue title>",
      "suggestion": "<actionable recommendation>"
    }}
  ],
  "strengths": ["<strength 1>", "<strength 2>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"]
}}"""

OPTIMIZE_PROMPT = """You are a professional resume writer and ATS optimization expert.
Rewrite the candidate's resume to be highly tailored to the provided job description.

ORIGINAL RESUME:
{resume}

TARGET JOB DESCRIPTION:
{jd}

IDENTIFIED MISSING SKILLS TO INCORPORATE (only if genuinely applicable):
{missing_skills}

RULES:
1. CRITICAL: Preserve the candidate's REAL name, contact details, job titles, company names, and dates exactly as they appear in the original resume. Do NOT invent or change any personal information.
2. Use strong action verbs and quantify achievements wherever possible.
3. Naturally incorporate missing keywords from the JD only if relevant to actual experience.
4. Structure sections in this order:
   CONTACT INFORMATION
   PROFESSIONAL SUMMARY
   TECHNICAL SKILLS
   WORK EXPERIENCE
   EDUCATION
   CERTIFICATIONS (only if present in original)
5. Each section header must be on its own line in ALL CAPS followed by a blank line.
6. For each job: Company Name | Job Title | Start Date - End Date on one line, then bullet points.
7. Use • for bullet points. Each bullet on its own line.
8. Keep contact info on separate lines: Name, then Email, then Phone, then Location, then LinkedIn.
9. Do NOT put multiple pieces of information on the same line unless they are the same field.
10. Skills should be grouped by category: Programming Languages: ..., Frameworks: ..., Tools: ...
11. Write a 3-4 sentence professional summary tailored to this specific role.
12. Optimize for ATS: no tables, no columns, no graphics.
13. CRITICAL SINGLE-PAGE CONSTRAINT: The optimized resume MUST fit on a single page. Keep the content extremely high-impact, tight, and concise. Avoid wordiness. Limit each job to a maximum of 3-4 highly relevant bullet points, and keep the professional summary to 2-3 sentences.

Output ONLY the resume text — no preamble, no explanation, no markdown."""


def _call_groq(api_key: str, prompt: str) -> str:
    try:
        from groq import Groq
        key = api_key or os.getenv("GROQ_API_KEY", "")
        if not key:
            raise ValueError("Groq API key not found. Add GROQ_API_KEY to your .env file.")
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4000,
        )
        return response.choices[0].message.content.strip()
    except ImportError:
        raise ImportError("Groq package not found. Run: pip install groq")


def _call_openai(api_key: str, prompt: str) -> str:
    try:
        from openai import OpenAI
        key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise ValueError("OpenAI API key not found.")
        client = OpenAI(api_key=key)
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except ImportError:
        raise ImportError("OpenAI package not found. Run: pip install openai")


def _call_ai(provider: str, api_key: str, prompt: str) -> str:
    if provider == "OpenAI GPT-4o":
        return _call_openai(api_key, prompt)
    else:
        return _call_groq(api_key, prompt)


def analyze_resume(resume_text: str, jd_text: str, provider: str, api_key: str) -> dict:
    prompt = ANALYSIS_PROMPT.format(resume=resume_text, jd=jd_text)
    raw = _call_ai(provider, api_key, prompt)
    
    # Extract only the JSON object boundaries to ignore conversational wrappers
    start_idx = raw.find("{")
    end_idx = raw.rfind("}")
    if start_idx != -1 and end_idx != -1:
        clean = raw[start_idx:end_idx+1].strip()
    else:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        
    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON.\n\nRaw snippet: {raw[:300]}\n\nError: {e}")


def optimize_resume(resume_text: str, jd_text: str, missing_skills: list[str], provider: str, api_key: str) -> str:
    skills_str = ", ".join(missing_skills) if missing_skills else "None identified"
    prompt = OPTIMIZE_PROMPT.format(resume=resume_text, jd=jd_text, missing_skills=skills_str)
    return _call_ai(provider, api_key, prompt)
