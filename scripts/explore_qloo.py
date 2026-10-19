import os
import json
import pathlib
import sys
import urllib.parse

import requests

# Load API key from .env using python-dotenv
from dotenv import load_dotenv
env_path = pathlib.Path('c:/Zzxxx Hackathon/memory-lane/.env')
load_dotenv(dotenv_path=env_path)
api_key = os.getenv('QLOO_API_KEY')
if not api_key:
    print('API key not found in .env', file=sys.stderr)
    sys.exit(1)

BASE_URL = 'https://hackathon.api.qloo.com'
HEADERS = {'X-Api-Key': api_key}

# Output directory for raw JSON samples
samples_dir = pathlib.Path(__file__).resolve().parents[2] / 'docs' / 'qloo_samples'
samples_dir.mkdir(parents=True, exist_ok=True)

# 1. Search calls
search_names = [
    'Lata Mangeshkar',
    'Kishore Kumar',
    'Sholay',
    'Mughal-e-Azam',
    'Vaishali'  # Pune restaurant
]
search_ids = {}
print('--- SEARCH CALLS ---')
for name in search_names:
    params = {'query': name}
    url = f"{BASE_URL}/search?{urllib.parse.urlencode(params)}"
    resp = requests.get(url, headers=HEADERS)
    try:
        data = resp.json()
    except Exception:
        data = {'error': resp.text}
    # Save raw response
    out_path = samples_dir / f"search_{name.replace(' ', '_')}.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{name}: {resp.status_code}")
    # Extract first entity id if possible
    entity_id = None
    if isinstance(data, dict):
        ents = data.get('entities') or data.get('results') or []
        if ents:
            entity_id = ents[0].get('id') or ents[0].get('entity_id')
    if entity_id:
        search_ids[name] = entity_id
        print(f"  id: {entity_id}")
    else:
        print('  no id extracted')

# Helper for insights
def call_insights(filter_type, entity_ids):
    ids_param = ','.join(entity_ids)
    params = {
        'filter.type': filter_type,
        'signal.interests.entities': ids_param
    }
    url = f"{BASE_URL}/v2/insights?{urllib.parse.urlencode(params)}"
    resp = requests.get(url, headers=HEADERS)
    try:
        data = resp.json()
    except Exception:
        data = {'error': resp.text}
    return resp.status_code, data

# 2. Insights calls
print('\n--- INSIGHTS CALLS ---')
# Artists
artist_ids = [search_ids.get('Lata Mangeshkar'), search_ids.get('Kishore Kumar')]
artist_ids = [i for i in artist_ids if i]
if artist_ids:
    status, data = call_insights('urn:entity:artist', artist_ids)
    (samples_dir / 'insights_artist.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Artist insights: {status}, ids {artist_ids}")

# Movies
movie_ids = [search_ids.get('Sholay'), search_ids.get('Mughal-e-Azam')]
movie_ids = [i for i in movie_ids if i]
if movie_ids:
    status, data = call_insights('urn:entity:movie', movie_ids)
    (samples_dir / 'insights_movie.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Movie insights: {status}, ids {movie_ids}")

# Places (restaurant)
place_ids = [search_ids.get('Vaishali')]
place_ids = [i for i in place_ids if i]
if place_ids:
    status, data = call_insights('urn:entity:place', place_ids)
    (samples_dir / 'insights_place.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Place insights: {status}, ids {place_ids}")

# 3. Location filtering tests
print('\n--- LOCATION FILTER TESTS ---')
location_params = ['filter.location', 'signal.location', 'filter.geography', 'signal.geography']
for param in location_params:
    params = {
        'filter.type': 'urn:entity:artist',
        'signal.interests.entities': ','.join(artist_ids),
        param: 'Pune'
    }
    url = f"{BASE_URL}/v2/insights?{urllib.parse.urlencode(params)}"
    resp = requests.get(url, headers=HEADERS)
    try:
        data = resp.json()
    except Exception:
        data = {'error': resp.text}
    (samples_dir / f'insights_location_{param}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{param}: {resp.status_code}")

# 4. Audience signal tests
print('\n--- AUDIENCE SIGNAL TESTS ---')
audience_urns = [
    'urn:audience:age_65+',
    'urn:audience:age_18-24',
    'urn:audience:senior',
    'urn:audience:adult'
]
for aud in audience_urns:
    params = {
        'filter.type': 'urn:entity:artist',
        'signal.interests.entities': ','.join(artist_ids),
        'signal.demographics.audiences': aud
    }
    url = f"{BASE_URL}/v2/insights?{urllib.parse.urlencode(params)}"
    resp = requests.get(url, headers=HEADERS)
    try:
        data = resp.json()
    except Exception:
        data = {'error': resp.text}
    safe_name = aud.replace(':', '_')
    (samples_dir / f'insights_audience_{safe_name}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{aud}: {resp.status_code}")

print('\n--- DONE ---')
