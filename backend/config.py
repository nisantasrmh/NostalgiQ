"""Application configuration for Memory Lane.

Loads settings from environment variables with sensible defaults.
Secrets and API keys must never be hardcoded.
"""

from functools import lru_cache
from typing import Any, List
import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for Memory Lane backend service."""

    # Qloo Taste Graph Settings
    # Toggle between real API calls and offline mock dataset
    use_mock_qloo: bool = Field(
        default=True,
        validation_alias="USE_MOCK_QLOO",
        description="When true, uses mock Qloo client with realistic fake entities tagged source=MOCK.",
    )
    qloo_api_key: str = Field(
        default="",
        validation_alias="QLOO_API_KEY",
        description="Official Qloo API Key. Leave empty when USE_MOCK_QLOO is true.",
    )
    qloo_api_base_url: str = Field(
        default="https://api.qloo.com/v1",
        validation_alias="QLOO_API_BASE_URL",
        description="Base URL for Qloo Taste Graph endpoints.",
    )

    # LLM Provider Configuration
    llm_provider: str = Field(
        default="mock",
        validation_alias="LLM_PROVIDER",
        description="LLM provider name: 'mock', 'openai', 'anthropic', or 'gemini'.",
    )
    llm_api_key: str = Field(
        default="",
        validation_alias="LLM_API_KEY",
        description="API key for chosen LLM provider.",
    )

    # Server & Networking
    backend_host: str = Field(
        default="127.0.0.1",
        validation_alias="BACKEND_HOST",
        description="Host interface for FastAPI server.",
    )
    backend_port: int = Field(
        default=8000,
        validation_alias="BACKEND_PORT",
        description="Port for FastAPI server.",
    )
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
        validation_alias="CORS_ORIGINS",
        description="Allowed CORS origins as comma-separated URLs or JSON list.",
    )

    @property
    def parsed_cors_origins(self) -> List[str]:
        """Parse cors_origins into a list of origin strings."""
        val = self.cors_origins.strip()
        if val.startswith("[") and val.endswith("]"):
            import json
            try:
                return json.loads(val)
            except Exception:
                pass
        return [i.strip() for i in val.split(",") if i.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached singleton instance of application settings."""
    return Settings()


# Convenience global instance
settings = get_settings()
