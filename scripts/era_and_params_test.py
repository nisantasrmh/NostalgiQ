import os, sys, json
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load env
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
    data = resp.json()
    entities = data.get('results') or data.get('entities') or []
    return entities

def get_insights(artist_id, extra_params=None):
    params = {
        'filter.type': 'urn:entity:artist',
        'signal.interests.entities': artist_id,
        'limit': '10'
    }
    if extra_params:
        params.update(extra_params)
    resp = requests.get(f"{base_url}/v2/insights", headers=headers, params=params)
    if resp.status_code != 200:
        print('Insights error', resp.status_code, resp.text)
        return []
    data = resp.json()
    # extract entities list
    entities = []
    if isinstance(data.get('results'), dict):
        entities = data['results'].get('entities') or []
    elif isinstance(data.get('entities'), list):
        entities = data['entities']
    elif isinstance(data.get('results'), list):
        entities = data['results']
    return entities

artists = ['Lata Mangeshkar', 'Kishore Kumar', 'Mohammed Rafi']
artist_ids = {}
print('--- Top 3 search results for each artist ---')
for art in artists:
    results = search_entity(art, limit=5)
    print(f"{art}:")
    for ent in results[:3]:
        print(f"  - {ent.get('name')} ({ent.get('subtype') or ent.get('type')}) ID: {ent.get('entity_id')}")
    if results:
        artist_ids[art] = results[0].get('entity_id')

print('\n--- Era test: insights start_year for each artist ---')
for art, aid in artist_ids.items():
    ents = get_insights(aid)
    print(f"Insights for {art} (top 10 names with start_year):")
    for e in ents[:10]:
        name = e.get('name')
        year = e.get('properties', {}).get('start_year')
        print(f"  - {name}: {year}")
    print()

# Parameter tests using Lata Mangeshkar ID as baseline
baseline_id = artist_ids.get('Lata Mangeshkar')
baseline = get_insights(baseline_id)
baseline_names = [e.get('name') for e in baseline[:10]]

print('--- Parameter tests (compare to baseline) ---')
# 1. Location parameter
loc_params = {'filter.location.query': 'Pune'}
loc_insights = get_insights(baseline_id, extra_params=loc_params)
loc_names = [e.get('name') for e in loc_insights[:10]]
print('Location filter = Pune:')
print('Changed' if loc_names != baseline_names else 'Same')

# 2. Audience parameter (using a known audience tag)
aud_params = {'signal.audience': 'urn:tag:audience:qloo:devoted'}
# Note: parameter name uncertain; attempt signal.audience
aud_insights = get_insights(baseline_id, extra_params=aud_params)
aud_names = [e.get('name') for e in aud_insights[:10]]
print('Audience filter = devoted:')
print('Changed' if aud_names != baseline_names else 'Same')

# 3. Release year filter (if supported)
year_params = {'filter.release_year': '1970'}
year_insights = get_insights(baseline_id, extra_params=year_params)
year_names = [e.get('name') for e in year_insights[:10]]
print('Release year filter = 1970:')
print('Changed' if year_names != baseline_names else 'Same')

# Movies era test
movies = ['Sholay', 'Mughal-e-Azam']
print('\n--- Movie era test ---')
for movie in movies:
    res = search_entity(movie, limit=5)
    if not res:
        print(f'No search results for {movie}')
        continue
    movie_id = res[0].get('entity_id')
    ents = get_insights(movie_id, extra_params={'filter.type': 'urn:entity:movie'})
    print(f'Insights for movie {movie}:')
    for e in ents[:10]:
        name = e.get('name')
        year = e.get('properties', {}).get('start_year')
        print(f"  - {name}: {year}")
    print()
