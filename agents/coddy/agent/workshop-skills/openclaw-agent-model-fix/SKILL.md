---
name: openclaw-agent-model-fix
description: Fix OpenClaw agent model configuration when model not found (HTTP 404) errors occur due to incorrect model naming (e.g., missing :free suffix).
---

# OpenClaw Agent Model Fix

## Trigger
A2A `sessions_send` to an agent fails with HTTP 404 "model not found" for a model like `openrouter/nvidia/nemotron-3-super-120b-a12b`. The agent config in `openclaw.json` has a model missing the required suffix (typically `:free` for free-tier models).

## Steps

1. Locate the agent config in `C:\Users\dizon\.openclaw\openclaw.json`:
   ```
   node -e "const fs=require('fs');const c=fs.readFileSync('C:\\\\Users\\\\dizon\\\\.openclaw\\\\openclaw.json','utf8');console.log(c.substring(c.indexOf('\"main\": {'),c.indexOf('\"main\": {')+500));"
   ```
   Check: Output shows the agent's `model.primary` value.

2. Fix the model name by adding the missing `:free` suffix:
   ```
   node -e "const fs=require('fs');const p='C:\\\\Users\\\\dizon\\\\.openclaw\\\\openclaw.json';const c=fs.readFileSync(p,'utf8');const n=c.replace('\"primary\": \"openrouter/nvidia/nemotron-3-super-120b-a12b\"','\"primary\": \"openrouter/nvidia/nemotron-3-super-120b-a12b:free\"');fs.writeFileSync(p,n);console.log('Fixed');"
   ```
   Check: Console prints "Fixed".

3. Validate JSON syntax:
   ```
   node -e "JSON.parse(require('fs').readFileSync('C:\\\\Users\\\\dizon\\\\.openclaw\\\\openclaw.json','utf8'));console.log('JSON valid')"
   ```
   Check: Prints "JSON valid".

4. Restart the affected agent session (Control UI or Gateway restart) for the config change to take effect.
   Check: Agent session shows new model in status.

## Standing preferences
- Always validate JSON after editing `openclaw.json`.
- Use `:free` suffix for OpenRouter free-tier models.
- Restart the agent session after config changes; edits alone do not reload models.