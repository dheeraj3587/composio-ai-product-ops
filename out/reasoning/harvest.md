# Harvest — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
The evidence clearly describes a broad REST API covering multiple domains (Invoices, Estimates, Expenses, Tasks, Timesheets, Projects, Users, Reports). Authentication is self-serve via Personal Access Tokens (PAT) for scripts or OAuth2 for applications. I ignored the 'HarvestAPI' (docs.harvestapi.io) and 'Greenhouse Harvest' results as they refer to different products (a LinkedIn scraper and an ATS respectively), focusing instead on the official getharvest.com documentation. Preseed was none.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** — Personal Access Tokens can be created directly from the Developers section of Harvest ID.
- recommended_next_action: **Build Now**
- confidence: **1.0**

## Evidence URLs (whitelist-enforced)
- https://help.getharvest.com/api-v2
- https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/
