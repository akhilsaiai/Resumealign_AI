# ResumeAlign AI 🎯

> Intelligent Resume Optimization Using Generative AI

ResumeAlign AI analyzes your resume against a job description and generates an ATS-optimized, keyword-rich resume tailored to the target role — powered by Google Gemini or OpenAI GPT-4o.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **ATS Scoring** | 0–100 score with letter grade (Excellent / Good / Fair / Poor) |
| 🎯 **Job Match %** | How well your resume aligns to the JD |
| 🔍 **Skill Gap Analysis** | Matched, missing & suggested skills |
| 🔑 **Keyword Optimization** | JD keywords found vs. missing |
| 📋 **Section Breakdown** | Scores for Experience, Skills, Education, Summary, Formatting |
| 🛠️ **Improvement Suggestions** | Prioritized, actionable recommendations |
| ✍️ **AI Resume Rewrite** | Full optimized resume in professional plain text |
| ⬇️ **Export** | Download as `.txt` or `.docx` |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **Google Gemini 1.5 Flash / OpenAI GPT-4o** — Generative AI
- **PyPDF2** — PDF text extraction
- **python-docx** — DOCX read/write
- **Pandas** — data utilities

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone <repo-url>
cd resumealign_ai
pip install -r requirements.txt
```

### 2. Get an API key

- **Google Gemini (recommended — free tier available)**  
  → https://aistudio.google.com/app/apikey

- **OpenAI GPT-4o**  
  → https://platform.openai.com/api-keys

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 📁 Project Structure

```
resumealign_ai/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Theme & server config
├── assets/
│   └── styles.css                  # Custom dark-mode CSS
├── components/
│   ├── sidebar.py                  # API config + how-it-works panel
│   ├── upload_section.py           # Resume upload & JD input
│   ├── analysis_dashboard.py       # Score rings, skill tags, charts
│   └── optimized_resume.py         # Resume preview + download
└── utils/
    ├── session_state.py            # Streamlit state management
    ├── file_parser.py              # PDF / DOCX / TXT extraction
    ├── ai_engine.py                # Gemini & OpenAI API calls
    └── export.py                   # .txt / .docx export
```

---

## 🔧 Configuration

All configuration is done through the **sidebar** at runtime:

1. Select your AI provider (Google Gemini or OpenAI GPT-4o)
2. Paste your API key (stored only in browser session, never persisted)
3. Upload resume + paste JD → click **Analyze Resume**

---

## 📌 Usage Tips

- **Best results**: paste the complete job description including responsibilities, requirements, and preferred qualifications.
- **Supported resume formats**: PDF, DOCX, TXT (plain text).
- **After optimization**: edit the resume directly in the text area before downloading — the AI output is a strong starting point, but your own voice and verified facts matter.
- **ATS tip**: submit as PDF for most applications; the DOCX download is useful for editing in Word.

---

## 🔐 Privacy

- Your resume and JD are sent directly to the AI provider you choose (Google or OpenAI) — they are not stored by this application.
- Your API key is held in browser session memory only and is never logged or transmitted beyond the AI provider's endpoint.

---

## 📄 License

MIT — free to use, modify, and distribute.
