"""Factory for instantiating Qloo client implementations.

Swaps between RealQlooClient and MockQlooClient based on configuration flag (USE_MOCK_QLOO).
"""

import logging
from typing import Optional

from backend.config import get_settings
from backend.qloo.base import BaseQlooClient
from backend.qloo.client import QlooClient
from backend.qloo.mock_client import MockQlooClient

logger = logging.getLogger(__name__)


def get_qloo_client(use_mock: Optional[bool] = None) -> BaseQlooClient:
    """Return configured Qloo client instance.

    Args:
        use_mock: Optional explicit boolean override. If None, reads from USE_MOCK_QLOO setting.

    Returns:
        Instance of BaseQlooClient (either MockQlooClient or QlooClient).
    """
    settings = get_settings()
    should_use_mock = use_mock if use_mock is not None else settings.use_mock_qloo

    if should_use_mock:
        logger.info("Instantiating MockQlooClient (USE_MOCK_QLOO=True)")
        return MockQlooClient()
    else:
        logger.info("Instantiating production QlooClient (USE_MOCK_QLOO=False)")
        return QlooClient(
            api_key=settings.qloo_api_key,
            base_url=settings.qloo_api_base_url,
        )
