# systeme.io - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["systeme.io official API authentication developer documentation", "systeme.io API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://systeme.io | HTTP 200 | hint | topics=api
- https://help.systeme.io/article/2329-how-to-use-systeme-io-public-api | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://help.systeme.io/article/2323-how-to-create-a-public-api-key-on-systeme-io | HTTP 200 | search_result | topics=api,auth,mcp
- https://aide.systeme.io/article/2328-comment-utiliser-api-publique-de-systemeio | HTTP 200 | search_result | topics=api,mcp
- https://developer.systeme.io | HTTP 200 | derived_guess | topics=api
- https://developers.systeme.io | HTTP 404 | derived_guess | topics=none

## Model reasoning
Systeme.io offers a self-serve REST API and an official MCP server. Users can create a free account and immediately generate API or MCP keys to manage contacts, tags, subscriptions, and newsletters.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up for a free account and generate API and MCP keys directly from the settings dashboard.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://help.systeme.io/article/2329-how-to-use-systeme-io-public-api
- https://help.systeme.io/article/2323-how-to-create-a-public-api-key-on-systeme-io
- https://help.systeme.io/article/9489-how-to-use-systeme-ios-mcp
- https://systeme.io

## Generated record
```json
{
  "app": "systeme.io",
  "category": "Ads/Marketing",
  "one_liner": "Systeme.io provides a REST API and an official MCP server for managing contacts, tags, subscriptions, and newsletters.",
  "auth_methods": [
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up for a free account and generate API and MCP keys directly from the settings dashboard."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://help.systeme.io/article/2329-how-to-use-systeme-io-public-api",
    "https://help.systeme.io/article/2323-how-to-create-a-public-api-key-on-systeme-io",
    "https://help.systeme.io/article/9489-how-to-use-systeme-ios-mcp",
    "https://systeme.io"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "systeme-io",
  "primary_docs_url": "https://help.systeme.io/article/2329-how-to-use-systeme-io-public-api",
  "rate_limit_note": "No specific rate limits are mentioned in the provided documentation.",
  "last_verified": "2026-07-10"
}
```
