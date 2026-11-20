---
name: jarvis-daily-report
description: "Generate the WJC GLOBAL Daily Morning Brief (08:30 Asia/Manila) using the local telemetry collector script. Produces a 7-section operational report from SQLite, agent workspaces, and cron state."
---

# Jarvis Daily Morning Brief

## Trigger
- Manual invocation or scheduled cron execution (`jarvis-daily-report` job at 08:30 Asia/Manila)

## Safety constraint (AGENTS.md §6)
Do not create, delete, replace, or modify cron jobs. Inspect existing `jarvis-daily-report` job read-only unless owner explicitly authorizes a schedule change.

## Procedure

### 1. Run Generation Script
The executable script at `skills/jarvis-daily-report/scripts/generate-report.mjs` invokes `telemetry-collector.py` which:
- Queries `C:\Users\dizon\.openclaw\state\openclaw.sqlite` for cron job telemetry (last 24h)
- Reads Vera's Notion payload files from `workspace-vera/scripts/`
- Checks Vortex completed MP4 renders in `workspace-vortex/production/completed/`
- Reads Marco's macro gate state from `workspace-marco/macro-gate-state.json`
- Reads Sniper trading mode from `workspace-sniper/.env`
- Outputs a 7-section Markdown report

Run with:
```bash
node skills/jarvis-daily-report/scripts/generate-report.mjs
```

### 2. Report Structure (7 Sections)
The telemetry collector produces exactly these sections:
1. **Executive Overview** — Group status, gateway health, automation counts, key accomplishment
2. **STZ Crypto Media** — Vera/Vortex/Moddy pipeline status with evidence
3. **OFW Digital Media** — Nova/Dave/June pipeline status, isolation verification
4. **Technology & Automation** — Coddy lead, gateway, git commits, Notion missions, system alerts
5. **Trading & Investment** — Marco macro gate, Sniper mode, risk discipline
6. **Kaixin Transport** — Kyle lead, inquiry automation, Facebook page, bookings
7. **CEO Attention Required** — Material blockers requiring executive decision

### 3. Delivery
- Save report to `workspace/reports/daily-brief-YYYY-MM-DD.md`
- Post to Discord channel `1557280479970066452`

### 4. Verification
- Script executes without errors
- All 7 sections populated with ground-truth data or explicit UNAVAILABLE markers
- Discord delivery succeeds
- No duplicate cronjob created

## Supporting Files
- `skills/jarvis-daily-report/scripts/generate-report.mjs` — Node wrapper calling Python collector
- `skills/jarvis-daily-report/scripts/telemetry-collector.py` — Core telemetry aggregation logic
- `skills/jarvis-daily-report/scripts/generate-report-fixed.mjs` — Alternative implementation (not used by cron)

## Completion Criteria
- Report generated and saved
- Delivered to Discord executive channel
- All sections reflect current ground truth
- No duplicate cronjob created