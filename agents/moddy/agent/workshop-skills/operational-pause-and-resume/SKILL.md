---
name: operational-pause-and-resume
version: 1.0.0
agent: moddy
category: social-media-operations
dependencies: [system-maintenance-awareness, jarvis-coordination, notion-task-mission-management, stz-operational-reporting]
description: Execute the mandatory pause and resume protocol for Moddy operations during system maintenance.
---

# Operational Pause and Resume Skill

## Purpose
Execute the 4-phase mandatory pause/resume protocol for Moddy publishing and community operations during system maintenance. This skill operationalizes the protocol defined in system-maintenance-awareness.

## Prerequisites
- Maintenance detected via calendar-operations or Jarvis notification
- Notion MCP for Tasks/Missions recording
- Jarvis coordination path verified
- Composio platform connections for health checks

## Phase A — Detect and Prepare (Entry Point: `prepare_for_maintenance`)
```
Input: maintenance_event (from calendar or Jarvis)

1. Parse event:
   - title, description, start, end, timezone, attendees
   - Convert start/end to PHT
2. Assess affected Moddy operations:
   - Publishing slots in window ±1 hour
   - Community management if API/auth affected
   - Notion/Drive/Calendar access if gateway affected
3. Notify Jarvis (jarvis-coordination):
   "Maintenance preparation: [title]. Window: [PHT start]-[PHT end]. Scope: [description]. Affected ops: [list]"
4. Create Tasks/Missions record:
   - Title: "Maintenance pause: [title]"
   - Mission ID: MAINT-YYYYMMDD-###
   - Pipeline: "maintenance"
   - Status: "In Progress"
   - Blocked Reason: "Scheduled maintenance [title] [PHT window]; pausing [affected ops]"
   - Related Record IDs: Affected Content Pipeline records
   - Due Date: Maintenance end (PHT)
5. Preserve pending work:
   - For each affected Content Pipeline record: note current status
   - Do NOT change statuses to Blocked unless actually blocked
   - Record pause state in Mission description
```

## Phase B — Pause (Entry Point: `execute_pause`)
```
Trigger: Maintenance start time reached OR Jarvis directs pause

1. STOP affected write operations:
   - No platform publishing (upload, post, container create, publish)
   - No community engagement (reply, DM, moderate)
   - No Drive/Calendar writes
   - No Notion writes (Content Pipeline, Tasks/Missions updates still allowed for tracking)
2. CONTINUE safe read-only:
   - Calendar monitoring (this skill)
   - Notion reads (status checks)
   - Composio connection health (list only)
   - Status reporting to Jarvis
3. Record pause execution:
   - Update Tasks/Missions: add pause timestamp
   - Set Status = "In Progress" (pause in progress)
4. Do NOT:
   - Enable disabled automation jobs
   - Reconnect OAuth
   - Modify Coddy's maintenance work
   - Cancel queued work (preserve state)
```

## Phase C — Wait for Dual Authorization (Entry Point: `await_resume_authorization`)
```
MUST receive from BOTH:
1. Jarvis: Operations coordinator confirmation
2. Coddy: Engineering/DevOps confirmation

Wait loop:
- Check for confirmations every 5 minutes
- Log each check in Tasks/Missions
- If only one received after 30 min: notify Jarvis
- If conflict: REMAIN PAUSED, escalate to Jarvis + Willy
- If scope unclear: REMAIN PAUSED, escalate
- If service unhealthy: REMAIN PAUSED, report specifics

Record:
- Jarvis confirmation timestamp + message
- Coddy confirmation timestamp + message
- Any conflicts or ambiguities
```

## Phase D — Verify and Resume (Entry Point: `verify_and_resume`)
```
After BOTH confirmations received:

1. Health Checks (read-only):
   a. Composio: list connections, verify all 5 toolkits connected
   b. Notion MCP: search/query test (if exposed)
   c. Google Calendar: list next 24h events
   d. Google Drive: list STZ Content folder
   e. Platform APIs: GET channel/user info for YouTube, Instagram, Facebook

2. Verify affected systems available:
   - All health checks pass
   - No error rates above threshold

3. Check queued work for duplicates:
   - Query Content Pipeline for records with status Published during maintenance
   - Check Platform Post IDs already recorded
   - Check Tasks/Missions for completions by other agents

4. Resume authorized operations:
   - Only operations with valid AUTHORIZED_PUBLISH
   - Only operations with ready content (Content Pipeline = Ready to Publish)
   - Only operations within scheduled windows

4. Record resumption:
   - Update Tasks/Missions:
     - Status = "Completed"
     - Result: "Pause: [start]-[end] PHT. Jarvis confirm: [ts]. Coddy confirm: [ts]. Health: [results]. Resumed: [ops]. Duplicates checked: [count]."
   - Clear Blocked Reason

5. Notify Jarvis: "Moddy resumed. Health: [pass/fail per service]. Resumed ops: [list]. Next scheduled: [next publish]"
```

## Critical Rules
- NEVER resume on elapsed time alone
- NEVER resume on calendar event end alone
- NEVER resume on single confirmation
- ALWAYS verify health before resume
- ALWAYS check duplicates before resume
- ALWAYS record full audit trail

## Failure Handling
| Condition | Action |
|---|---|
| Health check fails | Remain paused, report specifics to Jarvis |
| Duplicate publish risk | Check ALL Platform Post IDs, escalate ambiguous |
| Jarvis/Coddy conflict | Remain paused, escalate to Willy |
| Service partially healthy | Resume only healthy services, report degraded |
| No confirmations after 2hr | Escalate to Willy via Jarvis |

## Verification Requirements
- Health check results logged per service
- Both confirmations recorded with exact timestamps
- Duplicate check results recorded
- Resumption reported to Jarvis
- All via stz-operational-reporting

## Practical Example
```
# Phase A
event = get_maintenance_event()
affected = assess_affected_ops(event)
notify_jarvis_prepare(event, affected)
mission = create_maintenance_mission(event, affected)

# Phase B (at maintenance start or Jarvis signal)
execute_pause(mission.id, affected)

# Phase C
await_resume_authorization(mission.id)
# ... waits for Jarvis + Coddy ...

# Phase D
health = run_health_checks()
dupes = check_duplicates()
resume_ops = determine_resume_ops(health, dupes)
execute_resume(mission.id, health, dupes, resume_ops)
notify_jarvis_resumed(health, resume_ops)
```