"""
Export data from Oracle ATP (Insta-Outreach-Logger) to JSON files.

Run from the CRM-Tableturnerr root directory:
    python tools/migration/export_from_oracle.py

Requires:
    - oracledb package installed
    - Environment variables set (see .env.example)
"""

import os
import sys
import json
from datetime import datetime

try:
    import oracledb
except ImportError:
    print("Error: oracledb package not installed.")
    print("Install with: pip install oracledb")
    sys.exit(1)

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'exported_data', 'oracle')

# Oracle settings (from original Insta-Outreach-Logger .env)
DB_USER = os.getenv('DB_USER', os.getenv('ORACLE_USER', ''))
DB_PASSWORD = os.getenv('DB_PASSWORD', os.getenv('ORACLE_PASSWORD', ''))
DB_DSN = os.getenv('DB_DSN', os.getenv('ORACLE_CONN_STRING', ''))

# Tables to export
TABLES = [
    'OPERATORS',
    'ACTORS', 
    'TARGETS',
    'EVENT_LOGS',
    'OUTREACH_LOGS',
    'GOALS',
    'RULES',
]


def export_table(cursor, table_name: str) -> list:
    """Export all rows from a table."""
    print(f"  Exporting {table_name}...")
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        docs = []
        for row in rows:
            doc = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Handle special types
                if isinstance(value, datetime):
                    value = value.isoformat() + 'Z'
                elif hasattr(value, 'read'):  # LOB type
                    value = value.read()
                doc[col] = value
            docs.append(doc)
        
        print(f"    Found {len(docs)} records")
        return docs
        
    except Exception as e:
        print(f"    Warning: Error fetching {table_name}: {e}")
        return []


def main():
    print("=" * 60)
    print("CRM-Tableturnerr: Oracle ATP Data Export")
    print("=" * 60)
    
    # Validate configuration
    if not all([DB_USER, DB_PASSWORD, DB_DSN]):
        print("\nError: Missing Oracle configuration.")
        print("Please set the following environment variables:")
        print("  - DB_USER (or ORACLE_USER)")
        print("  - DB_PASSWORD (or ORACLE_PASSWORD)")
        print("  - DB_DSN (or ORACLE_CONN_STRING)")
        print("\nOr load them from your Insta-Outreach-Logger .env file.")
        sys.exit(1)
    
    # Connect to Oracle
    print(f"\nConnecting to Oracle...")
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN.replace('\\s+', '')  # Remove whitespace
        )
        cursor = conn.cursor()
        print("  Connected successfully!")
    except Exception as e:
        print(f"  Error connecting to Oracle: {e}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\nExporting to: {OUTPUT_DIR}")
    print("-" * 60)
    
    # Export each table
    exported = {}
    for table_name in TABLES:
        try:
            docs = export_table(cursor, table_name)
            exported[table_name] = docs
            
            # Save to JSON file
            output_file = os.path.join(OUTPUT_DIR, f"{table_name.lower()}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, default=str)
                
        except Exception as e:
            print(f"    Error exporting {table_name}: {e}")
            exported[table_name] = []
    
    # Close connection
    cursor.close()
    conn.close()
    
    # Print summary
    print("-" * 60)
    print("\nExport Summary:")
    total = 0
    for table_name, docs in exported.items():
        count = len(docs)
        total += count
        print(f"  {table_name}: {count} records")
    
    print(f"\nTotal: {total} records exported")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Save metadata
    metadata = {
        'exported_at': datetime.utcnow().isoformat() + 'Z',
        'source': 'oracle',
        'tables': {name: len(docs) for name, docs in exported.items()}
    }
    
    with open(os.path.join(OUTPUT_DIR, '_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
