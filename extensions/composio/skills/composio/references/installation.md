# Composio CLI installation and authentication

Read this reference only when the Composio CLI is missing, signed out, or
running in the wrong execution boundary.

## Check the actual execution environment

Run these read-only checks where OpenClaw will execute the eventual command:

```bash
command -v composio
composio whoami
```

Do not assume that a binary or login on the Gateway host is available inside a
container, sandbox, or remote node. Do not repair that mismatch by copying
host credentials or disabling isolation.

## Install the CLI

If `command -v composio` already succeeds in the execution environment, do not
reinstall or upgrade it. Continue to the sign-in check below.

Before running an installer, tell the trusted operator that the official
installer downloads and verifies a Composio release under `~/.composio`,
creates a `composio` entry point under `~/.local/bin` by default, and may add a
managed Composio block to supported shell startup files.

After the operator authorizes those host changes, run:

```bash
curl -fsSL https://composio.dev/install | sh
```

If execution is not authorized or the environment cannot install software,
show the command for manual use and stop.

The installer supports macOS and Linux. On Windows, use it inside WSL. Follow
the platform and architecture support reported by the official installer
rather than attempting an unlisted binary.

Verify the result. The version must be `0.4.0` or newer:

```bash
command -v composio
composio --version
```

If an existing installation is older than `0.4.0`, do not run the installer
again. Ask the trusted operator to authorize `composio upgrade`, then verify
the version again. When `~/.composio/update-check.json` contains a stable
`latestVersion` newer than the installed stable version, offer the same upgrade
without contacting the network or applying it automatically.

Shell startup changes affect future terminals. In the current task, use the
absolute executable path printed by the installer or ask the operator to begin
a fresh session. Do not make additional shell changes without authorization.

## Sign in

Treat empty `composio whoami` output, explicit unauthenticated output, or a
nonzero exit as signed out.

Ask the trusted operator before initiating login:

```bash
composio login --no-skill-install
```

Keep `--no-skill-install` on every login path. The plugin already supplies the
reviewed `composio` skill; the CLI otherwise adds a separate `composio-cli`
skill under `~/.agents/skills`.

For a headless private operator session:

```bash
composio login --no-browser --no-wait --no-skill-install
composio login --poll --no-skill-install
```

Give an authorization URL only to the trusted operator in a private context.
Never ask anyone to paste an API key, session key, OAuth code, or credential
file into chat. After authorization, run `composio whoami` again and require a
non-empty authenticated identity.

Do not run `composio upgrade` on your own initiative, log out another
session, replace an organization, or install additional agent integrations as
part of ordinary setup.

`composio --install-skill composio-cli openclaw` is unnecessary for this
plugin. If it already exists, OpenClaw can load it separately because this
plugin's reviewed skill uses the `composio` identity.
