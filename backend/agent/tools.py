"""Tool definitions for the Memory Lane tool-calling agent.

Defines callable interfaces for:
- search_entity: Querying cultural entities from the Qloo Taste Graph.
- get_recommendations: Retrieving taste correlations across music, film, and dining.
- adapt_for_health: Applying clinical dietary adaptation rules to culinary dishes.
"""

from typing import Any, Dict, List, Optional, Union
import logging

from backend.agent.health_rules import adapt_dish_for_health
from backend.models.schemas import (
    DietaryConstraint,
    HealthAdaptation,
    HealthConstraints,
    TextureRequirement,
)
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
        """Search the Qloo Taste Graph for cultural anchors (music artists, film titles, traditional dishes).

        Args:
            query: Name of artist, film, dish, cuisine, or cultural term.
            domain: Target domain ('music', 'film', 'dining') or None for cross-domain search.
            limit: Maximum number of candidate entities to return (default 5).

        Returns:
            List of matching entity dictionaries from the Qloo Taste Graph.
        """
        logger.info("Tool called: search_entity(query=%r, domain=%r, limit=%r)", query, domain, limit)
        return await self.qloo_client.search_entity(query=query, domain=domain, limit=limit)

    async def get_recommendations(
        self,
        seed_entity_ids: List[str],
        target_domain: str,
        era: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Query correlated recommendations across or within domains from seed entities in Qloo Taste Graph.

        Args:
            seed_entity_ids: Seed entity IDs representing the elder's known tastes or cultural anchors.
            target_domain: Domain to retrieve recommendations for ('music', 'film', 'dining').
            era: Historical decade filter (e.g. '1960s', '1970s').
            region: Cultural or geographic affinity filter (e.g. 'Maharashtra', 'Chicago').
            limit: Maximum number of recommendations to return (default 5).

        Returns:
            List of correlated entity dictionaries with confidence scores and provenance.
        """
        logger.info(
            "Tool called: get_recommendations(seeds=%r, target_domain=%r, era=%r, region=%r, limit=%r)",
            seed_entity_ids,
            target_domain,
            era,
            region,
            limit,
        )
        # Call the Qloo client using the unified BaseQlooClient signature and capture the raw response for debugging
        recommendations = await self.qloo_client.get_recommendations(
            seed_entity_ids=seed_entity_ids,
            target_domain=target_domain,
            era=era,
            region=region,
            limit=limit,
        )
        logger.debug(
            "Qloo get_recommendations returned %d items: %s",
            len(recommendations),
            recommendations[:3],
        )
        return recommendations

    def adapt_for_health(
        self,
        dish_title: str,
        dish_description: str,
        constraints: Optional[Union[HealthConstraints, Dict[str, Any]]] = None,
        texture_requirement: Optional[str] = None,
        dietary_restrictions: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Apply clinical dietary adaptation rules to traditional cultural recipes for patient safety.

        Args:
            dish_title: Name of the traditional cultural dish to adapt.
            dish_description: Description or traditional preparation of the dish.
            constraints: Optional HealthConstraints object or dictionary of constraints.
            texture_requirement: Swallowing/texture requirement ('normal', 'soft_food', 'minced_moist', 'puree').
            dietary_restrictions: Dietary guidelines list (e.g. ['diabetic_friendly', 'low_sodium']).
            allergies: Strict allergen exclusions (e.g. ['peanuts', 'shellfish']).

        Returns:
            Dictionary containing adapted dish title, texture instructions, safe substitutions, and addressed constraints.
        """
        logger.info("Tool called: adapt_for_health(dish=%r)", dish_title)

        # Parse or construct HealthConstraints
        resolved_constraints: HealthConstraints
        if isinstance(constraints, HealthConstraints):
            resolved_constraints = constraints
        elif isinstance(constraints, dict):
            resolved_constraints = HealthConstraints(**constraints)
        else:
            # Build from explicit kwargs
            tex = TextureRequirement.NORMAL
            if texture_requirement:
                try:
                    tex = TextureRequirement(texture_requirement.lower())
                except ValueError:
                    tex = TextureRequirement.SOFT_FOOD

            diet_list = []
            if dietary_restrictions:
                for r in dietary_restrictions:
                    try:
                        diet_list.append(DietaryConstraint(r.lower()))
                    except ValueError:
                        pass

            resolved_constraints = HealthConstraints(
                texture_requirement=tex,
                dietary_restrictions=diet_list,
                allergies=allergies or [],
            )

        adaptation = adapt_dish_for_health(
            dish_title=dish_title,
            dish_description=dish_description,
            constraints=resolved_constraints,
        )
        return adaptation.model_dump()


