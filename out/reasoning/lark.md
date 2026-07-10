# Lark (Larksuite) - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Lark (Larksuite) official API authentication developer documentation", "Lark (Larksuite) API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://open.larksuite.com | HTTP 200 | hint | topics=none
- https://open.larksuite.com/document/uAjLw4CM/ukTMukTMukTM/reference/authen-v1/oidc-access_token/create | HTTP 200 | search_result | topics=auth
- https://open.larksuite.com/document/server-docs/getting-started/api-access-token/app-access-token-development-guide | HTTP 200 | search_result | topics=api,auth
- https://open.larksuite.com/document/server-docs/getting-started/overview-of-app-scopes | HTTP 200 | search_result | topics=none
- https://developer.larksuite.com | HTTP 200 | derived_guess | topics=none
- https://developers.larksuite.com | HTTP 200 | derived_guess | topics=none

## Model reasoning
Evidence confirms an official MCP server exists on the larksuite GitHub and open.larksuite.com documentation. API access requires app review and approval, making it Gated.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - App permissions require review and approval before the app can invoke server APIs.
- recommended_next_action: **Needs Outreach**
- confidence: **0.85**

## Evidence URLs
- https://open.larksuite.com/document/server-docs/getting-started/overview-of-app-scopes
- https://open.larksuite.com/document/server-docs/getting-started/api-access-token/app-access-token-development-guide
- https://github.com/larksuite/lark-openapi-mcp
- https://open.larksuite.com/document/uAjLw4CM/ukTMukTMukTM/mcp_integration/mcp_introduction

## Generated record
```json
{
  "app": "Lark (Larksuite)",
  "category": "Comms",
  "one_liner": "Lark (Larksuite) provides a REST API and an official MCP server for integrating AI agents with its collaboration...",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "App permissions require review and approval before the app can invoke server APIs."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "App review and permission approval are required before API access is granted.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://open.larksuite.com/document/server-docs/getting-started/overview-of-app-scopes",
    "https://open.larksuite.com/document/server-docs/getting-started/api-access-token/app-access-token-development-guide",
    "https://github.com/larksuite/lark-openapi-mcp",
    "https://open.larksuite.com/document/uAjLw4CM/ukTMukTMukTM/mcp_integration/mcp_introduction"
  ],
  "confidence": 0.85,
  "verification_status": "Auto",
  "slug": "lark",
  "primary_docs_url": "https://github.com/larksuite/lark-openapi-mcp",
  "rate_limit_note": "Not explicitly detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
