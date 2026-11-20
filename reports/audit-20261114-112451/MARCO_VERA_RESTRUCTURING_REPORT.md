# Marco & Vera Restructuring — Completion Report

**Date:** 2026-11-14 (Asia/Manila)

## A. Executive summary

The role split and scheduler cleanup are implemented. **Marco is now limited to Trading & Investment macro/risk intelligence and the Sniper Macro Gate. Vera independently researches and scripts STZ content without waiting for, requesting, reading or requiring Marco's output.** The two Marco content-research Cron jobs were removed. The hourly Macro Gate job remains.

The software and schedule changes are verified, but the end-to-end organization is **NOT PRODUCTION READY**. A direct Macro Gate runtime check produced `BLOCK` because the report had fewer than two evidenced source hosts and no configured primary economic-calendar source. The fail-closed behavior correctly prevents new-entry evaluation. Vera's Notion scope is still unverified; Vortex, Moddy, Dave and June jobs are temporarily disabled by the content-readiness pass pending security/integration repairs.

## B. Agent-by-agent results

### Marco — Trading macro/risk intelligence

- Replaced active workspace instructions, memory/identity and macro/coordination skills with trading macro/risk-only responsibilities.
- Removed only the daily STZ content research and six-hour content research Cron jobs. Archived obsolete content-only skills and scripts after backups; no macro/risk scripts were removed.
- Preserved the hourly Macro Gate job. Its contract tests pass, but live state is currently BLOCK due incomplete source coverage/calendar configuration. Sniper must fail closed for new entries while that remains true.
- Marco has no publishing, position-management, trading-execution, or STZ content authority.

### Vera — independent crypto researcher and scriptwriter

- Updated active role, schedule, handoff and skills to perform discovery → source verification → brief → script → quality check independently.
- Preserved the existing 09:20 daily job. Its prompt now requires STZ-only Notion scope verification and local draft/blocked status when the scope is missing.
- Vera does not use Google Flow, produce images/videos, or publish. Her four-cycle image/text job remains disabled; no new cadence was introduced.
- Native Notion auth failed and the available shared connection is cross-division; no Notion reads/writes were made. Four unwanted Flow/Drive skills remain model-visible despite tool denials.

### Sniper — macro gate integration

- Retained deterministic-first SMC scans and existing position monitoring, risk settings and execution code.
- The Macro Gate consumer rejects stale/incomplete state and permits only a complete fresh ALLOW. It rejects BLOCK/RESTRICT, unverified calendar, missing expiry and halting states.
- SMC analysis suite passed 22/22. No trade, live exchange call, or position change was made. New-entry function is not available while current Macro Gate state is BLOCK.

### Jarvis — organizational coordination

- Updated active organization/A2A docs to put Marco and Sniper under Trading & Investment, and Vera under independent STZ research/scriptwriting.
- Removed the stale Marco→Vera content handoff and added division-scoped Notion fail-closed rules. A2A workflow was not functionally tested end-to-end.

### Nova, Vortex and Moddy compatibility

- Nova remains an independent OFW scriptwriter with the six-scene × ten-second × 60-second format. Its 13:25 authoring schedule remains enabled with a local-draft-only guard until OFW Notion scope is verified.
- Vortex remains STZ producer, but its 09:40 video job is preserved and disabled: all seven configured Flow working directories point to Vera's workspace. A supported config patch was rejected because Gateway lock ownership could not be verified; no mutation was made. Notion scope is unverified.
- Moddy remains STZ publisher and keeps its approval boundary. Its 10:40 job is preserved and disabled while its authorization helper is not integrated into the real publisher path and Notion scope is ambiguous. Local helper tests pass but are not production proof.

## C. Actual automation scheduler

Job identifiers below are from the live Cron scheduler or protected pre-change snapshot. The two removed Marco rows use the pre-change snapshot. The current full content scheduler table, including other image/text entries and last delivery status, is in [Content Automation Readiness](CONTENT_AUTOMATION_READINESS.md).

