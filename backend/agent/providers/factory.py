"""Factory for instantiating LLM Provider implementations.

Allows swapping between Gemini, Mock, and future LLM providers behind
a unified BaseLLMProvider interface.
"""

import logging
from typing import Optional

from backend.config import get_settings
from backend.agent.providers.base import BaseLLMProvider
from backend.services.gemini_service import get_gemini_model

from backend.agent.providers.mock_provider import MockLLMProvider

logger = logging.getLogger(__name__)


def get_llm_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseLLMProvider:
    """Return configured LLM provider instance.

    Args:
        provider_name: Optional explicit provider name ('gemini', 'mock').
        api_key: Optional explicit API key. If None, reads from LLM_API_KEY setting.
        model: Optional model name for Gemini (default 'gemini-2.5-flash').

    Returns:
        Instance conforming to BaseLLMProvider.
    """
    settings = get_settings()
    name = (provider_name or settings.llm_provider or "mock").lower().strip()
    key = api_key if api_key is not None else settings.llm_api_key

    # If Gemini is explicitly requested or key is present (and not explicitly forced mock)
    if name == "gemini" or (key and key.strip() and name != "mock"):
        if not key or not key.strip():
            logger.warning("Gemini provider requested but LLM_API_KEY is empty. Falling back to MockLLMProvider.")
            return MockLLMProvider()
        chosen_model = model or "gemini-1.5-flash"
        logger.info("Instantiating GeminiLLMProvider (model=%s)", chosen_model)
        try:
            return GeminiLLMProvider(api_key=key.strip(), model=chosen_model)
        except Exception as e:
            logger.exception("Failed to initialize GeminiLLMProvider: %s. Falling back to MockLLMProvider.", e)
            return MockLLMProvider()

    logger.info("Instantiating MockLLMProvider (provider=%s)", name)
    return MockLLMProvider()
