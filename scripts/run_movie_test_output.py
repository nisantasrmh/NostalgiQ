"""Movie test script that writes raw output to a file for inspection.
It performs:
1. Limit parameter test for /v2/insights using seed 'Sholay'.
2. Searches movie seeds, fetches insights, writes one raw entity JSON per seed.
3. Gets merged recommendations with era filter (1950-1975) and writes top 10.
"""

import asyncio
import json
import os
import sys
from typing import List, Tuple

project_root = os.path.abspath(os.path.join(__file__, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.qloo.client import QlooClient
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join("C:/Zzxxx Hackathon/memory-lane", ".env"))
API_KEY = os.getenv("QLOO_API_KEY")
BASE_URL = "https://hackathon.api.qloo.com"

OUTPUT_PATH = os.path.abspath(os.path.join("C:/Zzxxx Hackathon/memory-lane/scripts", "movie_test_output.txt"))

async def fetch_insights_raw(seed_id: str, limit: int) -> Tuple[int, List[dict]]:
    import httpx
    async with httpx.AsyncClient(timeout=15.0, headers={"X-Api-Key": API_KEY}) as client:
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
    lines = []
    try:
        # 1. Limit test for Sholay
        sholay_search = await client.search_entity("Sholay", kind="movie")
        if not sholay_search:
            lines.append("No movie entity found for 'Sholay' during limit test")
        else:
            sholay_id = sholay_search[0]["entity_id"]
            lines.append("--- Limit Parameter Test (seed: Sholay) ---")
            for lim in [10, 20, 50]:
                count, _ = await fetch_insights_raw(sholay_id, lim)
                lines.append(f"Requested limit {lim}: got {count} results")

        # 2. Movie seeds search and raw entity JSON
        movie_seeds = ["Sholay", "Mughal-e-Azam", "Mother India"]
        seed_info = []
        lines.append("\n--- Movie Seed Search Results ---")
        for title in movie_seeds:
            res = await client.search_entity(title, kind="movie")
            if res:
                ent = res[0]
                seed_info.append({"id": ent["entity_id"], "name": ent["name"]})
                lines.append(f"Seed '{title}' => {ent['name']} (ID: {ent['entity_id']})")
            else:
                lines.append(f"WARNING: No movie entity found for seed '{title}'")

        lines.append("\n--- Raw JSON of ONE result entity per seed (limit 100) ---")
        for seed in seed_info:
            _, entities = await fetch_insights_raw(seed["id"], 100)
            if entities:
                raw_json = json.dumps(entities[0], indent=2, ensure_ascii=False)
                lines.append(f"\nSeed '{seed['name']}' first result JSON:\n{raw_json}\n")
                # Identify release year field (usually properties.start_year)
                year = entities[0].get('properties', {}).get('start_year')
                lines.append(f"Detected release year field value: {year}\n")
            else:
                lines.append(f"No insight entities returned for seed '{seed['name']}'")

        # 3. Recommendations with era filter 1950-1975
        seed_ids = [s["id"] for s in seed_info]
        seed_names = [s["name"] for s in seed_info]
        recs = await client.get_recommendations(
            signal_ids=seed_ids,
            subtype="urn:entity:movie",
            era_range=(1950, 1975),
            limit=100,
            seed_names=seed_names,
        )
        lines.append("\n--- Top 10 movie recommendations (title | release year | linked_from | seed_count) ---")
        for rec in recs[:10]:
            title = rec.get('name') or ''
            year = rec.get('start_year') or ''
            linked = ', '.join(rec.get('linked_from', []))
            cnt = rec.get('seed_count', 0)
            lines.append(f"{title} | {year} | {linked} | {cnt}")
    finally:
        await client.close()

    # Write all gathered lines to output file
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == '__main__':
    asyncio.run(main())
