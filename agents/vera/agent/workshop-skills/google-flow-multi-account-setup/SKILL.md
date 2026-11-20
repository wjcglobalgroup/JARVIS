---
name: google-flow-multi-account-setup
description: When multiple Google Flow accounts need MCP access but single-profile MCP only provides one account. Creates isolated Chrome profiles, per-account MCP configs, registers multiple MCP servers, verifies project access and Smart Trader Zone avatar.
metadata:
  version: "1.0.0"
  openclaw:
    emoji: "🔐"
    owner: vera
    project: stz
---

# Google Flow Multi-Account MCP Setup

## Trigger
Need to access multiple Google Flow accounts through MCP when the single-profile MCP only provides one authenticated account.

## Prerequisites
- Google Flow MCP installed (`@park-sang-gwon/google-flow-mcp`)
- OpenClaw gateway running
- Five Google Flow accounts with existing projects and Smart Trader Zone avatar uploaded
- Chrome executable at `C:\Program Files\Google\Chrome\Application\chrome.exe`

## Procedure

### 1. Create isolated Chrome profiles
```powershell
mkdir "C:\Users\dizon\.google-flow-chrome\FLOW-B"
mkdir "C:\Users\dizon\.google-flow-chrome\FLOW-C"
mkdir "C:\Users\dizon\.google-flow-chrome\FLOW-D"
mkdir "C:\Users\dizon\.google-flow-chrome\FLOW-E"
```
Keep existing `Default` profile for FLOW-A (vipermir4@gmail.com).

### 2. Create MCP config files
For each account, create config at `C:\Users\dizon\.config\google-flow-mcp\config-FLOW-<X>.json`:
```json
{
  "chromePath": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "userDataDir": "C:\\Users\\dizon\\.google-flow-chrome\\FLOW-<X>",
  "profileDirectory": "Default",
  "cdpPort": 933<X>,
  "flowUrl": "https://flow.google.com",
  "stateDir": "C:\\Users\\dizon\\.google-flow-mcp\\FLOW-<X>",
  "generationTimeoutMs": 1800000,
  "pollIntervalMs": 6000,
  "lockWaitMs": 10000,
  "logLevel": "info",
  "account": "FLOW-<X>",
  "email": "<account-email>",
  "projectUrl": "https://flow.google.com/project/<project-id>",
  "projectId": "<project-id>"
}
```
Use ports 9333-9337 for FLOW-A through FLOW-E.

### 3. Create state directories
```powershell
mkdir "C:\Users\dizon\.google-flow-mcp\FLOW-B"
mkdir "C:\Users\dizon\.google-flow-mcp\FLOW-C"
mkdir "C:\Users\dizon\.google-flow-mcp\FLOW-D"
mkdir "C:\Users\dizon\.google-flow-mcp\FLOW-E"
```

### 4. Register MCP servers in openclaw.json
Add to `mcp.servers`:
```json
"google-flow": {
  "command": "google-flow-mcp",
  "cwd": "C:\\Users\\dizon\\.openclaw\\workspace-vera",
  "env": { "FLOW_MCP_CONFIG": "C:\\Users\\dizon\\.config\\google-flow-mcp\\config-FLOW-A.json" },
  "toolFilter": { "include": ["flow_connect", "flow_project_open", "flow_status"] }
},
"google-flow-B": { ... env: { "FLOW_MCP_CONFIG": "...config-FLOW-B.json" } },
"google-flow-C": { ... },
"google-flow-D": { ... },
"google-flow-E": { ... }
```
Each server gets unique `FLOW_MCP_CONFIG` env var pointing to its config file.

### 5. Sign in each account
Launch each profile and sign in interactively:
```powershell
# FLOW-B (wilcycrypto@gmail.com)
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="C:\Users\dizon\.google-flow-chrome\FLOW-B" --profile-directory=Default --remote-debugging-port=9334 https://flow.google.com
# Repeat for FLOW-C (9335), FLOW-D (9336), FLOW-E (9337)
```
Sign in with each account's credentials. Verify project access at `https://flow.google.com/project/<project-id>`.

### 6. Verify each account
For each MCP server, run:
```
flow_connect  # Should show logged_in: true
flow_project_open --project_url https://flow.google.com/project/<project-id>
```
Check:
- `ok: true`
- `project_id` matches expected
- `media_count >= 1` (Smart Trader Zone avatar present)
- Avatar title contains "stz willy" or similar

### 7. Update account ledger
Record in `production/accounts/flow-account-ledger.json`:
- `mcp_accessible: true` for verified accounts
- Avatar UUID and title
- Last verified timestamp

## Verification Checklist
- [ ] All 5 MCP servers show `flow_connect` → `logged_in: true`
- [ ] All 5 `flow_project_open` return `ok: true` with correct `project_id`
- [ ] All 5 projects have `media_count >= 1`
- [ ] Smart Trader Zone avatar found (title contains "stz willy" or known UUID)
- [ ] All 5 MCP servers registered in openclaw.json
- [ ] Account ledger updated with `mcp_accessible: true`

## Account Mapping
| Alias | Email | Project ID | CDP Port | Profile Dir |
|-------|-------|------------|----------|-------------|
| FLOW-A | vipermir4@gmail.com | e9550a2d-8bcc-4f04-884e-e61ddc3fab1b | 9333 | Default |
| FLOW-B | wilcycrypto@gmail.com | 7ea12bbf-fee1-440e-acfe-716f1aa9b055 | 9334 | FLOW-B |
| FLOW-C | wilcy2122@gmail.com | 35fb2f37-262f-465e-a305-ff0331080208 | 9335 | FLOW-C |
| FLOW-D | cryptophantom05@gmail.com | 303cb7cf-ecfd-4c05-9c27-b84a891edcce | 9336 | FLOW-D |
| FLOW-E | vipercrypto05@gmail.com | b16a8c81-d2e3-4149-a59f-b0714b163241 | 9337 | FLOW-E |

## Key Insight
The MCP URL regex only accepts `https://flow.google.com/project/<uuid>`. Google's `/u/1/`, `/u/2/` prefixes are UI routing only. Use base project URLs.

## Files Created
- `C:\Users\dizon\.config\google-flow-mcp\config-FLOW-<X>.json` (5 files)
- `C:\Users\dizon\.google-flow-chrome\FLOW-<X>` (4 dirs)
- `C:\Users\dizon\.google-flow-mcp\FLOW-<X>` (4 dirs)
- Updated `C:\Users\dizon\.openclaw\openclaw.json` (5 MCP servers)
- Updated `production/accounts/flow-account-ledger.json`
