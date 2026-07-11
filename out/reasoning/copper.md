# Copper - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Copper official API authentication developer documentation", "Copper API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://copper.com | HTTP 200 | hint | topics=api,access
- https://developer.copper.com/introduction/oauth/flow.html | HTTP 200 | search_result | topics=api,auth
- https://developer.copper.com/introduction/oauth/index.html | HTTP 200 | search_result | topics=api,auth
- https://developer.copper.com/introduction/requests.html | HTTP 200 | search_result | topics=api,auth
- https://developer.copper.com | HTTP 200 | derived_guess | topics=api,auth
- https://developers.copper.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
The Copper Developer API documentation clearly outlines support for OAuth2 and legacy API keys, with a broad set of REST endpoints covering leads, people, companies, and more. A free trial allows self-serve access. A community MCP server is available via SyncHub.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up for a free trial and create API keys or configure OAuth2 applications directly.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://developer.copper.com/introduction/oauth/flow.html
- https://developer.copper.com/introduction/oauth/index.html
- https://developer.copper.com/introduction/requests.html
- https://copper.com
- https://www.synchub.io/connectors/copper/knowledge-base/mcp

## Generated record
```json
{
  "app": "Copper",
  "category": "CRM",
  "one_liner": "Copper provides a comprehensive REST API for integrating with its CRM platform, supporting both OAuth2 and API keys.",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up for a free trial and create API keys or configure OAuth2 applications directly."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developer.copper.com/introduction/oauth/flow.html",
    "https://developer.copper.com/introduction/oauth/index.html",
    "https://developer.copper.com/introduction/requests.html",
    "https://copper.com",
    "https://www.synchub.io/connectors/copper/knowledge-base/mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "copper",
  "primary_docs_url": "https://developer.copper.com/introduction/oauth/flow.html",
  "rate_limit_note": "Rate limits are enforced and detailed in the API documentation.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Copper",
  "category": "CRM",
  "one_liner": "Copper provides a comprehensive REST API for integrating with its CRM platform, supporting both OAuth2 and API keys.",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Copper provides a temporary trial; continued production API use requires a paid Copper subscription."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Moderate",
  "main_blocker": "Production credentials require an existing paid customer account.",
  "recommended_next_action": "Partner-Gated",
  "evidence_urls": [
    "https://developer.copper.com/introduction/oauth/index.html",
    "https://developer.copper.com/introduction/requests.html",
    "https://www.copper.com/pricing",
    "https://www.synchub.io/connectors/copper/knowledge-base/mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Hand-Checked",
  "slug": "copper",
  "primary_docs_url": "https://developer.copper.com/introduction/oauth/index.html",
  "rate_limit_note": "Rate limits are enforced and detailed in the API documentation.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
