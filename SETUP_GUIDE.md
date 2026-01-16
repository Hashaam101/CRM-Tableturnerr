# CRM-Tableturnerr: Setup & Testing Guide

> Complete guide to set up and test the unified CRM after all agents have completed their tasks.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [PocketBase Setup](#2-pocketbase-setup)
3. [Import Schema](#3-import-schema)
4. [Seed Sample Data](#4-seed-sample-data)
5. [Dashboard Setup](#5-dashboard-setup)
6. [Transcriber Setup](#6-transcriber-setup)
7. [Testing Checklist](#7-testing-checklist)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

### Required Software
- **Node.js** v18+ (with pnpm)
- **Python** 3.10+
- **PocketBase** (self-hosted)

### Verify Installation
```bash
node --version    # Should be v18+
pnpm --version    # Should be v8+
python --version  # Should be 3.10+
```

---

## 2. PocketBase Setup

### Option A: Local PocketBase
1. Download PocketBase from https://pocketbase.io/docs
2. Extract to a folder (e.g., `C:\PocketBase`)
3. Run:
   ```bash
   cd C:\PocketBase
   pocketbase serve
   ```
4. Access Admin UI at http://127.0.0.1:8090/_/

### Option B: Remote PocketBase (Already Running)
- Ensure you have admin access to your PocketBase instance
- Default URL: `http://192.168.55.140:8090`

### Create Admin Account
1. Go to the PocketBase Admin UI
2. Create your first admin account with email and password
3. **Save these credentials** - you'll need them for the `.env` files

---

## 3. Import Schema

### Step-by-Step
1. Open PocketBase Admin UI (`http://your-pocketbase-url/_/`)
2. Log in with your admin credentials
3. Go to **Settings** → **Import Collections**
4. Click **Load from JSON file**
5. Select: `packages/pocketbase-client/pb_schema.json`
6. Click **Review** then **Confirm and import**

### Verify Collections
After import, you should see these collections:
- `users` (auth collection)
- `companies`
- `leads`
- `cold_calls`
- `call_transcripts`
- `insta_actors`
- `event_logs`
- `outreach_logs`
- `notes`
- `alerts`
- `goals`
- `rules`

---

## 4. Seed Sample Data

### Configure Environment
Create `.env` in `tools/migration/`:
```bash
cd tools/migration
copy ..\..\.env.example .env
```

Edit `.env` with your credentials:
```env
POCKETBASE_URL=http://192.168.55.140:8090
PB_ADMIN_EMAIL=your_admin_email
PB_ADMIN_PASSWORD=your_admin_password
```

### Install Dependencies
```bash
cd tools/migration
pip install httpx python-dotenv
```

### Run Seeder
```bash
python seed_data.py
```

### Expected Output
```
============================================================
CRM-Tableturnerr: Seed Sample Data
============================================================
🔑 Authenticating with PocketBase...
   ✓ Authenticated successfully

👥 Creating users...
   ✓ Created user: Admin User
   ✓ Created user: Sarah Johnson
   ✓ Created user: Mike Chen
   ✓ Created user: Emma Davis

🏢 Creating companies...
   ✓ Created company: Sunrise Restaurant
   ✓ Created company: Golden Gate Bistro
   ...

📞 Creating cold calls and transcripts...
   ✓ Created cold call: +1-310-555-0101 (Interested)
      → Created transcript
   ...

✅ Seeding Complete!
```

### Verify in PocketBase
1. Go to Admin UI → Collections
2. Check `companies` - should have 5 records
3. Check `cold_calls` - should have 4 records
4. Check `call_transcripts` - should have 4 records

---

## 5. Dashboard Setup

### Install Dependencies
```bash
cd apps/dashboard
pnpm install
```

### Configure Environment
Create `.env.local`:
```bash
copy .env.example .env.local
```

Edit with your PocketBase URL:
```env
NEXT_PUBLIC_POCKETBASE_URL=http://192.168.55.140:8090
```

### Start Development Server
```bash
pnpm dev
```

### Access Dashboard
Open http://localhost:3000 in your browser.

---

## 6. Transcriber Setup

### Install Dependencies
```bash
cd tools/transcriber
pip install -r requirements.txt
```

### Configure Environment
```bash
copy .env.example .env
```

Edit `.env`:
```env
POCKETBASE_URL=http://192.168.55.140:8090
PB_ADMIN_EMAIL=your_admin_email
PB_ADMIN_PASSWORD=your_admin_password
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

### Get Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add to your `.env` file

### Test Transcriber (Dry Run)
```bash
python transcribe_calls.py test_audio.mp3 --dry-run
```

---

## 7. Testing Checklist

### 7.1 Dashboard Pages

#### Overview Page (/)
- [ ] Stats cards display (Total Companies, Calls, Leads, Team)
- [ ] Recent activity shows events
- [ ] Navigation sidebar works

#### Cold Calls Page (/cold-calls)
- [ ] Table displays seeded calls
- [ ] Click "View" opens detail page
- [ ] Filters work (outcome, interest level)
- [ ] CSV export downloads file
- [ ] Sorting works on all columns

#### Cold Call Detail (/cold-calls/[id])
- [ ] Header shows company info, phone, date
- [ ] AI analysis displays (objections, pain points, follow-ups)
- [ ] Transcript expands/collapses
- [ ] Copy phone button works
- [ ] Company info card links work

#### Companies Page (/companies)
- [ ] All companies display in table
- [ ] Search filters results
- [ ] Inline edit works (click edit, modify, save)
- [ ] "Add Company" modal opens and creates new company
- [ ] Source badges display correctly
- [ ] Click company shows related calls in drawer

#### Leads Page (/leads)
- [ ] Leads display with status badges
- [ ] Filters work
- [ ] Status change dropdown works

#### Notes Page (/notes)
- [ ] Notes list displays
- [ ] Create new note works
- [ ] Archive/delete works
- [ ] Restore from recycle bin works

### 7.2 Transcriber Service

#### Prerequisites
- [ ] Gemini API key configured
- [ ] PocketBase running and accessible
- [ ] Sample audio file ready

#### Test Flow
```bash
cd tools/transcriber

# Test with dry-run (no DB save)
python transcribe_calls.py sample.mp3 --dry-run --json

# Test with DB save
python transcribe_calls.py sample.mp3 --phone "+1-555-0000"
```

#### Verify
- [ ] Script outputs parsed JSON
- [ ] New company created (if phone doesn't exist)
- [ ] New cold_call record in PocketBase
- [ ] New transcript linked to call
- [ ] Appears in Dashboard cold-calls page

### 7.3 Cross-System Integration

- [ ] Transcriber creates records visible in Dashboard
- [ ] Companies page shows all sources (Cold Call, Instagram, Manual)
- [ ] Real-time updates work (may need page refresh)
- [ ] No console errors in browser

---

## 8. Troubleshooting

### "Connection refused" Error
- **Cause**: PocketBase not running
- **Fix**: Start PocketBase server
  ```bash
  pocketbase serve
  ```

### "Missing collection context" Error
- **Cause**: Schema not imported
- **Fix**: Import `pb_schema.json` via Admin UI

### "Authentication failed" Error
- **Cause**: Wrong admin credentials
- **Fix**: Verify email/password in `.env`

### Dashboard shows empty data
- **Cause**: Sample data not seeded
- **Fix**: Run `python tools/migration/seed_data.py`

### "Module not found" in Python
- **Cause**: Dependencies not installed
- **Fix**: 
  ```bash
  pip install httpx python-dotenv google-generativeai
  ```

### pnpm command not found
- **Fix**: Install pnpm globally
  ```bash
  npm install -g pnpm
  ```

### Build fails with TypeScript errors
- **Fix**: 
  ```bash
  cd apps/dashboard
  pnpm install
  pnpm build
  ```

---

## Quick Reference

### URLs
| Service | URL |
|---------|-----|
| PocketBase Admin | http://192.168.55.140:8090/_/ |
| Dashboard | http://localhost:3000 |

### Default Test Credentials
| Email | Password | Role |
|-------|----------|------|
| admin@tableturnerr.com | Password123! | Admin |
| sarah@tableturnerr.com | Password123! | Operator |
| mike@tableturnerr.com | Password123! | Operator |

### Key Commands
```bash
# Start Dashboard
cd apps/dashboard && pnpm dev

# Seed Data
cd tools/migration && python seed_data.py

# Transcribe Audio
cd tools/transcriber && python transcribe_calls.py <audio.mp3>

# Build Dashboard
cd apps/dashboard && pnpm build
```

---

## Next Steps

After completing setup and testing:

1. **Production Deployment**: Set up proper domain and SSL
2. **User Management**: Create real user accounts in PocketBase
3. **Audio Recorder**: Set up the desktop audio recorder (apps/audio-recorder)
4. **Instagram Agent**: Configure the Instagram outreach agent

---

*Last updated: January 2026*
