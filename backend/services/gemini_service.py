"""Utility module for creating a Google Gemini GenerativeModel instance.
Ensures the model name is passed without the "models/" prefix, which is invalid for the v1beta API.
"""

from __future__ import annotations

import logging
from typing import Optional

from google import genai

logger = logging.getLogger(__name__)


def get_gemini_model(model_name: Optional[str] = None) -> genai.GenerativeModel:
    """Return a genai.GenerativeModel instance for the specified Gemini model.

    Args:
        model_name: Optional model identifier. If omitted or None,
            "gemini-1.5-flash" is used.

    The function strips any leading "models/" prefix to avoid 404 errors
    from the v1beta endpoint.
    """
    default_model = "gemini-1.5-flash"
    chosen = (model_name or default_model).strip()
    if chosen.startswith("models/"):
        logger.warning("Model name %s contains a 'models/' prefix; stripping it.", chosen)
        chosen = chosen[len("models/"):]
    logger.info("Creating Gemini GenerativeModel with name: %s", chosen)
    return genai.GenerativeModel(chosen)