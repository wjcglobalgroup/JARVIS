---
name: stz-operational-reporting
version: 1.0.0
agent: moddy
category: social-media-operations
dependencies: []
description: Standardized operational reporting format for Moddy activities, status, blockers, and results.
---

# STZ Operational Reporting Skill

## Purpose
Provide consistent, structured reporting for all Moddy operations. Ensures Willy, Jarvis, and other agents receive actionable, verifiable information.

## Reporting Vocabulary (STZ Agent Reporting Protocol)
| Status | Meaning | Evidence Required |
|---|---|---|
| `COMPLETED` | Evidence confirms success | Platform post ID, URL, timestamp |
| `INCOMPLETE` | Required work remains | Specific remaining steps |
| `BLOCKED` | Dependency/permission/integration obstacle | Blocker details, escalation path |
| `FAILED` | Operation failed | Error details, attempt evidence |
| `SYSTEM_ERROR` | Infrastructure/runtime/auth error | Error logs, service status |
| `NOT_VERIFIED` | Attempted but insufficient evidence | What was tried, what's missing |

**NEVER report INCOMPLETE as COMPLETED.**

## Report Types

### 1. Publishing Result Report
```
{
  "reportType": "PUBLISHING_RESULT",
  "contentId": "STZ-20261102-001",
  "contentType": "short-form-video",
  "targetPlatform": "instagram",
  "targetAccount": "@smarttraderzone",
  "scheduledTime": "2026-11-02T10:20:00+08:00",
  "actualTime": "2026-11-02T10:21:15+08:00",
  "status": "COMPLETED",
  "platformPostId": "178923456789",
  "platformUrl": "https://instagram.com/p/ABC123/",
  "error": null,
  "retryCount": 0,
  "authorizationId": "auth-20261102-001"
}
```

### 2. Partial Publishing Report
```
{
  "reportType": "PUBLISHING_RESULT",
  "contentId": "STZ-20261102-001",
  "contentType": "short-form-video",
  "overallStatus": "PARTIALLY_PUBLISHED",
  "platforms": [
    {"platform": "youtube", "status": "COMPLETED", "postId": "abc", "url": "..."},
    {"platform": "instagram", "status": "COMPLETED", "postId": "def", "url": "..."},
    {"platform": "facebook-page", "status": "FAILED", "error": "Token expired"},
    {"platform": "binance-square", "status": "NOT_VERIFIED", "error": "API timeout"}
  ]
}
```

### 3. Blocker Report
```
{
  "reportType": "BLOCKER",
  "contentId": "STZ-20261102-001",
  "missionId": "MODDY-20261102-001",
  "blockerType": "MISSING_ASSET | AUTH_EXPIRED | CONNECTION_FAILED | NOTION_UNAVAILABLE | CALENDAR_CONFLICT",
  "description": "Specific, actionable description",
  "affectedOperations": ["instagram_publish", "facebook_publish"],
  "escalationPath": "jarvis -> coddy -> willy",
  "preservedWork": "Content Pipeline status unchanged; queued for resume"
}
```

### 4. Maintenance Pause/Resume Report
```
{
  "reportType": "MAINTENANCE",
  "phase": "PREPARE | PAUSE | AWAIT_AUTH | RESUME",
  "eventTitle": "STZ Gateway Upgrade",
  "windowPHT": "2026-11-03 02:00 - 06:00",
  "affectedOps": ["video_publish", "community_mgmt"],
  "jarvisConfirmation": "2026-11-03T06:05:00+08:00",
  "coddyConfirmation": "2026-11-03T06:07:00+08:00",
  "healthChecks": {
    "composio": "PASS",
    "notion": "PASS",
    "calendar": "PASS",
    "drive": "PASS",
    "platforms": {"youtube": "PASS", "instagram": "PASS", "facebook": "PASS"}
  },
  "duplicateCheck": "0 conflicts found",
  "resumedOps": ["video_publish"]
}
```

### 5. Daily Status Report
```
{
  "reportType": "DAILY_STATUS",
  "date": "2026-11-03",
  "moddyStatus": "OPERATIONAL | PAUSED | DEGRADED",
  "activeContentIds": ["STZ-20261102-001", "STZ-20261103-001"],
  "upcomingPublishes": [
    {"contentId": "STZ-20261103-001", "slot": "10:20 PHT", "platforms": [...]} 
  ],
  "blockers": [
    {"contentId": "...", "type": "...", "escalation": "..."}
  ],
  "platformHealth": {
    "youtube": "CONNECTED",
    "instagram": "CONNECTED",
    "facebook": "CONNECTED",
    "binance-square": "NO_INTEGRATION",
    "notion": "MCP_NOT_EXPOSED",
    "drive": "NO_CONNECTION",
    "calendar": "NO_CONNECTION"
  }
}
```

### 6. Escalation Report (to Jarvis)
```
{
  "reportType": "ESCALATION",
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "summary": "One-line summary",
  "details": "Full description",
  "affectedAgents": ["moddy", "vera", "coddy"],
  "affectedServices": ["notion-mcp", "composio-instagram"],
  "contentIds": ["STZ-20261102-001"],
  "missionIds": ["MODDY-20261102-001"],
  "verified": ["Notion MCP configured but not exposed", "Composio Instagram 0 connections"],
  "tried": ["Checked gateway config", "Queried tool catalog"]
  "needs": "Coddy to expose Notion MCP to Moddy runtime"
}
```

## Delivery Methods
| Report Type | Delivery |
|---|---|
| Publishing Result | Update Content Pipeline + Tasks/Missions |
| Blocker | Update Tasks/Missions + notify Jarvis |
| Maintenance | Update Tasks/Missions + notify Jarvis |
| Daily Status | Notify Jarvis (scheduled) |
| Escalation | Notify Jarvis immediately |

## Verification Requirements
- Every report includes timestamp (ISO 8601, PHT)
- Every report includes Content ID or Mission ID
- Publishing reports include platform post ID or explicit NOT_VERIFIED
- Blocker reports include specific escalation path
- All reports logged for audit trail

## Practical Example
```
# After successful Instagram publish
report_publishing_result({
  "contentId": "STZ-20261102-001",
  "platform": "instagram",
  "status": "COMPLETED",
  "postId": "178923456789",
  "url": "https://instagram.com/p/ABC123/",
  "authorizationId": "auth-20261102-001"
})

# Updates Content Pipeline:
# - Instagram Status = Published
# - Platform Post IDs += "178923456789"
# - Platform URLs += "https://instagram.com/p/ABC123/"
# - Last Publish Attempt = now
# - Overall Status = Partially Published (if others pending)

# Creates Tasks/Missions log entry
```