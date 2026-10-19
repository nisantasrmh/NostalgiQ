"""Movie recommendations live test.

Steps:
1. Check /v2/insights limit handling for a single movie seed.
2. Search for movie seeds, call insights, print raw JSON of one result entity.
3. Apply era filter (1950-1975) and show top 10 movies.
"""

import asyncio
import json
import os
import sys
from typing import List, Tuple

# Ensure project root is on import path
project_root = os.path.abspath(os.path.join(__file__, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.qloo.client import QlooClient, normalize_name
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join("C:/Zzxxx Hackathon/memory-lane", ".env"))
API_KEY = os.getenv("QLOO_API_KEY")

BASE_URL = "https://hackathon.api.qloo.com"

async def fetch_insights_raw(seed_id: str, limit: int) -> Tuple[int, List[dict]]:
    import httpx
    async with httpx.AsyncClient(timeout=10.0, headers={"X-Api-Key": API_KEY}) as client:
        params = {
            "filter.type": "urn:entity:movie",
            "signal.interests.entities": seed_id,
            "limit": str(limit),
        }
        resp = await client.get(f"{BASE_URL}/v2/insights", params=params)
        payload = resp.json()
        entities = []
        results = payload.get("results")
        if isinstance(results, dict):
            entities = results.get("entities", [])
        elif isinstance(results, list):
            entities = results
        return len(entities), entities

async def main():
    client = QlooClient()
    try:
        # 1. Limit test with first movie seed (Sholay)
        # Find Sholay ID
        sholay_search = await client.search_entity("Sholay", kind="movie")
        if not sholay_search:
            print("No movie entity found for 'Sholay'")
            return
        sholay_id = sholay_search[0]["entity_id"]
        print("\n--- Limit parameter test (seed: Sholay) ---")
        for lim in [10, 20, 50]:
            count, _ = await fetch_insights_raw(sholay_id, lim)
            print(f"Requested limit {lim}: got {count} results")
        # Choose the largest that returned that many (or just report)

        # 2. Movie seeds search
        movie_seeds = ["Sholay", "Mughal-e-Azam", "Mother India"]
        seed_info = []
        for title in movie_seeds:
            res = await client.search_entity(title, kind="movie")
            if res:
                ent = res[0]
                seed_info.append({"id": ent["entity_id"], "name": ent["name"]})
                print(f"Seed '{title}' => {ent['name']} (ID: {ent['entity_id']})")
            else:
                print(f"WARNING: No movie entity found for seed '{title}'")

        # Fetch insights for each seed (use a generous limit, e.g., 100)
        print("\n--- Raw JSON of ONE result entity per seed ---")
        for seed in seed_info:
            _, entities = await fetch_insights_raw(seed["id"], 100)
            if entities:
                raw = json.dumps(entities[0], indent=2, ensure_ascii=False)
                print(f"\nSeed '{seed['name']}' first result JSON:\n{raw}\n")
                # Show which field holds the release year
                year = entities[0].get("properties", {}).get("start_year")
                print(f"Detected release year field: {year}\n")
            else:
                print(f"No insight results for seed '{seed['name']}'")

        # 3. Recommendations with era filter (1950-1975)
        seed_ids = [s["id"] for s in seed_info]
        seed_names = [s["name"] for s in seed_info]
        recs = await client.get_recommendations(
            signal_ids=seed_ids,
            subtype="urn:entity:movie",
            era_range=(1950, 1975),
            limit=100,
            seed_names=seed_names,
        )
        print("\n--- Top 10 movie recommendations (title | release year | linked_from | seed_count) ---")
        for rec in recs[:10]:
            title = rec.get("name") or ""
            year = rec.get("start_year") or ""
            linked = ", ".join(rec.get("linked_from", []))
            cnt = rec.get("seed_count", 0)
            print(f"{title} | {year} | {linked} | {cnt}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
