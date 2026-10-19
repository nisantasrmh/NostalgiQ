"""Tool definitions for the Memory Lane tool-calling agent.

Defines callable interfaces for:
- search_entity: Querying cultural entities from the Qloo Taste Graph.
- get_recommendations: Retrieving taste correlations across music, film, and dining.
- adapt_for_health: Applying clinical dietary adaptation rules to culinary dishes.
"""

from typing import Any, Dict, List, Optional
import logging

from backend.agent.health_rules import adapt_dish_for_health
from backend.models.schemas import HealthAdaptation, HealthConstraints
from backend.qloo.base import BaseQlooClient

logger = logging.getLogger(__name__)


class AgentTools:
    """Encapsulates executable tools exposed to the agent reasoning loop."""

    def __init__(self, qloo_client: BaseQlooClient) -> None:
        """Initialize tools with the injected Qloo client implementation."""
        self.qloo_client = qloo_client

    async def search_entity(
        self,
        query: str,
        domain: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search the Qloo Taste Graph for cultural anchors."""
        logger.info("Tool called: search_entity(query=%r, domain=%r)", query, domain)
        return await self.qloo_client.search_entity(query=query, domain=domain, limit=limit)

    async def get_recommendations(
        self,
        seed_entity_ids: List[str],
        target_domain: str,
        era: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve correlated recommendations from Qloo Taste Graph."""
        logger.info(
            "Tool called: get_recommendations(seeds=%r, target_domain=%r, era=%r, region=%r)",
            seed_entity_ids,
            target_domain,
            era,
            region,
        )
        return await self.qloo_client.get_recommendations(
            seed_entity_ids=seed_entity_ids,
            target_domain=target_domain,
            era=era,
            region=region,
            limit=limit,
        )

    def adapt_for_health(
        self,
        dish_title: str,
        dish_description: str,
        constraints: HealthConstraints,
    ) -> HealthAdaptation:
        """Adapt a culinary dish according to clinical and texture constraints."""
        logger.info("Tool called: adapt_for_health(dish=%r)", dish_title)
        return adapt_dish_for_health(
            dish_title=dish_title,
            dish_description=dish_description,
            constraints=constraints,
        )
