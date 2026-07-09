# Twenty — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
Official docs clearly describe dual Core + Metadata APIs exposed as both REST and GraphQL (schema-per-tenant, so custom objects get full CRUD endpoints), Bearer API-key auth created self-serve in workspace Settings, OAuth for third-party apps, interactive playground, and explicit rate limits. Breadth is Broad (records across People/Companies/Opportunities/custom objects plus programmatic schema management). No MCP evidence. Preseed was none; evidence fully supports Easy buildability and Build Now. api_type set to REST as the primary integration surface though GraphQL is equally first-class. Confidence high due to detailed official docs; slight residual uncertainty only on free-tier cloud quotas not stated.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — Create a Bearer API key in Settings → API & Webhooks; keys can be role-scoped. OAuth available for external apps.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs (whitelist-enforced)
- https://docs.twenty.com/developers/extend/api
- https://docs.twenty.com/developers/introduction
