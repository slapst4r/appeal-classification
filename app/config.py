import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str = os.getenv("DB_URL", "sqlite+aiosqlite:///./test.db")
    embeddings_model: str = os.getenv("EMBEDDINGS_MODEL", "intfloat/multilingual-e5-base")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    llm_backend: str = os.getenv("LLM_BACKEND", "ollama")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma4:e4b ")

    class Config:
        env_file = ".env"


settings = Settings()