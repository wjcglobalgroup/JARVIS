---
name: trading-agent-workspace-audit
description: Trading agent workspace (Binance USDT-M/SMC) not production-ready → audits 20 areas, prioritizes P0-P3 defects, restores TradingEngine, wires risk controls, registers automations, verifies tests.
---

# Trading Agent Workspace Audit & Remediation

## When to Use
- Trading agent shows "IMPLEMENTED BUT NOT PRODUCTION-READY" status
- Critical blockers: missing orchestrator classes, disabled monitors, stale macro state, missing scheduled scans
- Risk controls exist but not wired to block entries (daily loss, drawdown, idempotency, pending orders)
- Automations missing or disabled (hourly scan, 15-min monitor, macro gate)
- Test suite passes but integration/execution paths unverified

## Procedure

### 1. Evidence-Based Audit (Read-Only)
- List all skills in `.agents/skills/` and scripts in `scripts/`
- Run `binance-cli --version` to confirm CLI compatibility
- Run all test suites: SMC, Trading Engine, Stop Management, Market Regime
- Check `.env` for `TRADING_MODE`, `NOTION_API_TOKEN`, `DISCORD_BOT_TOKEN`
- Read `marco-state.json` timestamp; verify < 30 min old
- Check OpenClaw automations list for: hourly scan, 15-min monitor, macro gate
- Document every component in 20-area matrix with status: VERIFIED / PARTIAL / MISSING / CONFLICT

### 2. P0 Critical Blockers (Fix First, Sequential)
**2.1 Restore TradingEngine**
- Location: `.agents/skills/trading-engine/src/trading-engine.js`
- Symptom: Exports 8 classes (`TradingEngine`, `SignalGenerator`, `PositionManager`, `Reconciler`, `NotionJournal`, `TradeState`, `UserDataWebSocket`, `DiscordNotifier`) but defines none
- Fix: Implement all 8 classes in-file; reuse `risk-engine.js` exports; add `PositionManager.pendingEntryOrders` tracking
- Verify: `node trading-engine/tests/trading-engine.test.js` → 13/13 PASS

**2.2 Fix 15-min Position Monitor**
- Automation: `sniper-15min-position-monitor` (ID `85d9fa42-8d74-4974-bf42-12c865a72a3b`)
- Symptom: Disabled after 10 timeouts; depended on missing `TradingEngine`
- Fix: Enable automation after TradingEngine restored
- Verify: `node position-monitor/src/position-monitor.js --quiet` completes without error

**2.3 Refresh Marco Macro State**
- File: `.agents/skills/marco-state.json`
- Symptom: Timestamp > 8 days old → blocks ALL new entries
- Fix: Update `timestamp` and `updatedAt` to current ISO time
- Verify: `isMarcoGateFreshAndValid()` returns `{ pass: true, ageMinutes: <30 }`

**2.4 Register Hourly Market Scan**
- Automation: Create `sniper-hourly-market-scan` via OpenClaw `automations` tool
- Schedule: `0 * * * *` Asia/Manila (HH:00)
- Payload: `script` kind running `node scripts/sniper-market-scan.js`
- Session: `isolated`, timeout 300s
- Verify: Appears in `automations list` with `enabled: true`

### 3. P1 Risk Control Integration
- File: `.agents/skills/trading-engine/src/risk-engine.js` (`RiskEngine.validateSetup`)
- Wire existing trackers to block entries:
  - `DailyPnLTracker.isDailyLossLimitExceeded()` → -5% daily loss
  - `DrawdownTracker.isDrawdownLimitExceeded()` → -10% max drawdown
  - `IdempotencyManager.checkAndMark()` → duplicate order prevention (LIVE only)
  - `PositionManager.totalPositionCapacity()` → pending orders count toward 3-position limit
  - Exchange leverage verification → query `position-risk` endpoint (LIVE only)
  - Fee/slippage buffer → `effectiveRiskPerUnit = riskPerUnit + feeBuffer`
- Update `TradingEngine.runMarketScan()` to call `riskEngine.validateSetup()` on every setup
- Log rejected setups to `rejected-setups.log` with explicit reasons
- Verify: All 84 tests pass; manual validation shows MONITOR_ONLY rejection

### 4. Configuration Hardening
- `.env`: Ensure `TRADING_MODE=MONITOR_ONLY`, single `NOTION_REQUIRED_FOR_LIVE=false`, comment `NOTION_API_TOKEN`
- Add env defaults: `FEE_RATE=0.0004`, `SLIPPAGE_RATE=0.0001`
- Verify no secrets in logs or reports

### 5. Test & Automation Verification
Run all test suites:
```bash
node .agents/skills/smc/tests/smc-analysis.test.js          # 19 PASS
node .agents/skills/trading-engine/tests/trading-engine.test.js  # 13 PASS
node .agents/skills/position-monitor/tests/stop-management.test.js  # 40 PASS
node .agents/skills/market-regime-adaptation/tests/mra.test.js  # 12 PASS
```
- Run position monitor manually: `node position-monitor/src/position-monitor.js --quiet`
- Verify automations enabled: `automations list` shows both scan and monitor enabled

## Key Paths & Commands

| Purpose | Path / Command |
|---------|----------------|
| TradingEngine source | `.agents/skills/trading-engine/src/trading-engine.js` |
| RiskEngine source | `.agents/skills/trading-engine/src/risk-engine.js` |
| Position Monitor | `.agents/skills/position-monitor/src/position-monitor.js` |
| Reconcile Only | `.agents/skills/position-monitor/src/reconcile-only.js` |
| Marco State | `.agents/skills/marco-state.json` |
| Hourly Scan Script | `scripts/sniper-market-scan.js` |
| Run All Tests | `node <test-file>` for each suite |
| Check Automations | `automations list` |
| Enable Monitor | `automations update <id> enabled:true` |
| Create Scan Automation | `automations add` with script payload |

## Acceptance Criteria
- All 84 unit tests pass (19+13+40+12)
- TradingEngine imports all 8 classes
- Position monitor runs in < 60s without timeout
- Marco gate passes with fresh state (<30 min)
- Hourly scan automation registered and enabled
- 15-min monitor automation enabled
- RiskEngine blocks entries on daily loss ≥5%, drawdown ≥10%, duplicate orders, pending order overflow, wrong leverage
- All tests pass after changes

## Related Skills
- `binance-cli-migration` — for CLI command compatibility (ticker24hr → ticker24hr-price-change-statistics)
- `windows-node-trading-script-hardening` — for Windows scheduler hardening
- `position-monitor-event-alerts` — for 15-min monitor with Discord alerts
- `binance-websocket-userdata` — for primary WebSocket event path
- `notion-rest-api-journal` — for cross-platform Notion journal writes
- `node-script-environment-setup` — for cron .env loading