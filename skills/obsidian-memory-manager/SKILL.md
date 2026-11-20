---
name: obsidian-memory-manager
description: Manage and navigate the centralized STZ Obsidian memory vault. Allows agents to search, read, create, update, and validate Markdown notes with YAML frontmatter in 01-Memory, 02-Knowledge-Base, and 03-Agent-Protocols.
---

# Obsidian Memory Manager Skill

This skill teaches and empowers OpenClaw agents to interface with the centralized Obsidian vault at `C:\OPENCLAW\obsidian-vault\` (or `$env:STZ_VAULT_PATH`).

## Vault Architecture Reference
- **Vault Root**: `C:\OPENCLAW\obsidian-vault\`
- **Dashboards & Indexes**: `00-Home/`
- **Memory Root**: `01-Memory/`
  - System Memory: `01-Memory/System-Memory/`
  - Agent Memories: `01-Memory/Agent-Memory/<AgentName>/`
  - Decisions (ADRs): `01-Memory/Decisions/`
  - Operational History: `01-Memory/Operational-History/`
- **Knowledge Base Root**: `02-Knowledge-Base/`
  - Categories: `STZ-OS`, `OpenClaw`, `AI-Agents`, `Automation`, `Trading`, `Integrations`, `Research`
- **Agent Protocols**: `03-Agent-Protocols/` (Includes `GLOBAL-MEMORY-PROTOCOL.md`)
- **Templates**: `06-Templates/`
- **Archive**: `99-Archive/`

---

## 🛠️ Step-by-Step Operating Procedures

### 1. Searching the Vault
Before starting an operational or engineering task, search the vault to avoid duplicating research or repeating past errors.
- Target the appropriate category: e.g. `02-Knowledge-Base/Trading/` for trading rules, or `01-Memory/Agent-Memory/<Agent>/` for previous run logs.
- Scan for titles, tags, and content keywords.

### 2. Reading a Note
- Verify the file exists within `STZ_VAULT_PATH`.
- Parse the YAML frontmatter between `---` markers to determine ownership, type, and freshness.
- Read the body markdown. Follow relevant `[[wikilinks]]`.

### 3. Creating a Note
Always use the standardized frontmatter:
```markdown
---
title: Note Title
type: memory | knowledge | decision | incident
category: Target-Category
owner: Agent-Name
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Note Title

## Summary
...
```
- Ensure file naming matches topic (e.g. `2026-11-01-topic-name.md`).
- Always check that no identical document exists in the folder before writing.

### 4. Updating an Existing Note
- Never erase existing historical records without explicit authorization.
- Append new sections under an update header (e.g., `## Update YYYY-MM-DD (<Agent>)`).
- Always update `updated: YYYY-MM-DD` in frontmatter.

### 5. Writing to Authorized Directories Only
- Jarvis: Writes to `01-Memory/Agent-Memory/Jarvis/`, `01-Memory/System-Memory/`, `01-Memory/Decisions/`, `00-Home/`.
- Coddy: Writes to `01-Memory/Agent-Memory/Coddy/`, `01-Memory/Operational-History/`, `02-Knowledge-Base/OpenClaw/`, `02-Knowledge-Base/STZ-OS/`.
- Marco: Writes to `01-Memory/Agent-Memory/Marco/`, `02-Knowledge-Base/Research/`, `02-Knowledge-Base/Trading/` (Macro notes).
- Sniper: Writes to `01-Memory/Agent-Memory/Sniper/`, `02-Knowledge-Base/Trading/` (Execution/Paper Trading).
- Moddy: Writes to `01-Memory/Agent-Memory/Moddy/`, `02-Knowledge-Base/Integrations/` (Discord/Community).
- Vera: Writes to `01-Memory/Agent-Memory/Vera/`, `02-Knowledge-Base/Integrations/` (Media/Google Flow).

### 6. Error & Conflict Handling
- If a write operation fails (e.g., file lock, path error), report the exact error to Jarvis or log an incident in `01-Memory/Operational-History/`.
- Never report success if a write failed.
