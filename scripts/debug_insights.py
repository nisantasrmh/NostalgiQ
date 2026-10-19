import os, sys, json
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv('C:/Zzxxx Hackathon/memory-lane/.env')
api_key = os.getenv('QLOO_API_KEY')
if not api_key:
    print('Missing key')
    sys.exit(1)
base='https://hackathon.api.qloo.com'
headers={'X-Api-Key':api_key}
artist_id='98B6B5C8-62D0-42F1-ABA4-1CD7EBEACA58'
params={'filter.type':'urn:entity:artist','signal.interests.entities':artist_id,'limit':'10'}
resp=requests.get(f"{base}/v2/insights", headers=headers, params=params)
print('STATUS', resp.status_code)
print('Content-Type', resp.headers.get('Content-Type'))
print('BODY HEAD', resp.text[:500])
try:
    data=resp.json()
    print('JSON keys', list(data.keys()))
    print('type of results', type(data.get('results')))
    print('type of insights', type(data.get('insights')))
    print('full json', json.dumps(data, indent=2)[:1000])
except Exception as e:
    print('JSON parse error', e)
