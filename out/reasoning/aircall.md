# Aircall — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
Evidence from official developer.aircall.io/api-references and developer.aircall.io shows a public REST API with extensive resources (Users V1/V2, Teams, Calls, Numbers, Contacts, Tags, Webhooks, Company, Dialer Campaigns, Conversation Intelligence, Messages, Integrations, etc.) supporting full CRUD and actions—clearly Broad. Auth is self-serve Basic Auth (API ID+Token created in customer dashboard) plus OAuth for partners; aeroleads blog confirms token generation and first-call flow with no review gate. Docs are clear with pagination, errors, versioning, webhooks. Rate limit explicitly 100 req/min. No MCP mentioned (COMPOSIO_TOOLKIT=No). Buildability Easy and next action Build Now per rubrics (self-serve key + REST + clear docs). Preseed was none so no confirmation/contradiction. Confidence high as primary docs + secondary walkthrough align; minor ambiguity only on exact partner OAuth entry vs customer tokens.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — Aircall customers generate API tokens in dashboard Integrations > API; OAuth available for Technology Partners/marketplace apps
- recommended_next_action: **Build Now**
- confidence: **0.92**

## Evidence URLs (whitelist-enforced)
- https://developer.aircall.io/api-references/
- https://aeroleads.com/blog/getting-started-with-aircall-api-developer-documentation/
- https://developer.aircall.io/
- https://aircall.io
