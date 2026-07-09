# Intercom — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
Evidence confirms a public REST API with clear self-serve auth: Access Tokens for private/workspace apps (issued on app creation in Developer Hub) and OAuth for public apps. Docs and third-party guide describe multiple domains (contacts, conversations, tickets, help center, messenger/inbox, reporting, webhooks, Fin Agent API), so api_breadth is Broad. Buildability is Easy (self-serve key + REST + documented auth/patterns); no review gate for private tokens. Developer docs nav lists Model Context Protocol (MCP) under Using the APIs, treated as Official (page chrome also offers Cursor/VS Code MCP install for docs). Rate limits exist (429 guidance) but numeric limits are not in the fetched text. Preseed was none—no contradiction. Confidence high on auth/REST/self-serve; slightly reduced because MCP is only evidenced via nav labeling and rate-limit numbers are absent.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — Private apps: create an app in Developer Hub and get an Access Token immediately. Public multi-workspace apps use OAuth.
- recommended_next_action: **Build Now**
- confidence: **0.88**

## Evidence URLs (whitelist-enforced)
- https://developers.intercom.com/docs/build-an-integration/learn-more/authentication
- https://developers.intercom.com/docs/references/rest-api/api.intercom.io
- https://agentsapis.com/intercom-api/
