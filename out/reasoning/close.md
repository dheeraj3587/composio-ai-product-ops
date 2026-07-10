# Close - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Close official API authentication developer documentation", "Close API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://close.com | HTTP 200 | hint | topics=api,access,mcp
- https://developer.close.com/integrations/create-an-oauth-app | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developer.close.com/topics/authentication-oauth2/ | HTTP 200 | search_result | topics=api,auth,mcp
- https://help.close.com/docs/api-keys-oauth | HTTP 200 | search_result | topics=api,auth,access
- https://developer.close.com | HTTP 200 | derived_guess | topics=api,auth,access,mcp
- https://developers.close.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
The documentation clearly outlines self-serve access for both API keys and OAuth 2.0 apps. Close also provides an official MCP server (mcp.close.com) with documented scopes and authentication methods, making it highly buildable for AI integrations.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can create API keys or register OAuth applications directly from the Close settings dashboard without manual approval.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developer.close.com/integrations/create-an-oauth-app
- https://help.close.com/docs/api-keys-oauth
- https://developer.close.com
- https://help.close.com/docs/mcp-server

## Generated record
```json
{
  "app": "Close",
  "category": "CRM",
  "one_liner": "Close is a sales CRM providing a comprehensive REST API and an official MCP server for AI agents.",
  "auth_methods": [
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can create API keys or register OAuth applications directly from the Close settings dashboard without manual approval."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developer.close.com/integrations/create-an-oauth-app",
    "https://help.close.com/docs/api-keys-oauth",
    "https://developer.close.com",
    "https://help.close.com/docs/mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "close",
  "primary_docs_url": "https://developer.close.com/integrations/create-an-oauth-app",
  "rate_limit_note": "Rate limits exist and are documented in the API reference, though specific thresholds are not detailed in the fetched snippets.",
  "last_verified": "2026-07-10"
}
```
