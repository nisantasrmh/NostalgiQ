import sys, os
# Ensure project root on PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
import asyncio
from backend.qloo.client import QlooClient

async def get_place_insights(client, place_id):
    url = f"{client.base_url}/v2/insights"
    params = {
        "filter.type": "urn:entity:place",
        "signal.interests.entities": place_id,
        "limit": "10",
    }
    resp = await client._client.get(url, params=params)
    data = resp.json()
    entities = []
    results = data.get("results")
    if isinstance(results, dict):
        entities = results.get("entities", [])
    elif isinstance(results, list):
        entities = results
    return [e.get("name") for e in entities[:10]]

async def main():
    queries = ["Katz's Delicatessen", "Vaishali Pune", "Leopold Cafe Mumbai"]
    async with QlooClient() as client:
        for q in queries:
            results = await client.search_entity(q, kind="place")
            if not results:
                print(f"{q}: no place found")
                continue
            place = results[0]
            pid = place.get("entity_id")
            print(f"--- {q} (ID {pid}) ---")
            names = await get_place_insights(client, pid)
            for name in names:
                print(name)

if __name__ == "__main__":
    asyncio.run(main())
