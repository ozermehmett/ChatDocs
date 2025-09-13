import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from .env"""
    
    # App
    APP_NAME: str = os.getenv("APP_NAME", "ChatDocs")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/database.db")
    
    # FastAPI
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "localhost")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8080"))
    
    # Streamlit
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Embedding Service
    EMBEDDING_API_URL: str = os.getenv("EMBEDDING_API_URL", "http://localhost:8000")
    
    # ChromaDB
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "data/vector_stores")
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads")
    LOG_DIR: str = os.getenv("LOG_DIR", "data/logs")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        # Create directories if they don't exist
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.LOG_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)
        Path("data").mkdir(exist_ok=True)

# Global settings instance
settings = Settings()
