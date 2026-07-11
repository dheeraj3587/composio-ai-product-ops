# Front - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Front official API authentication developer documentation", "Front API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://front.com | HTTP 200 | hint | topics=api,access
- https://help.front.com/en/categories/326 | HTTP 200 | search_result | topics=api,auth
- https://community.front.com/developers-36 | HTTP 200 | search_result | topics=api,access,mcp
- https://dev.frontapp.com/docs/oauth | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developer.front.com | HTTP 0 | derived_guess | topics=none
- https://developers.front.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
Front provides comprehensive REST API documentation with self-serve API tokens and OAuth2 support. The official documentation also includes a dedicated section for an MCP Server, indicating official support.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - API tokens and OAuth apps can be created directly in the Front settings by admins.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://dev.frontapp.com/docs/oauth
- https://help.front.com/en/categories/326
- https://dev.frontapp.com/docs/mcp-server

## Generated record
```json
{
  "app": "Front",
  "category": "Support",
  "one_liner": "Front provides a Core API and an official MCP server for building custom workflows, messaging channels, and AI...",
  "auth_methods": [
    "Bearer Token",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "API tokens and OAuth apps can be created directly in the Front settings by admins."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://dev.frontapp.com/docs/oauth",
    "https://help.front.com/en/categories/326",
    "https://dev.frontapp.com/docs/mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "front",
  "primary_docs_url": "https://dev.frontapp.com/docs/oauth",
  "rate_limit_note": "Front has two rate limits: global and burst.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Front",
  "category": "Support",
  "one_liner": "Front provides a Core API and an official MCP server for building custom workflows, messaging channels, and AI...",
  "auth_methods": [
    "Bearer Token",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Front API access is included with paid plans; the self-serve trial is temporary and does not satisfy the production-access rubric."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Moderate",
  "main_blocker": "Production API use requires an existing paid Front customer account.",
  "recommended_next_action": "Partner-Gated",
  "evidence_urls": [
    "https://dev.frontapp.com/docs/authentication",
    "https://help.front.com/en/articles/2438",
    "https://dev.frontapp.com/docs/mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "front",
  "primary_docs_url": "https://dev.frontapp.com/docs/authentication",
  "rate_limit_note": "Front has two rate limits: global and burst.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
