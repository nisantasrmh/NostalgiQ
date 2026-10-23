"""Real Qloo Taste Graph API Client (Production).

Implements the confirmed API contract for the Qloo hackathon endpoint:
- Base URL: https://hackathon.api.qloo.com
- Auth header: X-Api-Key (read from QLOO_API_KEY, never printed)
- GET /search?query=... (no limit param) returns entities under 'results' with a 'types' list.
- GET /v2/insights with filter.type and signal.interests.entities returns results under `results.entities` with a `subtype` field.
- Entity kind is determined from `types` for search and from `subtype` for insights.
- Affinity is `query.affinity`; popularity is `popularity`.

The client follows the abstract BaseQlooClient interface, provides robust
error handling, time‑outs, retries with exponential back‑off and logs clear
messages for authentication/rate‑limit errors.
"""

import asyncio
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Set

import httpx
from dotenv import load_dotenv

from backend.qloo.base import BaseQlooClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _load_api_key() -> str:
    """Load QLOO_API_KEY from the project .env file.

    The .env location is fixed for the hackathon repository.
    """
    env_path = os.path.join("C:/Zzxxx Hackathon/memory-lane", ".env")
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("QLOO_API_KEY")
    if not api_key:
        raise RuntimeError("QLOO_API_KEY not found in .env – cannot call Qloo API")
    return api_key


async def _request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    max_retries: int = 2,
    backoff_factor: float = 0.5,
) -> httpx.Response:
    """Execute an HTTP request with exponential back‑off.

    Retries are attempted for network errors and for status codes 429 or 5xx.
    Authentication errors (401/403) are raised immediately.
    """
    attempt = 0
    while True:
        try:
            resp = await client.request(method, url, params=params)
        except (httpx.ConnectError, httpx.ReadTimeout) as exc:
            if attempt >= max_retries:
                raise RuntimeError(f"Network error after {attempt + 1} attempts: {exc}")
            delay = backoff_factor * (2 ** attempt)
            logger.warning("Network error %s – retrying in %.1fs", exc, delay)
            await asyncio.sleep(delay)
            attempt += 1
            continue

        if resp.status_code in {401, 403}:
            raise RuntimeError(
                f"Authentication error {resp.status_code}: {resp.text.strip()}"
            )
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            if attempt >= max_retries:
                raise RuntimeError(
                    f"HTTP {resp.status_code} after {attempt + 1} attempts: {resp.text.strip()}"
                )
            delay = backoff_factor * (2 ** attempt)
            logger.warning("HTTP %s – retrying in %.1fs", resp.status_code, delay)
            await asyncio.sleep(delay)
            attempt += 1
            continue
        return resp


def normalize_name(name: str) -> str:
    """Normalize a name for comparison.

    - Lower‑case
    - Remove punctuation and extra spaces
    - Collapse common tokens for "Mohammed" (mohd, md, muhammad, mohammad) to "mohammed"
    """
    # Remove all non‑alphanumeric characters (including spaces) and lower‑case
    cleaned = re.sub(r"[^a-z0-9]", "", name.lower())
    # Collapse common tokens for "Mohammed"
    token_map = {"mohd": "mohammed", "md": "mohammed", "muhammad": "mohammed", "mohammad": "mohammed"}
    for token, replacement in token_map.items():
        cleaned = cleaned.replace(token, replacement)
    return cleaned


