# Xero - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Xero official API authentication developer documentation", "Xero API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developer.xero.com | HTTP 200 | hint | topics=api,auth,access,mcp
- https://developer.xero.com/documentation/guides/oauth2/auth-flow/ | HTTP 200 | search_result | topics=auth
- https://developer.xero.com/documentation/guides/oauth2/overview/ | HTTP 200 | search_result | topics=auth
- https://developer.xero.com/documentation/guides/oauth2/troubleshooting | HTTP 200 | search_result | topics=auth
- https://developers.xero.com | HTTP 0 | derived_guess | topics=none
- https://docs.xero.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
Xero provides a comprehensive developer platform with standard OAuth2 authentication, REST APIs, and an official MCP server (xero-mcp-server) available on GitHub. Access is self-serve via a free developer account.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up for a free account to build on the Xero platform and access the API and MCP server.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developer.xero.com
- https://developer.xero.com/documentation/guides/oauth2/auth-flow/
- https://github.com/xeroapi/xero-mcp-server
- https://developer.xero.com/faq/AI-Toolkit

## Generated record
```json
{
  "app": "Xero",
  "category": "Fintech",
  "one_liner": "Xero provides a comprehensive developer platform with REST APIs and an official MCP server for accounting data...",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up for a free account to build on the Xero platform and access the API and MCP server."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developer.xero.com",
    "https://developer.xero.com/documentation/guides/oauth2/auth-flow/",
    "https://github.com/xeroapi/xero-mcp-server",
    "https://developer.xero.com/faq/AI-Toolkit"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "xero",
  "primary_docs_url": "https://developer.xero.com",
  "rate_limit_note": "Not explicitly detailed in the provided evidence.",
  "last_verified": "2026-07-10"
}
```
