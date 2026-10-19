import os, sys, json
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables from the .env file
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
        print(f'Search error for "{name}":', resp.status_code, resp.text)
        return []
    data = resp.json()
    # Qloo search may return 'results' or 'entities'
    return data.get('results') or data.get('entities') or []

def get_insights(entity_id, extra_params=None):
    # baseline artist insights params
    params = {
        'filter.type': 'urn:entity:artist',
        'signal.interests.entities': entity_id,
        'limit': '10'
    }
    if extra_params:
        params.update(extra_params)
    resp = requests.get(f"{base_url}/v2/insights", headers=headers, params=params)
    if resp.status_code != 200:
        print('Insights error', resp.status_code, resp.text)
        return [], resp
    return resp.json(), resp

def print_top3(name, results):
    print(f"Top 3 results for {name}:")
    for ent in results[:3]:
        entity_type = ent.get('subtype') or ent.get('type')
        print(f"  - {ent.get('name')} ({entity_type}) ID: {ent.get('entity_id')}")
    # Simple heuristic: check if name appears in the result name (case-insensitive)
    if results:
        top_name = results[0].get('name', '').lower()
        expected = name.lower()
        correct = expected in top_name or top_name in expected
        print(f"    Top result correct? {'YES' if correct else 'NO'}")
    print()

# 1. Search for the five items
search_names = ["Lata Mangeshkar", "Kishore Kumar", "Sholay", "Mughal-e-Azam", "Vaishali"]
search_results = {}
for name in search_names:
    results = search_entity(name, limit=5)
    search_results[name] = results
    print_top3(name, results)

# 2. Place verification (using the Vaishali search which should be a place)
place_name = "Vaishali"
place_results = search_results.get(place_name, [])
place_entity = None
for ent in place_results:
    if ent.get('subtype') == 'urn:entity:place' or ent.get('type') == 'urn:entity':
        # Heuristic: pick first place subtype if available
        place_entity = ent
        break
if not place_entity:
    print('No place-type entity found for Vaishali')
else:
    place_id = place_entity.get('entity_id')
    print(f"Verified place entity for {place_name}: {place_entity.get('name')} ID: {place_id}\n")
    # Call insights with filter.type=urn:entity:place
    extra = {'filter.type': 'urn:entity:place', 'signal.interests.entities': place_id, 'limit': '5'}
    insights_data, resp = get_insights(place_id, extra_params=extra)
    # Show request URL and full response body (truncated for brevity)
    print('Request URL:', resp.request.url)
    print('Full Insights Response (truncated to 500 chars):')
    print(json.dumps(insights_data)[:500])
    print('\n')
    # Retry with a known restaurant (e.g., "The Table" in Mumbai) if needed
    # For demonstration, we'll just attempt the same call again to see if it works.
    # In a real test we would use a different place ID.

# 3. Location effect test using Lata Mangeshkar artist ID
artist_name = "Lata Mangeshkar"
artist_id = (search_results.get(artist_name) or [])[0].get('entity_id') if search_results.get(artist_name) else None
if not artist_id:
    print('No artist ID for Lata Mangeshkar')
else:
    # Baseline (no location)
    baseline_data, _ = get_insights(artist_id)
    baseline_names = [e.get('name') for e in baseline_data.get('results', {}).get('entities', [])[:10]]

    # (b) filter.location.query = Pune
    loc_params = {'filter.location.query': 'Pune'}
    loc_data, _ = get_insights(artist_id, extra_params=loc_params)
    loc_names = [e.get('name') for e in loc_data.get('results', {}).get('entities', [])[:10]]

    # (c) signal.geography (attempting) - using same format as filter.location.query but as signal
    signal_geo_params = {'signal.geography': 'Pune'}
    signal_geo_data, _ = get_insights(artist_id, extra_params=signal_geo_params)
    signal_geo_names = [e.get('name') for e in signal_geo_data.get('results', {}).get('entities', [])[:10]]

    print('Location Effect Test (Top 10 names):')
    print('Baseline:', baseline_names)
    print('filter.location.query=Pune:', loc_names)
    print('signal.geography=Pune:', signal_geo_names)
    print('Changed vs baseline?')
    print('  filter.location.query changed:', 'YES' if loc_names != baseline_names else 'NO')
    print('  signal.geography changed:', 'YES' if signal_geo_names != baseline_names else 'NO')
    print('\n')

# 4. Audience effect test - using audience tags observed in previous sample
audience_urns = [
    'urn:tag:audience:qloo:devoted',
    'urn:tag:audience:qloo:passionate',
    'urn:tag:audience:qloo:energetic',
    'urn:tag:audience:qloo:appreciative'
]
if artist_id:
    for aud in audience_urns:
        aud_params = {'signal.audience': aud}
        aud_data, _ = get_insights(artist_id, extra_params=aud_params)
        aud_names = [e.get('name') for e in aud_data.get('results', {}).get('entities', [])[:10]]
        print(f'Audience URN {aud}:')
        print('  Top 10 names:', aud_names)
        print('  Changed vs baseline?', 'YES' if aud_names != baseline_names else 'NO')
        print()
