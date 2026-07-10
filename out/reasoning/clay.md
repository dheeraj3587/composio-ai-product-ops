# Clay - synthesis reasoning
_generated 2026-07-11 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Clay official API authentication developer documentation", "Clay API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://clay.com | HTTP 200 | hint | topics=api,access,mcp
- https://community.clay.com/x/support/5cwjpgptccda/authenticating-an-api-key-in-clay-steps-beyond-cur | HTTP 200 | search_result | topics=api,auth
- https://docs.clay.com/en/articles/9672399-http-api-with-jwt-authentication-with-clay | HTTP 404 | search_result | topics=none
- https://university.clay.com/docs/http-api-with-jwt-authentication-integration-overview | HTTP 200 | search_result | topics=api,auth,access
- https://developer.clay.com | HTTP 0 | derived_guess | topics=none
- https://developers.clay.com | HTTP 200 | derived_guess | topics=api,mcp

## Model reasoning
The developer documentation and official MCP repository indicate that users can generate an API key and use the REST API or MCP server. The main site offers a free trial, indicating self-serve access. The community post confirms API key usage.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can start a free trial, log into Clay, and generate an API key to use the API and MCP server.
- recommended_next_action: **Build Now**
- confidence: **0.8**

## Evidence URLs
- https://clay.com
- https://developers.clay.com
- https://github.com/clay-inc/clay-mcp
- https://community.clay.com/x/support/5cwjpgptccda/authenticating-an-api-key-in-clay-steps-beyond-cur

## Generated record
```json
{
  "app": "Clay",
  "category": "Research/Scraping",
  "one_liner": "Clay provides a developer API and an official MCP server for searching GTM data, running routines, and reading tables.",
  "auth_methods": [
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can start a free trial, log into Clay, and generate an API key to use the API and MCP server."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None. The API and MCP server are available and documented.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://clay.com",
    "https://developers.clay.com",
    "https://github.com/clay-inc/clay-mcp",
    "https://community.clay.com/x/support/5cwjpgptccda/authenticating-an-api-key-in-clay-steps-beyond-cur"
  ],
  "confidence": 0.8,
  "verification_status": "Auto",
  "slug": "clay",
  "primary_docs_url": "https://university.clay.com/docs/http-api-with-jwt-authentication-integration-overview",
  "rate_limit_note": "Not explicitly detailed in the provided documentation snippets.",
  "last_verified": "2026-07-11"
}
```
