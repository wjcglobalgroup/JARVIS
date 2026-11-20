# Content Automation Production Readiness — 2026-11-14

## Executive summary

**Overall: NOT PRODUCTION READY.** None of the six content workflows can be certified production-ready from current runtime evidence. Two authoring jobs remain enabled with fail-closed local-draft instructions; four production/media/publication jobs are preserved but temporarily disabled until blocking security and integration defects are repaired. No agent, workspace, model assignment, account allocation, or schedule definition was deleted. No public content was published, no customer message was sent, and no media-generation credits or live trades were used during this pass.

## Current readiness matrix

| Agent | Role path | Key verified state | Schedule | Status |
|---|---|---|---|---|
| Vera | Independent STZ crypto research and scriptwriting | Daily prompt forbids Marco dependency and requires owner-approved STZ-only Notion scope; four unwanted Flow/Drive skills remain model-visible despite tool-deny rules. | 09:20 enabled; local draft only while Notion scope is unverified. | Needs Attention |
| Vortex | STZ video/image production | Static MCP definitions exist, but all seven Flow working directories point to Vera's workspace. Supported config patch was refused because Gateway lock ownership could not be verified. Notion scope is unverified. | 09:40 video disabled; six-hour image job remains disabled. | Blocked |
| Moddy | STZ publishing/community operations | Local authorization helper now fails closed; 13 simulations pass. The live job checked only the `AUTHORIZED_PUBLISH` status and did not bind a signature to content/destination or consume a nonce. Shared Notion scope remains unsafe. | 10:40 video disabled; legacy text/image job remains disabled. | Blocked |
| Nova | OFW researcher/scriptwriter | Six-scene × ten-second × 60-second contract present in instructions and job prompt. No generated-script conformance or Notion write was tested. OFW-only Notion scope is unverified. | 13:25 enabled; local draft only. | Needs Attention |
| Dave | OFW video/image production | Seven Dave-specific static Flow server definitions pass config doctor; live login/generation are untested. Notion authentication failed and Drive list/search is unavailable in the current tool catalog. | 13:40 video disabled; image job remains disabled. | Blocked |
| June | OFW publishing | Two latest Cron runs failed (completion failed; delivery unknown/not delivered); scheduler diagnostics did not identify a specific root cause. Separate read-only checks found cross-division Facebook visibility, YouTube `quotaExceeded`, no verified OFW Instagram mapping, and unavailable Drive list/search. | 15:25 video disabled; image job remains disabled. | Blocked |

## Scheduler inventory

The following entries were read from the live scheduler and protected pre-change backup. Job IDs are scheduler identifiers, not credentials. Disabled jobs remain present with their original cadence and now include fail-closed readiness instructions.

| Agent | Automation | Job ID | Existing schedule (Asia/Manila) | Final state | Last scheduler state |
|---|---|---|---|---|---|
| Marco | marco-daily-video-content-research | `34369cd8-42fb-4c6f-ab30-47b26438be75` | 20 8 * * * (Asia/Manila) | REMOVED | removed by restructuring |
| Marco | marco-6h-content-research | `fdd48ecf-ea1f-4e22-bab3-bc5514044217` | 46 5,11,17,23 * * * (Asia/Manila) | REMOVED | removed by restructuring |
| Marco | marco-hourly-macro-gate | `9390be92-913f-43ee-8dcf-e339434dde63` | 50 * * * * (Asia/Manila) | ENABLED | ok; delivery delivered |
| Vera | vera-daily-script-production | `4278320c-c293-48bd-a388-7001d889807e` | 20 9 * * * (Asia/Manila) | ENABLED | ok; delivery not-requested |
| Vera | vera-image-text-script | `94727289-6325-447e-8c84-3ab45b0c27e3` | 55 5,11,17,23 * * * (Asia/Manila) | DISABLED | not run/recorded |
| Vortex | stz-video-generation | `879dfb9c-16d8-42b5-a791-500945a821ba` | 40 9 * * * (Asia/Manila) | DISABLED | ok; delivery delivered |
| Vortex | stz-image-generation | `508220ff-346f-4aae-9319-e25943381622` | 10 */6 * * * (Asia/Manila) | DISABLED | not run/recorded |
| Moddy | MODDY — SHORT-FORM VIDEO PUBLISHING | `4870814d-ed4f-44f8-a6e9-35817467e4c2` | 40 10 * * * (Asia/Manila) | DISABLED | ok; delivery delivered |
| Moddy | MODDY — IMAGE & TEXT PUBLISHING | `07999c30-323e-4e36-b6b0-4f66186ba54a` | 35 */6 * * * (Asia/Manila) | DISABLED | not run/recorded |
| Nova | nova_ofw_video_script_daily | `69707af7-0003-4d16-ab48-8a9d6eaee23a` | 25 13 * * * (Asia/Manila) | ENABLED | ok; delivery delivered |
| Nova | nova_ofw_image_text_daily | `481bb68b-f749-46cf-b1a9-d592b1fda80a` | 50 2,8,14,20 * * * (Asia/Manila) | DISABLED | not run/recorded |
| Dave | dave_ofw_video_production_daily | `5deda03a-02b4-4b00-8fe1-239ed9d6a734` | 40 13 * * * (Asia/Manila) | DISABLED | ok; delivery delivered |
| Dave | dave_ofw_image_production_daily | `a8a5d9f3-6fa8-48e1-ad52-c090485d3017` | 10 3,9,15,21 * * * (Asia/Manila) | DISABLED | not run/recorded |
| June | june_ofw_video_publishing_daily | `756050e8-9937-4103-ad9a-47cf478debf5` | 25 15 * * * (Asia/Manila) | DISABLED | error; delivery unknown |
| June | june_ofw_image_publishing_daily | `73dd4b16-9ffc-4483-8858-78b9a8013976` | 0 4,10,16,22 * * * (Asia/Manila) | DISABLED | not run/recorded |

