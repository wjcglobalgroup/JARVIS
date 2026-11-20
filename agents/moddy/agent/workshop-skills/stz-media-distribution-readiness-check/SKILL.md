---
name: stz-media-distribution-readiness-check
description: Verify all STZ media distribution prerequisites before publishing — Composio toolkits, OAuth connections, scheduled jobs, authorization, escalation channels, Notion handoff.
---

# STZ Media Distribution Readiness Check

## Trigger
Need to verify all publishing prerequisites before executing any STZ media distribution workflow (short-form video at 10:20 PHT, text-and-image at 00/06/12/18 PHT, or event-driven engagement). Run this check at session start or before any publishing attempt.

## Produces
A complete readiness report with PASS/FAIL per category, specific blockers identified, and ordered remediation steps.

## Steps

### 1. Verify Composio SDK connectivity and toolkit availability
```javascript
import { Composio } from '@composio/core';
const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });
const toolkits = await composio.toolkits.getMany(['youtube', 'instagram', 'facebook', 'discord', 'twitter', 'notion']);
```
Check: Each returns toolkit metadata with `composioManagedAuthSchemes: ['OAUTH2']` (except twitter: `[]`).
**Critical:** Binance Square has NO toolkit — document as limitation.

### 2. Verify OAuth connections for all target platforms (WSL CLI authoritative for Moddy runtime)
```bash
# Authoritative check via WSL CLI
wsl.exe -e bash -c "/home/dizon/.local/bin/composio connections list"
```
Check: Returns JSON with ACTIVE connections for:
- youtube: youtube_puck-asuri (ACTIVE)
- instagram: instagram_tec-bought (ACTIVE, alias: stz, MEDIA_CREATOR)
- facebook: facebook_simmon-enate (ACTIVE, alias: STZ PAGE)
- googledrive: googledrive_swale-jumper (ACTIVE, Will Cy)
- googlecalendar: googlecalendar_chopa-begone (ACTIVE, owner)
If empty or missing platforms → BLOCKER: Owner must authorize via OAuth.

### 3. Per-platform read-only verification via WSL CLI proxy
```bash
# Instagram media retrieval
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url,timestamp&limit=5' --toolkit instagram --account instagram_tec-bought --method GET"

# Google Drive files
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://www.googleapis.com/drive/v3/files?q=trashed=false&fields=files(id,name,mimeType,modifiedTime,size,webViewLink)&pageSize=5&orderBy=modifiedTime desc' --toolkit googledrive --account googledrive_swale-jumper --method GET"

# Google Calendar events (PHT timezone)
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=2026-11-01T00:00:00Z&timeMax=2026-11-08T00:00:00Z&singleEvents=true&orderBy=startTime&maxResults=10&timeZone=Asia/Manila' --toolkit googlecalendar --account googlecalendar_chopa-begone --method GET"

# Facebook Page: get Page access token then test
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://graph.facebook.com/v18.0/me/accounts' --toolkit facebook --account facebook_simmon-enate --method GET"
# Use returned Page access_token in subsequent calls: access_token=<page_token>
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://graph.facebook.com/v18.0/106487954533737/posts?limit=5&fields=id,message,created_time,permalink_url&access_token=***' --toolkit facebook --account facebook_simmon-enate --method GET"

# YouTube: test after quota reset (1:00 PM PHT daily)
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true' --toolkit youtube --account youtube_puck-asuri --method GET"
```
Check: Each platform returns expected data structure.

### 4. Check scheduled publishing jobs status
Use `automations` tool: `list(includeDisabled: true)`
Check these jobs exist and their status:
| Job ID | Name | Schedule (PHT) | Required State |
|--------|------|----------------|----------------|
| `355fef67-...` | moddy-daily-short-video-publishing | 20 10 * * * (10:20 AM) | ENABLED |
| `fc5d1a0f-...` | moddy-scheduled-publishing | 0 0,6,12,18 * * * (00/06/12/18) | ENABLED |
| (missing) | Moddy heartbeat | ~30 min (stagger ~:25) | CREATE if missing |
Check: `enabled: true`, `lastRunStatus: ok`, no recurring errors.

### 4. Verify STZ authorization mechanism
- Check MEMORY.md for `STZ authorization mechanism: NOT VERIFIED` status
- Coordinate with JARVIS to confirm `AUTHORIZED_PUBLISH` webhook/endpoint exists
- Without explicit authorization, ALL publishing is BLOCKED per policy

### 5. Verify escalation channels
- Test JARVIS webhook delivery (if configured)
- Confirm Discord channel ID for owner notifications (not `channel:gateway-owner`)
- Use `message` tool with valid Discord target: `<channelId|user:ID|channel:ID>` format
- If both unverified → BLOCKER: Cannot alert on failures

### 6. Check Notion Task/Mission page accessibility
```javascript
// Via Notion MCP or web_fetch
const response = await fetch('https://app.notion.com/p/4ce0c5cb5a6348ce9ae0b6bc184d6816');
```
Check: Returns task content (not login shell). If auth-gated → BLOCKER: Cannot locate `READY_FOR_MODDY` content.
**Current status:** Notion plugin enabled in Gateway but Moddy runtime has no MCP client tool — cannot read Task/Mission database.

### 7. Compile readiness report
Output format:
```
STZ MEDIA DISTRIBUTION READINESS REPORT
========================================
Timestamp: <ISO8601>

✅ PASS / ❌ FAIL / ⚠️ WARNING per category:
- Composio SDK: PASS/FAIL
- Toolkit Availability: PASS/FAIL (list missing)
- OAuth Connections: PASS/FAIL (list missing platforms)
- Scheduled Jobs: PASS/FAIL (list job status)
- STZ Authorization: PASS/FAIL
- Escalation Channels: PASS/FAIL
- Notion Handoff: PASS/FAIL

BLOCKERS (must resolve before publishing):
1. <specific blocker>
2. <specific blocker>
...

REMEDIATION ORDER:
1. <highest priority action>
2. <next action>
...
```

## Standing Preferences
- Run this check at session start before ANY publishing workflow
- Never proceed to publishing with any BLOCKER unresolved
- Document Binance Square limitation in every report
- Share authorization URLs only in private operator context
- Treat current exec surface as authoritative for CLI/SDK checks

## References
- Composio SDK: @composio/core@0.27.0+
- Legacy CLI: composio-core@0.5.39 (deprecated, DO NOT USE)
- Working WSL CLI: /home/dizon/.local/bin/composio (v0.5.0+)
- Notion Task/Mission page: https://app.notion.com/p/4ce0c5cb5a6348ce9ae0b6bc184d6816
- Composio dashboard: https://app.composio.dev
- STZ authorization: coordinate with JARVIS
- Skills: moddy-social-media-management (publishing workflows), event-driven-social-security (engagement layer)