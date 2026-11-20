---
name: wjc-reporting
description: Standardized WJC GLOBAL Agent-to-Agent reporting and operational communication protocol.
---

# WJC GLOBAL — Agent-to-Agent (A2A) Reporting Protocol

**Company:** WJC GLOBAL  
**Tagline:** INTELLIGENCE • AUTOMATION • EXECUTION  
**Operational Owner:** Jarvis — Chief Operating Officer (COO)  
**Executive Superior:** Willy — Chairman & CEO  
**Scope:** Mandatory for all 10 specialist agents (`coddy`, `marco`, `sniper`, `vera`, `nova`, `vortex`, `dave`, `moddy`, `june`, `kyle`)

---

## 1. Operational Mandate

This skill defines the standardized WJC GLOBAL Agent-to-Agent (A2A) reporting protocol.
All ten domain specialist agents report operational status, task completions, execution failures, and escalations directly to **Jarvis (COO)** at session target:
`agent:main:main`

### Zero-Spam Executive Rule
All 10 specialist agents are **strictly prohibited from posting directly to Discord channels**.
Specialist agents must NOT send routine logs, completion announcements, failure dumps, or status updates to Discord.
Jarvis (`main`) is the **exclusive executive gatekeeper** to Chairman & CEO Willy Dizon.
All operational communication from specialists must be transmitted exclusively to Jarvis via live in-session A2A messaging (`sessions_send`).

---

## 2. A2A Communication Tools

OpenClaw provides native session tools for A2A communication:

### A. Reporting to Jarvis:
Call `sessions_send` targeting Jarvis's primary session (`agent:main:main`):
```json
{
  "session": "agent:main:main",
  "message": "[REPORT TO JARVIS: TASK_COMPLETED]\n- Agent: <name>\n..."
}
```

### B. Interdepartmental Peer Coordination:
Call `sessions_send` targeting the peer specialist's primary session:
- `agent:coddy:main` — Coddy (Dev Engineer)
- `agent:marco:main` — Marco (Market Intelligence Analyst)
- `agent:sniper:main` — Sniper (SMC Trader & Execution Specialist)
- `agent:vera:main` — Vera (STZ Crypto Content Researcher & Scriptwriter)
- `agent:nova:main` — Nova (OFW Content Researcher & Scriptwriter)
- `agent:vortex:main` — Vortex (STZ Crypto Video & Graphics Producer)
- `agent:dave:main` — Dave (OFW Video & Graphics Producer)
- `agent:moddy:main` — Moddy (STZ Crypto Social Media Operations Manager)
- `agent:june:main` — June (OFW Social Media Manager)
- `agent:kyle:main` — Kyle (Marketing Manager — Kaixin Transport)

---

## 3. Mandatory Reporting Triggers

Every specialist agent must report to Jarvis under these specific conditions:

### A. Task Completion (`TASK_COMPLETED`)
Dispatched immediately upon successful completion of an assigned task, scheduled job, or pipeline stage.
Must include verifiable deliverables or references (Notion page ID, Google Drive path, Git commit hash, or order ID).

### B. Workspace or Execution Failure (`TASK_FAILED`)
Dispatched immediately when:
- A workspace execution fails.
- An automated job or script crashes or throws unhandled exceptions.
- A required tool, integration, or dependency is unavailable.
- External API rate limits (HTTP 429) or authentication failures (HTTP 401/403) occur.
- An assigned task cannot be completed.
Do NOT silently abandon tasks.

### C. Operational Escalation (`TASK_BLOCKED`)
Dispatched immediately when:
- A decision exceeds the agent's authority or permissions.
- Work cannot proceed due to missing upstream handoffs or dependencies.
- A critical business, technical, or timeline issue arises requiring higher authority intervention.

### D. No Unnecessary Reporting
Do NOT report routine internal steps, healthy heartbeat polls, or minor operations. Reports must be meaningful, concise, and actionable.

---

## 4. Standardized Reporting Message Formats

Always use these exact schemas when sending reports to Jarvis:

### TASK_COMPLETED
```text
[REPORT TO JARVIS: TASK_COMPLETED]
- Agent: <agent_name>
- Department: <department_name>
- Task ID: <task_id_or_none>
- Task: <task_name_and_description>
- Status: COMPLETED
- Summary: <concise_summary_of_work_performed>
- Deliverables: <output_locations_or_deliverables>
- Artifact references: <notion_page_id_or_drive_link_or_file_path>
- Remaining issues: <none_or_description>
```

### TASK_FAILED
```text
[REPORT TO JARVIS: TASK_FAILED]
- Agent: <agent_name>
- Department: <department_name>
- Task ID: <task_id_or_none>
- Task: <task_name_and_affected_workspace>
- Status: FAILED
- Error: <exact_error_message_or_trace_snippet>
- Impact: <operational_impact_and_affected_dependencies>
- Recovery attempts: <troubleshooting_steps_already_attempted>
- Required intervention: <technical_repair_or_credential_update_or_coo_direction>
- Recommended next action: <suggested_remedy>
```

### TASK_BLOCKED
```text
[REPORT TO JARVIS: TASK_BLOCKED]
- Agent: <agent_name>
- Department: <department_name>
- Task ID: <task_id_or_none>
- Task: <task_name_and_description>
- Status: BLOCKED
- Blocker: <description_of_blocker>
- Dependencies: <missing_upstream_deliverables_or_external_service>
- Required assistance: <required_intervention_from_jarvis_or_department>
- Recommended action: <suggested_workaround_or_action>
```

---

## 5. Offline Fallback Protocol

If `sessions_send` is temporarily unavailable:
1. Log the report locally to session memory or a local log file.
2. Retry delivery on the next execution cycle or heartbeat.
3. NEVER fall back to posting on Discord or public channels.