# Outstanding Issues and Required Actions

| Priority | Issue | Required action |
|---|---|---|
| High | Sniper secrets in local history | Rotate/revoke credentials; owner decide on history rewrite after reviewing consumers. |
| High | Moddy helper is hardened but not wired into the live publisher; Cron previously trusted status-only authorization | Define owner signing/verification policy and durable nonce store, wire to real call path, prove binding/expiry/replay tests; keep the preserved job disabled. |
| High | Shared Notion cross-division access; native MCP auth failed | Split STZ/OFW connections, repair auth, verify read-only scope before authorized write validation. |
| High | June's two latest jobs failed; diagnostics do not identify the root cause; YouTube quota prevents channel verification | Recover quota/provider, investigate Cron failure without publishing, verify OFW channel read-only; keep the preserved job disabled. |
| High | June Facebook sees both divisions; OFW Instagram absent | Restrict account scope and provision/authorize OFW Instagram if needed. |
| Medium | Drive list/search unavailable | Grant least-privilege approved folder listing/upload and verify. |
| Medium | Vera four extra skills visible | Resolve skill discovery and verify tool denial at runtime. |
| Medium | Coddy repo 6,832 untracked, no remote | Owner define scope/remote and review ignore policy before staging. |
| Medium | Provider 429 errors | Review quota/backoff without changing assigned models or routing. |
| High | Vortex Flow cwd mismatch; supported patch blocked by Gateway lock ownership check | Use the supported service-owner procedure, repair only the Vortex cwd values and verify isolation; keep production schedule disabled. |
| Low | Dave check-kit expects missing CLAUDE.md | Update helper for actual workspace convention; rerun. |
| Medium | Marco/Vera restructuring and downstream readiness | Role/schedule changes are implemented; verify a primary economic calendar/source for Macro Gate, owner-scoped Notion, Vortex Flow isolation and downstream handoffs before re-enabling production jobs. |

Four production schedules (Vortex, Moddy, Dave and June) are temporarily disabled, not deleted. Their job IDs and original cadences remain in `CONTENT_AUTOMATION_READINESS.md` and the protected backup. No schedule should be re-enabled until its listed gate is verified.
