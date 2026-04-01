from pydantic_settings import BaseSettings
from typing import Literal, Optional

class Settings(BaseSettings):
    # API Keys (server-side fallbacks; users can supply their own per-request)
    google_api_keys: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Provider defaults (overridable per-request)
    default_llm_provider: str = "gemini"
    default_embed_provider: str = "gemini"
    
    # Model names (change here to upgrade models, zero code change elsewhere)
    gemini_llm_model: str = "gemini-2.0-flash"
    gemini_embed_model: str = "models/text-embedding-004"
    openai_llm_model: str = "gpt-4o"
    openai_embed_model: str = "text-embedding-3-small"
    anthropic_llm_model: str = "claude-3-5-sonnet-20241022"
    
    # Pipeline config
    dedup_similarity_threshold: float = 0.85
    max_pdf_size_mb: int = 50
    job_ttl_seconds: int = 3600  # delete results after 1 hour
    
    # Storage
    storage_backend: Literal["local", "gcs"] = "local"
    local_storage_path: str = "/tmp/ddr_jobs"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
