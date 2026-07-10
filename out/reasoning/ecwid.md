# Ecwid - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Ecwid official API authentication developer documentation", "Ecwid API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://api-docs.ecwid.com | HTTP 200 | hint | topics=api
- https://docs.ecwid.com/api-reference | HTTP 200 | search_result | topics=api,auth
- https://docs.ecwid.com/changelog | HTTP 200 | search_result | topics=api,auth
- https://docs.ecwid.com/get-started/make-your-first-api-request | HTTP 200 | search_result | topics=api,auth,access
- https://developer.ecwid.com | HTTP 404 | derived_guess | topics=none
- https://developers.ecwid.com | HTTP 200 | derived_guess | topics=api

## Model reasoning
The official documentation clearly details a REST API with self-serve access via custom apps (providing public and secret tokens) or OAuth 2.0 for public apps. Rate limits are explicitly stated. Community MCPs exist via Zapier and viaSocket, but no official MCP was found.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up, create a custom app, and immediately obtain public and secret access tokens for their own store.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://docs.ecwid.com/get-started/make-your-first-api-request
- https://docs.ecwid.com/api-reference
- https://viasocket.com/mcp/ecwid-by-lightspeed

## Generated record
```json
{
  "app": "Ecwid",
  "category": "Commerce",
  "one_liner": "Ecwid provides a comprehensive REST API for managing store data, products, orders, and customers using OAuth 2.0.",
  "auth_methods": [
    "OAuth2",
    "Personal Access Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up, create a custom app, and immediately obtain public and secret access tokens for their own store."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.ecwid.com/get-started/make-your-first-api-request",
    "https://docs.ecwid.com/api-reference",
    "https://viasocket.com/mcp/ecwid-by-lightspeed"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "ecwid",
  "primary_docs_url": "https://docs.ecwid.com/get-started/make-your-first-api-request",
  "rate_limit_note": "600 requests per minute per token. Exceeding this returns a 429 error with a Retry-After header.",
  "last_verified": "2026-07-10"
}
```
