# Security Assessment — 2026-11-14

Secrets, tokens, account IDs, emails, page/database IDs and credential-bearing logs are omitted.

| ID | Severity | Confirmed finding | Status |
|---|---|---|---|
| SEC-01 | High | Sniper .env with five credentials was tracked; local Git history retains secrets. | Index cleaned; owner rotation/revocation and history decision required. |
| SEC-02 | High | Moddy scheduler accepted a status-only `AUTHORIZED_PUBLISH` gate; live prompt did not require signature, exact content/destination binding, expiry or nonce replay checks. | Local helper hardened and passes 13 mocked cases; still not wired to live publish path. Moddy job preserved and disabled until verified. |
| SEC-03 | High | Shared Notion connection is labeled across divisions, reads OFW metadata and exposes generic write tools. | No writes; split/re-scope and reauthenticate. |
| SEC-04 | High | June Facebook auth sees both OFW and STZ pages. | June job preserved and disabled; owner-scoped OFW access required. |
| SEC-05 | Medium | Vera checker reports four Drive/Flow skills visible beyond allowlist. | Tool denials compensate; runtime visibility issue open. |
| SEC-06 | Medium | Secret-bearing OpenClaw config ACL was broad. | Restricted to owner/SYSTEM/Admin and rechecked. |
| SEC-07 | Medium | Coddy repository has 6,832 untracked files, no remote, weak ignore rules. | No stage/commit; owner scope needed. |
| SEC-08 | High | Vortex Flow MCP working directories point at Vera workspace; supported patch blocked because Gateway lock ownership could not be verified. | No mutation; video job preserved and disabled; resolve via supported service owner. |

No secret values entered reports or commits. No live trades, publishing, customer messages, history rewrite, or media generation occurred. Static MCP validation is not live authentication proof. The completion pass disabled the Vortex, Moddy, Dave and June production jobs without deleting them, and added scheduler-level fail-closed instructions.
