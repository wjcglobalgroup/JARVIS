---
name: composio-connection-verification
description: Verify Composio CLI availability, version, and auth on any exec surface — check whoami, list connections, confirm connected platforms.
---

# Composio Connection Verification

## Trigger
Need to verify which social media platforms are connected to Composio before running publishing workflows (YouTube, Instagram, Facebook Page, Binance Square, Discord, X).

## Produces
A confirmed list of connected platforms with ACTIVE status, or a clear statement of which platforms need reconnection via the Composio dashboard.

## Pre-flight checks (every run)

1. Check CLI availability on the current exec surface:
   command -v composio
   Check: Returns a path. If empty, the Composio CLI is not installed — stop and ask the operator.

2. Check CLI version:
   composio --version
   Check: Returns a version number ≥ 0.4.0. If --version is not supported, check the installed package version (e.g., package.json version field or composio --help output).

3. Check CLI auth status:
   composio whoami
   Check: Returns account email, org, and account_type. Empty output or nonzero exit means signed out — stop and ask the operator before proceeding.

4. List active connections (WSL CLI is authoritative for Moddy runtime):
   wsl.exe -e bash -c "/home/dizon/.local/bin/composio connections list"
   Check: Returns JSON with toolkit arrays. Look for these platforms with "status": "ACTIVE":
   - youtube (youtube_puck-asuri)
   - instagram (instagram_tec-bought, alias: stz)
   - facebook (facebook_simmon-enate, alias: STZ PAGE)
   - googledrive (googledrive_swale-jumper)
   - googlecalendar (googlecalendar_chopa-begone)
   If a platform is missing or shows EXPIRED/FAILED, it needs reconnection.
   The Windows SDK returns zero connections (different project); WSL CLI is the authenticated surface.

5. Verify per-platform tool availability (optional but recommended):
   wsl.exe -e bash -c "/home/dizon/.local/bin/composio tools list youtube"
   wsl.exe -e bash -c "/home/dizon/.local/bin/composio tools list instagram"
   wsl.exe -e bash -c "/home/dizon/.local/bin/composio tools list facebook"
   wsl.exe -e bash -c "/home/dizon/.local/bin/composio tools list googledrive"
   wsl.exe -e bash -c "/home/dizon/.local/bin/composio tools list googlecalendar"
   Check: Each returns a non-empty array of tool slugs.

## Known issues

- YouTube API quota may be exceeded (Google 403) — this is a Google-side rate limit, not a Composio connection issue. Quota resets at 16:00 PHT daily (midnight Pacific Time). Do not repeatedly retry; wait for reset.
- Some CLI builds do not support --version. If composio --version returns an error, check the installed package version instead (package.json version field or composio --help output).
- The legacy Windows CLI (composio-core@0.5.39) may crash on connection listing and app management. If composio connections list or composio tools list fails on the current surface, retry via WSL: wsl.exe -e bash -c "/home/dizon/.local/bin/composio <command>".
- The working WSL CLI is at /home/dizon/.local/bin/composio (v0.6.0, installed via official installer).
- Facebook Page operations require explicit Page access token: Composio proxy does not auto-swap user→Page tokens. Retrieve via `/me/accounts` then pass `access_token=<page_token>` in API calls.
- Windows SDK (@composio/core) uses different project/API key — returns zero connections. WSL CLI is the authenticated surface for Moddy runtime.

## Standing preferences

- Ask the trusted operator before installing, upgrading, or signing in to Composio CLI.
- Share authorization URLs only in a private operator context, never in chat.
- Never replay an uncertain write through another surface.
- Treat the current exec surface as authoritative for CLI checks.
- If the current surface CLI fails for connection listing or tool verification, retry via WSL: wsl.exe -e bash -c "/home/dizon/.local/bin/composio <command>".
- If the current surface CLI returns authenticated but a platform shows EXPIRED/FAILED, that specific platform needs reconnection via the Composio dashboard (https://app.composio.dev).

## References
- Working WSL CLI: /home/dizon/.local/bin/composio (v0.6.0, installed via official installer)
- Windows CLI: C:\Users\dizon\AppData\Roaming\npm\composio.ps1 (proxies to WSL v0.6.0; whoami, version, and execute work; connection listing via WSL)
- Composio dashboard: https://app.composio.dev (for adding/reconnecting platforms)
- Composio base URL: https://backend.composio.dev
- Authenticated account: wilcycrypto05@gmail.com / org wilcycrypto05_workspace
