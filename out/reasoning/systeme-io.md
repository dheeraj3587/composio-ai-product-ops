# systeme.io — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
Evidence confirms a public REST API (base https://api.systeme.io/api) with self-serve API-key creation in the dashboard and documented endpoints for contacts (CRUD-ish + filter), tags, subscriptions (list/unsub), newsletters, and indirect automation triggers—matching Moderate breadth. Auth is X-API-Key (not OAuth); docs exist via help center + reference. Rate limits and key limits (3) are stated. Rollout guide is secondary and has minor auth/base-URL inconsistencies so was de-weighted. Preseed was 'none' (no contradiction). Buildability Easy + Self-Serve => Build Now; no blocker. Confidence high but not 1.0 because full OpenAPI/spec details are only summarized, not fully fetched.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — Users generate up to 3 public API keys in dashboard profile settings (name + optional expiry; shown once).
- recommended_next_action: **Build Now**
- confidence: **0.88**

## Evidence URLs (whitelist-enforced)
- https://systeme.io
- https://help.systeme.io/article/2329-how-to-use-systeme-io-public-api
- https://grokipedia.com/page/Systemeio_API
