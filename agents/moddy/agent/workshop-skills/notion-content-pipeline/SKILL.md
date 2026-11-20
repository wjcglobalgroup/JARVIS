---
name: notion-content-pipeline
version: 1.0.0
agent: moddy
category: social-media-operations
dependencies: [jarvis-coordination, stz-operational-reporting]
description: Read and maintain the STZ Content Pipeline database in Notion via the OpenClaw MCP integration.
---

# Notion Content Pipeline Skill

## Purpose
Read and maintain the STZ Content Pipeline database in Notion via the OpenClaw MCP integration. This skill provides procedures for finding content assigned to Moddy, checking Ready to Publish status, validating assets and captions, updating platform statuses, and recording execution results.

## Prerequisites
- Notion MCP server must be exposed to Moddy's runtime (currently configured at gateway level but not accessible)
- Authorization to read/write only the STZ Content Pipeline database
- No schema, property, or view changes permitted

## Required Tools
When Notion MCP is exposed, the following tools should be available:
- `mcp:notion:notion__search` - Search for pages/databases
- `mcp:notion:notion__query_database` - Query database with filters
- `mcp:notion:notion__get_page` - Get page content
- `mcp:notion:notion__update_page` - Update page properties
- `mcp:notion:notion__create_page` - Create new page (for linking)

## Database Schema Understanding

### STZ Content Pipeline - Key Fields
| Property | Type | Description |
|---|---|---|
| Content ID | Title/ID | Unique identifier (e.g., STZ-20261102-001) |
| Story ID | Text | Related story reference |
| Content Type | Select | short-form-video | text-and-image |
| Assigned Agent | Select | marco | vera | moddy | sniper | coddy | jarvis |
| Publish Date | Date | Target publication date |
| Preparation Slot | Date/Time | When Vera prepares the package |
| Scheduled Slot | Date/Time | When Moddy should publish |
| Target Platforms | Multi-select | youtube | instagram | facebook-page | binance-square |
| Overall Status | Select | See status options below |
| Facebook Caption | Rich Text | Caption for Facebook |
| Facebook Page Status | Select | not-started | ready | published | failed | partially-published |
| Instagram Caption | Rich Text | Caption for Instagram |
| Instagram Status | Select | not-started | ready | published | failed | partially-published |
| Binance Square Caption | Rich Text | Caption for Binance Square |
| Binance Square Status | Select | not-started | ready | published | failed | partially-published |
| Platform Post IDs | Text | Comma-separated external IDs |
| Platform URLs | Text | Comma-separated URLs |
| Image Asset | Files | Uploaded image |
| Image Asset URL | URL | Direct image URL |
| Google Drive File ID | Text | Drive reference |
| Publishing Error | Rich Text | Error details |
| Result | Rich Text | Execution result summary |
| Retry Count | Number | Number of retry attempts |
| Last Publish Attempt | Date/Time | Timestamp of last attempt |

### Status Options (Exact Values)
**Overall Status:**
- `Not Started`
- `In Preparation` (Vera)
- `Ready to Publish` (handoff to Moddy)
- `In Publishing` (Moddy active)
- `Published` (all selected platforms confirmed)
- `Partially Published` (some platforms succeeded, some failed)
- `Failed` (all selected platforms failed)
- `Blocked` (dependency issue)
- `Cancelled`

**Per-Platform Status (Facebook/Instagram/Binance Square):**
- `Not Started`
- `Ready`
- `Published`
- `Failed`
- `Partially Published`

## Procedures

### 1. Find Moddy-Assigned Content Ready to Publish
```
1. Query STZ Content Pipeline database with filters:
   - Assigned Agent = "moddy"
   - Overall Status = "Ready to Publish"
2. For each result, extract:
   - Content ID
   - Content Type
   - Target Platforms
   - Scheduled Slot
   - Captions per platform
   - Asset references (Image Asset URL, Google Drive File ID)
3. Validate each record (see Validation Rules)
4. Return prioritized list by Scheduled Slot
```

