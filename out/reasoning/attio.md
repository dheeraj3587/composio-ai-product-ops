# Attio — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
Evidence from official docs and developer platform pages confirms a public REST API (JSON/HTTPS) with clear guides for auth, rate limits, webhooks, pagination, filtering; full read/write on core CRM objects (people, companies, deals, lists, notes, tasks, etc.) plus SCIM/webhooks, supporting Broad breadth. Auth is self-serve via workspace API keys or OAuth 2.0; start-for-free and developer dashboard indicate no gate. Official MCP is prominently offered alongside REST and App SDK. Buildability Easy and next action Build Now follow directly (self-serve + REST + docs). Preseed was none so no confirmation/contradiction needed. Minor ambiguity on exact rate numbers and GraphQL claim (blog only; official text is REST-focused) keeps confidence at 0.9 rather than 1.0.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — API keys generated in Workspace Settings > Developers; OAuth 2.0 for apps; free signup
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs (whitelist-enforced)
- https://attio.com
- https://docs.attio.com/rest-api/overview
- https://attio.com/platform/developers
- https://blog.coffee.ai/attio-crm-public-api-docs
