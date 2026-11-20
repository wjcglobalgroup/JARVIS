# Composio for OpenClaw

[![CI](https://github.com/ComposioHQ/composio-openclaw-plugin/actions/workflows/ci.yml/badge.svg)](https://github.com/ComposioHQ/composio-openclaw-plugin/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

Connect OpenClaw to [1,000+ apps](https://composio.dev/toolkits) through the
[Composio CLI](https://docs.composio.dev/docs/cli). Ask for the outcome;
OpenClaw chooses the workflow, while [Composio](https://composio.dev) handles
tool discovery, live schemas, OAuth connections, and execution.

## What you can do

- Read email, calendars, tickets, source control, CRM records, and cloud files.
- Create approved issues, messages, events, tasks, and other app records.
- Connect a missing account without leaving the active task.
- Coordinate multi-app workflows with parallel calls or reviewed control flow.
- Reach an authenticated API endpoint when no dedicated Composio tool exists.

For example:

```text
List my open GitHub pull requests and the Linear issues linked to them.
Draft a summary of today's meetings, then ask before sending it to Slack.
Connect my Notion account and resume the database lookup after I authorize it.
```

## Install

Install and enable the plugin from ClawHub:

```bash
openclaw plugins install clawhub:@composio/composio
openclaw plugins enable composio
openclaw config set plugins.entries.composio.hooks.allowConversationAccess true --strict-json
openclaw gateway restart
```

OpenClaw requires the explicit conversation-access grant for third-party prompt
hooks. This plugin does not inspect or transmit the prompt: its hook adds the
same fixed routing and safety context on every eligible turn, after
OpenClaw resolves tool policy and only when `exec` is available.

Inspect the installed plugin and bundled skill:

```bash
openclaw plugins inspect composio --runtime --json
openclaw skills info composio --json
```

The runtime inspection should report one typed `before_prompt_build` hook. The
`composio` skill should be eligible, model-visible, and user-invocable.

### Install the Composio CLI

The OpenClaw plugin does not install or sign in to the separate Composio CLI.
When the CLI is missing, old, or signed out, OpenClaw asks the trusted operator
before changing the execution environment.

```bash
curl -fsSL https://composio.dev/install | sh
composio login --no-skill-install
composio whoami
```

The plugin requires Composio CLI 0.4.0 or newer and OpenClaw 2026.9.1 or newer.
`--no-skill-install` avoids installing a duplicate CLI-managed skill because
this plugin already bundles the OpenClaw workflow. An existing `composio-cli`
skill can still coexist with the plugin's `composio` skill.

## How it works

```text
external-app request
        |
        v
OpenClaw policy -> Composio hook + bundled skill
        |
        v
local composio executable in the resolved exec environment
        |
        v
Composio-managed app connection and tool
```

The package is a native OpenClaw code plugin, not a model CLI backend or MCP
server. CLI backends provide text inference and are selected as model
references. Composio instead gives the active model authenticated app actions,
so the integration uses:

- One typed `before_prompt_build` hook with `requiresToolAuthority`.
- Fixed prompt context that makes Composio the default external-app
  route and requires runtime checks in the same environment as agent commands.
- A bundled `composio` skill with discovery, authentication, execution,
  recovery, and safety guidance.

Before its first Composio operation, the agent checks `command -v composio`,
`composio --version`, and `composio whoami` where `exec` actually runs. It does
not infer CLI state from the Gateway daemon's environment. If `exec` is denied
by OpenClaw policy, the hook injects nothing.

## Use

Natural-language external-app requests route through Composio by default after
the plugin is installed. You can also invoke the skill explicitly:

```text
/composio List my open GitHub pull requests.
/composio Send this approved update to the release channel.
```

The skill follows a narrow workflow:

1. Run a known tool slug with `composio execute ... -d`.
2. Inspect the live schema or dry-run when inputs are unclear.
3. List tools for a known toolkit; otherwise run a bounded search.
4. Link a missing toolkit and resume after private operator authorization.
5. Run independent calls in parallel, or use `composio run` for reviewed logic.
6. Use `composio proxy` only when no dedicated tool covers the API action.

Another integration is used only when the user asks for it or Composio cannot
provide the required capability. Native OpenClaw tools remain the route for
local files, shell work, browser interaction, and public web search.

## Trust boundary

The CLI uses accounts connected in its execution environment. This integration
is intended for a trusted local operator or a deployment whose sender, shell,
and plugin policies explicitly authorize those accounts.

Installing the plugin does not authorize arbitrary channel participants,
scheduled jobs, subagents, or sandboxes to inherit host credentials. Share
authorization URLs only with the trusted operator in a private context. Never
replay an uncertain write through another execution surface.

OpenClaw controls plugin enablement, prompt injection, tool availability,
sandboxing, and approvals. Composio accounts and some connected services may
require paid plans.

## Updates

Preview and apply plugin updates through OpenClaw's tracked ClawHub install:

```bash
openclaw plugins update composio --dry-run
openclaw plugins update composio
```

The bundled skill checks the Composio CLI's stable update cache when available
and tells the trusted operator about a newer version. It never upgrades the CLI
without authorization.

## Development

Install dependencies and run all static and unit contracts:

```bash
npm ci --ignore-scripts
npm run check
npm test
python3 -m unittest discover -s tests -v
```

Build and verify a real packed-plugin installation with OpenClaw on `PATH`:

```bash
npm run build
python3 scripts/smoke_openclaw.py
```

The smoke test uses an isolated home, a real OpenClaw Gateway, and a
deterministic local model endpoint. It installs the exact `npm pack` artifact,
inspects the loaded runtime and skill, and executes real Gateway-backed agent
turns to prove that the hook context is present when `exec` is allowed and
absent when it is denied.

When the Composio CLI is installed, also verify coexistence with its separate
OpenClaw skill target:

```bash
python3 scripts/smoke_openclaw.py --verify-cli-coexistence
```

That mode verifies both `composio` and `composio-cli` remain eligible,
model-visible, and user-invocable.

### First-release acceptance

Public CI intentionally has neither operator credentials nor publisher access.
Before the first ClawHub release, run a credentialed canary in a trusted,
disposable OpenClaw workspace:

1. Install the packed plugin and confirm the runtime and skill checks above.
2. Run a real, read-only request such as listing open GitHub pull requests.
3. Link an unconnected test toolkit and resume the original read after private
   authorization.
4. In a disposable repository, create one issue with a unique marker and
   verify exactly one issue exists after any uncertain response.
5. After publishing, repeat the read-only canary from a fresh
   `clawhub:@composio/composio` installation.

## Release

`package.json` is the release-version source; the manifest and skill metadata
must match it. Pull requests fail when packaged files change without a
monotonically increasing version. They run the pinned official ClawHub CLI's
runtime validator against the real pinned OpenClaw SDK and a metadata-complete
`code-plugin` publish dry-run.

A version bump merged to `main` publishes with the same pinned ClawHub CLI,
waits for definitive publication, and creates a matching GitHub release. A
manual dispatch from `main` is available for release recovery with an explicit
changelog. The initial release can use `CLAWHUB_TOKEN`; manual dispatches can
use ClawHub OIDC trusted publishing once configured. Every third-party action
is commit-pinned to comply with the repository's Actions policy.

## License

MIT. See [LICENSE](./LICENSE).
