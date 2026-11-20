---
name: composio-sdk-connection-setup
description: Set up Composio platform OAuth connections via @composio/core SDK (v0.27.0+) — legacy CLI deprecated. Verifies toolkits, creates auth configs, initiates OAuth, confirms connections for YouTube, Instagram, Facebook, Google Drive, Discord.
---

# Composio SDK Connection Setup

## Trigger
Need to establish OAuth connections for social media platforms (YouTube, Instagram, Facebook Pages, Google Drive, Discord, X/Twitter) using Composio after the legacy CLI is deprecated/broken.

## Produces
Verified connected accounts for each target platform via the new SDK, ready for publishing workflows.

## Prerequisites
- Node.js >= 22.22.3
- `COMPOSIO_API_KEY` environment variable set (full key, not masked)
- OAuth client credentials (client_id, client_secret) for each target platform from their developer consoles
- Redirect URI configured in each platform's OAuth app: `https://backend.composio.dev/api/v1/auth-apps/add`

## Steps

1. Install the new SDK:
   ```
   npm install @composio/core@latest
   ```
   Check: `@composio/core@0.27.0+` installed, `composio-core` (legacy) NOT used.

2. Verify SDK authentication:
   ```javascript
   import { Composio } from '@composio/core';
   const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });
   const accounts = await composio.connectedAccounts.list();
   ```
   Check: Returns `{ items: [], nextCursor: null, totalPages: 0 }` (empty list = authenticated, no connections yet).

3. Check toolkit availability for each platform:
   ```javascript
   const toolkit = await composio.toolkits.getToolkitBySlug('youtube');
   // Also check: instagram, facebook, googledrive, discord, twitter
   ```
   Check: Each returns toolkit metadata with `composioManagedAuthSchemes: ['OAUTH2']` (except twitter which returns `[]`).
   **Note:** Binance Square has NO toolkit in Composio.

4. Get auth config fields for each platform:
   ```javascript
   const fields = await composio.toolkits.getAuthConfigCreationFields('youtube');
   ```
   Check: Returns required fields `client_id`, `client_secret` plus optional `oauth_redirect_uri` and `scopes`.

5. Create auth config for each platform (requires operator to provide credentials):
   ```javascript
   const authConfig = await composio.authConfigs.create({
     toolkitSlug: 'youtube',
     authScheme: 'OAUTH2',
     fields: { client_id: '...', client_secret: '...' }
   });
   ```
   Check: Returns authConfigId for use in connection initiation.

6. Initiate OAuth connection for each platform:
   ```javascript
   const result = await composio.connectedAccounts.initiate({
     toolkitSlug: 'youtube',
     authConfigId: authConfigId
   });
   ```
   Check: Returns `{ redirectUrl, connectedAccountId }`. Share `redirectUrl` privately with operator.

7. Operator completes OAuth in browser:
   Open each `redirectUrl` in browser, authorize the app, wait for redirect to Composio success page.

8. Verify connections established:
   ```javascript
   const accounts = await composio.connectedAccounts.list();
   ```
   Check: `items` array contains connected accounts for all target platforms.

## Platform Notes

| Platform | Toolkit Slug | Tools | Auth | Notes |
|----------|--------------|-------|------|-------|
| YouTube | youtube | 59 | OAUTH2 | Google Cloud Console |
| Instagram | instagram | 33 | OAUTH2 | Meta Developer Console (Business) |
| Facebook Pages | facebook | 55 | OAUTH2 | Meta Developer Console (covers Pages) |
| Google Drive | googledrive | 92 | OAUTH2 | Google Cloud Console |
| Discord | discord | 23 | OAUTH2 | Discord Developer Portal |
| X/Twitter | twitter | 84 | NONE | No managed auth — may need custom API keys |
| Binance Square | — | — | — | **NOT AVAILABLE** in Composio |

## Standing Preferences
- Ask the trusted operator before creating auth configs (requires client credentials).
- Share authorization URLs only in a private operator context, never in chat.
- Verify each platform connection independently before proceeding to publishing workflows.
- Do not use legacy `composio` CLI — it is deprecated and broken (TypeError on error handling).

## References
- SDK package: @composio/core@0.27.0+
- Legacy CLI: composio-core@0.5.39 (deprecated, DO NOT USE)
- Composio base URL: https://backend.composio.dev
- Redirect URI for all platforms: https://backend.composio.dev/api/v1/auth-apps/add