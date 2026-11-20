# Production Readiness — 2026-11-14 (completion pass)

A response ping and successful scheduled run do not establish end-to-end production readiness. Statuses below use current schedule and integration evidence; detailed content-agent evidence is in [CONTENT_AUTOMATION_READINESS.md](CONTENT_AUTOMATION_READINESS.md).

| Agent | Workspace | Model | Skills | Integrations | Automation | Functional evidence | Status |
|---|---|---|---|---|---|---|---|
| Jarvis | Repaired | Preserved | Syntax pass | A2A not end-to-end tested | Org docs corrected | Response ping/scripts | Ready With Warnings |
| Marco | Repaired | Preserved | Helpers parse | Macro sources incomplete | Content jobs removed; Macro Gate preserved | Last direct gate evaluation BLOCK | Needs Attention |
| Coddy | Repaired | Preserved | 0 invalid; host dependencies unmet | Read-only GitHub pass | Weekly jobs preserved | Response ping | Ready With Warnings |
| Sniper | Repaired | Preserved | Core inspected | Live APIs untested | Position monitor preserved | SMC tests 22/22; no trade test | Needs Attention |
| Vera | Repaired | Preserved | Four extra Flow/Drive skills visible | STZ Notion scope/auth blocked | 09:20 authoring enabled with local-draft guard | Independent research instructions; no end-to-end handoff | Needs Attention |
| Vortex | Repaired | Preserved | Flow safety gate updated | Seven server cwd values point to Vera workspace; live auth unverified | 09:40 job disabled; preserved | Static MCP only | Blocked |
| Moddy | Repaired | Preserved | Publish gate docs corrected | Shared Notion scope; actual auth path unwired | 10:40 job disabled; preserved | Authorization simulations 13/13, mocked adapters | Blocked |
| Nova | Repaired | Preserved | Six-scene 60-second contract | OFW Notion scope blocked | 13:25 authoring enabled with local-draft guard | Format instructions inspected; generated script not tested | Needs Attention |
| Dave | Repaired | Preserved | Flow isolation docs updated | Notion/Drive unverified; live Flow auth unverified | 13:40 job disabled; preserved | Static MCP; optional check-kit fails on missing CLAUDE.md | Blocked |
| June | Repaired | Preserved | Destination/scope gates corrected | Facebook scope crosses divisions; YouTube quotaExceeded; Drive/Notion blocked | 15:25 job disabled; preserved after two failed runs | Read-only checks only | Blocked |

**Current count:** 0 Production Ready, 2 Ready With Warnings, 4 Needs Attention, 4 Blocked.

Four potentially unsafe production jobs were temporarily disabled with their original cadence preserved: Vortex generation, Moddy publishing, Dave production and June publishing. Vera and Nova authoring jobs remain enabled only with local-draft/no-write guards when division-scoped Notion access is not verified. No trades, public posts, customer messages, media generation or Gateway restart occurred during the completion pass.