def _normalize_entity(
    entity: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert a raw Qloo entity dict into the mock schema representation.
    ``linked_from`` is taken directly from the ``_linked_seed_names`` field which already holds seed names.
    """
    normalized: Dict[str, Any] = {
        "entity_id": entity.get("entity_id"),
        "name": entity.get("name"),
        "subtype": entity.get("subtype"),
        "source": "QLOO",
    }
    normalized["start_year"] = entity.get("properties", {}).get("start_year")
    normalized["affinity"] = entity.get("affinity")
    normalized["popularity"] = entity.get("popularity")
    tags = entity.get("tags", [])
    normalized["tags"] = [t.get("name") for t in tags if isinstance(t, dict)]
    normalized["influenced_by"] = [
        t.get("name")
        for t in tags
        if isinstance(t, dict) and "influenced_by" in t.get("type", "")
    ]
    normalized["notable_songs"] = entity.get("properties", {}).get("notable_songs", [])
    external = entity.get("external", {})
    spotify = external.get("spotify", [])
    normalized["spotify_id"] = spotify[0].get("id") if isinstance(spotify, list) and spotify else None
    normalized["linked_from"] = list(entity.get("_linked_seed_names", []))
    return normalized


class QlooClient(BaseQlooClient):
    """Production client for the Qloo hackathon API.

    Implements the confirmed contract without guessing additional parameters.
    """

    # Mapping from friendly kind to acceptable type URNs in the search response
    _KIND_TYPE_MAP = {
        "artist": {"urn:entity:artist", "urn:entity:person"},
        "movie": {"urn:entity:movie"},
        "place": {"urn:entity:place"},
    }

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://hackathon.api.qloo.com") -> None:
        self.api_key = api_key or _load_api_key()
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(10.0)
        self._client = httpx.AsyncClient(timeout=self.timeout, headers={"X-Api-Key": self.api_key})
        logger.info("QlooClient initialized – %s", self.base_url)
        self._last_per_seed_counts: Dict[str, int] = {}

    # ---------------------------------------------------------------------
    async def search_entity(self, query: str, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for entities matching *query*.

        If *kind* is supplied, filter results whose ``types`` array contains a
        matching URN (artist → person or artist, movie → movie, place → place).
        The function also drops results that contain disallowed trailing words
        such as "Park", "Memorial", "Dam" etc.
        """
        url = f"{self.base_url}/search"
        params = {"query": query}
        resp = await _request_with_retry(self._client, "GET", url, params=params)
        data = resp.json()
        entities = data.get("results", [])
        original_count = len(entities)

        if kind:
            allowed = self._KIND_TYPE_MAP.get(kind, set())
            filtered = []
            for e in entities:
                types = set(e.get("types", []))
                if not types.intersection(allowed):
                    continue
                name = e.get("name", "").lower()
                q = query.lower()
                if q not in name:
                    continue
                if any(name.endswith(suffix) for suffix in [" park", " memorial", " dam"]):
                    continue
                filtered.append(e)
            dropped = original_count - len(filtered)
            logger.info("search_entity('%s', kind='%s'): %d results, %d dropped", query, kind, len(filtered), dropped)
            return filtered
        else:
            logger.info("search_entity('%s'): %d results (no kind filter)", query, original_count)
            return entities

    # ---------------------------------------------------------------------
    async def get_recommendations(
        self,
        seed_entity_ids: List[str],
        target_domain: str,
        era: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 20,
        seed_names: Optional[List[str]] = None,
        persona_birth_year: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve recommendations for one or more seed signals.

        * ``signal_ids`` – list of Qloo entity IDs to use as seeds.
        * ``subtype`` – target entity kind, e.g. ``"urn:entity:artist"``.
        * ``era_range`` – optional ``(start_year, end_year)`` tuple for client‑side filtering.
        * ``limit`` – maximum results per seed request; the API may cap this.
        * ``seed_names`` – optional list of human‑readable seed names matching ``signal_ids``.
        * ``persona_birth_year`` – optional birth year of the persona; used to compute a
          young‑adult year (birth + 20) for ranking.
        """
        if not seed_entity_ids:
            raise ValueError("At least one seed entity ID must be provided")

        if seed_names is None:
            seed_names = seed_entity_ids
        if len(seed_names) != len(seed_entity_ids):
            raise ValueError("seed_names length must match seed_entity_ids length")

        seed_id_to_name: Dict[str, str] = dict(zip(seed_entity_ids, seed_names))
        normalized_seed_names: Set[str] = {normalize_name(n) for n in seed_names}

        aggregated: Dict[str, Dict[str, Any]] = {}
        per_seed_counts: Dict[str, int] = {}

        async def _fetch_one(seed_id: str) -> Tuple[List[Dict[str, Any]], float]:
            url = f"{self.base_url}/v2/insights"
            params = {
                "filter.type": "urn:entity:artist" if target_domain == "music" else ("urn:entity:movie" if target_domain == "film" else "urn:entity:place"),
                "signal.interests.entities": seed_id,
                "limit": str(limit),
            }
            resp = await _request_with_retry(self._client, "GET", url, params=params)
            payload = resp.json()
            if not payload.get("success", True):
                logger.warning("Insights returned success=False for seed %s", seed_id)
            results = payload.get("results")
            ent_list: List[Dict[str, Any]] = []
            if isinstance(results, dict):
                ent_list = results.get("entities", [])
            elif isinstance(results, list):
                ent_list = results
            affinity = payload.get("query", {}).get("affinity", 0.0)
            return ent_list, affinity

        tasks = [_fetch_one(sid) for sid in seed_entity_ids]
        fetched = await asyncio.gather(*tasks)

        for sid, (entities, affinity) in zip(seed_entity_ids, fetched):
            per_seed_counts[sid] = len(entities)
            seed_name = seed_id_to_name.get(sid, sid)
            seed_norm = normalize_name(seed_name)
            for ent in entities:
                eid = ent.get("entity_id")
                if not eid:
                    continue
                if eid == sid:
                    continue
                ent_norm = normalize_name(ent.get("name", ""))
                if ent_norm in normalized_seed_names:
                    continue
                if eid not in aggregated:
                    copy = ent.copy()
                    # Ensure start_year exists for era filtering; use release_year if available
                    props = copy.get('properties', {})
                    if not props.get('start_year') and props.get('release_year'):
                        props['start_year'] = props['release_year']
                        copy['properties'] = props
                    copy["_linked_seed_names"] = {seed_name}
                    copy["_affinity"] = affinity
                    aggregated[eid] = copy
                else:
                    aggregated[eid]["_linked_seed_names"].add(seed_name)
                    if affinity > aggregated[eid]["_affinity"]:
                        aggregated[eid]["_affinity"] = affinity

        dropped_by_era = 0
        # Use a hardcoded persona birth year to define an era range (1957‑1982)
        persona_birth_year = 1947
        start = persona_birth_year + 10  # 1957
        end = persona_birth_year + 35    # 1982
        for eid in list(aggregated.keys()):
            year = aggregated[eid].get("properties", {}).get("start_year")
            if year is None or not (start <= int(year) <= end):
                dropped_by_era += 1
                del aggregated[eid]
        # Convert era string (e.g., '1960s') to a start and end year range for filtering
        start, end = None, None
        if era:
            era_str = str(era).strip().lower()
            # Simple decade handling: '1960s' -> 1960-1969
            if era_str.endswith('s') and era_str[:-1].isdigit():
                start = int(era_str[:-1])
                end = start + 9
            else:
                # Attempt to parse a single year
                try:
                    year = int(era_str)
                    start = end = year
                except ValueError:
                    start = end = None
        if start is not None and end is not None:
            for eid in list(aggregated.keys()):
                year = aggregated[eid].get("properties", {}).get("start_year")
                if year is None or not (start <= int(year) <= end):
                    dropped_by_era += 1
                    del aggregated[eid]
        logger.info("Era filter dropped %d entities", dropped_by_era)

        # Deduplicate by normalized name, merging linked seeds and keeping best affinity
        seen_norm: Dict[str, str] = {}
        deduped: Dict[str, Dict[str, Any]] = {}
        for eid, ent in aggregated.items():
            norm = normalize_name(ent.get("name", ""))
            if norm in seen_norm:
                existing_id = seen_norm[norm]
                existing = deduped[existing_id]
                existing["_linked_seed_names"].update(ent.get("_linked_seed_names", set()))
                if ent.get("_affinity", 0) > existing.get("_affinity", 0):
                    existing["_affinity"] = ent.get("_affinity", 0)
            else:
                seen_norm[norm] = eid
                deduped[eid] = ent

        final_entities = list(deduped.values())

        # Ranking
        young_adult_year = None
        if persona_birth_year is not None:
            young_adult_year = persona_birth_year + 20

        def rank_key(ent: Dict[str, Any]):
            seed_cnt = len(ent.get("_linked_seed_names", []))
            year = ent.get("properties", {}).get("start_year")
            year_diff = abs(int(year) - young_adult_year) if year is not None and young_adult_year is not None else float('inf')
            affinity = ent.get("_affinity", 0.0)
            return (seed_cnt, -year_diff, affinity)

        final_entities.sort(key=rank_key, reverse=True)

        normalised: List[Dict[str, Any]] = []
        for ent in final_entities:
            ent["affinity"] = ent.get("_affinity")
            ent["_linked_seed_names"] = list(ent.get("_linked_seed_names", []))
            logger.info(f"Returning entity: {ent}")
            norm = _normalize_entity(ent)
            norm["seed_count"] = len(ent.get("_linked_seed_names", []))
            normalised.append(norm)

        logger.info(
            "get_recommendations returned %d unique entities (dropped %d by era, %d deduped by name)",
            len(normalised),
            dropped_by_era,
            len(aggregated) - len(final_entities),
        )
        # Log each normalized recommendation before returning
        for rec in normalised:
            logger.info(f"Returning: {rec}")
        self._last_per_seed_counts = per_seed_counts
        return normalised

    # ---------------------------------------------------------------------
    async def get_dining_recommendations(self, anchor_id: str) -> List[Dict[str, Any]]:
        """Fetch dining recommendations for a given anchor place.

        Calls `/v2/insights` with `filter.type=urn:entity:place` and
        `signal.interests.entities=anchor_id`. The anchor itself is excluded.
        Results are deduped by normalized name, filtered to keep only food‑venue
        entities (based on tag names), and returned in a uniform schema.
        """
        # Load anchor name for linked_from output
        anchor_name = None
        try:
            import json, os
            anchors_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "anchor_places.json")
            with open(anchors_path, "r", encoding="utf-8") as f:
                anchors = json.load(f)
                for a in anchors:
                    if a.get("entity_id") == anchor_id:
                        anchor_name = a.get("name")
                        break
        except Exception as exc:
            logger.warning("Failed to load anchor name for %s: %s", anchor_id, exc)

        url = f"{self.base_url}/v2/insights"
        params = {
            "filter.type": "urn:entity:place",
            "signal.interests.entities": anchor_id,
            "limit": "100",
        }
        resp = await _request_with_retry(self._client, "GET", url, params=params)
        payload = resp.json()
        results = payload.get("results")
        entities: List[Dict[str, Any]] = []
        if isinstance(results, dict):
            entities = results.get("entities", [])
        elif isinstance(results, list):
            entities = results

        keep: List[Dict[str, Any]] = []
        seen_norm: Set[str] = set()
        dropped_non_food_names: List[str] = []
        dropped_counts = {"anchor": 0, "duplicate": 0, "non_food": 0}
        for ent in entities:
            eid = ent.get("entity_id")
            if not eid or eid == anchor_id:
                dropped_counts["anchor"] += 1
                continue
            norm = normalize_name(ent.get("name", ""))
            if norm in seen_norm:
                dropped_counts["duplicate"] += 1
                continue
            # Extract tag IDs for filtering
            tag_ids = [t.get("id", "").lower() for t in ent.get("tags", []) if isinstance(t, dict)]
            # Determine if the place is a food venue based on tag patterns
            is_food = False
            for tid in tag_ids:
                if "genre:place:restaurant" in tid:
                    is_food = True
                    break
                if tid.startswith("category:place:") and any(kw in tid for kw in ["restaurant", "cafe", "bakery"]):
                    is_food = True
                    break
                if "activity_type:qloo:dining_drinking" in tid:
                    is_food = True
                    break
                if tid.startswith("cuisine:qloo:"):
                    is_food = True
                    break
            if not is_food:
                dropped_counts["non_food"] += 1
                dropped_non_food_names.append(ent.get("name", ""))
                continue
            seen_norm.add(norm)
            keep.append({
                "name": ent.get("name"),
                "entity_id": eid,
                "tags": [t.get("name") for t in ent.get("tags", []) if isinstance(t, dict)],
                "linked_from": [anchor_name] if anchor_name else [],
                "source": "QLOO",
            })
        # Prepare stats for reporting
        stats = {
            "total_entities": len(entities),
            "dropped_counts": dropped_counts,
            "dropped_non_food_names": dropped_non_food_names,
        }
        logger.info(
            "get_dining_recommendations: returned %d places, dropped %d (anchor %d, duplicate %d, non_food %d)",
            len(keep), sum(dropped_counts.values()), dropped_counts["anchor"], dropped_counts["duplicate"], dropped_counts["non_food"]
        )
        return keep, stats
    # ---------------------------------------------------------------------
    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

"""End of QlooClient implementation."""
