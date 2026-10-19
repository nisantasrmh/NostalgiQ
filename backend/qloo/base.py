"""Abstract base class interface for Qloo Taste Graph Client.

Both the mock client and the production Qloo API client must implement
this common interface so they can be seamlessly swapped via configuration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseQlooClient(ABC):
    """Abstract interface for querying the Qloo Taste Graph."""

    @abstractmethod
    async def search_entity(
        self,
        query: str,
        domain: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for cultural entities in the Qloo graph.

        Args:
            query: Name of artist, film, dish, cuisine, or cultural term.
            domain: Target domain ('music', 'film', 'dining') or None for cross-domain.
            limit: Maximum number of candidate entities to return.

        Returns:
            List of matching entity dictionaries with standardized fields.
        """
        pass

    @abstractmethod
    async def get_recommendations(
        self,
        seed_entity_ids: List[str],
        target_domain: str,
        era: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Query correlated recommendations across or within domains from seed entities.

        Args:
            seed_entity_ids: List of Qloo entity IDs that represent the elder's known tastes.
            target_domain: Domain to retrieve recommendations for ('music', 'film', 'dining').
            era: Historical decade filter (e.g. '1960s', '1970s').
            region: Cultural or geographic affinity filter (e.g. 'Maharashtra', 'Chicago').
            limit: Maximum number of recommendations to return.

        Returns:
            List of recommended entity dictionaries from the taste graph.
        """
        pass
