---
name: moddy-production-readiness-audit
description: Full diagnostic of Moddy operational readiness for autonomous social media publishing and community management. Run at onboarding, after major changes, or when publishing fails repeatedly.
---

# Moddy Production Readiness Audit

## Trigger
Need a full diagnostic of Moddy's operational readiness for autonomous social media publishing and community management. Run at onboarding, after major changes, or when publishing fails repeatedly.

## Produces
A complete readiness report: overall status (READY/PARTIALLY READY/NOT READY), findings by severity (CRITICAL/HIGH/MEDIUM/LOW), evidence with file references, fixes applied, broken integrations, platform-by-platform status, exact blockers, and ordered next actions.

## Steps

### 1. Workspace audit — inspect instruction files, skills, configs, memory, scheduled tasks
```bash
# List workspace root
ls C:\Users\dizon\.openclaw\workspace-moddy

# Read core instruction files
read AGENTS.md
read SOUL.md
read IDENTITY.md
read USER.md
read HEARTBEAT.md
read DREAMS.md
read MEMORY.md

# List skills directories
ls C:\Users\dizon\.openclaw\workspace-moddy\skills
ls C:\Users\dizon\.openclaw\workspace-moddy\.agents
ls C:\Users\dizon\.openclaw\workspace-moddy\memory

# Read each skill's SKILL.md
read skills/moddy-social-media-management/SKILL.md
read skills/event-driven-social-security/SKILL.md
```
Check: All files present, no conflicting instructions, SOUL/AGENTS/IDENTITY/USER aligned, skills load without error.

### 2. Publishing audit — verify platform integrations (YouTube, Instagram, Facebook, Binance Square, Discord, X)
```bash
# Verify Composio SDK connectivity
node test-targeted.mjs

# Check OAuth connections via WSL CLI (authoritative for Moddy runtime)
wsl.exe -e bash -c "/home/dizon/.local/bin/composio connections list"

# Verify WSL CLI availability and auth
wsl.exe -e bash -c "/home/dizon/.local/bin/composio --version"
wsl.exe -e bash -c "/home/dizon/.local/bin/composio whoami"

# Per-platform read-only test via WSL CLI proxy
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url,timestamp&limit=5' --toolkit instagram --account instagram_tec-bought --method GET"
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://www.googleapis.com/drive/v3/files?q=trashed=false&fields=files(id,name,mimeType,modifiedTime,size,webViewLink)&pageSize=5&orderBy=modifiedTime desc' --toolkit googledrive --account googledrive_swale-jumper --method GET"
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=2026-11-01T00:00:00Z&timeMax=2026-11-08T00:00:00Z&singleEvents=true&orderBy=startTime&maxResults=10&timeZone=Asia/Manila' --toolkit googlecalendar --account googlecalendar_chopa-begone --method GET"

# Facebook: retrieve Page access token then test
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://graph.facebook.com/v18.0/me/accounts' --toolkit facebook --account facebook_simmon-enate --method GET"
# Use returned Page access_token in subsequent calls: access_token=<page_token>

# YouTube: test after quota reset (1:00 PM PHT daily)
wsl.exe -e bash -c "/home/dizon/.local/bin/composio proxy 'https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true' --toolkit youtube --account youtube_puck-asuri --method GET"
```
Check per platform:
| Platform | Toolkit Available | OAuth Connected (WSL CLI) | Triggers | Publishing Ready |
|----------|-------------------|---------------------------|----------|------------------|
| YouTube | ✅ OAUTH2, 4 triggers | ✅ youtube_puck-asuri (ACTIVE) | ✅ | quota + auth |
| Instagram | ✅ OAUTH2, 0 triggers | ✅ instagram_tec-bought (ACTIVE, MEDIA_CREATOR) | ⚠️ polling only | requires auth |
| Facebook | ✅ OAUTH2, 0 triggers | ✅ facebook_simmon-enate (ACTIVE, STZ PAGE) | ⚠️ polling only | requires Page token + auth |
| Binance Square | ❌ NO toolkit | N/A | N/A | ❌ no integration |
| Discord | ✅ OAUTH2, 1 trigger | items[] contains discord | ✅ | requires auth |
| X (Twitter) | ✅ OAUTH2, 0 triggers | items[] contains twitter | N/A | requires auth |
Critical: Binance Square has NO Composio toolkit — document as hard limitation.
Critical: Facebook Page operations require explicit Page access token via `/me/accounts` — Composio proxy does not auto-swap user→Page tokens.
Critical: YouTube quota resets 1:00 PM PHT daily (midnight Pacific Time).

