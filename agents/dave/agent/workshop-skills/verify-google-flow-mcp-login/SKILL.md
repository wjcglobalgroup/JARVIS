---
name: verify-google-flow-mcp-login
description: Verify Flow MCP login: google-flow-mcp doctor with FLOW_MCP_CONFIG per account, one at a time, never parallelize.
---

# Verify Google Flow MCP Login

Verify login status for multiple isolated Google Flow MCP accounts.

## Steps

1. For each account X (1 through 7), set the environment variable and run the doctor check:
   ```powershell
   $env:FLOW_MCP_CONFIG="C:\Users\dizon\.openclaw\workspace-dave\google-flow-mcp\configs\config-DAVE-FLOW-X.json"
   google-flow-mcp doctor
   ```
   Use the global `google-flow-mcp` binary, not `npx -y @park-sang-gwon\google-flow-mcp` (npx looks for a local package.json in Dave's workspace and fails).

2. Check the output for:
   - `ok   config:` — confirms the custom config file is read
   - `ok   cdp: port 310X free` — confirms the port is available
   - `ok   flow: logged in (https://flow.google.com/)` — confirms authentication

3. Run accounts one at a time. Never parallelize — multiple concurrent Chrome sessions lock OpenClaw's SQLite database and can shut down the Gateway.

4. If any account shows `flow: logged in` is missing or `NOT_LOGGED_IN`, stop and have the user complete manual sign-in for that account before proceeding.

## User Preferences

- Run one account at a time only.
- Never use `npx -y @park-sang-gwon\google-flow-mcp` from Dave's workspace directory.
- Verify all 7 accounts before any video generation.
- Never use Vortex's Flow accounts, ports, or browser profiles.

project: path:C:\Users\dizon\.openclaw\workspace-dave