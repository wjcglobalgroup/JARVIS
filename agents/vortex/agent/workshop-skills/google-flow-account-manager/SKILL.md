---
name: google-flow-account-manager
description: Manage the seven authorized Google Flow accounts for STZ video production. Tracks account priority, authentication state, credit balances, available models, generation costs, and per-account scene assignments (1 scene per primary account).
metadata:
  version: "2.0.0"
  openclaw:
    emoji: "🔐"
    owner: vera
    project: stz
---

# Google Flow Account Manager

## Purpose
Manage Vera's seven authorized Google Flow accounts for the STZ Content Pipeline. Tracks account eligibility, authentication, credit balances, available models, generation costs, and scene assignments.

## Authorized Accounts (Priority Order)

| Priority | Account | Role | Scene | Status |
|----------|---------|------|-------|--------|
| 1 | SMARTTRADERZONE22@gmail.com | Primary 1 | scene_001 | Pending auth check |
| 2 | wilcycrypto@gmail.com | Primary 2 | scene_002 | Pending auth check |
| 3 | wilcycrypto05@gmail.com | Primary 3 | scene_003 | Pending auth check |
| 4 | 4.vipermir4@gmail.com | Primary 4 | scene_004 | Pending auth check |
| 5 | wilcy2122@gmail.com | Primary 5 | scene_005 | Pending auth check |
| 6 | cryptophantom05@gmail.com | Primary 6 | scene_006 | Pending auth check |
| 7 | vipercrypto05@gmail.com | Fallback 1 | Replacement only | Pending auth check |

## Rules (Absolute)

- Free access only. Never purchase credits, upgrade accounts, or incur charges.
- Do not rotate accounts to evade rate limits, quotas, or enforcement.
- Use another account only when the intended use is permitted and that account is independently authenticated and eligible.
- If no eligible account has sufficient free credits, preserve the unfinished scene queue and report the blocker.
- Never assume all accounts have 50 credits — verify actual balances where possible.
- Never regenerate a validated scene just because another account becomes available.

## Composio CLI Pre-Flight Check

Before any Composio operation:
1. Check `command -v composio` — confirm the CLI is on PATH.
2. Check `composio --version` — require CLI 0.4.0 or newer.
3. Check `composio whoami` — confirm the operator is signed in to the expected account.
4. If the CLI is missing, outdated, or not signed in, ask the trusted operator before installing, upgrading, or signing in. Share authorization URLs only in a private operator context.

## Account State Record

Each account must have a record file: `accounts/<account-slug>.json`

Fields:
- `email`: account email
- `priority`: 1–5
- `role`: "primary" | "fallback"
- `assigned_scenes`: array of scene IDs
- `auth_status`: "pending" | "authenticated" | "expired" | "blocked"
- `auth_method`: "browser" | "mcp" | "composio" | "none"
- `last_auth_check`: ISO timestamp
- `credits_balance`: number | "unknown"
- `credits_verified`: boolean
- `available_models`: array of model IDs
- `models_verified`: boolean
- `generation_cost_per_clip`: number | "unknown"
- `daily_limit`: number | "unknown"
- `used_today`: number
- `rate_limit_remaining`: number | "unknown"
- `active_jobs`: array of job IDs
- `completed_jobs`: array of {job_id, scene_id, cost, duration, status}
- `failed_jobs`: array of {job_id, scene_id, error, timestamp}
- `blocked_reason`: string | null

## Workflow

1. **Before any generation batch**: Check each account's auth status, credit balance, available models, and active jobs.
2. **Dry-run check**: Verify estimated cost vs. available credits before submitting.
3. **Account selection**: Use priority order. Fall back only when the primary account cannot lawfully continue.
4. **Record updates**: After each job submission, completion, or failure, update the account record.

## Multi-Account Isolation

Do not assume repeated login commands create isolated persistent browser profiles. Each account's authentication must be independently verified. Use the browser tool with separate profiles or the MCP's multi-account support if available.

## Credit Awareness

- Do not assume 50 credits = fixed number of clips. Costs vary by model, duration, and settings.
- If credits are exhausted, preserve the manifest and completed clips. Continue only if another account is permitted and eligible.
- Otherwise, leave affected scenes pending and report exactly what remains.