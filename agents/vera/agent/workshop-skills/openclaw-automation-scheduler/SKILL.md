---
name: openclaw-automation-scheduler
description: Register automation scheduler cron jobs in the OpenClaw gateway config so jobs appear in the web UI and run on schedule.
metadata:
  version: "1.0.0"
  openclaw:
    emoji: "⏰"
    owner: vera
    project: stz
---

## 1. Add Cron Jobs to openclaw.json

Edit `C:\Users\dizon\.openclaw\openclaw.json`. Add a `cron` object inside `gateway` with `enabled: true` and a `jobs` array. Each job needs: `id`, `description`, `agent`, `expression`, `timezone`, `enabled`.

Example:
```json
{
  "cron": {
    "enabled": true,
    "jobs": [
      {
        "id": "vera-daily-video-script",
        "description": "STZ Daily Video Scriptwriting at 09:20 PHT",
        "agent": "vera",
        "expression": "20 9 * * *",
        "timezone": "Asia/Manila",
        "enabled": true
      },
      {
        "id": "vera-image-text-script",
        "description": "STZ Image/Text Scriptwriting every 6 hours",
        "agent": "vera",
        "expression": "55 */6 * * *",
        "timezone": "Asia/Manila",
        "enabled": true
      }
    ]
  }
}
```

## 2. Enable Cron and Control UI in the Running Gateway

Run both `openclaw config.set` commands so the live gateway picks up the settings without a restart:

```
openclaw config.set gateway.cron.enabled true
openclaw config.set gateway.controlUi.enabled true
```

If `openclaw` returns an inference error, retry once. If it still fails, proceed to step 3 — the JSON config is already written and will take effect on next gateway start.

## 3. Verify the Config via PowerShell

Read the file directly to confirm both jobs are present:

```powershell
(Get-Content C:\Users\dizon\.openclaw\openclaw.json | ConvertFrom-Json).gateway.cron.jobs | Format-Table id, expression, timezone, enabled -AutoSize
```

Expected output: both jobs listed with `enabled: True` and correct expressions/timezone.

Also confirm the top-level settings:

```powershell
(Get-Content C:\Users\dizon\.openclaw\openclaw.json | ConvertFrom-Json).gateway | Select-Object controlUi, cron
```

Expected output: `controlUi.enabled` and `cron.enabled` both true.

## 4. Access the Automation Scheduler in the Web UI

Open `http://127.0.0.1:18789` in a browser. Wait for the Control UI app bundle to load (up to ~15 seconds). The automation scheduler page should list both registered jobs.

If the page shows a fallback mount screen, wait and reload. Do not restart the gateway.

## 5. Gateway Restart Policy

Never stop, restart, kill, or interrupt the OpenClaw Gateway without Willy's explicit authorization. The cron jobs take effect on the next gateway start; if they do not appear in the web UI after the app bundle loads, ask Willy for authorization to restart before proceeding.

## Standing Preferences

- Always verify config via PowerShell reading openclaw.json — do not rely solely on `openclaw` tool output.
- Report results to Jarvis via A2A after registration.
- Timezone is always Asia/Manila for STZ production schedules.