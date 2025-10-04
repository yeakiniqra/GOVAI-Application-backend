from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings and environment variables"""
    
    HF_TOKEN: str
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # API settings
    API_TITLE: str = "GovAI Bangladesh API"
    API_DESCRIPTION: str = "AI-powered government information assistant for Bangladesh"
    API_VERSION: str = "1.0.0"
    
    # AI Model settings
    AI_MODEL: str = "openai/gpt-oss-120b"
    AI_PROVIDER: str = "fireworks-ai"
    MAX_TOKENS: int = 3000
    TEMPERATURE: float = 0.2
    
    # Search settings
    SEARCH_MAX_RESULTS: int = 6
    SEARCH_TIMEOUT: int = 10
    
    # LangChain settings
    TAVILY_API_KEY: Optional[str] = None
    SERPAPI_API_KEY: Optional[str] = None
    
    # Admin Authentication
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    SECRET_KEY: str = "admin"
    SESSION_EXPIRE_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()