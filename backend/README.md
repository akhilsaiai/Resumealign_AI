# ResumeAlign AI Backend API 🚀

This is the production-ready FastAPI backend framework for **ResumeAlign AI**. It exposes all core capabilities—resume parsing, ATS scoring, AI optimization, and PDF/DOCX exporting—via a unified RESTful API.

---

## 🛠️ Installation & Setup

1. **Install Dependencies**  
   Ensure you install the updated requirements containing FastAPI, Uvicorn, and other dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**  
   Add your keys to a `.env` file in the root of the project:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start the FastAPI Server**  
   Run the following command from the `resumealign_ai/resumealign_ai` directory:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   The API will be available at http://localhost:8000.

---

## 🎨 Interactive API Documentation

Go to **http://localhost:8000/docs** in your browser to view a beautifully themed, interactive Swagger UI documentation. You can test all routes directly from your browser!

---

## 📋 API Endpoint Summary

### 1. Health Check
* **`GET /api/health`**  
  Checks if all services are operational.

### 2. Resume Text Parser
* **`POST /api/parse`**  
  Accepts a multipart file upload (`.pdf`, `.docx`, or `.txt`) and returns the parsed plain text.
  * **cURL Example**:
    ```bash
    curl -X POST "http://localhost:8000/api/parse" \
      -H "accept: application/json" \
      -H "Content-Type: multipart/form-data" \
      -F "file=@/path/to/resume.pdf"
    ```

### 3. ATS Resume Analyzer
* **`POST /api/analyze`**  
  Analyzes raw resume text against a job description. Returns scoring metrics, matched/missing skills, and prioritized improvements in JSON.
  * **JSON Body**:
    ```json
    {
      "resume_text": "...",
      "jd_text": "...",
      "provider": "Groq Llama 3.3",
      "api_key": "optional_override_key"
    }
    ```
  * **cURL Example**:
    ```bash
    curl -X POST "http://localhost:8000/api/analyze" \
      -H "Content-Type: application/json" \
      -d '{
        "resume_text": "Candidate details...",
        "jd_text": "Job requirements...",
        "provider": "Groq Llama 3.3"
      }'
    ```

### 4. Resume Optimizer
* **`POST /api/optimize`**  
  Generates an ATS-optimized, keyword-rich plain-text resume tailoring the candidate's experience to the JD.
  * **JSON Body**:
    ```json
    {
      "resume_text": "...",
      "jd_text": "...",
      "missing_skills": ["Docker", "Kubernetes"],
      "provider": "Groq Llama 3.3"
    }
    ```

### 5. Consolidated Pipeline
* **`POST /api/pipeline`**  
  A single form-based endpoint that extracts text from an uploaded file, analyzes it, optimizes it, and scores the optimized version in a single request.
  * **cURL Example**:
    ```bash
    curl -X POST "http://localhost:8000/api/pipeline" \
      -H "Content-Type: multipart/form-data" \
      -F "file=@/path/to/resume.pdf" \
      -F "jd_text=Looking for Python developer..." \
      -F "provider=Groq Llama 3.3"
    ```

### 6. Document Exporters
Generate formatted Word (`.docx`) or styled PDF documents.
* **`POST /api/export/docx`** (Returns file attachment stream)
* **`POST /api/export/pdf`** (Returns template-styled PDF stream)
  * **JSON Body (PDF)**:
    ```json
    {
      "text": "Optimized resume text content...",
      "template_name": "Modern Minimal"
    }
    ```
    *Available Templates: `Classic Professional`, `Modern Minimal`, `Executive Elite`, `Tech Focused`, `Creative Clean`.*

---

## 🧪 Running Local Integration Tests

We have included a CLI testing client to quickly test your setup. Run the server, then execute:
```bash
python backend/client_test.py
```
If you have a key configured in your `.env`, it will automatically test the complete pipeline including the AI agents and document exporters.
