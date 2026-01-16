import json
import random
import string

def generate_id(length=15):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

input_file = 'pb_schema.json'
output_file = 'pb_schema_fixed.json'

with open(input_file, 'r', encoding='utf-8') as f:
    collections = json.load(f)

for collection in collections:
    # Remove 'system' property if present, as it might cause issues on import
    if 'system' in collection:
        del collection['system']
    
    # Ensure 'fields' exists
    if 'fields' in collection:
        for field in collection['fields']:
            # Add 'id' if missing
            if 'id' not in field:
                field['id'] = generate_id()
            
            # Ensure 'system' is false for fields if not set
            if 'system' not in field:
                field['system'] = False

print(f"Processed {len(collections)} collections.")

with open(input_file, 'w', encoding='utf-8') as f:
    json.dump(collections, f, indent=4)

print("Updated schema saved to pb_schema.json")
