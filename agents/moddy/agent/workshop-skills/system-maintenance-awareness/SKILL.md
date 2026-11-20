---
name: system-maintenance-awareness
version: 1.0.0
agent: moddy
category: social-media-operations
dependencies: [calendar-operations, jarvis-coordination, notion-task-mission-management, stz-operational-reporting]
description: Detect, prepare for, and respond to system maintenance windows using Google Calendar and Jarvis coordination.
---

# System Maintenance Awareness Skill

## Purpose
Monitor Google Calendar for STZ system maintenance windows, prepare Moddy operations for pause, execute mandatory pause protocol, and resume only after dual confirmation from Jarvis and Coddy.

## Prerequisites
- Authorized Google Calendar connection (Composio googlecalendar toolkit)
- Calendar monitoring does NOT grant permission to create/modify/delete events
- Notion MCP for Tasks/Missions recording
- Jarvis coordination path verified

## Calendar Monitoring

### Target Calendars
- Primary STZ operations calendar (owner-shared)
- Any calendar with "maintenance", "STZ", "system", "infrastructure" in title
- Events created by Coddy, Jarvis, or Willy

### Event Detection Criteria
Monitor for events with:
- Title containing: maintenance, maintenance window, system maintenance, downtime, upgrade, migration, deployment
- Description mentioning: API, database, gateway, connector, authentication, publishing, content pipeline
- Time window overlapping Moddy publishing slots (10:20 PHT, 00/06/12/18 PHT)
- Attendees including: Coddy, Jarvis, Willy, or STZ infrastructure

### Timezone Handling
- STZ operating timezone: Asia/Manila (PHT, UTC+8)
- Calendar events may be in any timezone
- ALWAYS interpret using event's actual timezone property
- NEVER assume UTC display equals PHT
- Convert using proper timezone-aware conversion

## Maintenance Detection Procedure
```
1. Query Google Calendar for next 7 days:
   - timeMin: now (RFC3339, PHT)
   - timeMax: now + 7 days
   - maxResults: 50
   - orderBy: startTime
2. Filter events matching maintenance criteria
3. For each maintenance event:
   - Extract: title, start, end, timezone, description, attendees
   - Convert start/end to PHT
   - Determine affected Moddy operations
   - Check if overlaps with scheduled publishes
4. Record findings in Tasks/Missions
5. Notify Jarvis per jarvis-coordination skill
```

## Affected Operations Assessment
| Moddy Operation | Affected by Maintenance? |
|---|---|
| Short-form video publishing (10:20 PHT) | Yes if window overlaps 09:00-11:00 PHT |
| Text-and-image publishing (00/06/12/18 PHT) | Yes if window overlaps ±1 hour of slot |
| Community management (comments/DMs) | Yes if API/auth affected |
| Notion reads/writes | Yes if Notion MCP or gateway affected |
| Composio platform APIs | Yes if connector infra affected |
| Drive reads | Yes if Google Workspace affected |
| Calendar reads | Yes if Calendar API affected |

## Mandatory Pause Protocol (4 Phases)

### Phase A — Detect and Prepare
```
When maintenance detected:
1. Confirm window, scope, affected services from event details
2. Notify Jarvis: "Maintenance detected: [event]. Window: [PHT start-end]. Scope: [services]. Affected Moddy ops: [list]"
3. Create/update Tasks/Missions record:
   - Title: "Maintenance pause: [event title]"
   - Pipeline: "maintenance"
   - Status: "In Progress"
   - Blocked Reason: "Scheduled maintenance [event title] [PHT window]; pausing [affected ops]"
   - Related Record ID: Link affected Content Pipeline records
4. Identify content/publishing work affected
5. Preserve pending work state (do not cancel, mark as paused)
```

### Phase B — Pause
```
When maintenance begins OR Jarvis directs pause:
1. STOP affected publishing operations:
   - No new uploads, posts, replies, DMs, moderation
   - No container creation (Instagram, etc.)
   - No platform API write calls
2. STOP community management write operations
3. CONTINUE safe read-only:
   - Calendar monitoring
   - Notion reads (if available)
   - Status reporting
   - Health checks (read-only)
4. Do NOT change or enable disabled automation jobs
5. Do NOT interfere with Coddy's maintenance work
6. Record pause timestamp in Tasks/Missions
```

### Phase C — Wait for Dual Authorization
```
MUST receive completion confirmation from BOTH:
1. Jarvis (operations coordinator)
2. Coddy (engineering/DevOps)

Do NOT resume if either missing.

If conflict:
- Jarvis says complete, Coddy says not -> REMAIN PAUSED, escalate
- Scope unclear -> REMAIN PAUSED, escalate
- Service unhealthy after confirmations -> REMAIN PAUSED, escalate

Escalation: Notify Jarvis AND Willy with details
```

### Phase D — Verify and Resume
```
After BOTH confirmations received:
1. Perform read-only health checks:
   - Composio connections (list, no write)
   - Notion MCP (search/query, no write)
   - Google Calendar (list events)
   - Google Drive (list files)
   - Platform APIs (GET channel/user info)
2. Confirm affected systems available
3. Check queued work:
   - Any Content Pipeline records marked Published during maintenance?
   - Any Tasks/Missions completed by other agents?
   - Check existing Platform Post IDs to prevent duplicates
4. Resume ONLY authorized, ready operations
5. Record in Tasks/Missions:
   - Pause start/end timestamps
   - Both confirmation sources + timestamps
   - Health check results
   - Resumption timestamp
6. Notify Jarvis: "Moddy resumed. Health checks: [results]. Resumed ops: [list]"
```

## Critical Rules
- NEVER resume based on elapsed time alone
- NEVER resume based on calendar event end time alone
- NEVER resume based on single agent confirmation
- ALWAYS verify health before resuming
- ALWAYS check for duplicate prevention before resuming publishes
- ALWAYS record full audit trail in Notion

## Failure Handling
| Condition | Action |
|---|---|
| Calendar not accessible | Escalate to Jarvis, use last known schedule |
| Maintenance event ambiguous | Clarify with Jarvis before acting |
| Jarvis/Coddy confirmation conflict | Remain paused, escalate to Willy |
| Service unhealthy post-maintenance | Remain paused, report specifics to Jarvis |
| Duplicate publish risk | Check all Platform Post IDs before any resume |

## Verification Requirements
- Health check results logged
- Both confirmations recorded with timestamps
- Resumption reported to Jarvis
- All via stz-operational-reporting

## Practical Example
```
# Detect maintenance
events = list_calendar_events(time_min=now, time_max=now+7d)
maintenance = filter_maintenance_events(events)

for event in maintenance:
  pht_start = convert_to_pht(event.start, event.timezone)
  pht_end = convert_to_pht(event.end, event.timezone)
  affected = assess_affected_ops(pht_start, pht_end)
  
  notify_jarvis({
    event: event.title,
    window: f"{pht_start} - {pht_end} PHT",
    scope: event.description,
    affected_ops: affected
  })
  
  create_mission({
    title: f"Maintenance pause: {event.title}",
    blocked_reason: f"Maintenance {pht_start}-{pht_end} PHT; pausing {affected}",
    pipeline: "maintenance"
  })

# When maintenance starts -> Phase B pause
# Wait for Jarvis + Coddy confirmations -> Phase C
# Health checks -> Phase D resume
```