### 2. Validate Content Record
```
For each platform in Target Platforms:
1. Check caption exists and is non-empty
2. Check asset reference exists (Image Asset URL or Google Drive File ID)
3. If video: verify Google Drive File ID present
4. If image: verify Image Asset URL accessible
5. Check for duplicate Content ID in recent published records
6. Check Scheduled Slot is not in past (unless catch-up authorized)
7. Flag any:
   - Missing captions
   - Missing/invalid asset URLs
   - Invalid Google Drive File IDs
   - Scheduling conflicts (same slot, same platform)
   - Duplicate Content IDs
```

### 3. Update Platform Status (Pre-Publish)
```
Before publishing to a platform:
1. Update platform-specific status to "Ready"
2. Record attempt timestamp in Last Publish Attempt
3. Increment Retry Count if retry
4. Clear previous Publishing Error
```

### 4. Record Publication Result
```
After publishing attempt (per platform):
1. If SUCCESS:
   - Update platform status to "Published"
   - Record Platform Post ID
   - Record Platform URL
   - Clear Publishing Error
2. If FAILED:
   - Update platform status to "Failed"
   - Record error details in Publishing Error
   - Record error in Result
3. If PARTIAL (some platforms succeeded):
   - Update each platform status individually
   - Update Overall Status to "Partially Published"
   - Record all Post IDs and URLs
   - Record errors for failed platforms
```

### 5. Update Overall Status
```
After all target platforms attempted:
- All Published -> Overall Status = "Published"
- Some Published, some Failed -> Overall Status = "Partially Published"
- All Failed -> Overall Status = "Failed"
- Blocked by dependency -> Overall Status = "Blocked" (set Blocked Reason in Tasks/Missions)
```

### 6. Pre-Retry Checks
```
Before any retry:
1. Check existing Platform Post IDs - do not repost if ID exists
2. Check Platform URLs - verify content not already live
3. Check Retry Count < 3 (escalate if >= 3)
4. Verify authorization still valid (AUTHORIZED_PUBLISH)
5. Verify platform connection healthy
```

## Permission Boundaries
- READ: All Content Pipeline records
- WRITE: Only platform status fields, Platform Post IDs, Platform URLs, Publishing Error, Result, Retry Count, Last Publish Attempt
- NO WRITE: Content ID, Story ID, Content Type, Assigned Agent, Publish Date, Preparation Slot, Scheduled Slot, Target Platforms, Captions, Asset fields, Overall Status (except via computed result)
- NO SCHEMA CHANGES: Never modify properties, views, or database configuration

## Failure Handling & Escalation
| Condition | Action |
|---|---|
| Notion MCP not accessible | Escalate to Jarvis -> Coddy to expose MCP |
| Database query fails | Retry once, then escalate to Jarvis |
| Schema mismatch (missing fields) | Report to Jarvis, do not assume fields |
| Asset missing (Drive file not found) | Escalate to Jarvis -> Vera/Willy |
| Duplicate Content ID found | Escalate to Jarvis before publishing |
| Authorization expired | Stop, escalate to Jarvis |
| Mixed results (partial) | Record as Partially Published, escalate failed platforms |

## Verification Requirements
- After every write, re-query the record to confirm changes persisted
- Cross-reference Platform Post IDs with actual platform API when possible
- Never mark Published without confirmed platform post ID or URL
- Report all operations via stz-operational-reporting skill

## Practical Example
```
# Find today's short-form video content
filters = {
  "and": [
    {"property": "Assigned Agent", "select": {"equals": "moddy"}},
    {"property": "Overall Status", "select": {"equals": "Ready to Publish"}},
    {"property": "Content Type", "select": {"equals": "short-form-video"}},
    {"property": "Publish Date", "date": {"equals": "2026-11-03"}}
  ]
}
results = query_database("STZ Content Pipeline", filters)

for record in results:
  validate_record(record)
  # ... publish workflow ...
  update_platform_status(record.id, "instagram", "Published", post_id="123", url="https://...")
  verify_update(record.id)
```

## Integration Notes
- This skill assumes Notion MCP tools are exposed as `mcp:notion:notion__<tool>`
- If tools have different names, update the Required Tools section
- Coordinate with jarvis-coordination for any cross-agent dependencies
- All Notion operations are tracking only - external publishing requires AUTHORIZED_PUBLISH gate