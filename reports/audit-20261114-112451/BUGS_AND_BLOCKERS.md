# Bugs and Blockers — 2026-11-14

| ID | Component | Severity | Root cause/evidence | Status |
|---|---|---|---|---|
| BUG-01 | Marco→Vera | Medium | Old handoff helper wrote locally and created a content dependency. | Resolved operationally: Marco content jobs removed; Vera is independent; no replacement dependency. |
| BUG-02 | Sniper | High | .env entered local Git history. | Index fixed; credentials/history remain. |
| BUG-03 | Moddy | High | Live job relied on `AUTHORIZED_PUBLISH` status only; helper was not called by publisher. | Helper now fails closed; 13 mocked tests pass. Production integration is still missing; job disabled. |
| BUG-04 | Vera | Medium | Four disallowed Drive/Flow skills remain model-visible. | Tool-deny compensation; unresolved. |
| BUG-05 | Notion | High | Native auth failed; shared Composio scope crosses divisions and has write tools. | No writes; scoped accounts required. |
| BUG-06 | June | High | Two latest scheduled runs failed (completion failed; one delivery not delivered, latest unknown); scheduler diagnostic fields did not identify a root cause. Separate YouTube verification returned quotaExceeded. | Job disabled; no rerun/post. Investigate run failure after scoped access/quota recovery. |
| BUG-07 | June | High | Facebook auth sees STZ and OFW; no active OFW Instagram. | No publish; least-privilege account mapping required. |
| BUG-08 | Drive | Medium | Current tools lack list/search; asset folder scope not verified. | Handoffs unverified. |
| BUG-09 | Vortex | High | All seven Flow MCP working directories point to Vera's workspace; supported patch rejected because Gateway lock owner could not be verified. | No config mutation; video job disabled pending supported repair. |
| BUG-10 | Dave | Low | check-kit expects absent CLAUDE.md. | Helper fails; not in package scripts. |
| BUG-11 | Coddy | Medium | 6,832 untracked/no remote/weak ignore. | No stage/commit. |
| BUG-12 | Provider | Medium | Repeated HTTP 429 in prior logs; some heartbeat/ops failures. | No model routing changes. |

## Selected schedules (Asia/Manila)
Marco daily and six-hour content jobs are removed; hourly Macro Gate is preserved. Vera script 09:20 and Nova script 13:25 remain enabled with local-draft-only guards. Vortex video 09:40, Moddy video 10:40, Dave production 13:40 and June publishing 15:25 are preserved but disabled pending their blockers. June's two latest runs failed; scheduler history did not establish the root cause. Scheduler states are not end-to-end workflow tests. See `CONTENT_AUTOMATION_READINESS.md` for job IDs, exact cadence, delivery states and tests.
