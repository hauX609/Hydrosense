"""
Configuration settings for the FastAPI backend
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Bangladesh Flood Prediction API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:8080",
        "*",  # Allow all origins for Vercel deployment
    ]
    
    # Model paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MODEL_DIR: Path = BASE_DIR / "models"
    MODEL_PATH: Path = MODEL_DIR / "catboost_multi.cbm"
    MODEL_META_PATH: Path = MODEL_DIR / "model_meta.json"
    
    # Prediction thresholds
    LOW_RISK_THRESHOLD: float = 0.3
    MEDIUM_RISK_THRESHOLD: float = 0.6
    HIGH_RISK_THRESHOLD: float = 0.6
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
