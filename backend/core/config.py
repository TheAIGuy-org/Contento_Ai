# ============================================================================
# FILE: backend/core/config.py
# ============================================================================

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """System configuration"""
    
    # API Keys
    GROQ_API_KEY: str
    TAVILY_API_KEY: str
    
    # Model Configuration
    DIRECTOR_MODEL: str = "llama-3.1-70b-versatile"
    ARCHITECT_MODEL: str = "llama-3.1-8b-instant"
    RESEARCH_MODEL: str = "llama-3.1-8b-instant"
    
    # System Parameters
    MAX_LOOP_ATTEMPTS: int = 3
    CREATIVE_THRESHOLD: float = 8.5
    COMPLIANCE_THRESHOLD: float = 100.0
    
    # Temperature Settings
    DIRECTOR_TEMPERATURE: float = 0.9
    ARCHITECT_TEMPERATURE: float = 0.7
    RESEARCH_TEMPERATURE: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
