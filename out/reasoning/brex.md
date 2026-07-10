# Brex - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Brex official API authentication developer documentation", "Brex API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developer.brex.com | HTTP 200 | hint | topics=api,access,mcp
- https://developer.brex.com/guides/partner_authentication | HTTP 200 | search_result | topics=api,auth,access
- https://developer.brex.com/guides/authentication | HTTP 200 | search_result | topics=api,auth,access
- https://developer.brex.com/guides/roles_permissions_scopes | HTTP 200 | search_result | topics=api,auth,access
- https://developers.brex.com | HTTP 200 | derived_guess | topics=api,access,mcp
- https://docs.brex.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
The documentation clearly outlines REST API access via Bearer tokens and an official MCP server hosted at api.brex.com/mcp using OAuth. However, both require an existing Brex business account with admin privileges to accept the developer agreement and generate credentials, making it gated for solo developers without a Brex account.

## Key decisions
- buildability: **Moderate**
- access_model: **Gated** - Requires an active Brex business account with admin privileges to accept the developer agreement and generate tokens or enable the MCP beta.
- recommended_next_action: **Needs Outreach**
- confidence: **0.95**

## Evidence URLs
- https://developer.brex.com/guides/authentication
- https://developer.brex.com/docs/mcp
- https://developer.brex.com

## Generated record
```json
{
  "app": "Brex",
  "category": "Fintech",
  "one_liner": "Brex provides a unified spend platform API and an official MCP server for managing expenses, cards, and budgets.",
  "auth_methods": [
    "Bearer Token",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Requires an active Brex business account with admin privileges to accept the developer agreement and generate tokens or enable the MCP beta."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Moderate",
  "main_blocker": "Developers must have an active Brex business account with admin privileges to access the Developer settings, generate API tokens, or enable the MCP integration.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developer.brex.com/guides/authentication",
    "https://developer.brex.com/docs/mcp",
    "https://developer.brex.com"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "brex",
  "primary_docs_url": "https://developer.brex.com/guides/partner_authentication",
  "rate_limit_note": "Rate limits are mentioned in the documentation navigation, but specific limits are not detailed in the fetched text.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "API access is tied to being a Brex business customer; not self-serve for a solo developer testing."
}
```
