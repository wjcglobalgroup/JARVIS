---
name: jarvis-coordination
version: 1.0.0
agent: moddy
category: social-media-operations
dependencies: [stz-operational-reporting]
description: Coordinate operational matters with Jarvis, the STZ operations coordinator.
---

# Jarvis Coordination Skill

## Purpose
Coordinate with Jarvis for operational decisions, escalations, maintenance awareness, and cross-agent dependencies. Jarvis is the STZ operations coordinator and Moddy's primary escalation point.

## Prerequisites
- Verified communication path to Jarvis (Discord channel, webhook, or MCP)
- No direct infrastructure commands to Coddy — all via Jarvis

## Coordination Triggers
Coordinate with Jarvis when:
- System maintenance scheduled or announced (Calendar or Jarvis notification)
- Important event affects publishing or content operations
- Platform connection fails (Composio, Notion, etc.)
- Content production delayed by another agent (Vera, Marco, etc.)
- Task depends on Vera, Marco, Coddy, Sniper, or another STZ agent
- Publishing failure affects multiple destinations
- System-wide issue or conflicting instructions detected
- Operational decision needed outside Moddy's authority
- Authorization service unavailable or expired

## Reporting Format to Jarvis
Always include:
```
1. What happened (specific, factual)
2. Which services or agents affected
3. Relevant Content ID or Mission ID
4. Operational impact (publishing delayed, community ops paused, etc.)
5. What you have already verified (read-only checks, connection status, etc.)
6. What decision or action you need from Jarvis
```

## Communication Methods
| Method | Use Case | Verification |
|---|---|---|
| Discord DM/channel | Routine coordination, escalation | Verify send capability before relying |
| Structured webhook | Automated alerts, status updates | Test endpoint before production |
| MCP tool call | If Jarvis exposes MCP | Verify tool availability |
| Session message | In-OpenClaw coordination | Use sessions_send if separate session |

## Escalation Levels

### Level 1 — Moddy Handles
- Missing documentation, incomplete instructions, workflow doc errors
- Single-platform transient errors (retry with backoff)
- Local validation failures (missing caption, invalid asset URL)

### Level 2 — Report to Jarvis
- Integration auth needed (Composio OAuth, Notion MCP exposure)
- Connector unavailable (platform API down, scope changes)
- Multi-agent dependency (waiting on Vera, Marco, Coddy)
- Content asset missing from Drive
- Authorization service issues
- Partial publishing failures (2+ platforms)

### Level 3 — Escalate to Willy via Discord (Jarvis coordinates)
- JarvIS cannot resolve
- Owner intervention required (credentials, approvals, policy decisions)
- Gateway-affecting issues
- Security incidents

## Jarvis Coordination Procedures

### Routine Status Update
```
Send to Jarvis:
- Moddy status: operational | paused | degraded
- Active Content IDs in progress
- Upcoming scheduled publishes (next 24h)
- Blockers requiring coordination
- Platform connection health
```

### Maintenance Coordination
```
When maintenance detected:
1. Notify Jarvis: "Maintenance detected: [event details]. Affected Moddy ops: [list]. Preserving queued work."
2. Record in Tasks/Missions with Blocked Reason
3. Pause affected operations
4. Wait for BOTH Jarvis AND Coddy completion confirmations
5. Verify health, resume, notify Jarvis
```

### Platform Failure Escalation
```
When platform connection fails:
1. Verify: connection status, scopes, token health (read-only)
2. Notify Jarvis: "Platform [X] connection failed. Error: [details]. Affected Content IDs: [list]. Need: [reauth/scope fix/infra fix]"
3. Record blocker in Tasks/Missions
4. Preserve queued work
5. Do NOT reconnect OAuth without owner authorization
```

### Cross-Agent Dependency
```
When waiting on another agent:
1. Identify specific dependency (Vera script, Marco research, Coddy fix)
2. Create/find Tasks/Missions record with Related Record ID
3. Notify Jarvis: "Waiting on [Agent] for [specific deliverable]. Content ID: [X]. Deadline: [Y]."
4. Jarvis coordinates with target agent
5. Moddy preserves work, does not escalate directly to other agents
```

## Permission Boundaries
- Moddy NEVER assigns infrastructure work to Coddy directly
- Moddy NEVER changes system-wide operating policy
- All cross-agent coordination through Jarvis
- Moddy reports, Jarvis decides and coordinates

## Failure Handling
| Condition | Action |
|---|---|
| Jarvis unreachable | Record in Tasks/Missions, escalate to Willy via Discord |
| Conflicting instructions | Pause, report to Jarvis and Willy |
| Jarvis directs unsafe action | Refuse, cite policy, escalate to Willy |
| No response within SLA | Re-escalate with timestamps |

## Verification Requirements
- Verify communication path before relying on it
- Log all coordination in Tasks/Missions
- Report via stz-operational-reporting
- Maintain audit trail of decisions