---
name: openclaw-cron-scheduler
description: Schedule a recurring agent task via OpenClaw automations.
---

1. Verify Composio CLI is available and authenticated: run `command -v composio`, `composio --version`, `composio whoami`. Require CLI >= 0.4.0.
2. List existing automations to prevent duplicates: call dispatch_action with id openclaw:core:automations, action list.
3. Confirm the agent identity: call agents_list and verify the agent id matches the job owner.
4. Build job parameters:
   - name: descriptive, prefixed with agent id (e.g., nova_ofw_video_script_daily)
   - agentId: configured agent id (e.g., nova)
   - sessionTarget: current
   - payload: { kind: "agentTurn", message: "<task instructions>" }
   - schedule: { kind: "cron", expr: "<standard cron>", tz: "<IANA timezone>" } — never UTC-convert
5. Add the job: dispatch_action with id openclaw:core:automations, action add, job with name, agentId, sessionTarget, payload, schedule.
6. Verify live registration: dispatch_action with id openclaw:core:automations, action list. Confirm enabled: true, correct cron/tz, future nextRunAt.
7. Confirm no duplicates: only one job with the new name.
8. Confirm Gateway untouched: no stop/restart/reconfigure.

Preferences: STZ Media pattern (cron kind/expr/tz, agentId, {agent}-{purpose} naming); OFW resource isolation; Gateway safety; verify live state before claiming success.