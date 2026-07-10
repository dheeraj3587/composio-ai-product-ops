# Squarespace - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Squarespace official API authentication developer documentation", "Squarespace API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developers.squarespace.com | HTTP 200 | hint | topics=api
- https://developers.squarespace.com/oauth | HTTP 200 | search_result | topics=api,auth,access
- https://developers.squarespace.com/commerce-apis/authentication-and-permissions | HTTP 200 | search_result | topics=api,auth
- https://developers.squarespace.com/commerce-apis/website-overview | HTTP 200 | search_result | topics=api,auth
- https://developer.squarespace.com | HTTP 200 | derived_guess | topics=none
- https://docs.squarespace.com | HTTP 404 | derived_guess | topics=none

## Model reasoning
The documentation clearly outlines OAuth 2.0 and API Key authentication for the REST Commerce APIs. OAuth requires submitting a form for review, and API keys require a Commerce Advanced plan, making production access gated. Community MCPs exist but are unofficial.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - API keys require a Commerce Advanced plan. OAuth client registration requires submitting a form for manual review by Squarespace.
- recommended_next_action: **Needs Outreach**
- confidence: **0.9**

## Evidence URLs
- https://developers.squarespace.com/oauth
- https://developers.squarespace.com/commerce-apis/authentication-and-permissions
- https://github.com/BusyBee3333/squarespace-mcp-2026-complete

## Generated record
```json
{
  "app": "Squarespace",
  "category": "Commerce",
  "one_liner": "Squarespace provides REST Commerce APIs to manage merchant site data such as products, orders, inventory, and...",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "API keys require a Commerce Advanced plan. OAuth client registration requires submitting a form for manual review by Squarespace."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "OAuth client registration requires manual review, and generating API keys requires an existing Commerce Advanced paid plan.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developers.squarespace.com/oauth",
    "https://developers.squarespace.com/commerce-apis/authentication-and-permissions",
    "https://github.com/BusyBee3333/squarespace-mcp-2026-complete"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "squarespace",
  "primary_docs_url": "https://developers.squarespace.com/oauth",
  "rate_limit_note": "No specific rate limits were found in the provided documentation.",
  "last_verified": "2026-07-10"
}
```
