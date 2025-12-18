"""
Configuration module for RAG-Anything MCP Server
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class APIConfig(BaseModel):
    """API configuration"""
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL"))
    azure_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY"))
    azure_endpoint: Optional[str] = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))


class ModelConfig(BaseModel):
    """Model configuration"""
    llm_model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    vision_model: str = Field(default_factory=lambda: os.getenv("VISION_MODEL", "gpt-4o"))
    embedding_model: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"))
    embedding_dim: int = Field(default_factory=lambda: int(os.getenv("EMBEDDING_DIM", "3072")))


class StorageConfig(BaseModel):
    """Storage configuration"""
    rag_storage_dir: Path = Field(default_factory=lambda: Path(os.getenv("RAG_STORAGE_DIR", "./rag_storage")))
    upload_dir: Path = Field(default_factory=lambda: Path(os.getenv("UPLOAD_DIR", "./uploads")))
    max_file_size: int = Field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", "100")))  # MB

    def __init__(self, **data):
        super().__init__(**data)
        # Create directories if they don't exist
        self.rag_storage_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


class ServerConfig(BaseModel):
    """Server configuration"""
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    max_concurrent_files: int = Field(default_factory=lambda: int(os.getenv("MAX_CONCURRENT_FILES", "3")))


class Config(BaseModel):
    """Main configuration"""
    api: APIConfig = Field(default_factory=APIConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment"""
        return cls()

    def validate_api_keys(self) -> bool:
        """Validate that required API keys are present"""
        if not self.api.openai_api_key and not self.api.azure_api_key:
            return False
        return True
