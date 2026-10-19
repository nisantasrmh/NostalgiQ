import os, json, sys
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

# Artist ID for Lata Mangeshkar (person) known from earlier search
artist_id = '98B6B5C8-62D0-42F1-ABA4-1CD7EBEACA58'
params = {
    'filter.type': 'urn:entity:artist',
    'signal.interests.entities': artist_id,
    'limit': '10'
}
resp = requests.get(f"{base_url}/v2/insights", headers=headers, params=params)
if resp.status_code != 200:
    print('Error', resp.status_code, resp.text)
    sys.exit(1)
data = resp.json()
# Ensure 'results' key holds insights (may also be 'insights')
insights = data.get('results') or data.get('insights') or []
# Keep first 3 entities
sample = insights[:3]
output_path = Path(r"C:/Zzxxx Hackathon/memory-lane/docs/qloo_samples/artist_insights_sample.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(sample, f, indent=2)
print('Saved sample to', output_path)
print('Top-level keys:', list(data.keys()))
print('Full JSON (truncated):', json.dumps(data)[:500])
