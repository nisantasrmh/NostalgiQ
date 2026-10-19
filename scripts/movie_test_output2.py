"""Movie recommendation test script (raw output).

Steps:
1. Test /v2/insights limit parameter for seed 'Sholay' with limits 10,20,50.
2. Search movie seeds, fetch insights, write raw JSON of first entity per seed.
3. Get merged recommendations with era filter (1950-1975) and write top 10 movies.
"""

import asyncio
import json
import os
import sys
from typing import List, Tuple

# Ensure project root on path
project_root = os.path.abspath(os.path.join(__file__, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.qloo.client import QlooClient
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join("C:/Zzxxx Hackathon/memory-lane", ".env"))
API_KEY = os.getenv("QLOO_API_KEY")
BASE_URL = "https://hackathon.api.qloo.com"

OUTPUT_FILE = os.path.abspath(os.path.join("C:/Zzxxx Hackathon/memory-lane/scripts", "movie_test_output2.txt"))

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
    lines: List[str] = []
    try:
        # Step 1: limit test for Sholay
        sholay_res = await client.search_entity("Sholay", kind="movie")
        if not sholay_res:
            lines.append("Limit test: No movie entity found for 'Sholay'.")
        else:
            sholay_id = sholay_res[0]["entity_id"]
            lines.append("--- Limit Parameter Test (seed: Sholay) ---")
            for lim in [10, 20, 50]:
                count, _ = await fetch_insights_raw(sholay_id, lim)
                lines.append(f"Requested limit {lim}: got {count} results")

        # Step 2: movie seeds search and raw JSON
        movie_seeds = ["Sholay", "Mughal-e-Azam", "Mother India"]
        seed_info = []
        lines.append("\n--- Movie Seed Search ---")
        for title in movie_seeds:
            res = await client.search_entity(title, kind="movie")
            if res:
                ent = res[0]
                seed_info.append({"id": ent["entity_id"], "name": ent["name"]})
                lines.append(f"Seed '{title}' => {ent['name']} (ID: {ent['entity_id']})")
            else:
                lines.append(f"WARNING: No movie entity for seed '{title}'")

        lines.append("\n--- Raw JSON of ONE result entity per seed (limit 100) ---")
        for seed in seed_info:
            _, entities = await fetch_insights_raw(seed["id"], 100)
            if entities:
                raw = json.dumps(entities[0], indent=2, ensure_ascii=False)
                lines.append(f"\nSeed '{seed['name']}' first result JSON:\n{raw}\n")
                year = entities[0].get('properties', {}).get('start_year')
                lines.append(f"Detected release year field value: {year}\n")
            else:
                lines.append(f"No insight results for seed '{seed['name']}'")

        # Step 3: merged recommendations with era filter 1950-1975
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

    # Write to output file (utf-8)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == '__main__':
    asyncio.run(main())