| Agent | Automation | Job ID | Schedule (Asia/Manila) | Final state | Last scheduler state |
|---|---|---|---|---|---|
| Marco | marco-daily-video-content-research | `34369cd8-42fb-4c6f-ab30-47b26438be75` | 20 8 * * * (Asia/Manila) | REMOVED | removed by restructuring |
| Marco | marco-6h-content-research | `fdd48ecf-ea1f-4e22-bab3-bc5514044217` | 46 5,11,17,23 * * * (Asia/Manila) | REMOVED | removed by restructuring |
| Marco | marco-hourly-macro-gate | `9390be92-913f-43ee-8dcf-e339434dde63` | 50 * * * * (Asia/Manila) | ENABLED | ok |
| Vera | vera-daily-script-production | `4278320c-c293-48bd-a388-7001d889807e` | 20 9 * * * (Asia/Manila) | ENABLED | ok |
| Vera | vera-image-text-script | `94727289-6325-447e-8c84-3ab45b0c27e3` | 55 5,11,17,23 * * * (Asia/Manila) | DISABLED | not run/recorded |
| Vortex | stz-video-generation | `879dfb9c-16d8-42b5-a791-500945a821ba` | 40 9 * * * (Asia/Manila) | DISABLED | ok |
| Moddy | MODDY — SHORT-FORM VIDEO PUBLISHING | `4870814d-ed4f-44f8-a6e9-35817467e4c2` | 40 10 * * * (Asia/Manila) | DISABLED | ok |
| Nova | nova_ofw_video_script_daily | `69707af7-0003-4d16-ab48-8a9d6eaee23a` | 25 13 * * * (Asia/Manila) | ENABLED | ok |
| Dave | dave_ofw_video_production_daily | `5deda03a-02b4-4b00-8fe1-239ed9d6a734` | 40 13 * * * (Asia/Manila) | DISABLED | ok |
| June | june_ofw_video_publishing_daily | `756050e8-9937-4103-ad9a-47cf478debf5` | 25 15 * * * (Asia/Manila) | DISABLED | error |


Vortex 09:40 video generation, Moddy 10:40 publishing, Dave 13:40 production and June 15:25 publishing were subsequently disabled while retaining their schedule definitions. Their scheduler prompts now contain role-specific fail-closed gates. Vera and Nova authoring jobs stay enabled with local-draft-only guards. No schedule was created to replace the removed Marco jobs.

## D. Sniper integration and safety

Sniper receives the structured Macro Gate state from Marco and checks decision, freshness, explicit expiry, source/calendar verification, status and restrictions before evaluating new entries. Current state is BLOCK; the safe effect is no new entry. Existing position monitoring stays scheduled and was not changed. The SMC test suite passed 22/22. No live trades were executed.

## E. Files and backups

- Marco active role, memory, A2A and macro skills/scripts under `workspace-marco`; two content-only skills and associated scripts were moved to the dated retired-workflow archive after backup.
- Vera active role, schedule, memory, handoff and content-research/script skills under `workspace-vera`.
- Jarvis active org/A2A documents: `workspace\A2A_GOVERNANCE.md` and `workspace\A2A-COORDINATION.md`.
- Sniper Macro Gate parser/consumer checks and tests in the existing Sniper skill workspace.
- Moddy/Vortex/Nova/Dave/June readiness instructions and schedule prompts; four production jobs are paused, not deleted.
- Protected backups are under `C:\Users\dizon\.openclaw\backups\restructure-20261114\continued\`. No credentials or secret values are included here.

## F. Validation results

| Test | Result | Evidence/limit |
|---|---|---|
| Macro Gate contract | PASS | 8 cases and atomic write; live data availability is a separate blocker. |
| PowerShell syntax | PASS | Macro risk, runner, contract and test scripts parsed. |
| Sniper SMC analysis | PASS | 22/22 tests; no live trading. |
| OpenClaw config validation | PASS | `valid=true`, no warnings. |
| Static MCP doctor | PASS with auth warning | 15 definitions pass static checks; Notion OAuth is not authorized. |
| Cron restructure | PASS | Live scheduler confirms Marco content jobs absent, Macro Gate preserved, Vera independent, and four unsafe downstream production jobs disabled. |
| End-to-end media workflows | BLOCKED / NOT TESTED | No Notion writes, media generation, asset uploads or public posts were performed. |

## G. Remaining blockers

1. Configure and verify an owner-approved primary economic calendar and independent source coverage for Marco. Keep Macro Gate fail-closed until a fresh valid state is verified.
2. Provide separate, least-privilege STZ and OFW Notion access; verify identities and allowed databases before read/write tests.
3. Correct Vortex Flow server working directories using the supported Gateway-owner procedure; preserve profiles, account allocation and ports.
4. Integrate a real owner signature verifier and durable single-use nonce store into Moddy's actual publish call path.
5. Resolve Dave/June Drive and destination scope, YouTube quota/channel verification and any required OFW Instagram mapping.
6. Resolve Vera's extra model-visible Flow/Drive skills while maintaining existing tool denials.
7. Keep the Vortex, Moddy, Dave and June schedules disabled until their specific readiness gates pass; then owner may re-enable without changing their cadence.

**Final status: NOT PRODUCTION READY.** Role restructuring and safe scheduler edits are complete; required external authentication, Flow isolation and authorization work remains.
