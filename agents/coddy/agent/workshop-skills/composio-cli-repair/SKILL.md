---
name: composio-cli-repair
description: Install or upgrade the Composio CLI in WSL when the Windows installation returns HTTP 410 Gone from retired v1 API endpoints.
---

# Composio CLI Repair

## Trigger
The Windows `composio` CLI returns HTTP 410 Gone for `apps`, `connections`, `actions`, `execute`, or `triggers` commands. `composio whoami` succeeds locally but no real API calls work.

## Prerequisite check (run before every Composio operation)

1. Confirm the CLI is installed and on PATH:
   ```
   command -v composio
   ```
   Check: returns a path. If missing, stop and ask the operator before installing.

2. Confirm authentication:
   ```
   composio whoami
   ```
   Check: returns account information and base URL. `whoami` is a local config read, not an API call — success does not prove the backend works.

3. Confirm the CLI version is 0.4.0 or newer. `composio --version` is unsupported on some builds; read it from the installed `composio-core` package.json instead.
   Check: version is 0.4.0 or newer. If below 0.4.0, stop and ask the operator before upgrading.

## Steps

1. Start WSL Ubuntu:
   ```
   wsl.exe -d Ubuntu
   ```
   Check: WSL starts without error and returns to a bash prompt.

2. Install required system utilities:
   ```
   sudo apt-get update && sudo apt-get install -y unzip
   ```
   Check: `which unzip` returns a path.

3. Download and run the official Composio CLI installer (WSL already has Node.js):
   ```
   curl -fsSL https://composio.dev/install -o /tmp/install-composio.sh
   /usr/bin/bash /tmp/install-composio.sh
   ```
   Check: Output says "Composio CLI was installed to ~/.composio/composio" and "Configured bash shell setup."

5. Verify the new CLI works:
   ```
   /home/dizon/.local/bin/composio whoami
   ```
   Check: `whoami` returns account information (not HTTP 410 Gone).

6. Authenticate (operator action):
   ```
   /home/dizon/.local/bin/composio login
   ```
   Check: `composio whoami` returns account information.

## Standing preferences
- Do not uninstall legacy Windows npm packages until dependencies and migration plan are understood.
- Do not stop or restart the OpenClaw Gateway.
- Share authorization URLs only with the operator in private context.
- The operator must complete any browser-based OAuth flow themselves.

## Notes
- The new CLI lives in WSL at `~/.local/bin/composio`. The Windows Gateway does not automatically see WSL-installed CLIs; plan PATH or symlink integration before expecting OpenClaw to use it.
- `composio whoami` on the old CLI is a local config read, not an API call — it does not prove the backend works.
- The Composio installer explicitly requires `unzip` and will fail with an error before doing anything if it is missing.
- **Host credential isolation**: Windows host (`C:\Users\...\npm\composio`) and WSL host (`~/.composio/composio`) maintain separate credential stores. Connections authorized in one do not propagate to the other.
- **Generate OAuth URLs without browser**: Use `--no-browser --no-wait` flags to get redirect URLs for private operator authorization.
- **Switch API keys per agent**: Use `COMPOSIO_API_KEY=ak_...` environment variable to operate with different agent credentials on the same host.
- **Windows npm CLI is deprecated**: The npm package `@composio/core` (v0.27.0) uses retired v1 API endpoints (HTTP 410 Gone). Use the standalone WSL CLI `@composio/cli@0.6.0` instead.