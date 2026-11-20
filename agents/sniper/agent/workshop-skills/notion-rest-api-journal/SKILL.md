---
name: notion-rest-api-journal
description: Implement Notion trading journal writes via direct REST API (curl) instead of ntn CLI. The ntn CLI is a shell script that fails on Windows; REST API works cross-platform with only NOTION_API_TOKEN required.
---

# Notion Trading Journal via REST API

## Triggering Task

You need to write trade lifecycle events (setup, entry, breakeven_activation, trailing_update, exit) to the STZ Trading Pipeline database from a Node.js script that runs on Windows (or any platform). The `ntn` CLI is unavailable or fails (it's a shell script wrapper), and you want a dependency-free solution using only `curl` and `NOTION_API_TOKEN`.

## Procedure

### 1. Prerequisites

- Notion integration created at https://www.notion.so/my-integrations
- Integration token (starts with `ntn_` or `secret_`)
- STZ Trading Pipeline database shared with the integration
- Data Source ID for the database (not the database ID)

### 2. Required Environment Variable

```bash
# Add to .env
NOTION_API_TOKEN=secret_xxx
NOTION_TRADING_PIPELINE_DS_ID=e5b7e481-efa6-4504-9105-684cc6fc6d56
```

### 3. Core REST API Wrapper (Node.js)

```javascript
class NotionJournal {
  constructor() {
    this.token = process.env.NOTION_API_TOKEN || '';
    this.dsId = process.env.NOTION_TRADING_PIPELINE_DS_ID;
    this.enabled = !!this.token;
    this.apiVersion = '2026-03-11';
    this.baseUrl = 'https://api.notion.com/v1';
  }

  async _request(method, path, body = null) {
    if (!this.enabled) return { ok: false, reason: 'NOTION_API_TOKEN not set' };
    const { execSync } = require('child_process');
    const url = `${this.baseUrl}${path}`;
    const headers = [
      '-H', 'Authorization: Bearer ' + this.token,
      '-H', `Notion-Version: ${this.apiVersion}`,
      '-H', 'Content-Type: application/json',
    ];
    let cmd = `curl -sS -X ${method} ${headers.map(h => `'${h}'`).join(' ')} '${url}'`;
    if (body) {
      cmd += ` --data '${JSON.stringify(body).replace(/'/g, "\\'")}'`;
    }
    try {
      const out = execSync(cmd, { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
      return { ok: true, data: JSON.parse(out) };
    } catch (e) {
      return { ok: false, error: e.message, stderr: e.stderr?.toString() };
    }
  }
}
```

### 4. Dedup via External Ref (Upsert Pattern)

```javascript
async upsertTrade(trade) {
  // 1. Query by External Ref (unique per trade lifecycle)
  const filter = {
    filter: { property: 'External Ref', rich_text: { equals: trade.externalRef } },
    page_size: 1,
  };
  const queryRes = await this._request('POST', `/data_sources/${this.dsId}/query`, filter);
  if (!queryRes.ok) return queryRes;

  // 2. Update existing or create new
  if (queryRes.data.results?.length > 0) {
    return this._request('PATCH', `/pages/${queryRes.data.results[0].id}`, { properties: this.tradeToProperties(trade) });
  }
  return this._request('POST', '/pages', {
    parent: { data_source_id: this.dsId },
    properties: this.tradeToProperties(trade),
  });
}
```

### 5. Map Trade Object to Notion Properties

```javascript
tradeToProperties(trade) {
  const props = {};
  const add = (name, value, type = 'rich_text') => {
    if (value === undefined || value === null || value === '') return;
    if (type === 'rich_text') props[name] = { rich_text: [{ text: { content: String(value) } }] };
    else if (type === 'title') props[name] = { title: [{ text: { content: String(value) } }] };
    else if (type === 'number') props[name] = { number: Number(value) };
    else if (type === 'select') props[name] = { select: { name: String(value) } };
    else if (type === 'date') props[name] = { date: { start: String(value) } };
    else if (type === 'checkbox') props[name] = { checkbox: Boolean(value) };
  };
  add('Trade ID', trade.tradeId);
  add('Symbol', trade.symbol);
  add('Direction', trade.direction, 'select');
  add('Setup / Strategy', 'SMC');
  add('Exchange', 'Binance');
  add('Market Type', 'USDT-M Futures');
  add('Entry Price', trade.entryPrice, 'number');
  add('Stop Loss', trade.stopLoss, 'number');
  add('Take Profit', trade.takeProfit, 'number');
  add('Position Size', trade.positionSizeUsdt, 'number');
  add('Leverage', 20, 'number');
  add('Risk %', trade.riskPct, 'number');
  add('Planned R:R', trade.rrToLiquidityTarget, 'number');
  add('Entry Time', trade.entryTime || new Date().toISOString(), 'date');
  add('Status', trade.status || 'Setup', 'select');
  add('Outcome', trade.outcome || 'Open', 'select');
  add('External Ref', trade.externalRef);
  add('Assigned Agent', 'Sniper', 'select');
  add('Execution Mode', process.env.TRADING_MODE || 'MONITOR_ONLY', 'select');
  // Optional SMC fields
  if (trade.bias1d) add('1D Bias', trade.bias1d);
  if (trade.structure4h) add('4H Structure', trade.structure4h);
  if (trade.entry15m) add('15M Entry', trade.entry15m);
  if (trade.sscValid !== undefined) add('SSC Valid', trade.sscValid, 'checkbox');
  if (trade.regime) add('Regime', trade.regime);
  if (trade.activationPrice) add('Activation Price (+1.1R)', trade.activationPrice, 'number');
  if (trade.feeAdjustedBreakeven) add('Fee-Adjusted Breakeven', trade.feeAdjustedBreakeven, 'number');
  if (trade.trailingDistance) add('Trailing Distance', trade.trailingDistance, 'number');
  if (trade.fees) add('Fees', trade.fees);
  if (trade.journalAnalysis) add('Journal / Analysis', trade.journalAnalysis);
  if (trade.lessons) add('Lessons', trade.lessons);
  if (trade.pnl !== undefined) add('P&L', trade.pnl, 'number');
  if (trade.pnlPct !== undefined) add('P&L %', trade.pnlPct, 'number');
  if (trade.rMultiple !== undefined) add('R Multiple', trade.rMultiple, 'number');
  if (trade.result) add('Result', trade.result);
  if (trade.setupGrade) add('Setup Grade', trade.setupGrade);
  if (trade.exitPrice) add('Exit Price', trade.exitPrice, 'number');
  if (trade.exitTime) add('Exit Time', trade.exitTime, 'date');
  if (trade.exitReason) add('Exit Reason', trade.exitReason);
  if (trade.entryReason) add('Entry Reason', trade.entryReason);
  if (trade.mistakes) add('Mistakes', trade.mistakes);
  return props;
}
```

### 6. Journal Lifecycle Events

| Event | When | Required Fields |
|-------|------|-----------------|
| `setup` | Candidate evaluated | symbol, direction, externalRef, bias1d, structure4h, entry15m, sscValid, regime |
| `entry` | Fill confirmed | symbol, direction, entryPrice, entryTime, stopLoss, takeProfit, positionSizeUsdt, riskPct, rrToLiquidityTarget, externalRef |
| `breakeven_activation` | +1.1R reached | symbol, activationPrice, feeAdjustedBreakeven, trailingDistance, externalRef |
| `trailing_update` | Trailing stop moved | symbol, previousStop, newStop, stopSource, externalRef |
| `exit` | SL/TP/manual close | symbol, exitPrice, exitTime, exitReason, pnl, pnlPct, rMultiple, outcome, externalRef |

## Decision Rules

| Situation | Rule |
|-----------|------|
| ntn CLI fails on Windows (SyntaxError) | Use REST API directly — no ntn dependency |
| Journal write fails | Log error, continue trading; never block position management |
| Duplicate trade records | Upsert by External Ref — query first, update if exists |
| NOTION_API_TOKEN not set | Return `{ ok: false, reason: 'NOTION_API_TOKEN not set' }`; don't crash |
| Trade lifecycle event | Call `upsertTrade()` with event-specific fields + stable `externalRef` |

## What Not to Do

- Do not use `ntn` CLI in scheduled scripts — it's a shell script that fails on Windows.
- Do not use markdown content (`ntn pages create --content`) — use structured properties via REST API.
- Do not make journal writes synchronous with protective order handling — journal is async, best-effort.
- Do not log `NOTION_API_TOKEN` or full curl command with token — truncate in logs.

## Supporting Evidence

During Sniper LIVE mode activation (2026-10-20):
- `ntn` CLI installed via npm but failed: shell script wrapper (`#!/bin/sh`) caused `SyntaxError` on Node.js Windows
- Rewrote `NotionJournal` class in `trading-engine/src/trading-engine.js` to use `curl` via `execSync` against Notion REST API v1
- Verified: upsert by External Ref works (query data source → PATCH existing or POST new)
- Verified: all 37 STZ Trading Pipeline properties map correctly (rich_text, number, select, date, checkbox)
- Verified: journal writes are non-blocking — trading continues if Notion unavailable

## Related Skills

- `node-script-environment-setup` — scripts must load `.env` for `NOTION_API_TOKEN`
- `trading-engine` (workspace skill) — uses this journal implementation
- `position-monitor` (workspace skill) — journals breakeven/trailing events