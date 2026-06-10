import requests
import os
import json
import sys
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

MOCK_RESUME = """
John Doe
Email: john.doe@example.com | Phone: +1-555-0199 | Location: San Francisco, CA

PROFESSIONAL SUMMARY
Highly skilled Software Engineer with 3 years of experience building scalable web applications. Proficient in Python, JavaScript, and database management.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, SQL
Frameworks & Libraries: Django, React, Flask
Databases: PostgreSQL, Redis

WORK EXPERIENCE
Software Engineer | Tech Solutions Inc. | Jan 2024 - Present
• Designed and developed RESTful APIs using Django Rest Framework, improving response times by 20%.
• Collaborated with frontend teams to implement responsive user interfaces in React.
• Optimized PostgreSQL query performance, reducing database latency by 15%.

Associate Engineer | CodeCorp | Jun 2023 - Dec 2023
• Maintained and enhanced internal tools written in Python and Flask.
• Wrote unit and integration tests to increase test coverage from 70% to 85%.

EDUCATION
B.S. in Computer Science | University of State | 2019 - 2023
"""

MOCK_JD = """
We are looking for a Software Engineer to join our development team. 
Key Responsibilities:
- Design, build, and maintain efficient, reusable, and reliable Python code.
- Develop front-end components using React.
- Integrate data storage solutions including PostgreSQL and Redis.
- Familiarity with FastAPI, Docker, and CI/CD pipelines is a plus.

Requirements:
- Strong experience with Python (Django, Flask, or FastAPI).
- Experience with React or modern frontend frameworks.
- Strong SQL and database optimization skills (PostgreSQL preferred).
"""

def test_health():
    print("Testing /api/health...")
    try:
        resp = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {resp.status_code}")
        print(resp.json())
        return resp.status_code == 200
    except Exception as e:
        print(f"Failed to connect to backend: {e}")
        return False

def test_parse():
    print("\nTesting /api/parse (File Upload)...")
    # Write a temporary txt file
    temp_file = "temp_test_resume.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(MOCK_RESUME.strip())
        
    try:
        with open(temp_file, "rb") as f:
            files = {"file": (temp_file, f, "text/plain")}
            resp = requests.post(f"{BASE_URL}/api/parse", files=files)
            print(f"Status: {resp.status_code}")
            result = resp.json()
            print(f"Extracted {result.get('word_count')} words.")
            print(f"Sample: {result.get('text')[:150]}...")
            return resp.status_code == 200
    except Exception as e:
        print(f"Error during parsing test: {e}")
        return False
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_analyze(api_key, provider):
    print("\nTesting /api/analyze...")
    payload = {
        "resume_text": MOCK_RESUME.strip(),
        "jd_text": MOCK_JD.strip(),
        "provider": provider,
        "api_key": api_key
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze", json=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            res = resp.json()
            print(f"ATS Score: {res.get('ats_score')} / 100 ({res.get('grade')})")
            print(f"Missing Skills: {res.get('missing_skills')}")
            return True
        else:
            print(resp.text)
            return False
    except Exception as e:
        print(f"Error during analysis test: {e}")
        return False

def test_optimize(api_key, provider):
    print("\nTesting /api/optimize...")
    payload = {
        "resume_text": MOCK_RESUME.strip(),
        "jd_text": MOCK_JD.strip(),
        "missing_skills": ["FastAPI", "Docker", "CI/CD"],
        "provider": provider,
        "api_key": api_key
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/optimize", json=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            res = resp.json()
            print(f"Optimized Resume length: {len(res.get('optimized_resume'))} chars")
            print(f"Sample:\n{res.get('optimized_resume')[:250]}...")
            return res.get("optimized_resume")
        else:
            print(resp.text)
            return None
    except Exception as e:
        print(f"Error during optimization test: {e}")
        return None

def test_export(optimized_text):
    if not optimized_text:
        print("Skipping export tests due to empty optimized resume text.")
        return
    
    print("\nTesting /api/export/docx...")
    try:
        resp = requests.post(f"{BASE_URL}/api/export/docx", json={"text": optimized_text})
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            with open("test_exported.docx", "wb") as f:
                f.write(resp.content)
            print("Successfully exported test_exported.docx")
            if os.path.exists("test_exported.docx"):
                os.remove("test_exported.docx")
        else:
            print(resp.text)
    except Exception as e:
        print(f"Error exporting docx: {e}")

    print("\nTesting /api/export/pdf...")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/export/pdf", 
            json={"text": optimized_text, "template_name": "Modern Minimal"}
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            with open("test_exported.pdf", "wb") as f:
                f.write(resp.content)
            print("Successfully exported test_exported.pdf")
            if os.path.exists("test_exported.pdf"):
                os.remove("test_exported.pdf")
        else:
            print(resp.text)
    except Exception as e:
        print(f"Error exporting pdf: {e}")

if __name__ == "__main__":
    print("ResumeAlign AI API CLI Test Client")
    print("=" * 40)
    
    # Read API Key from environment or CLI argument
    api_key = os.getenv("GROQ_API_KEY", "")
    provider = "Groq Llama 3.3"
    
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            provider = "OpenAI GPT-4o"
            
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        if len(sys.argv) > 2:
            provider = sys.argv[2]
            
    if not api_key:
        print("WARNING: No GROQ_API_KEY or OPENAI_API_KEY environment variable detected.")
        print("Tests requiring AI providers will fail unless api_key is supplied.")
        print("Usage: python backend/client_test.py <API_KEY> [PROVIDER_NAME]")
        print("Continuing with health & parsing tests only...\n")
        
    if not test_health():
        print("\nERROR: Could not contact backend server at http://localhost:8000.")
        print("Please ensure your server is running: uvicorn backend.main:app --reload")
        sys.exit(1)
        
    test_parse()
    
    if api_key:
        print(f"\nUsing provider: {provider}")
        test_analyze(api_key, provider)
        opt_text = test_optimize(api_key, provider)
        if opt_text:
            test_export(opt_text)
    else:
        print("\nSkipped AI-related tests (no API Key available).")
