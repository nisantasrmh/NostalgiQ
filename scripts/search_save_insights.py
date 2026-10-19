import os, json, sys
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables
env_path = Path(r"C:/Zzxxx Hackathon/memory-lane/.env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv('QLOO_API_KEY')
if not api_key:
    print('Missing QLOO_API_KEY')
    sys.exit(1)

base_url = 'https://hackathon.api.qloo.com'
headers = {'X-Api-Key': api_key}

def search_name(name):
    params = {'q': name, 'limit': '5'}
    resp = requests.get(f"{base_url}/search", headers=headers, params=params)
    if resp.status_code != 200:
        print(f'Search error for {name}:', resp.status_code, resp.text)
        return []
    data = resp.json()
    # The response shape may contain 'results' or 'entities'
    entities = data.get('results') or data.get('entities') or []
    return entities

# Search for Lata Mangeshkar to obtain an artist entity ID
search_results = search_name('Lata Mangeshkar')
if not search_results:
    print('No search results for Lata Mangeshkar')
    sys.exit(1)

# Show top 3 names, subtypes, IDs
print('Top 3 search results for Lata Mangeshkar:')
for ent in search_results[:3]:
    name = ent.get('name')
    subtype = ent.get('subtype') or ent.get('type')
    eid = ent.get('entity_id')
    print(f'  - {name} ({subtype}) ID: {eid}')

# Choose the first entity ID (assume it's an artist)
artist_id = search_results[0].get('entity_id')
if not artist_id:
    print('No entity_id found')
    sys.exit(1)

# Fetch artist insights
insight_params = {
    'filter.type': 'urn:entity:artist',
    'signal.interests.entities': artist_id,
    'limit': '10'
}
resp = requests.get(f"{base_url}/v2/insights", headers=headers, params=insight_params)
print('Insights request status:', resp.status_code)
if resp.status_code != 200:
    print('Error body:', resp.text)
    sys.exit(1)

insight_data = resp.json()
print('Top-level keys in insights response:', list(insight_data.keys()))

# Extract entities list – may be under 'results'->'entities' or directly 'entities'
entities = []
if isinstance(insight_data.get('results'), dict):
    entities = insight_data['results'].get('entities') or []
elif isinstance(insight_data.get('entities'), list):
    entities = insight_data['entities']

if not entities:
    print('No entities found in insights')
    sys.exit(1)

sample_entities = entities[:3]
output_path = Path(r"C:/Zzxxx Hackathon/memory-lane/docs/qloo_samples/artist_insights_sample.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(sample_entities, f, indent=2)
print('Saved first 3 insight entities to', output_path)
