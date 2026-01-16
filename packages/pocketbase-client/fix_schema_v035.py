import json
import random

def generate_collection_id():
    """Generate a PocketBase collection ID like pbc_1234567890"""
    return f"pbc_{random.randint(1000000000, 9999999999)}"

def generate_field_id(field_type):
    """Generate a PocketBase field ID like text1234567890"""
    return f"{field_type}{random.randint(1000000000, 9999999999)}"

# Read the current schema
with open('pb_schema.json', 'r', encoding='utf-8') as f:
    collections = json.load(f)

for collection in collections:
    # Add collection ID if missing
    if 'id' not in collection:
        collection['id'] = generate_collection_id()
    
    # Ensure system is set
    if 'system' not in collection:
        collection['system'] = False
    
    # Convert rules to null if empty string (except for createRule which can be empty for public creation)
    for rule_name in ['listRule', 'viewRule', 'updateRule', 'deleteRule']:
        if rule_name in collection and collection[rule_name] == '':
            collection[rule_name] = None
    
    # Process fields
    if 'fields' in collection:
        new_fields = []
        for field in collection['fields']:
            field_type = field.get('type', 'text')
            
            # Generate proper field ID if missing or in old format
            if 'id' not in field or not field['id'].startswith(field_type):
                field['id'] = generate_field_id(field_type)
            
            # Add required v0.35 properties
            if 'presentable' not in field:
                field['presentable'] = False
            if 'hidden' not in field:
                field['hidden'] = False
            if 'system' not in field:
                field['system'] = False
            
            # Handle type-specific options transformation
            # In v0.35, options are flattened into the field object
            if 'options' in field:
                opts = field.pop('options')
                for key, value in opts.items():
                    # Map old option names to new ones
                    if key == 'values' and field_type == 'select':
                        field['values'] = value
                        if 'maxSelect' not in field:
                            field['maxSelect'] = 1
                    elif key == 'collectionId' and field_type == 'relation':
                        field['collectionId'] = value
                    elif key == 'cascadeDelete' and field_type == 'relation':
                        field['cascadeDelete'] = value
                    elif key == 'maxSelect' and field_type == 'relation':
                        field['maxSelect'] = value
                    elif key == 'min':
                        field['min'] = value
                    elif key == 'max':
                        field['max'] = value
                    else:
                        field[key] = value
            
            new_fields.append(field)
        
        collection['fields'] = new_fields

# Save the updated schema
with open('pb_schema.json', 'w', encoding='utf-8') as f:
    json.dump(collections, f, indent=4)

print(f"Updated {len(collections)} collections to v0.35 format")
print("Schema saved to pb_schema.json")
