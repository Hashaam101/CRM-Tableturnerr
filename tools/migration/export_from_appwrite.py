"""
Export data from Appwrite (ColdCallMonitor) to JSON files.

Run from the CRM-Tableturnerr root directory:
    python tools/migration/export_from_appwrite.py

Requires:
    - appwrite package installed
    - Environment variables set (see .env.example)
"""

import os
import sys
import json
from datetime import datetime

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from appwrite.client import Client
    from appwrite.services.databases import Databases
    from appwrite.query import Query
except ImportError:
    print("Error: appwrite package not installed.")
    print("Install with: pip install appwrite")
    sys.exit(1)

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'exported_data', 'appwrite')

# Appwrite settings (from original ColdCallMonitor .env)
ENDPOINT = os.getenv('APPWRITE_ENDPOINT', 'https://fra.cloud.appwrite.io/v1')
PROJECT_ID = os.getenv('APPWRITE_PROJECT_ID', '')
API_KEY = os.getenv('APPWRITE_API_KEY', '')
DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID', '')

# Collection IDs (from original ColdCallMonitor)
COLLECTIONS = {
    'companies': os.getenv('APPWRITE_COMPANIES_COLLECTION_ID', 'companies'),
    'transcripts': os.getenv('APPWRITE_TRANSCRIPTS_COLLECTION_ID', 'transcripts'),
    'coldcalls': os.getenv('APPWRITE_COLDCALLS_COLLECTION_ID', 'coldcalls'),
    'team_members': os.getenv('APPWRITE_TEAM_MEMBERS_COLLECTION_ID', 'team_members'),
    'alerts': os.getenv('APPWRITE_ALERTS_COLLECTION_ID', 'alerts'),
    'notes': os.getenv('APPWRITE_NOTES_COLLECTION_ID', 'notes'),
}


def export_collection(databases: Databases, collection_id: str, name: str) -> list:
    """Export all documents from a collection."""
    print(f"  Exporting {name}...")
    
    all_docs = []
    offset = 0
    limit = 100
    
    while True:
        try:
            result = databases.list_documents(
                DATABASE_ID,
                collection_id,
                queries=[
                    Query.limit(limit),
                    Query.offset(offset)
                ]
            )
            
            docs = result.get('documents', [])
            if not docs:
                break
                
            all_docs.extend(docs)
            offset += limit
            
            if len(docs) < limit:
                break
                
        except Exception as e:
            print(f"    Warning: Error fetching {name}: {e}")
            break
    
    print(f"    Found {len(all_docs)} records")
    return all_docs


def main():
    print("=" * 60)
    print("CRM-Tableturnerr: Appwrite Data Export")
    print("=" * 60)
    
    # Validate configuration
    if not all([PROJECT_ID, API_KEY, DATABASE_ID]):
        print("\nError: Missing Appwrite configuration.")
        print("Please set the following environment variables:")
        print("  - APPWRITE_PROJECT_ID")
        print("  - APPWRITE_API_KEY")
        print("  - APPWRITE_DATABASE_ID")
        print("\nOr load them from your ColdCallMonitor .env file.")
        sys.exit(1)
    
    # Initialize Appwrite client
    client = Client()
    client.set_endpoint(ENDPOINT).set_project(PROJECT_ID).set_key(API_KEY)
    databases = Databases(client)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\nExporting to: {OUTPUT_DIR}")
    print("-" * 60)
    
    # Export each collection
    exported = {}
    for name, collection_id in COLLECTIONS.items():
        try:
            docs = export_collection(databases, collection_id, name)
            exported[name] = docs
            
            # Save to JSON file
            output_file = os.path.join(OUTPUT_DIR, f"{name}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, default=str)
                
        except Exception as e:
            print(f"    Error exporting {name}: {e}")
            exported[name] = []
    
    # Print summary
    print("-" * 60)
    print("\nExport Summary:")
    total = 0
    for name, docs in exported.items():
        count = len(docs)
        total += count
        print(f"  {name}: {count} records")
    
    print(f"\nTotal: {total} records exported")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Save metadata
    metadata = {
        'exported_at': datetime.utcnow().isoformat() + 'Z',
        'source': 'appwrite',
        'endpoint': ENDPOINT,
        'project_id': PROJECT_ID,
        'database_id': DATABASE_ID,
        'collections': {name: len(docs) for name, docs in exported.items()}
    }
    
    with open(os.path.join(OUTPUT_DIR, '_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
