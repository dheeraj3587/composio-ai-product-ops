# Ahrefs — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
The evidence confirms the preseed hypothesis: the API is gated behind eligible paid plans, although free test queries exist. Buildability is Moderate because while documentation is clear and API keys are self-managed, the financial barrier (paid plan) is a prerequisite for production use. The API breadth is Broad, covering Site Explorer, Keywords Explorer, Site Audit, Rank Tracker, and Brand Radar. Official MCP support is explicitly mentioned for Claude and ChatGPT. Recommended action is Partner-Gated because a paid account is required for meaningful integration.

## Key decisions
- buildability: **Moderate**
- access_model: **Gated** — Available on eligible paid plans; limited free test queries available for non-eligible plans.
- recommended_next_action: **Partner-Gated**
- confidence: **1.0**

## Evidence URLs (whitelist-enforced)
- https://ahrefs.com/api
- https://docs.ahrefs.com/en/api/docs/introduction
- https://docs.ahrefs.com/

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "API access likely requires a paid Ahrefs plan at a certain tier (verify)."
}
```
_The model was instructed to trust evidence over this prior and note contradictions above._
