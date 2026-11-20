---
name: windows-node-trading-script-hardening
description: Node.js trading script fails on Windows scheduler: binance-cli wrapper broken, LIVE fallback bypasses gates, hardcoded paths, dead code. Hardens execution, safety, portability.
---

# Windows Node Trading Script Hardening

## Triggering Task

A Node.js trading script works in manual terminal but fails or behaves dangerously when run on Windows via scheduler. Common failures: binance-cli shell wrapper doesn't execute, hardcoded absolute .env paths break portability, dangerous fallbacks silently enable LIVE trading, dead duplicate functions cause confusion.

## Procedure

### 1. Fix Windows binance-cli execution

The global `binance-cli` is a POSIX shell wrapper that fails on Windows. Call the ESM entry point directly via Node:

```javascript
// At top of script, after dotenv config
const BINANCE_CLI = process.platform === 'win32'
  ? 'node C:\\Users\\dizon\\AppData\\Roaming\\npm\\node_modules\\@binance\\binance-cli\\dist\\index.mjs'
  : 'binance-cli';

function runBinanceCli(args) {
  try {
    const cmd = [BINANCE_CLI, ...args].join(' ');
    const out = execSync(cmd, {
      encoding: 'utf8',
      maxBuffer: 10 * 1024 * 1024,
      shell: true,
    });
    return { ok: true, stdout: out, stderr: '' };
  } catch (err) {
    return {
      ok: false,
      stdout: err.stdout ? err.stdout.toString() : '',
      stderr: err.stderr ? err.stderr.toString() : String(err),
    };
  }
}

// Replace all execSync(['binance-cli', ...args].join(' ')) calls with runBinanceCli(args)
```

### 2. Remove dangerous LIVE fallback

Scripts must default to MONITOR_ONLY. Never silently upgrade to LIVE:

```javascript
// WRONG - silently enables LIVE trading
if (!process.env.TRADING_MODE || process.env.TRADING_MODE === 'MONITOR_ONLY') {
  process.env.TRADING_MODE = 'LIVE';
}

// CORRECT - safe default, explicit opt-in required
if (!process.env.TRADING_MODE) {
  process.env.TRADING_MODE = 'MONITOR_ONLY';
}
```

### 3. Use relative .env path

```javascript
// WRONG - hardcoded absolute path
require('dotenv').config({ path: 'C:\\Users\\dizon\\.openclaw\\workspace-sniper\\.env' });

// CORRECT - portable relative path
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });
```

### 4. Consolidate duplicate config loading

Remove duplicate functions that load the same config file from multiple paths. Keep one canonical path:

```javascript
// Single canonical path
const marcoStatePath = path.join(__dirname, '..', '.agents', 'skills', 'marco-state.json');
```

### 5. Remove dead code

Delete unused duplicate functions (e.g., `loadMarcoStateFn`, `isMarcoGateFreshAndValidFn`) and references to undefined config (e.g., `ENV.MARCO_MACRO_STATE_PATH`).

### 6. Verify the fix

```bash
# Syntax check
node --check scripts/sniper-market-scan.js
node --check scripts/sniper-position-monitor.js

# Run scripts
node scripts/sniper-market-scan.js
# Should show: ◇ injected env (N) from .env
# Marco gate fails cleanly with stale state reason

node scripts/sniper-position-monitor.js
# Should show: SNIPER RECONCILIATION REPORT - Status: PASS
```

## Decision Rules

| Observation | Rule |
|-------------|------|
| `binance-cli` command not found / no output on Windows | Use node direct call to ESM entry point |
| Script silently changes TRADING_MODE to LIVE | Remove fallback; require explicit LIVE in .env |
| Hardcoded absolute .env path | Replace with `path.join(__dirname, '..', '.env')` |
| Multiple functions load same config file | Consolidate to single canonical path |
| Unused duplicate functions remain | Delete dead code |

## What Not to Do

- Wrap binance-cli in cmd /c or powershell -Command on Windows — use node direct call
- Assume the global binance-cli shell wrapper works cross-platform — test on target OS
- Leave MONITOR_ONLY → LIVE fallback — it bypasses authorization gates; require explicit LIVE
- Hardcode user-specific paths (C:\Users\dizon...) in scripts — use relative paths from __dirname
- Keep dead duplicate functions — delete them to avoid maintenance confusion

## Supporting Evidence

- `sniper-market-scan.js` and `sniper-position-monitor.js` both fixed
- Windows binance-cli execution verified: `node .../index.mjs futures-usds ticker24hr-price-change-statistics --symbol BTCUSDT` returns JSON
- Dangerous LIVE fallback removed from both scripts
- Hardcoded .env paths replaced with relative paths
- Duplicate Marco state loading consolidated to single path
- Dead code (loadMarcoStateFn, isMarcoGateFreshAndValidFn, ENV.MARCO_MACRO_STATE_PATH) removed
- Both scripts pass syntax check and execute correctly

## Related Skills

- `node-script-environment-setup` — .env loading for cron/scheduler
- `binance-cli-migration` — command name changes across binance-cli versions
- `trading-engine` (workspace skill) — uses these scripts for market scan and position monitor