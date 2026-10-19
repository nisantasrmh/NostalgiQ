"""Live test for Qloo client – Pune 1960s persona (fixed bugs).

The script:
1. Searches for seed artists and obtains their entity IDs (using kind='artist').
2. Calls ``get_recommendations`` with those IDs and captures per‑seed raw result counts.
3. Applies the era filter (1940‑1975) and prints:
   - For each seed: how many entities its insights call returned before filtering.
   - Top 10 recommendations as ``name | start_year | linked_from (seed names) | seed_count``.
"""

import asyncio
import os
import sys
from typing import List, Dict

# Ensure project root is on import path
project_root = os.path.abspath(os.path.join(__file__, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.qloo.client import QlooClient

SEEDS = ["Lata Mangeshkar", "Kishore Kumar", "Mukesh", "Mohammed Rafi"]
TARGET_SUBTYPE = "urn:entity:artist"
ERA_RANGE = (1940, 1975)
TOP_N = 10


def safe_print(text: str) -> None:
    sys.stdout.buffer.write((text + "\n").encode("utf-8", "replace"))
    sys.stdout.buffer.flush()


async def fetch_seed_ids_and_names(client: QlooClient) -> List[Dict[str, str]]:
    """Return a list of dicts with 'id' and 'name' for each seed artist."""
    seed_info = []
    for name in SEEDS:
        results = await client.search_entity(name, kind="artist")
        if results:
            entity = results[0]
            seed_info.append({"id": entity.get("entity_id"), "name": entity.get("name")})
            safe_print(f"Seed '{name}' => {entity.get('name')} (ID: {entity.get('entity_id')})")
        else:
            safe_print(f"WARNING: No artist entity found for seed '{name}'")
    return seed_info


async def main():
    client = QlooClient()
    try:
        seed_info = await fetch_seed_ids_and_names(client)
        if not seed_info:
            safe_print("No seed IDs available – aborting test.")
            return
        seed_ids = [s["id"] for s in seed_info]
        seed_names = [s["name"] for s in seed_info]

        # Get recommendations with era filter; client stores per‑seed counts internally
        recs = await client.get_recommendations(
            signal_ids=seed_ids,
            subtype=TARGET_SUBTYPE,
            era_range=ERA_RANGE,
            limit=100,
            seed_names=seed_names,
        )

        # Print per‑seed raw result counts (before era filter)
        safe_print("\nPer‑seed raw insight result counts (before era filter):")
        for sid, name in zip(seed_ids, seed_names):
            count = client._last_per_seed_counts.get(sid, 0)
            safe_print(f"- {name}: {count} entities")

        safe_print("\nTop recommendations (name | start_year | linked_from | seed_count):")
        for rec in recs[:TOP_N]:
            name = rec.get("name") or ""
            year = rec.get("start_year") or ""
            linked = ", ".join(rec.get("linked_from", []))
            seed_cnt = rec.get("seed_count", 0)
            safe_print(f"{name} | {year} | {linked} | {seed_cnt}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
