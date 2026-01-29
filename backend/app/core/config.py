"""
Application Configuration
"""
import os
from typing import List, Optional
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Application
    APP_NAME: str = "AI Companion"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_companion.db"

    # JWT Authentication
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LLM Providers (云端API - MiniMax + Kimi)
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_MODEL: str = "minimax-m2.1"
    MINIMAX_BASE_URL: str = "https://api.minimax.chat/v1/text/chatcompletion_v2"

    KIMI_API_KEY: Optional[str] = None
    KIMI_MODEL: str = "kimi-k2.5"
    KIMI_BASE_URL: str = "https://api.moonshot.cn/v1"

    DEFAULT_LLM_PROVIDER: str = "minimax"

    # Embedding Model
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh"
    EMBEDDING_API_KEY: Optional[str] = None

    # Qdrant Vector Database (可选，未安装时自动使用内存模式)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "ai_companion_memory"
    QDRANT_ENABLED: bool = False  # 设置为 True 启用 Qdrant

    # Neo4j Graph Database (可选，未安装时自动使用内存模式)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_password"
    NEO4J_ENABLED: bool = False  # 设置为 True 启用 Neo4j

    # Redis (optional)
    REDIS_URL: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8080"
    ])


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
