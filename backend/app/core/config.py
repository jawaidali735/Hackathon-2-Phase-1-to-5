import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables.
    """

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # Authentication settings
    BETTER_AUTH_SECRET: str = os.getenv("BETTER_AUTH_SECRET", "dev-secret-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Application settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = APP_ENV == "development"

    # CORS settings
    CORS_ALLOWED_ORIGINS: List[str] = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")

    # API settings
    API_V1_STR: str = "/api/v1"

    # AI Chatbot settings (Phase 3) - Fallback order: Groq -> Gemini -> OpenAI
    _GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    _GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    _COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")  # Disabled - incompatible with strict mode
    _OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Use default API key if environment variable is not set or is empty
    GROQ_API_KEY: str = _GROQ_API_KEY if _GROQ_API_KEY else ""
    GEMINI_API_KEY: str = _GEMINI_API_KEY if _GEMINI_API_KEY else ""
    COHERE_API_KEY: str = _COHERE_API_KEY if _COHERE_API_KEY else ""
    # Don't use invalid OpenRouter key as OpenAI key - let it be empty to skip OpenAI fallback
    OPENAI_API_KEY: str = _OPENAI_API_KEY if _OPENAI_API_KEY and not _OPENAI_API_KEY.startswith("sk-or-") else ""

settings = Settings()