"""Safe live test for Qloo client – Pune 1960s persona.

This script obtains seed entity IDs for the four classic Indian singers, then
retrieves artist recommendations twice: once without any era filter and once
with the era range (1940‑1975). It reports how many recommendations were
removed by the era filter and prints the top‑10 results in a UTF‑8‑safe
format (name | start_year | linked_from).
"""

import asyncio
import os
import sys
from typing import List

# Ensure project root is on import path
project_root = os.path.abspath(os.path.join(__file__, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.qloo.client import QlooClient

SEEDS = ["Lata Mangeshkar", "Kishore Kumar", "Mukesh", "Mohammed Rafi"]
TARGET_SUBTYPE = "urn:entity:artist"
ERA_RANGE = (1940, 1975)
TOP_N = 10


async def fetch_seed_ids(client: QlooClient) -> List[str]:
    ids = []
    for name in SEEDS:
        results = await client.search_entity(name, kind="artist")
        if results:
            entity = results[0]
            ids.append(entity.get("entity_id"))
            safe_print(f"Seed '{name}' => {entity.get('name')} (ID: {entity.get('entity_id')})")
        else:
            safe_print(f"WARNING: No artist entity found for seed '{name}'")
    return ids


def safe_print(text: str) -> None:
    # Write UTF‑8 bytes directly to stdout to avoid console encoding issues
    sys.stdout.buffer.write((text + "\n").encode("utf-8", "replace"))
    sys.stdout.buffer.flush()


async def main():
    client = QlooClient()
    try:
        seed_ids = await fetch_seed_ids(client)
        if not seed_ids:
            safe_print("No seed IDs available – aborting test.")
            return
        # Baseline (no era filter)
        baseline = await client.get_recommendations(
            signal_ids=seed_ids,
            subtype=TARGET_SUBTYPE,
            era_range=None,
            limit=100,
        )
        # With era filter
        filtered = await client.get_recommendations(
            signal_ids=seed_ids,
            subtype=TARGET_SUBTYPE,
            era_range=ERA_RANGE,
            limit=100,
        )
        dropped = len(baseline) - len(filtered)
        safe_print(f"\nEra filter dropped {dropped} recommendations.")
        safe_print("\nTop recommendations (name | start_year | linked_from):")
        for rec in filtered[:TOP_N]:
            name = rec.get("name") or ""
            year = rec.get("start_year") or ""
            linked = ", ".join(rec.get("linked_from", []))
            safe_print(f"{name} | {year} | {linked}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
