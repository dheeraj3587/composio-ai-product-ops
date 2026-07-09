# Shopify — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
Official Shopify.dev docs show extensive public APIs: GraphQL Admin API (primary), legacy REST Admin, Storefront API, Partner API, webhooks, Functions, and more—clear Broad breadth. Auth is documented as session tokens/token exchange for admin apps plus public/private Storefront tokens, with Shopify CLI scaffolding auth boilerplate and managed install—self-serve Easy buildability. Access is Self-Serve (CLI init, dev stores, App Store path). No MCP mentioned in evidence → existing_mcp None. No material blocker; recommended_next_action Build Now. Rate limits are referenced but not quantified in excerpts. PRESEED was none; evidence fully supports a mature public API platform. Cleverence URL added no usable API detail. Confidence high due to first-party docs, slightly reduced only because rate-limit numbers and full OAuth flow detail are summarized rather than fully excerpted.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — Partner apps and dev stores via Shopify CLI; managed installation and App Store distribution available
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs (whitelist-enforced)
- https://shopify.dev
- https://shopify.dev/docs/api/usage/authentication
- https://shopify.dev/docs/api
