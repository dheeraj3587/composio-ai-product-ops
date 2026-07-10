# Twenty - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Twenty official API authentication developer documentation", "Twenty API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://twenty.com | HTTP 200 | hint | topics=api,auth,access,mcp
- https://docs.twenty.com/developers/extend/oauth | HTTP 200 | search_result | topics=api,auth
- https://docs.twenty.com/l/zh/developers/extend/oauth | HTTP 200 | search_result | topics=api,auth
- https://docs.twenty.com/developers/extend/api | HTTP 200 | search_result | topics=api,auth,access
- https://developer.twenty.com | HTTP 200 | derived_guess | topics=none
- https://developers.twenty.com | HTTP 200 | derived_guess | topics=none

## Model reasoning
The documentation clearly outlines self-serve API key generation and dynamic OAuth client registration. Both REST and GraphQL APIs are available and dynamically generated based on the workspace schema. No MCP server was found in the evidence.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - API keys can be generated directly in the workspace settings, and OAuth clients can be registered dynamically via API without manual dashboard setup.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://docs.twenty.com/developers/extend/api
- https://docs.twenty.com/developers/extend/oauth

## Generated record
```json
{
  "app": "Twenty",
  "category": "CRM",
  "one_liner": "Twenty is an open-source CRM that provides dynamically generated REST and GraphQL APIs based on workspace schemas.",
  "auth_methods": [
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "API keys can be generated directly in the workspace settings, and OAuth clients can be registered dynamically via API without manual dashboard setup."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "None",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.twenty.com/developers/extend/api",
    "https://docs.twenty.com/developers/extend/oauth"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "twenty",
  "primary_docs_url": "https://docs.twenty.com/developers/extend/api",
  "rate_limit_note": "100 requests per minute, batch size up to 60 records per call.",
  "last_verified": "2026-07-10"
}
```
