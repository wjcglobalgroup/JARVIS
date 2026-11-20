---
name: calendar-operations
version: 1.0.0
agent: moddy
category: social-media-operations
dependencies: [jarvis-coordination, stz-operational-reporting]
description: Read Google Calendar for STZ maintenance windows, publishing schedules, and operational events using authorized Composio connection.
---

# Calendar Operations Skill

## Purpose
Read Google Calendar via authorized Composio connection to discover maintenance windows, publishing schedules, campaign deadlines, and coordination events. This skill covers read-only calendar operations only.

## Prerequisites
- Composio googlecalendar toolkit connected (OAuth: googlecalendar_oauth)
- Scopes: calendar, calendar.events (read)
- Calendar monitoring does NOT grant create/modify/delete permissions
- Request owner authorization before any calendar changes

## Required Composio Tools
- `GOOGLECALENDAR_GET_CALENDAR` - Get primary calendar metadata
- `GOOGLECALENDAR_CALENDAR_LIST_GET` - Get specific calendar metadata
- `GOOGLECALENDAR_EVENTS_LIST_ALL_CALENDARS` - List events across calendars in date range
- `GOOGLECALENDAR_FIND_EVENT` - Search events by text query and time ranges
- `GOOGLECALENDAR_EVENTS_GET` - Get single event by ID
- `GOOGLECALENDAR_EVENTS_INSTANCES` - Get instances of recurring event
- `GOOGLECALENDAR_FREE_BUSY_QUERY` - Query busy intervals

## Calendar Access Procedure
```
1. List available calendars to identify STZ-relevant ones
2. Query events for next 7-30 days
3. Filter for maintenance, publishing, campaign, coordination events
4. Convert all timestamps to PHT (Asia/Manila) using event timezone
5. Record findings in Tasks/Missions if actionable
```

## Event Discovery Patterns

### Maintenance Events
- Title keywords: maintenance, downtime, upgrade, migration, deployment, outage
- Description keywords: API, database, gateway, connector, auth, publishing
- Attendees: Coddy, Jarvis, Willy, STZ infrastructure

### Publishing Schedule Events
- Title keywords: publish, posting, campaign, content, video, short-form
- Time slots matching: 10:20 PHT (video), 00/06/12/18 PHT (text-image)
- Related Content IDs in description

### Coordination Events
- Title keywords: coordination, sync, standup, review, planning
- Attendees: multiple STZ agents
- Decisions affecting publishing schedule

## Timezone Handling (Critical)
```
// ALWAYS use event's timezone property
// Google Calendar returns RFC3339 with timezone offset
// Convert to PHT for STZ operations

event.start.dateTime  // e.g., "2026-11-03T02:20:00-08:00" (PST)
event.start.timeZone  // e.g., "America/Los_Angeles"

// Convert to PHT:
const phtTime = new Date(event.start.dateTime).toLocaleString('en-US', {
  timeZone: 'Asia/Manila',
  hour12: false
})
// Result: "11/3/2026, 16:20:00" (PHT)
```

**NEVER assume UTC display equals PHT.**
**ALWAYS use the event's explicit timezone.**

## Query Procedures

### List Events (Date Range)
```
params = {
  time_min: "2026-11-03T00:00:00+08:00",  // RFC3339, PHT
  time_max: "2026-11-10T00:00:00+08:00",
  max_results: 50,
  order_by: "startTime"
}
result = execute("GOOGLECALENDAR_EVENTS_LIST_ALL_CALENDARS", params)
```

### Find Events (Text Search)
```
params = {
  calendar_id: "primary",  // or specific calendar ID
  query: "maintenance",
  time_min: "2026-11-03T00:00:00+08:00",
  time_max: "2026-11-10T00:00:00+08:00"
}
result = execute("GOOGLECALENDAR_FIND_EVENT", params)
```

### Get Recurring Event Instances
```
params = {
  calendar_id: "primary",
  event_id: "recurring_event_id",
  time_min: "2026-11-03T00:00:00+08:00",
  time_max: "2026-11-10T00:00:00+08:00"
}
result = execute("GOOGLECALENDAR_EVENTS_INSTANCES", params)
```

## Integration with Maintenance Awareness
- This skill provides the CALENDAR READ layer
- system-maintenance-awareness skill uses this for detection
- jarvis-coordination skill uses this for scheduling context

## Permission Boundaries
- READ: All calendar events, metadata, free/busy
- NO WRITE: Create, update, delete events, calendars, ACLs
- NO MODIFY: Calendar settings, sharing, notifications
- Authorization required from Willy for any write operations

## Failure Handling
| Condition | Action |
|---|---|
| Composio connection not found | Escalate to Jarvis -> owner OAuth needed |
| Insufficient scopes | Report missing scopes, request re-auth |
| Calendar not found | List calendars first, verify ID |
| Timezone parsing error | Log raw event, escalate to Jarvis |
| Rate limited | Exponential backoff, retry once |

## Verification Requirements
- After query, verify event count reasonable
- Cross-reference known maintenance windows
- Report findings via stz-operational-reporting
- Log all calendar reads for audit

## Practical Example
```
# Weekly calendar scan (run daily at startup)
now_pht = "2026-11-03T00:00:00+08:00"
week_later = "2026-11-10T00:00:00+08:00"

events = execute("GOOGLECALENDAR_EVENTS_LIST_ALL_CALENDARS", {
  time_min: now_pht,
  time_max: week_later,
  max_results: 100,
  order_by: "startTime"
})

maintenance_events = []
publishing_events = []

for event in events.items:
  pht_start = convert_to_pht(event.start.dateTime, event.start.timeZone)
  pht_end = convert_to_pht(event.end.dateTime, event.end.timeZone)
  
  if is_maintenance_event(event):
    maintenance_events.append({
      title: event.summary,
      start: pht_start,
      end: pht_end,
      description: event.description
    })
  elif is_publishing_event(event):
    publishing_events.append({
      title: event.summary,
      slot: pht_start,
      content_id: extract_content_id(event.description)
    })

if maintenance_events:
  notify_jarvis(maintenance_events)
  create_maintenance_missions(maintenance_events)
```