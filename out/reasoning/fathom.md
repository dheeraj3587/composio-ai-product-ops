# Fathom — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
The evidence explicitly confirms a public REST API with a developer hub, SDKs (TypeScript/Python), and multiple auth methods including API keys and OAuth. The preseed hypothesis that it might be webhook/Zapier-only is refuted by the existence of the developer portal at developers.fathom.ai. Note: api-docs.fathom.global refers to a different 'Fathom' (flood risk intelligence), which was ignored in favor of the meeting-tool evidence. Fathom.video also explicitly mentions 'Public API & MCP' in its integrations list.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — Quickstart guide allows generating an API key and making calls in minutes.
- recommended_next_action: **Build Now**
- confidence: **1.0**

## Evidence URLs (whitelist-enforced)
- https://fathom.video
- https://developers.fathom.ai/
- https://developers.fathom.ai/sdks/authentication

## Preseed hypothesis (unverified prior)
```json
{
  "api_type": "None",
  "main_blocker": "May be webhook/Zapier-only; unclear whether a fully public REST API exists — verify against docs, do not trust memory."
}
```
_The model was instructed to trust evidence over this prior and note contradictions above._
