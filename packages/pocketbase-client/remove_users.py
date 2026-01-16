import json

with open('pb_schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Remove users collection to avoid overwriting PocketBase's built-in auth fields
data = [c for c in data if c['name'] != 'users']

with open('pb_schema.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print(f"Removed users collection. {len(data)} collections remaining.")
