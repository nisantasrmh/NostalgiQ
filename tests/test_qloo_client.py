"""Unit tests for QlooClient exclusion and deduplication.

These tests verify:
1. An alias "Mohd Rafi" is excluded when the seed is "Mohammed Rafi".
2. A seed entity itself never appears in its own recommendation list.
"""

import asyncio
import os
import sys
import unittest

# Ensure project root is on import path
project_root = os.path.abspath(os.path.join(__file__, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.qloo.client import QlooClient, normalize_name

class TestQlooClientExclusions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = QlooClient()

    async def asyncTearDown(self):
        await self.client.close()

    async def test_alias_exclusion(self):
        # Use "Mohammed Rafi" as seed
        seed_results = await self.client.search_entity("Mohammed Rafi", kind="artist")
        self.assertTrue(seed_results, "Seed search returned no results")
        seed_entity = seed_results[0]
        seed_id = seed_entity["entity_id"]
        # Get recommendations
        recs = await self.client.get_recommendations(
            signal_ids=[seed_id],
            subtype="urn:entity:artist",
            seed_names=["Mohammed Rafi"],
        )
        # Ensure no result has normalized name equal to "mohdrifi"
        for r in recs:
            self.assertNotEqual(normalize_name(r["name"]), normalize_name("Mohd Rafi"), "Alias appeared in results")

    async def test_seed_not_in_results(self):
        # Seed "Lata Mangeshkar"
        seed_results = await self.client.search_entity("Lata Mangeshkar", kind="artist")
        self.assertTrue(seed_results, "Seed search returned no results")
        seed_entity = seed_results[0]
        seed_id = seed_entity["entity_id"]
        recs = await self.client.get_recommendations(
            signal_ids=[seed_id],
            subtype="urn:entity:artist",
            seed_names=["Lata Mangeshkar"],
        )
        ids = {r["entity_id"] for r in recs}
        self.assertNotIn(seed_id, ids, "Seed entity appeared in recommendations")

if __name__ == "__main__":
    unittest.main()
