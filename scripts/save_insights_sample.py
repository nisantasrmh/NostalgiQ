import os, sys, json
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables from the given .env path
env_path = Path(r"C:/Zzxxx Hackathon/memory-lane/.env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv('QLOO_API_KEY')
if not api_key:
    print('Missing QLOO_API_KEY')
    sys.exit(1)

base_url = 'https://hackathon.api.qloo.com'
headers = {'X-Api-Key': api_key}

def search_entity(name, limit=5):
    params = {'query': name, 'limit': str(limit)}
    resp = requests.get(f"{base_url}/search", headers=headers, params=params)
    if resp.status_code != 200:
        print(f'Search error for {name}:', resp.status_code, resp.text)
        return []
    data = resp.json()
    # Qloo search response may have 'results' or 'entities'
    entities = data.get('results') or data.get('entities') or []
    return entities

# 1. Search for Lata Mangeshkar and show top 3 results
search_name = 'Lata Mangeshkar'
search_results = search_entity(search_name, limit=5)
if not search_results:
    print('No search results for', search_name)
    sys.exit(1)
print('Top 3 search results for', search_name + ':')
for ent in search_results[:3]:
    name = ent.get('name')
    subtype = ent.get('subtype') or ent.get('type')
    eid = ent.get('entity_id')
    print(f'  - {name} ({subtype}) ID: {eid}')

# Use the first result's entity_id as the artist signal
artist_id = search_results[0].get('entity_id')
if not artist_id:
    print('First search result missing entity_id')
    sys.exit(1)

# 2. Fetch artist insights using the artist_id
insight_params = {
    'filter.type': 'urn:entity:artist',
    'signal.interests.entities': artist_id,
    'limit': '10'
}
resp = requests.get(f"{base_url}/v2/insights", headers=headers, params=insight_params)
print('Insights request status:', resp.status_code)
if resp.status_code != 200:
    print('Insights error body:', resp.text)
    sys.exit(1)
insight_data = resp.json()
print('Top-level keys in insights response:', list(insight_data.keys()))

# Extract entities list – could be under 'results'->'entities' or directly 'entities'
entities = []
if isinstance(insight_data.get('results'), dict):
    entities = insight_data['results'].get('entities') or []
elif isinstance(insight_data.get('entities'), list):
    entities = insight_data['entities']
else:
    # Sometimes 'results' may be a list of entities directly
    if isinstance(insight_data.get('results'), list):
        entities = insight_data['results']

if not entities:
    print('No entities found in insights response')
    sys.exit(1)

# Save first 3 entities to file
sample_entities = entities[:3]
output_path = Path(r"C:/Zzxxx Hackathon/memory-lane/docs/qloo_samples/artist_insights_sample.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(sample_entities, f, indent=2)
print('Saved first 3 insight entities to', output_path)
