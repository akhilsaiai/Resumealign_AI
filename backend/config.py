import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TITLE: str = "ResumeAlign AI API"
    API_DESCRIPTION: str = "FastAPI backend for ATS scoring, resume parsing, and AI optimization."
    API_VERSION: str = "1.0.0"
    
    # API Keys (optional; can fall back to environment variables or request headers)
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