**Changed in this pass:** Vortex 09:40 video generation, Moddy 10:40 video publishing, Dave 13:40 production and June 15:25 publishing were preserved and disabled. Their schedule expressions remain unchanged. Vera 09:20 and Nova 13:25 authoring jobs remain enabled with local-draft-only guards when Notion scope cannot be verified. No image/text automation was enabled. The two Marco content-research jobs were removed in the preceding restructuring; Marco's Macro Gate schedule remains.

## Repairs completed

- Corrected active Jarvis A2A governance and coordination docs: Marco owns Trading & Investment macro/risk intelligence only; Vera independently researches and scripts STZ content.
- Updated Moddy operating instructions and skills to remove Marco as an upstream content dependency, distinguish disabled legacy image/text cadence from live schedules, and require verified owner authorization rather than a status string.
- Hardened `verifyPublishingAuthorization` to require exact content/destination bindings, timezone-explicit future expiry, a trusted signature-verification callback and a durable single-use nonce-consumption callback. It fails closed if an adapter is missing or fails.
- Added role-specific readiness gates to the six content-job prompts. Disabled four jobs that could invoke unverified Flow accounts or publish with ambiguous authorization/destination scope.
- Corrected June workspace instructions that previously claimed current Drive/Facebook scopes were exclusively verified.

## Verification evidence

| Check | Result | Limit |
|---|---|---|
| `openclaw config validate --json` | PASS; valid configuration, no warnings. | Does not prove external authentication. |
| `openclaw mcp doctor --json` | PASS for 15 static server definitions; Notion reports missing OAuth authorization. | Static paths/configuration only; no live generation. |
| Moddy JS syntax and authorization simulations | PASS; 13/13 local cases. | Signature and nonce adapters are test mocks; production call path remains unwired. |
| SMC analysis tests | PASS; 22/22. | No trades or live market execution. |
| Macro Gate contract tests | PASS; 8 cases and atomic write. | Last direct runtime evaluation produced BLOCK due insufficient independent source hosts and no configured primary economic-calendar source; no new live fetch was run in this completion pass. |
| Cron inventory/update | PASS; scheduler API returned updated job states and preserved schedules. | Full Gateway health command was not re-run; no Gateway restart was performed. |
| End-to-end content handoffs | BLOCKED / NOT TESTED. | No Notion write, Flow generation, upload or public post was performed. |

## Outstanding blockers and exact next actions

1. **Division-scoped Notion access:** Provide separate owner-approved STZ and OFW connections. Verify runtime identity, allowed database scope and minimum permissions before any read; separately authorize and verify needed writes.
2. **Vortex Flow isolation:** Resolve Gateway lock ownership through the supported service owner; change only the seven Vortex working-directory fields to Vortex's workspace, preserve account allocations/ports, run static doctor, then perform owner-approved read-only authentication checks. Keep video disabled until complete.
3. **Moddy publish authorization:** Define the owner signing key/verification policy and durable atomic nonce store; wire the hardened helper into the actual platform-call path; prove content/destination/expiry/replay failures in dry-run. Keep publishing disabled until this passes.
4. **Dave production access:** Provide and verify owner-scoped OFW Notion and Drive tools plus Dave-only Flow authentication. The optional `scripts/check-kit.mjs` also fails because its distribution check expects a missing `CLAUDE.md`; decide whether this workspace must ship synchronized Claude instructions before changing the checker.
5. **June publishing destinations:** Verify OFW-only Facebook permissions, recover YouTube quota and verify channel ownership, provide scoped Drive/Notion access, and confirm whether an OFW Instagram destination exists. Investigate the failed Cron runs; re-enable only after the failure root cause and destinations are verified.
6. **Vera skill isolation:** Resolve why four Flow/Drive skills remain model-visible despite configured denies; verify runtime tool visibility before granting any downstream access.
7. **Nova/Vera handoff:** After scoped Notion authentication is available, test authoring locally, then perform authorized read/write verification against the correct division database and confirm downstream handoffs.

**Final status:** The six-agent content automation group is **NOT PRODUCTION READY**. Vera and Nova can prepare local drafts under current scheduler guards; Vortex, Moddy, Dave and June production jobs remain paused. Re-enable a paused job only after its named blocker is fixed and the corresponding functional test passes.

## Backups and change record

Scheduler pre-change state and affected workspace files are preserved under `C:\Users\dizon\.openclaw\backups\restructure-20261114\continued\content-readiness-20261114\`. No secret values are included in this report.
## Reusable audit skill update

The generic Codex audit playbook now allows temporary schedule containment only under explicit owner authorization, with a full backup, preserved schedule/payload and exact re-enable criteria. Frontmatter and local links validate; no owner roster is included. Exactly one generic reference file was pushed to [the skill repository](https://github.com/stzsniper/openclaw-audit-repair-engineer); no OpenClaw settings or agent configurations were included.
