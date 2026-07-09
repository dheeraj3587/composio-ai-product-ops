# PitchBook — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
The preseed hypothesis is confirmed. The provided evidence from Matia (a connector service) confirms the existence of a PitchBook API with specific streams (company, deal, etc.) and accessToken authentication, but the nature of PitchBook as an enterprise fintech platform means access is gated behind paid accounts. Buildability is 'Hard' because there is no public self-serve portal for API keys; users must be existing customers.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** — Enterprise research platform; API access is typically tied to a paid subscription and not self-serve.
- recommended_next_action: **Partner-Gated**
- confidence: **0.8**

## Evidence URLs (whitelist-enforced)
- https://docs.matia.io/docs/connectors/etl/pitchbook/api-configuration

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Partner-Gated",
  "main_blocker": "Enterprise research platform; API is contact-sales / partner-only, no public self-serve tier."
}
```
_The model was instructed to trust evidence over this prior and note contradictions above._
