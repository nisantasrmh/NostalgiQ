"""Mock Qloo Taste Graph Client.

Loads realistic offline mock data for music, film, and dining entities.
Every item returned by this mock client is guaranteed to have 'source': 'MOCK'.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from backend.qloo.base import BaseQlooClient

logger = logging.getLogger(__name__)

MOCK_DATA_DIR = Path(__file__).parent / "mock_data"


class MockQlooClient(BaseQlooClient):
    """Offline mock client simulating Qloo Taste Graph responses."""

    def __init__(self, mock_dir: Optional[Path] = None) -> None:
        """Initialize mock client and load local datasets."""
        self.mock_dir = mock_dir or MOCK_DATA_DIR
        self._music_data: List[Dict[str, Any]] = self._load_json("music.json")
        self._film_data: List[Dict[str, Any]] = self._load_json("film.json")
        self._dining_data: List[Dict[str, Any]] = self._load_json("dining.json")
        logger.info(
            "MockQlooClient initialized with %d music, %d film, %d dining items.",
            len(self._music_data),
            len(self._film_data),
            len(self._dining_data),
        )

    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        """Load and parse JSON file from mock data directory."""
        file_path = self.mock_dir / filename
        if not file_path.exists():
            logger.warning("Mock data file %s not found in %s", filename, self.mock_dir)
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Guarantee that every item has source: "MOCK"
                for item in data:
                    item["source"] = "MOCK"
                return data
        except Exception as e:
            logger.error("Failed to load mock data from %s: %s", file_path, e)
            return []

    def _get_dataset_for_domain(self, domain: Optional[str]) -> List[Dict[str, Any]]:
        """Retrieve dataset matching the requested domain or combine all."""
        if not domain:
            return self._music_data + self._film_data + self._dining_data
        dom = domain.lower()
        if dom == "music":
            return self._music_data
        elif dom in ("film", "tv", "movie"):
            return self._film_data
        elif dom in ("dining", "food", "meal"):
            return self._dining_data
        return self._music_data + self._film_data + self._dining_data

    async def search_entity(
        self,
        query: str,
        domain: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for entities matching query string in title, artist, or tags."""
        q = query.strip().lower()
        pool = self._get_dataset_for_domain(domain)
        matches = []

        for item in pool:
            title = str(item.get("title", "")).lower()
            creator = str(item.get("artist") or item.get("creator_or_artist", "")).lower()
            tags = [t.lower() for t in item.get("tags", [])]
            region = str(item.get("region", "")).lower()

            if q in title or q in creator or any(q in t for t in tags) or q in region:
                # Add copy with confirmed MOCK source
                match = dict(item)
                match["source"] = "MOCK"
                matches.append(match)

        # Fallback: if no direct match, return top pool items to ensure agent workflow continues
        if not matches:
            matches = [dict(item) for item in pool[:limit]]
            for m in matches:
                m["source"] = "MOCK"

        return matches[:limit]

    async def get_recommendations(
        self,
        seed_entity_ids: List[str],
        target_domain: str,
        era: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Return correlated mock recommendations matching domain, era, or region."""
        logger.debug(
            "MockQlooClient.get_recommendations called with seed_entity_ids=%r, target_domain=%r, era=%r, region=%r, limit=%r",
            seed_entity_ids,
            target_domain,
            era,
            region,
            limit,
        )
        pool = self._get_dataset_for_domain(target_domain)
        scored_items: List[tuple[int, Dict[str, Any]]] = []

        region_lower = (region or "").lower()
        era_lower = (era or "").lower()
        seed_set = set(seed_entity_ids or [])

        for item in pool:
            score = 1  # Base affinity
            # Check seed correlation
            item_correlated_seeds = set(item.get("correlated_seed_ids", []))
            if seed_set.intersection(item_correlated_seeds):
                score += 3

            # Check region affinity
            item_region = str(item.get("region", "")).lower()
            if region_lower and (region_lower in item_region or any(part in item_region for part in region_lower.split())):
                score += 2

            # Check era affinity
            item_era = str(item.get("era", "")).lower()
            if era_lower and (era_lower in item_era or "classic" in item_era):
                score += 2

            scored_item = dict(item)
            scored_item["source"] = "MOCK"
            scored_item["confidence_score"] = min(0.98, 0.70 + (score * 0.05))
            scored_items.append((score, scored_item))

        # Sort by score descending
        scored_items.sort(key=lambda x: x[0], reverse=True)
        results = [item for _, item in scored_items[:limit]]
        return results

    async def close(self) -> None:
        """No-op close for mock client to match interface."""
        return None
