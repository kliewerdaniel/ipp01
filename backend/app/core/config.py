from pydantic_settings import BaseSettings
from typing import List, Union, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "Interview Prep Platform"
    PROJECT_DESCRIPTION: str = "API for the Interview Prep Platform"
    PROJECT_VERSION: str = "0.1.0"
    
    # API settings
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")  # Change in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend local development
        "http://localhost:8000",  # Backend API
        "https://interviewprep.example.com",  # Production domain (update this)
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./interview_prep.db"
    )
    
    # Stripe
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4"  # Or other models like "gpt-3.5-turbo"
    
    # File storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
