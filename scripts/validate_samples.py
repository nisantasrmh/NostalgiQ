import json
from pathlib import Path

def validate_json_files():
    base_dirs = [
        Path(r'C:/Zzxxx Hackathon/memory-lane/docs/qloo_samples'),
        Path(r'C:/Zzxxx Hackathon/memory-lane/docs/dining_responses'),
    ]
    for base in base_dirs:
        if not base.is_dir():
            print(f'Directory not found: {base}')
            continue
        for file_path in base.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f'OK: {file_path.name}')
            except Exception as e:
                print(f'FAILED: {file_path.name} – {e}')

if __name__ ==  __main__:
    validate_json_files()
