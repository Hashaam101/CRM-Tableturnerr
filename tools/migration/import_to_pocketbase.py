"""
Import exported data from Appwrite and Oracle into PocketBase.

Run from the CRM-Tableturnerr root directory:
    python tools/migration/import_to_pocketbase.py

Prerequisites:
    1. PocketBase must be running
    2. Collections must be created (import pb_schema.json via Admin UI)
    3. Admin credentials configured in .env
    4. Run export scripts first to generate JSON files
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add parent path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'pocketbase-client', 'src', 'python'))

try:
    from pocketbase_client import CRMPocketBase
except ImportError:
    # Fallback to direct httpx implementation
    import httpx
    CRMPocketBase = None

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), 'exported_data')
POCKETBASE_URL = os.getenv('POCKETBASE_URL', 'http://localhost:8090')
PB_ADMIN_EMAIL = os.getenv('PB_ADMIN_EMAIL', '')
PB_ADMIN_PASSWORD = os.getenv('PB_ADMIN_PASSWORD', '')


class PocketBaseImporter:
    """Import data to PocketBase."""
    
    def __init__(self, url: str, admin_email: str, admin_password: str):
        self.url = url
        self.client = httpx.Client(timeout=30.0)
        self.token = None
        self._authenticate(admin_email, admin_password)
        
        # ID mappings for relations
        self.id_maps: Dict[str, Dict[str, str]] = {}
    
    def _authenticate(self, email: str, password: str):
        """Authenticate as admin."""
        response = self.client.post(
            f"{self.url}/api/admins/auth-with-password",
            json={'identity': email, 'password': password}
        )
        response.raise_for_status()
        self.token = response.json()['token']
    
    def _headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': self.token
        }
    
    def create_record(self, collection: str, data: dict) -> dict:
        """Create a record in PocketBase."""
        response = self.client.post(
            f"{self.url}/api/collections/{collection}/records",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def import_appwrite_data(self):
        """Import data exported from Appwrite."""
        appwrite_dir = os.path.join(DATA_DIR, 'appwrite')
        if not os.path.exists(appwrite_dir):
            print("  No Appwrite data found. Skipping.")
            return
        
        print("\n--- Importing Appwrite Data ---")
        
        # 1. Import team_members → users
        self._import_team_members(appwrite_dir)
        
        # 2. Import companies
        self._import_companies(appwrite_dir)
        
        # 3. Import cold calls
        self._import_cold_calls(appwrite_dir)
        
        # 4. Import transcripts
        self._import_transcripts(appwrite_dir)
        
        # 5. Import alerts
        self._import_alerts(appwrite_dir)
        
        # 6. Import notes
        self._import_notes(appwrite_dir)
    
    def _import_team_members(self, data_dir: str):
        """Import team_members as users."""
        file_path = os.path.join(data_dir, 'team_members.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing team members → users...")
        with open(file_path) as f:
            records = json.load(f)
        
        self.id_maps['team_members'] = {}
        for rec in records:
            try:
                new_rec = self.create_record('users', {
                    'email': rec.get('email', f"user_{rec['$id']}@example.com"),
                    'password': 'TempPassword123!',  # Require password reset
                    'passwordConfirm': 'TempPassword123!',
                    'name': rec.get('name', 'Unknown'),
                    'role': rec.get('role', 'member'),
                    'status': 'offline'
                })
                self.id_maps['team_members'][rec['$id']] = new_rec['id']
            except Exception as e:
                print(f"    Warning: Failed to import team member: {e}")
        
        print(f"    Imported {len(self.id_maps['team_members'])} users")
    
    def _import_companies(self, data_dir: str):
        """Import companies."""
        file_path = os.path.join(data_dir, 'companies.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing companies...")
        with open(file_path) as f:
            records = json.load(f)
        
        self.id_maps['companies'] = {}
        for rec in records:
            try:
                new_rec = self.create_record('companies', {
                    'company_name': rec.get('company_name', 'Unknown'),
                    'owner_name': rec.get('owner_name'),
                    'company_location': rec.get('company_location'),
                    'google_maps_link': rec.get('google_maps_link'),
                    'phone_numbers': rec.get('phone_numbers'),
                    'source': 'cold_call'
                })
                self.id_maps['companies'][rec['$id']] = new_rec['id']
            except Exception as e:
                print(f"    Warning: Failed to import company: {e}")
        
        print(f"    Imported {len(self.id_maps['companies'])} companies")
    
    def _import_cold_calls(self, data_dir: str):
        """Import cold calls."""
        file_path = os.path.join(data_dir, 'coldcalls.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing cold calls...")
        with open(file_path) as f:
            records = json.load(f)
        
        self.id_maps['coldcalls'] = {}
        for rec in records:
            try:
                # Map relations
                company_id = self.id_maps.get('companies', {}).get(rec.get('company_id'))
                claimed_by = self.id_maps.get('team_members', {}).get(rec.get('claimed_by'))
                
                new_rec = self.create_record('cold_calls', {
                    'company': company_id,
                    'caller_name': rec.get('caller_name'),
                    'recipients': rec.get('recipients'),
                    'call_outcome': rec.get('call_outcome'),
                    'interest_level': rec.get('interest_level'),
                    'objections': rec.get('objections'),
                    'pain_points': rec.get('pain_points'),
                    'follow_up_actions': rec.get('follow_up_actions'),
                    'call_summary': rec.get('call_summary'),
                    'call_duration_estimate': rec.get('call_duration_estimate'),
                    'model_used': rec.get('model_used'),
                    'phone_number': rec.get('phone_number'),
                    'owner_name': rec.get('owner_name'),
                    'claimed_by': claimed_by
                })
                self.id_maps['coldcalls'][rec['$id']] = new_rec['id']
            except Exception as e:
                print(f"    Warning: Failed to import cold call: {e}")
        
        print(f"    Imported {len(self.id_maps['coldcalls'])} cold calls")
    
    def _import_transcripts(self, data_dir: str):
        """Import transcripts."""
        file_path = os.path.join(data_dir, 'transcripts.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing transcripts...")
        with open(file_path) as f:
            records = json.load(f)
        
        count = 0
        for rec in records:
            try:
                call_id = self.id_maps.get('coldcalls', {}).get(rec.get('call_id'))
                if not call_id:
                    continue
                
                self.create_record('call_transcripts', {
                    'call': call_id,
                    'transcript': rec.get('transcript', '')
                })
                count += 1
            except Exception as e:
                print(f"    Warning: Failed to import transcript: {e}")
        
        print(f"    Imported {count} transcripts")
    
    def _import_alerts(self, data_dir: str):
        """Import alerts."""
        file_path = os.path.join(data_dir, 'alerts.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing alerts...")
        with open(file_path) as f:
            records = json.load(f)
        
        count = 0
        for rec in records:
            try:
                created_by = self.id_maps.get('team_members', {}).get(rec.get('created_by'))
                target_user = self.id_maps.get('team_members', {}).get(rec.get('target_user'))
                
                if not created_by or not target_user:
                    continue
                
                self.create_record('alerts', {
                    'created_by': created_by,
                    'target_user': target_user,
                    'entity_type': rec.get('entity_type', 'cold_call'),
                    'entity_id': rec.get('entity_id'),
                    'entity_label': rec.get('entity_label'),
                    'alert_time': rec.get('alert_time'),
                    'message': rec.get('message'),
                    'is_dismissed': rec.get('is_dismissed', False)
                })
                count += 1
            except Exception as e:
                print(f"    Warning: Failed to import alert: {e}")
        
        print(f"    Imported {count} alerts")
    
    def _import_notes(self, data_dir: str):
        """Import notes."""
        file_path = os.path.join(data_dir, 'notes.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing notes...")
        with open(file_path) as f:
            records = json.load(f)
        
        count = 0
        for rec in records:
            try:
                created_by = self.id_maps.get('team_members', {}).get(rec.get('created_by'))
                if not created_by:
                    continue
                
                self.create_record('notes', {
                    'title': rec.get('title', 'Untitled'),
                    'note_text': rec.get('note_text', ''),
                    'created_by': created_by,
                    'is_archived': rec.get('is_archived', False),
                    'is_deleted': rec.get('is_deleted', False),
                    'deleted_at': rec.get('deleted_at')
                })
                count += 1
            except Exception as e:
                print(f"    Warning: Failed to import note: {e}")
        
        print(f"    Imported {count} notes")
    
    def import_oracle_data(self):
        """Import data exported from Oracle."""
        oracle_dir = os.path.join(DATA_DIR, 'oracle')
        if not os.path.exists(oracle_dir):
            print("  No Oracle data found. Skipping.")
            return
        
        print("\n--- Importing Oracle Data ---")
        
        # 1. Import OPERATORS → users (merge with existing)
        self._import_operators(oracle_dir)
        
        # 2. Import ACTORS → insta_actors
        self._import_actors(oracle_dir)
        
        # 3. Import TARGETS → leads
        self._import_targets(oracle_dir)
        
        # 4. Import GOALS
        self._import_goals(oracle_dir)
        
        # 5. Import RULES
        self._import_rules(oracle_dir)
        
        # 6. Import EVENT_LOGS and OUTREACH_LOGS
        self._import_event_logs(oracle_dir)
    
    def _import_operators(self, data_dir: str):
        """Import operators as users."""
        file_path = os.path.join(data_dir, 'operators.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing operators → users...")
        with open(file_path) as f:
            records = json.load(f)
        
        if 'operators' not in self.id_maps:
            self.id_maps['operators'] = {}
        
        for rec in records:
            try:
                new_rec = self.create_record('users', {
                    'email': rec.get('OPR_EMAIL', f"opr_{rec['OPR_ID']}@example.com"),
                    'password': 'TempPassword123!',
                    'passwordConfirm': 'TempPassword123!',
                    'name': rec.get('OPR_NAME', 'Unknown'),
                    'role': 'operator',
                    'status': rec.get('OPR_STATUS', 'offline').lower()
                })
                self.id_maps['operators'][rec['OPR_ID']] = new_rec['id']
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    print(f"    Warning: Failed to import operator: {e}")
        
        print(f"    Imported {len(self.id_maps['operators'])} operators")
    
    def _import_actors(self, data_dir: str):
        """Import actors."""
        file_path = os.path.join(data_dir, 'actors.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing actors → insta_actors...")
        with open(file_path) as f:
            records = json.load(f)
        
        self.id_maps['actors'] = {}
        for rec in records:
            try:
                owner_id = self.id_maps.get('operators', {}).get(rec.get('OPR_ID'))
                if not owner_id:
                    continue
                
                new_rec = self.create_record('insta_actors', {
                    'username': rec.get('ACT_USERNAME', 'unknown'),
                    'owner': owner_id,
                    'status': rec.get('ACT_STATUS', 'Active'),
                    'last_activity': rec.get('LAST_ACTIVITY')
                })
                self.id_maps['actors'][rec['ACT_ID']] = new_rec['id']
            except Exception as e:
                print(f"    Warning: Failed to import actor: {e}")
        
        print(f"    Imported {len(self.id_maps['actors'])} actors")
    
    def _import_targets(self, data_dir: str):
        """Import targets as leads."""
        file_path = os.path.join(data_dir, 'targets.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing targets → leads...")
        with open(file_path) as f:
            records = json.load(f)
        
        self.id_maps['targets'] = {}
        for rec in records:
            try:
                new_rec = self.create_record('leads', {
                    'username': rec.get('TAR_USERNAME', 'unknown'),
                    'status': rec.get('TAR_STATUS', 'Cold No Reply'),
                    'first_contacted': rec.get('FIRST_CONTACTED'),
                    'last_updated': rec.get('LAST_UPDATED'),
                    'notes': rec.get('NOTES'),
                    'email': rec.get('EMAIL') if rec.get('EMAIL') not in ['N/S', 'N/F'] else None,
                    'phone': rec.get('PHONE_NUM') if rec.get('PHONE_NUM') not in ['N/S', 'N/F'] else None,
                    'contact_source': rec.get('CONT_SOURCE'),
                    'source': 'instagram'
                })
                self.id_maps['targets'][rec['TAR_ID']] = new_rec['id']
            except Exception as e:
                print(f"    Warning: Failed to import target: {e}")
        
        print(f"    Imported {len(self.id_maps['targets'])} leads")
    
    def _import_goals(self, data_dir: str):
        """Import goals."""
        file_path = os.path.join(data_dir, 'goals.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing goals...")
        with open(file_path) as f:
            records = json.load(f)
        
        count = 0
        for rec in records:
            try:
                self.create_record('goals', {
                    'metric': rec.get('METRIC', 'Total Messages Sent'),
                    'target_value': rec.get('TARGET_VALUE', 100),
                    'frequency': rec.get('FREQUENCY', 'Daily'),
                    'assigned_to_user': self.id_maps.get('operators', {}).get(rec.get('ASSIGNED_TO_OPR')),
                    'assigned_to_actor': self.id_maps.get('actors', {}).get(rec.get('ASSIGNED_TO_ACT')),
                    'status': rec.get('STATUS', 'Active'),
                    'suggested_by': self.id_maps.get('operators', {}).get(rec.get('SUGGESTED_BY')),
                    'start_date': rec.get('START_DATE'),
                    'end_date': rec.get('END_DATE')
                })
                count += 1
            except Exception as e:
                print(f"    Warning: Failed to import goal: {e}")
        
        print(f"    Imported {count} goals")
    
    def _import_rules(self, data_dir: str):
        """Import rules."""
        file_path = os.path.join(data_dir, 'rules.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing rules...")
        with open(file_path) as f:
            records = json.load(f)
        
        count = 0
        for rec in records:
            try:
                self.create_record('rules', {
                    'type': rec.get('TYPE', 'Frequency Cap'),
                    'metric': rec.get('METRIC', 'Total Messages Sent'),
                    'limit_value': rec.get('LIMIT_VALUE', 50),
                    'time_window_sec': rec.get('TIME_WINDOW_SEC', 3600),
                    'severity': rec.get('SEVERITY'),
                    'assigned_to_user': self.id_maps.get('operators', {}).get(rec.get('ASSIGNED_TO_OPR')),
                    'assigned_to_actor': self.id_maps.get('actors', {}).get(rec.get('ASSIGNED_TO_ACT')),
                    'status': rec.get('STATUS', 'Active'),
                    'suggested_by': self.id_maps.get('operators', {}).get(rec.get('SUGGESTED_BY'))
                })
                count += 1
            except Exception as e:
                print(f"    Warning: Failed to import rule: {e}")
        
        print(f"    Imported {count} rules")
    
    def _import_event_logs(self, data_dir: str):
        """Import event logs."""
        file_path = os.path.join(data_dir, 'event_logs.json')
        if not os.path.exists(file_path):
            return
        
        print("  Importing event logs...")
        with open(file_path) as f:
            records = json.load(f)
        
        # Also load outreach logs for matching
        outreach_file = os.path.join(data_dir, 'outreach_logs.json')
        outreach_map = {}
        if os.path.exists(outreach_file):
            with open(outreach_file) as f:
                for ol in json.load(f):
                    outreach_map[ol.get('ELG_ID')] = ol
        
        self.id_maps['event_logs'] = {}
        count = 0
        outreach_count = 0
        
        for rec in records:
            try:
                new_rec = self.create_record('event_logs', {
                    'event_type': rec.get('EVENT_TYPE', 'Outreach'),
                    'actor': self.id_maps.get('actors', {}).get(rec.get('ACT_ID')),
                    'user': self.id_maps.get('operators', {}).get(rec.get('OPR_ID')),
                    'target': self.id_maps.get('targets', {}).get(rec.get('TAR_ID')),
                    'details': rec.get('DETAILS'),
                    'source': 'instagram'
                })
                self.id_maps['event_logs'][rec['ELG_ID']] = new_rec['id']
                count += 1
                
                # Check for matching outreach log
                if rec['ELG_ID'] in outreach_map:
                    ol = outreach_map[rec['ELG_ID']]
                    self.create_record('outreach_logs', {
                        'event': new_rec['id'],
                        'message_text': ol.get('MESSAGE_TEXT'),
                        'sent_at': ol.get('SENT_AT')
                    })
                    outreach_count += 1
                    
            except Exception as e:
                print(f"    Warning: Failed to import event log: {e}")
        
        print(f"    Imported {count} event logs, {outreach_count} outreach logs")
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


def main():
    print("=" * 60)
    print("CRM-Tableturnerr: PocketBase Data Import")
    print("=" * 60)
    
    # Validate configuration
    if not all([PB_ADMIN_EMAIL, PB_ADMIN_PASSWORD]):
        print("\nError: Missing PocketBase admin credentials.")
        print("Please set the following environment variables:")
        print("  - PB_ADMIN_EMAIL")
        print("  - PB_ADMIN_PASSWORD")
        sys.exit(1)
    
    print(f"\nPocketBase URL: {POCKETBASE_URL}")
    print(f"Data directory: {DATA_DIR}")
    
    # Check if data exists
    if not os.path.exists(DATA_DIR):
        print("\nError: No exported data found.")
        print("Please run the export scripts first:")
        print("  python tools/migration/export_from_appwrite.py")
        print("  python tools/migration/export_from_oracle.py")
        sys.exit(1)
    
    # Create importer
    try:
        importer = PocketBaseImporter(POCKETBASE_URL, PB_ADMIN_EMAIL, PB_ADMIN_PASSWORD)
    except Exception as e:
        print(f"\nError connecting to PocketBase: {e}")
        print("Make sure PocketBase is running and credentials are correct.")
        sys.exit(1)
    
    try:
        # Import data
        importer.import_appwrite_data()
        importer.import_oracle_data()
        
        print("\n" + "=" * 60)
        print("Import Complete!")
        print("=" * 60)
        
    finally:
        importer.close()


if __name__ == '__main__':
    main()
