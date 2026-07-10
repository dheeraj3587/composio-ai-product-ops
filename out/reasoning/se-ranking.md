# SE Ranking - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["SE Ranking official API authentication developer documentation", "SE Ranking API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://seranking.com/api | HTTP 404 | hint | topics=none
- https://seranking.com/api/project/getting-started/ | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://seranking.com/api/data/quickstarts/ | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://seranking.com/api/data/getting-started/ | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developer.seranking.com | HTTP 0 | derived_guess | topics=none
- https://developers.seranking.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
The evidence confirms SE Ranking offers a REST API authenticated via API Key and an official MCP server published by the vendor. Access is self-serve but requires purchasing API credits.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - API access requires an SE Ranking account and is billed via an API credit system (e.g., $50 for 250K credits).
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://seranking.com/api/project/getting-started/
- https://seranking.com/api/data/getting-started/
- https://seranking.com/api/integrations/mcp/
- https://mcp.directory/servers/se-ranking

## Generated record
```json
{
  "app": "SE Ranking",
  "category": "Research/Scraping",
  "one_liner": "SE Ranking provides a REST API and an official MCP server for programmatic access to SEO data, keyword research, and...",
  "auth_methods": [
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "API access requires an SE Ranking account and is billed via an API credit system (e.g., $50 for 250K credits)."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "Requires a paid SE Ranking account with API credits to execute queries.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://seranking.com/api/project/getting-started/",
    "https://seranking.com/api/data/getting-started/",
    "https://seranking.com/api/integrations/mcp/",
    "https://mcp.directory/servers/se-ranking"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "se-ranking",
  "primary_docs_url": "https://seranking.com/api/project/getting-started/",
  "rate_limit_note": "Rate limits and usage are governed by the API credit system associated with the user's plan.",
  "last_verified": "2026-07-10"
}
```
