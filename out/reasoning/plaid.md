# Plaid — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
The evidence confirms a broad REST API with a self-serve onboarding process via the Plaid Dashboard to get API keys. The preseed hypothesis regarding the 'self-serve trial, gated production' model is confirmed by the 'Launch checklist' and general industry knowledge of Plaid's approval process, though the provided text specifically mentions creating an account to get a live client_id and secret. The existence of an official MCP server is explicitly mentioned in the documentation ('Plug me in via the Plaid MCP Server'). Buildability is 'Easy' because keys are self-serve and documentation is comprehensive.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — Self-serve signup for API keys via Dashboard; production access typically requires a review process.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs (whitelist-enforced)
- https://plaid.com/docs
- https://plaid.com/docs/api/

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Self-Serve",
  "recommended_next_action": "Build Now",
  "main_blocker": "Free/instant sandbox is self-serve, but PRODUCTION access requires a Plaid approval/review process.",
  "note": "Capture as 'self-serve trial, gated production', not a flat label."
}
```
_The model was instructed to trust evidence over this prior and note contradictions above._