### 3. Community management audit — Discord, comments, DMs, customer support
```bash
# Check event-driven skill deployment
ls skills/event-driven-social-security/src/handlers/

# Verify webhook server code exists
read skills/event-driven-social-security/src/webhook-server.ts

# Check security layer
read skills/event-driven-social-security/src/security/injection-defense.ts
read skills/event-driven-social-security/src/security/dedupe.ts
read skills/event-driven-social-security/src/security/rate-limiter.ts
```
Check:
- Event handlers exist for Discord, YouTube, Instagram, Facebook, Binance Square (stub)
- Prompt injection defense: ALLOWED_EVENT_TYPES, ALLOWED_ACTIONS, SENSITIVE_ACTIONS enforced
- Idempotency: dedupe store with 24h TTL, content hash
- Rate limiting: per-platform buckets (Discord 5/min, YouTube 3/hr, Instagram 20/hr, Facebook 20/hr)
- Webhook signature verification: Discord Ed25519, Meta HMAC-SHA256, YouTube HMAC-SHA1
- Templates only (no LLM) for auto-replies; LLM requires explicit enable
- Escalation to JARVIS for security incidents, system errors, blocked actions

### 4. Content pipeline audit — Marco → Vera → Moddy → Publishing
```bash
# Check scheduled jobs for each agent
automations list(includeDisabled: true)

# Verify handoff states in MEMORY.md / skills
read MEMORY.md
```
Check:
- Marco daily research: 08:20 PHT (job `02b34d71-...`)
- Vera script production: 09:20 PHT (job `d9912b46-...`)
- Owner uploads rendered video → STZ Task/Mission → READY_FOR_MODDY
- Moddy short-form video: 10:20 PHT (job `355fef67-...`)
- Vera text-image prep: 23:55/05:55/11:55/17:55 PHT (job `9ee12fe4-...`)
- Moddy text-image publish: 00:00/06:00/12:00/18:00 PHT (job `fc5d1a0f-...`)
- State machine: PRODUCTION_READY → READY_FOR_MODDY → MODDY_REVIEW → PUBLISH_READY → AUTHORIZED_PUBLISH → PUBLISHED
- Duplicate prevention: Content ID/version check per platform before publish
- Unknown outcome reconciliation before retry

### 5. Reliability & security audit
```bash
# Check credential handling
read MEMORY.md (look for secrets exposure)

# Check scheduled job health
automations list(includeDisabled: true)
```
Check:
- No secrets in code, logs, prompts, or LLM context (Composio handles auth)
- Least-privilege: Composio tool allowlists per platform (ALLOWED_ACTIONS)
- No admin/delete/permission-change tools enabled
- Audit logging: SecurityAuditEntry for all events, decisions, results
- Failure recovery: Unknown outcome reconciliation, partial success recording
- Scheduled task reliability: Jobs exist, enabled, no recurring errors
- Gateway protection: NEVER stop/restart Gateway (read-only diagnostics only)

### 6. Live verification — distinguish verified vs configured/simulated/untested
For each capability, classify:
- ✅ VERIFIED LIVE: Executed successfully with confirmed result (external ID, URL, timestamp)
- ⚠️ CONFIGURED: Code exists, connections established, but not executed in production
- 🔄 SIMULATED: Dry-run or test mode only
- ❌ UNAVAILABLE: No integration, no toolkit, no API access
- ❓ UNTESTED: Code exists but never run against live platform

