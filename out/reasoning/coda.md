# Coda - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Coda official API authentication developer documentation", "Coda API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://coda.io/developers | HTTP 200 | hint | topics=api,auth,mcp
- https://coda.io/packs/build/latest/guides/basics/authentication/oauth2/ | HTTP 200 | search_result | topics=api,auth,access
- https://coda.io/developers/apis/admin/v1 | HTTP 200 | search_result | topics=api,auth
- https://coda.io/developers/apis/v1 | HTTP 200 | search_result | topics=api,auth,mcp
- https://developer.coda.io | HTTP 0 | derived_guess | topics=none
- https://developers.coda.io | HTTP 0 | derived_guess | topics=none

## Model reasoning
The official documentation confirms a REST API with OAuth2 and Bearer Token authentication. It also explicitly mentions an official Superhuman Docs MCP server for AI integrations, making it highly buildable.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Standard API tokens and OAuth2 apps can be created by users, though some Admin API endpoints require Enterprise plans.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://coda.io/developers/apis/v1
- https://coda.io/packs/build/latest/guides/basics/authentication/oauth2/
- https://coda.io/resources/guides/getting_started_with_coda_mcp

## Generated record
```json
{
  "app": "Coda",
  "category": "Productivity/PM",
  "one_liner": "Coda (now Superhuman Docs) provides a comprehensive REST API and an official MCP server for interacting with docs...",
  "auth_methods": [
    "OAuth2",
    "Bearer Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Standard API tokens and OAuth2 apps can be created by users, though some Admin API endpoints require Enterprise plans."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://coda.io/developers/apis/v1",
    "https://coda.io/packs/build/latest/guides/basics/authentication/oauth2/",
    "https://coda.io/resources/guides/getting_started_with_coda_mcp"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "coda",
  "primary_docs_url": "https://coda.io/packs/build/latest/guides/basics/authentication/oauth2/",
  "rate_limit_note": "Rate limiting is enforced; specific limits are detailed in the API documentation.",
  "last_verified": "2026-07-10"
}
```
