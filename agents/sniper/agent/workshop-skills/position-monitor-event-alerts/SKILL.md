---
name: position-monitor-event-alerts
description: Create/update 15-min Binance position monitor with actionable-event-only Discord alerts (entry, TP, SL, breakeven, close, errors). Includes deduplication, simulation mode, OpenClaw cron.
---

# Position Monitor with Event-Based Discord Alerts

## When to Use
- Need a recurring 15-minute position reconciliation job for Binance USDT-M Futures
- Must send Discord alerts ONLY for actionable trading events (entry confirmed, TP/SL hit, breakeven activated/hit, position closed, order errors)
- Must suppress routine monitoring output (no hourly summaries, no unchanged position status)
- Need simulation mode for testing without live Binance credentials
- Need idempotent event deduplication across monitor runs

## Prerequisites
- Binance CLI v1.3.0+ with configured profile (commands: `position-information-v3`, `current-all-open-orders`, `account-information-v3`)
- OpenClaw Gateway with automation/cron support
- Discord bot token + channel ID (not webhook)
- Node.js environment with access to trading-engine state files

## Procedure

### 1. Create Position Monitor Script
**File**: `.agents/skills/position-monitor/src/position-monitor.js`

Key implementation points:
- Load local positions from `trading-engine/state/trade-state.json`
- Query Binance using correct v1.3.0+ commands:
  - `binance-cli futures-usds position-information-v3 --json`
  - `binance-cli futures-usds current-all-open-orders --json`
  - `binance-cli futures-usds account-information-v3 --json`
- Build position/order maps from Binance response (authoritative source)
- Detect events by comparing local vs exchange state:
  - `ENTRY_CONFIRMED`: position on Binance, not in local state
  - `TP_HIT` / `SL_HIT`: protective order filled (check order status + position size change)
  - `BREAKEVEN_ACTIVATED`: +1.1R reached (mark price >= entry + 1.1×risk for LONG)
  - `BREAKEVEN_HIT`: price reaches fee-adjusted breakeven stop
  - `POSITION_CLOSED`: local position missing on Binance (amt = 0)
  - `ORDER_ERROR`: missing SL or TP order on exchange
- **Deduplication**: Generate stable event ID: `${symbol}-${eventType}-${price}-${5minBucket}`; track in `events/processed-events.json`
- **Discord**: Only send for actionable event types; use bot token auth (`Authorization: Bot <token>`) to `https://discord.com/api/v10/channels/${channelId}/messages`
- **Simulation mode**: `POSITION_MONITOR_SIMULATION=true` skips Binance queries, logs only
- **File persistence**: Atomic writes (`write tmp → rename`); events per symbol in `events/${symbol}-events.json`; cycle reports in `logs/position-monitor-reports.json`

### 2. Create OpenClaw 15-Minute Cron Automation
```bash
openclaw cron add \
  --name "sniper-15min-position-monitor" \
  --cron "*/15 * * * *" \
  --tz "Asia/Manila" \
  --agent "sniper" \
  --session "isolated" \
  --declaration-key "sniper-15min-position-monitor" \
  --command-env "POSITION_MONITOR_SIMULATION=true" \
  --message "Run 15-minute position monitor: reconcile positions, check TP/SL/BE events, send actionable Discord alerts only"
```
- `--declaration-key` makes it idempotent (re-running updates existing job)
- `--command-env` passes simulation mode env var
- `--session isolated` runs in clean context
- Timezone `Asia/Manila` aligns with STZ schedule

### 3. Verify
- Run manually: `POSITION_MONITOR_SIMULATION=true node src/position-monitor.js`
- Check output: `positionsChecked`, `newEvents`, `alertsSent`, `alertsSuppressed`, `errors`
- Verify automation appears in `openclaw automations list`
- Confirm Discord channel resolves correctly (Sniper Discord account → channel `1442192165722914857`)

### 4. Enable Live Mode
- Fix Binance CLI profile credentials (RSA/ED25519 private key)
- Remove `POSITION_MONITOR_SIMULATION=true` from automation or set `POSITION_MONITOR_SIMULATION=false`
- Ensure `DISCORD_BOT_TOKEN` in `.env` for Discord alerts

## Key Patterns Learned
- **Binance CLI v1.3.0+**: Use `position-information-v3`, `current-all-open-orders`, `account-information-v3` with `--json` flag; old commands (`position`, `open-orders`, `account`) removed
- **OpenClaw cron**: `--declaration-key` for idempotent updates; `--command-env` for env vars; `--tz` for timezone
- **Event deduplication**: 5-minute time buckets in event ID prevent duplicate alerts on re-runs
- **Discord bot token**: Use `Authorization: Bot <token>` header, POST to `/channels/{id}/messages` (not webhook)
- **Simulation env var**: `POSITION_MONITOR_SIMULATION=true` allows testing without credentials
- **Quiet mode for scheduler stdout**: Add `--quiet` flag (or `QUIET=true` env var) to suppress routine PASS output. When the monitor is run via Windows Task Scheduler or cron, stdout capture can pipe routine reports to Discord webhooks. Quiet mode only outputs on FAIL/WARNING/errors, preventing Discord spam while preserving actionable event visibility.
  ```javascript
  const QUIET = process.argv.includes('--quiet') || process.env.QUIET === 'true';
  if (!QUIET || status !== 'PASS' || errors.length > 0) {
    console.log(report); // only outputs on actionable issues
  }
  ```
  Scheduler command: `node scripts/sniper-position-monitor.js --quiet`

## Files Created
- `.agents/skills/position-monitor/src/position-monitor.js` — main monitor script
- OpenClaw automation `sniper-15min-position-monitor` — 15-min cron job

## Standing Preferences
- Discord channel: `1442192165722914857` (STZ trading signals)
- Actionable events only: `ENTRY_CONFIRMED`, `TP_HIT`, `SL_HIT`, `BREAKEVEN_ACTIVATED`, `BREAKEVEN_HIT`, `POSITION_CLOSED`, `ORDER_ERROR`
- No routine monitoring spam in Discord
- Simulation mode default for safety
- Asia/Manila timezone for all STZ schedules