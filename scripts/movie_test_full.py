"""Movie insights and recommendations test.

Steps:
1. Resolve movie seed IDs (Sholay, Mughal-e-Azam, Mother India) using a single search per seed.
2. Fetch a raw insights response for the Sholay seed, keep the first two entities, and write to
   docs/qloo_samples/movie_insights_sample.json.
3. Print the first 60 lines of that file.
4. Run recommendations for all three seeds, applying an era filter on release_year (1950‑1975).
5. Report how many entities were dropped by the era filter.
6. Print the top‑10 movies as "title | release_year | linked_from | seed_count".
"""

import asyncio
import json
import os
import sys
from typing import List, Tuple

# Ensure project root is on sys.path
project_root = os.path.abspath(os.path.join(__file__, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.qloo.client import QlooClient, normalize_name
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join("C:/Zzxxx Hackathon/memory-lane", ".env"))

SEEDS = ["Sholay", "Mughal-e-Azam", "Mother India"]
SUBTYPE = "urn:entity:movie"
ERA_START, ERA_END = 1950, 1975
OUTPUT_SAMPLE = os.path.abspath(os.path.join("C:/Zzxxx Hackathon/memory-lane/docs/qloo_samples", "movie_insights_sample.json"))

async def resolve_seed_ids(client: QlooClient) -> List[Tuple[str, str]]:
    """Search each movie seed, return a list of (entity_id, name) tuples.
    Guarantees a single, consistent ID per seed.
    """
    result = []
    for name in SEEDS:
        search_res = await client.search_entity(name, kind="movie")
        if not search_res:
            print(f"WARNING: No movie entity found for seed '{name}'")
            continue
        ent = search_res[0]
        result.append((ent["entity_id"], ent["name"]))
        print(f"Resolved seed '{name}' -> ID {ent['entity_id']}")
    return result

async def fetch_and_save_sholay_insights(client: QlooClient, sholay_id: str) -> None:
    url = f"{client.base_url}/v2/insights"
    params = {"filter.type": SUBTYPE, "signal.interests.entities": sholay_id, "limit": "100"}
    # Direct request to avoid going through get_recommendations aggregation logic
    resp = await client._client.get(url, params=params)
    payload = resp.json()
    # Keep only the first two entities in results.entities (or results if list)
    results = payload.get("results")
    if isinstance(results, dict):
        entities = results.get("entities", [])
        results["entities"] = entities[:2]
    elif isinstance(results, list):
        payload["results"] = results[:2]
    # Write to file
    os.makedirs(os.path.dirname(OUTPUT_SAMPLE), exist_ok=True)
    with open(OUTPUT_SAMPLE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Saved first two insight entities for Sholay to {OUTPUT_SAMPLE}")

async def print_file_head(path: str, lines: int = 60) -> None:
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= lines:
                break
            # Write using binary buffer to avoid console encoding issues
            sys.stdout.buffer.write((line.rstrip() + "\n").encode("utf-8", "replace"))
            sys.stdout.buffer.flush()

async def run_recommendations(client: QlooClient, seed_ids: List[str], seed_names: List[str]) -> Tuple[List[dict], int, int]:
    # All recommendations without era filter
    all_recs = await client.get_recommendations(
        signal_ids=seed_ids,
        subtype=SUBTYPE,
        era_range=None,
        limit=100,
        seed_names=seed_names,
    )
    # With era filter
    filtered_recs = await client.get_recommendations(
        signal_ids=seed_ids,
        subtype=SUBTYPE,
        era_range=(ERA_START, ERA_END),
        limit=100,
        seed_names=seed_names,
    )
    dropped = len(all_recs) - len(filtered_recs)
    return filtered_recs, dropped, len(all_recs)

async def main():
    client = QlooClient()
    try:
        seed_info = await resolve_seed_ids(client)
        if len(seed_info) < 3:
            print("Not all seeds resolved – aborting.")
            return
        seed_ids, seed_names = zip(*seed_info)
        # 1. Save raw insights for Sholay
        await fetch_and_save_sholay_insights(client, seed_ids[0])
        # 2. Print first 60 lines of the saved file
        print("\nFirst 60 lines of movie_insights_sample.json:")
        await print_file_head(OUTPUT_SAMPLE, 60)
        # 3. Recommendations with era filter and count dropped
        recs, dropped, total = await run_recommendations(client, list(seed_ids), list(seed_names))
        print(f"\nEra filter ( {ERA_START}-{ERA_END} ) dropped {dropped} out of {total} entities.")
        # 4. Top 10 movies
        print("\nTop 10 movies (title | release_year | linked_from | seed_count):")
        for rec in recs[:10]:
            title = rec.get("name", "")
            year = rec.get("start_year", "")
            linked = ", ".join(rec.get("linked_from", []))
            cnt = rec.get("seed_count", 0)
            print(f"{title} | {year} | {linked} | {cnt}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
