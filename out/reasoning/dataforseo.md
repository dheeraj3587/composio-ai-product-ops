# DataForSEO - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["DataForSEO official API authentication developer documentation", "DataForSEO API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://docs.dataforseo.com | HTTP 200 | hint | topics=api,auth,access
- https://docs.dataforseo.com/v3/auth/ | HTTP 200 | search_result | topics=api,auth,access
- https://dataforseo.com/help-center/how-to-authenticate-with-dataforseo-google-search-serp-api-api-key-setup-and-code-examples | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://docs.dataforseo.com/v3/appendix-user-data/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.dataforseo.com | HTTP 0 | derived_guess | topics=none
- https://developers.dataforseo.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
The evidence clearly shows DataForSEO offers a self-serve REST API authenticated via Basic Auth (using login and password). They also recently launched an official MCP server, making integration straightforward.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can create a free account and immediately access their API login and password from the dashboard.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://docs.dataforseo.com/v3/auth/
- https://dataforseo.com/help-center/how-to-authenticate-with-dataforseo-google-search-serp-api-api-key-setup-and-code-examples
- https://dataforseo.com/update/dataforseo-mcp-server-launch
- https://dataforseo.com/model-context-protocol

## Generated record
```json
{
  "app": "DataForSEO",
  "category": "Research/Scraping",
  "one_liner": "DataForSEO provides a comprehensive suite of APIs and an official MCP server for SEO, SERP, and digital marketing data.",
  "auth_methods": [
    "Basic Auth"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can create a free account and immediately access their API login and password from the dashboard."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.dataforseo.com/v3/auth/",
    "https://dataforseo.com/help-center/how-to-authenticate-with-dataforseo-google-search-serp-api-api-key-setup-and-code-examples",
    "https://dataforseo.com/update/dataforseo-mcp-server-launch",
    "https://dataforseo.com/model-context-protocol"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "dataforseo",
  "primary_docs_url": "https://docs.dataforseo.com/v3/auth/",
  "rate_limit_note": "Usage is typically billed based on API calls and spending limits rather than strict rate limits, though specific rate limits are not detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
