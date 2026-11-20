---
name: notion-task-mission-management
version: 1.0.0
agent: moddy
category: social-media-operations
dependencies: [jarvis-coordination, stz-operational-reporting]
description: Read and maintain the STZ Tasks / Missions database in Notion for operational coordination.
---

# Notion Task / Mission Management Skill

## Purpose
Read and maintain the STZ Tasks / Missions database in Notion via the OpenClaw MCP integration. This skill provides procedures for finding existing missions, creating operational tasks, linking to Content Pipeline records, and tracking blockers and results.

## Prerequisites
- Notion MCP server must be exposed to Moddy's runtime
- Authorization to read/write only the STZ Tasks / Missions database
- No schema, property, or view changes permitted

## Required Tools
When Notion MCP is exposed:
- `mcp:notion:notion__search` - Search for pages/databases
- `mcp:notion:notion__query_database` - Query database with filters
- `mcp:notion:notion__get_page` - Get page content
- `mcp:notion:notion__update_page` - Update page properties
- `mcp:notion:notion__create_page` - Create new task/mission record

## Database Schema Understanding

### STZ Tasks / Missions — Key Fields
| Property | Type | Description |
|---|---|---|
| Title | Title | Actionable task title |
| Mission ID | Text | Unique mission identifier (e.g., MODDY-20261103-001) |
| Assigned Agent | Select | marco | vera | moddy | sniper | coddy | jarvis |
| Pipeline | Select | content-pipeline | publishing | maintenance | coordination |
| Priority | Select | critical | high | medium | low |
| Due Date | Date | Target completion date |
| Description | Rich Text | Detailed task description |
| Status | Select | See status options below |
| Blocked Reason | Rich Text | Specific blocker description |
| Related Record ID | Relation | Link to Content Pipeline record |
| Related URL | URL | External reference (platform post, Drive file, etc.) |
| Result | Rich Text | Verified deliverable summary |

### Status Options (Exact Values)
- `Not Started`
- `In Progress`
- `Blocked`
- `Completed`
- `Failed`
- `Cancelled`

## Procedures

### 1. Find Existing Mission
```
Before creating a new mission:
1. Query STZ Tasks / Missions with filters:
   - Assigned Agent = "moddy"
   - Status in ["Not Started", "In Progress", "Blocked"]
   - Related Record ID matches Content ID (if known)
2. If found, update existing record instead of creating duplicate
3. If not found, proceed to create
```

### 2. Create Mission Record
```
Required fields:
- Title: Actionable, specific (e.g., "Publish short-form video STZ-20261102-001 to Instagram")
- Mission ID: MODDY-YYYYMMDD-### format
- Assigned Agent: "moddy"
- Pipeline: "publishing" | "maintenance" | "coordination"
- Priority: Per urgency
- Due Date: Scheduled Slot from Content Pipeline or operational deadline
- Description: Include Content ID, platforms, asset refs, blockers
- Status: "Not Started"
- Blocked Reason: Empty unless initially blocked
- Related Record ID: Link to Content Pipeline record
- Related URL: Drive folder, Notion page, or platform URL
```

### 3. Update Mission Status
```
Transitions:
- Not Started -> In Progress: When work begins
- In Progress -> Blocked: When dependency blocks (MUST set Blocked Reason)
- Blocked -> In Progress: When blocker resolved (clear Blocked Reason)
- In Progress -> Completed: ONLY with verified deliverable evidence
- In Progress -> Failed: After actual unsuccessful attempt (record in Result)
- Any -> Cancelled: When work obsoleted (record reason in Result)

Never:
- Mark Completed without evidence
- Mark Failed without actual attempt
- Clear Blocked Reason without verification
```

### 4. Record Blocker
```
When blocked:
1. Set Status = "Blocked"
2. Set Blocked Reason = specific, actionable description
   - Bad: "Waiting for asset"
   - Good: "Video asset missing for Content ID STZ-20261102-001; Drive file ID not found in metadata.json; escalated to Jarvis -> Vera"
3. Link Related Record ID if Content Pipeline related
4. Escalate to Jarvis per jarvis-coordination skill
```

### 5. Record Completion
```
When completing:
1. Set Status = "Completed"
2. Set Result = verified deliverable summary
   - Include: Content ID, platforms published, post IDs, URLs, timestamps
   - Reference: Content Pipeline record updated
3. Clear Blocked Reason
4. Verify by re-querying record
```

### 6. Link Content Pipeline Records
```
Use Related Record ID (relation field) to link:
- Mission -> Content Pipeline record (many-to-one)
- Enables traceability from task to content
- Query missions by Content ID for status overview
```

## Permission Boundaries
- READ: All Tasks / Missions records
- WRITE: Title, Mission ID, Assigned Agent, Pipeline, Priority, Due Date, Description, Status, Blocked Reason, Related Record ID, Related URL, Result
- NO WRITE: Schema, properties, views, other databases
- NO CREATE: Records for other agents without coordination

## Failure Handling & Escalation
| Condition | Action |
|---|---|
| Notion MCP not accessible | Escalate to Jarvis -> Coddy |
| Duplicate Mission ID | Search first, update existing |
| Invalid Status transition | Follow exact transitions only |
| Missing Blocked Reason on Blocked | Reject transition, require reason |
| Completed without Result evidence | Reject, require deliverable proof |

## Verification Requirements
- After every write, re-query to confirm
- Cross-reference with Content Pipeline for consistency
- Report via stz-operational-reporting

## Practical Example
```
# Create publishing mission for today's video
mission = create_page("STZ Tasks / Missions", {
  "Title": "Publish short-form video STZ-20261102-001 to YouTube, Instagram, Facebook, Binance Square",
  "Mission ID": "MODDY-20261102-001",
  "Assigned Agent": "moddy",
  "Pipeline": "publishing",
  "Priority": "high",
  "Due Date": "2026-11-02",
  "Description": "Content ID: STZ-20261102-001\nPlatforms: youtube, instagram, facebook-page, binance-square\nAsset: Drive file ID from metadata.json\nScheduled: 10:20 PHT",
  "Status": "Not Started",
  "Related Record ID": [content_pipeline_record_id]
})

# Start work
update_page(mission.id, {"Status": "In Progress"})

# ... publish workflow ...

# Complete with evidence
update_page(mission.id, {
  "Status": "Completed",
  "Result": "Published to all 4 platforms. YouTube: abc123, Instagram: def456, Facebook: ghi789, Binance: jkl012. Content Pipeline updated."
})
```