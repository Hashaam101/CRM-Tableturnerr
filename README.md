# CRM-Tableturnerr

Unified CRM System combining Cold Call Monitoring and Instagram Outreach.

## Structure

```
CRM-Tableturnerr/
├── packages/
│   └── pocketbase-client/     # Shared PocketBase SDK wrapper
├── apps/
│   ├── dashboard/             # Unified Next.js dashboard
│   └── insta-outreach-agent/  # Python desktop agent + Chrome extension
└── tools/
    ├── audio-recorder/        # PyQt recording app
    ├── transcriber/           # Cold call transcription service
    └── migration/             # Data migration scripts
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pnpm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your PocketBase credentials
   ```

3. **Start PocketBase:**
   ```bash
   # Ensure PocketBase is running at http://localhost:8090
   ```

4. **Run dashboard:**
   ```bash
   cd apps/dashboard
   pnpm dev
   ```

## Components

- **Dashboard**: Unified web interface for cold calls + Instagram outreach
- **Insta Outreach Agent**: Desktop app for stealth Instagram DM logging
- **Audio Recorder**: Record cold calls with hotkey support
- **Transcriber**: AI-powered call transcription using Gemini

## License

MIT
