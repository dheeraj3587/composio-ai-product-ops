# Pylon — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
Evidence from usepylon.com docs confirms a public REST API with Bearer token auth generated self-serve by Admins in the dashboard, plus /me and endpoints for customers/issues (create/read). Nav explicitly lists Pylon MCP and MCP Connections, supporting Official MCP. Breadth assessed Moderate from listed use cases and API reference mention (full endpoint list not fetched). No rate limits, review gates, or blockers described. getpylon.com/developers is a different solar product (ignored as mismatched to Support category and evidence). Preseed was none so no confirmation/contradiction. Confidence moderate due to thin page content and unfetched full reference.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — Admin users generate API tokens directly in the Pylon dashboard
- recommended_next_action: **Build Now**
- confidence: **0.72**

## Evidence URLs (whitelist-enforced)
- https://usepylon.com
- https://docs.usepylon.com/pylon-docs/developer/api
- https://docs.usepylon.com/pylon-docs/developer/api/authentication
