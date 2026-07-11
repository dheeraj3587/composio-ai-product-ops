# Ahrefs - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Ahrefs official API authentication developer documentation", "Ahrefs API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://ahrefs.com/api | HTTP 200 | hint | topics=api,auth,mcp
- https://docs.ahrefs.com/ahrefs-connect/docs/oauth-guide | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://docs.ahrefs.com/en/api/docs/introduction | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://docs.ahrefs.com/uk | HTTP 200 | search_result | topics=api,auth,mcp
- https://developer.ahrefs.com | HTTP 404 | derived_guess | topics=none
- https://developers.ahrefs.com | HTTP 404 | derived_guess | topics=none

## Model reasoning
The documentation clearly details both a REST API and an official hosted MCP server. Authentication is supported via API Keys and OAuth 2.0 (for Ahrefs Connect). Production use of both the API and MCP requires a paid plan, making the access model Gated.

## Key decisions
- buildability: **Moderate**
- access_model: **Gated** - Production access to the API and the remote MCP server requires a paid Ahrefs subscription (Lite plan or higher). Free test queries are available without a paid plan.
- recommended_next_action: **Needs Outreach**
- confidence: **0.95**

## Evidence URLs
- https://docs.ahrefs.com/en/api/docs/introduction
- https://docs.ahrefs.com/en/mcp/docs/introduction
- https://docs.ahrefs.com/ahrefs-connect/docs/oauth-guide

## Generated record
```json
{
  "app": "Ahrefs",
  "category": "Research/Scraping",
  "one_liner": "Ahrefs provides a REST API and an official MCP server to access comprehensive SEO, marketing, and search data.",
  "auth_methods": [
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Production access to the API and the remote MCP server requires a paid Ahrefs subscription (Lite plan or higher). Free test queries are available without a paid plan."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Moderate",
  "main_blocker": "Accessing real production data requires an active paid Ahrefs subscription.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://docs.ahrefs.com/en/api/docs/introduction",
    "https://docs.ahrefs.com/en/mcp/docs/introduction",
    "https://docs.ahrefs.com/ahrefs-connect/docs/oauth-guide"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "ahrefs",
  "primary_docs_url": "https://docs.ahrefs.com/ahrefs-connect/docs/oauth-guide",
  "rate_limit_note": "API requests consume units based on rows and fields returned (minimum 50 units per request). The MCP server also enforces row and request limits based on the subscription tier.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "API access likely requires a paid Ahrefs plan at a certain tier (verify)."
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Ahrefs",
  "category": "Research/Scraping",
  "one_liner": "Ahrefs provides a REST API and an official MCP server to access comprehensive SEO, marketing, and search data.",
  "auth_methods": [
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Production access to the API and the remote MCP server requires a paid Ahrefs subscription (Lite plan or higher). Free test queries are available without a paid plan."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Moderate",
  "main_blocker": "Accessing real production data requires an active paid Ahrefs subscription.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://docs.ahrefs.com/en/api/docs/introduction",
    "https://docs.ahrefs.com/ahrefs-connect/docs/oauth-guide",
    "https://docs.ahrefs.com/en/mcp/docs/introduction"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "ahrefs",
  "primary_docs_url": "https://docs.ahrefs.com/en/api/docs/introduction",
  "rate_limit_note": "API requests consume units based on rows and fields returned (minimum 50 units per request). The MCP server also enforces row and request limits based on the subscription tier.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
