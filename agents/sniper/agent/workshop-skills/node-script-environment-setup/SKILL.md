---
name: node-script-environment-setup
description: Configure Node.js scripts to load environment variables from .env when executed via cron, Task Scheduler, or other schedulers that don't inherit the shell environment.
---

# Node Script Environment Setup

## Triggering Task

A Node.js script runs successfully when invoked manually in a terminal with `source .env` or when environment variables are pre-set, but fails when executed via cron, Windows Task Scheduler, or systemd because `process.env` lacks the required variables.

## Procedure

### 1. Install dotenv

```bash
npm install dotenv --prefix /path/to/workspace
```

### 2. Load .env at script entry point (before any other requires)

```javascript
// FIRST LINE of the script (before any require/import that reads process.env)
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

// Now other modules can safely read process.env.VAR_NAME
const { TradingEngine } = require('./.agents/skills/trading-engine/src/trading-engine');
```

### 3. Verify injection works

```bash
node scripts/your-script.js
# Output should show: ◇ injected env (N) from .env
```

## Decision Rules

| Situation | Rule |
|-----------|------|
| Script runs manually but fails via cron/scheduler | Missing `dotenv.config()` — add at top of script |
| `process.env.MY_VAR` is `undefined` in scheduled run | `.env` not loaded — verify dotenv call executes first |
| Multiple scripts need same env | Each script must call `dotenv.config()` independently |
| `.env` path differs from script location | Use `path.join(__dirname, '..', '.env')` to resolve relative to project root |

## What Not to Do

- Do not rely on shell sourcing (`. .env`) in cron — the scheduler spawns a non-interactive shell.
- Do not assume `process.env` is populated from `.env` without explicit `dotenv.config()`.
- Do not place `require('dotenv').config()` after other requires that read `process.env` — they will see undefined values.
- Do not hardcode absolute paths to `.env` — use `path.join(__dirname, '..', '.env')` for portability.

## Supporting Evidence

During Sniper LIVE mode activation (2026-10-20):
- `sniper-position-monitor.js` and `sniper-market-scan.js` ran via scheduler showing `MONITOR_ONLY` despite `.env` containing `TRADING_MODE=LIVE`
- Root cause: scripts executed by scheduler didn't load `.env` automatically
- Fix: Added `require('dotenv').config({ path: path.join(__dirname, '..', '.env') })` as first executable line in both scripts
- Verification: `◇ injected env (5) from .env` confirmed injection; output now shows `Trading Mode: LIVE`

## Related Skills

- `trading-engine` (workspace skill) — uses `TRADING_MODE`, `NOTION_API_TOKEN`, `DISCORD_BOT_TOKEN`, etc.
- `binance-cli-migration` — binance-cli commands also need env vars for API credentials