Apply to: publishing, comment replies, DM replies, welcome messages, webhook reception, escalation delivery, Notion reads.

### 7. Compile final report
```
MODDY PRODUCTION READINESS AUDIT REPORT
========================================
Timestamp: <ISO8601>

OVERALL READINESS: READY / PARTIALLY READY / NOT READY

FINDINGS BY SEVERITY:
🔴 CRITICAL (<count>): <list with evidence>
🟠 HIGH (<count>): <list with evidence>
🟡 MEDIUM (<count>): <list with evidence>
🟢 LOW (<count>): <list with evidence>

PLATFORM-BY-PLATFORM:
| Platform | Connector | OAuth | Triggers | Publishing | Community | Status |
|----------|-----------|-------|----------|------------|-----------|--------|
| YouTube  | ✅/❌     | ✅/❌ | ✅/❌    | ✅/❌      | ✅/❌     | READY/NOT READY |
| Instagram| ...       | ...   | ...      | ...        | ...       | ...    |
| Facebook | ...       | ...   | ...      | ...        | ...       | ...    |
| Binance  | ...       | ...   | ...      | ...        | ...       | ...    |
| Discord  | ...       | ...   | ...      | N/A        | ...       | ...    |
| X        | ...       | ...   | ...      | N/A        | ...       | ...    |

EXACT BLOCKERS:
1. <blocker> — <evidence> — <resolution>
2. <blocker> — <evidence> — <resolution>
...

FIXES APPLIED:
- <action> — <verification result>

RECOMMENDED NEXT ACTIONS (priority order):
1. <action>
2. <action>
...
```

## Standing Preferences
- Run this audit at session start if publishing failed previously
- Never declare READY with any CRITICAL blocker unresolved
- Document Binance Square limitation in every report
- Distinguish VERIFIED LIVE from CONFIGURED/UNTESTED explicitly
- Share authorization URLs only in private operator context
- Treat current exec surface as authoritative for CLI/SDK checks
- Preserve existing working systems; only fix safe, clearly understood defects
- Do not interrupt or restart OpenClaw Gateway
- WSL CLI (/home/dizon/.local/bin/composio) is the authoritative authenticated surface for Moddy runtime
- Windows SDK (@composio/core) uses different project — returns zero connections
- Facebook Page operations require explicit Page access token via `/me/accounts`
- YouTube quota resets 1:00 PM PHT daily
- Notion Task/Mission access requires MCP client tool in Moddy runtime

## AUTHORIZED_PUBLISH Gate Design (from 2026-11-01 session)
Each approval bound to:
- Owner identity, exact platform, exact destination account, exact operation
- Exact caption/message, exact media asset (hash-verified), exact scheduled time
- Approval timestamp, unique approval ID, expiration/invalidation rule (24h max, single-use nonce)

Permission categories (default: READ + DRAFT only):
READ — Retrieve data
DRAFT — Prepare content without publishing
PUBLISH — Execute specifically approved publishing operations
ENGAGE — Execute specifically approved replies/messages
MODERATE — Execute specifically approved moderation actions
ADMIN — Manage integration configuration and permissions

Gate rejects: missing approval, expired approval, reused nonce, content/media hash mismatch, platform/account/operation/scheduled time mismatch, permission insufficient.

## References
- Skills: moddy-social-media-management (publishing workflows), event-driven-social-security (engagement layer)
- Composio SDK: @composio/core@0.27.0+
- Notion Task/Mission page: https://app.notion.com/p/4ce0c5cb5a6348ce9ae0b6bc184d6816
- STZ authorization: coordinate with JARVIS
- Test scripts: test-targeted.mjs, test-composio2.mjs, test-composio.mjs
- Working WSL CLI: /home/dizon/.local/bin/composio (v0.5.0+)
- Composio dashboard: https://app.composio.dev