# Asana - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Asana official API authentication developer documentation", "Asana API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developers.asana.com | HTTP 200 | hint | topics=api,auth
- https://developers.asana.com/docs/oauth-scopes | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developers.asana.com/docs/oauth | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developers.asana.com/docs/authentication | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developer.asana.com | HTTP 200 | derived_guess | topics=api,access
- https://docs.asana.com | HTTP 404 | derived_guess | topics=none

## Model reasoning
Asana provides comprehensive developer documentation, self-serve access via PATs and OAuth2, a broad REST API, and an official MCP server, making it highly buildable.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can quickly generate a Personal Access Token (PAT) or set up an OAuth app via the developer console without manual approval.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developers.asana.com/docs/authentication
- https://developers.asana.com/docs/oauth
- https://developers.asana.com/docs/mcp-server
- https://developers.asana.com/docs/using-asanas-mcp-server

## Generated record
```json
{
  "app": "Asana",
  "category": "Productivity/PM",
  "one_liner": "Asana provides a comprehensive REST API and an official MCP server to integrate applications and AI assistants with...",
  "auth_methods": [
    "Personal Access Token",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can quickly generate a Personal Access Token (PAT) or set up an OAuth app via the developer console without manual approval."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.asana.com/docs/authentication",
    "https://developers.asana.com/docs/oauth",
    "https://developers.asana.com/docs/mcp-server",
    "https://developers.asana.com/docs/using-asanas-mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "asana",
  "primary_docs_url": "https://developers.asana.com/docs/oauth-scopes",
  "rate_limit_note": "Rate limits apply and are documented in the API reference, though specific limits are not detailed in the fetched snippets.",
  "last_verified": "2026-07-10"
}
```
