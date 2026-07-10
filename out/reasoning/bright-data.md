# Bright Data - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Bright Data official API authentication developer documentation", "Bright Data API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://brightdata.com | HTTP 200 | hint | topics=api,access,mcp
- https://docs.brightdata.com/api-reference/authentication | HTTP 200 | search_result | topics=api,auth,access
- https://docs.brightdata.com/api-reference/marketplace-dataset-api/get-dataset-list | HTTP 200 | search_result | topics=api,auth,access
- https://docs.brightdata.com/datasets/scrapers/scrapers-library/authentication-guide | HTTP 200 | search_result | topics=api,auth,access
- https://developer.brightdata.com | HTTP 0 | derived_guess | topics=none
- https://developers.brightdata.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
Bright Data offers a self-serve platform with clear documentation for its REST APIs. Authentication is handled via a static API key passed as a Bearer token. They also provide an official MCP server for AI agents to access web data, making integration highly accessible.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up for a free trial and an API key is automatically generated upon account creation.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://docs.brightdata.com/api-reference/authentication
- https://docs.brightdata.com/api-reference/marketplace-dataset-api/get-dataset-list
- https://brightdata.com/ai/mcp-server
- https://docs.brightdata.com/cn/ai/mcp-server/faqs

## Generated record
```json
{
  "app": "Bright Data",
  "category": "Research/Scraping",
  "one_liner": "Bright Data provides APIs and an official MCP server for web scraping, proxy infrastructure, and dataset extraction.",
  "auth_methods": [
    "API Key",
    "Bearer Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up for a free trial and an API key is automatically generated upon account creation."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.brightdata.com/api-reference/authentication",
    "https://docs.brightdata.com/api-reference/marketplace-dataset-api/get-dataset-list",
    "https://brightdata.com/ai/mcp-server",
    "https://docs.brightdata.com/cn/ai/mcp-server/faqs"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "bright-data",
  "primary_docs_url": "https://docs.brightdata.com/api-reference/authentication",
  "rate_limit_note": "The free tier for the MCP server is limited to 5,000 requests per month.",
  "last_verified": "2026-07-10"
}
```
