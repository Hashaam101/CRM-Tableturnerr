import json

with open('pb_schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix all relation fields that reference 'users' to use the actual collection ID
count = 0
for collection in data:
    if 'fields' in collection:
        for field in collection['fields']:
            if field.get('type') == 'relation' and field.get('collectionId') == 'users':
                field['collectionId'] = '_pb_users_auth_'
                count += 1
                print(f"Fixed: {collection['name']}.{field['name']} -> _pb_users_auth_")

with open('pb_schema.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print(f"\nFixed {count} relation fields.")
