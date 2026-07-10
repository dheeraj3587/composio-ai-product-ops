# Harvest - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Harvest official API authentication developer documentation", "Harvest API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://help.getharvest.com/api-v2 | HTTP 200 | hint | topics=api,auth
- https://support.getharvest.com/hc/en-us/articles/360048180732-The-Harvest-API | HTTP 200 | derived_guess | topics=api,access
- https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/ | HTTP 200 | search_result | topics=api,auth
- https://help.getharvest.com/api-v1/authentication/authentication/server-side-apps/ | HTTP 200 | search_result | topics=api,auth
- https://help.getharvest.com/api-v2/ | HTTP 200 | search_result | topics=api,auth
- https://developer.getharvest.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
The official documentation confirms that all Harvest accounts have API access and can generate Personal Access Tokens or use OAuth2. Community MCP servers exist.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - All Harvest accounts have API access. Developers can generate Personal Access Tokens or register OAuth2 applications directly from the Developers section of Harvest ID.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/
- https://support.getharvest.com/hc/en-us/articles/360048180732-The-Harvest-API
- https://github.com/taiste/harvest-mcp-server

## Generated record
```json
{
  "app": "Harvest",
  "category": "Productivity/PM",
  "one_liner": "Harvest provides a REST API and community MCP servers for managing time tracking, invoicing, and projects.",
  "auth_methods": [
    "Personal Access Token",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "All Harvest accounts have API access. Developers can generate Personal Access Tokens or register OAuth2 applications directly from the Developers section of Harvest ID."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/",
    "https://support.getharvest.com/hc/en-us/articles/360048180732-The-Harvest-API",
    "https://github.com/taiste/harvest-mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "harvest",
  "primary_docs_url": "https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/",
  "rate_limit_note": "Harvest throttles API requests, with details available in their API overview documentation.",
  "last_verified": "2026-07-10"
}
```
