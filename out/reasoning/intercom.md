# Intercom - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Intercom official API authentication developer documentation", "Intercom API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://intercom.com | HTTP 200 | hint | topics=access
- https://developers.intercom.com/docs/build-an-integration/learn-more/authentication/setting-up-oauth | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developers.intercom.com/docs/build-an-integration/learn-more/authentication | HTTP 200 | search_result | topics=api,auth,mcp
- https://community.intercom.com/getting-started-with-intercom-43/api-how-to-set-up-an-access-bearer-token-a-k-a-find-workspace-access-token-7212 | HTTP 200 | search_result | topics=api,auth,access
- https://developer.intercom.com | HTTP 0 | derived_guess | topics=none
- https://developers.intercom.com | HTTP 200 | derived_guess | topics=api,access

## Model reasoning
Intercom offers a well-documented REST API and an official MCP server. Authentication is handled via OAuth2 for public apps and Access Tokens for private apps. A free developer workspace is available, making it self-serve.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up for a free development workspace to test and build apps.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developers.intercom.com/docs/build-an-integration/learn-more/authentication
- https://developers.intercom.com/docs/guides/mcp
- https://developers.intercom.com

## Generated record
```json
{
  "app": "Intercom",
  "category": "Support",
  "one_liner": "Intercom provides a comprehensive REST API and an official MCP server for integrating AI agents with customer...",
  "auth_methods": [
    "OAuth2",
    "Personal Access Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up for a free development workspace to test and build apps."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "The official MCP server is currently only supported in US hosted workspaces.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.intercom.com/docs/build-an-integration/learn-more/authentication",
    "https://developers.intercom.com/docs/guides/mcp",
    "https://developers.intercom.com"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "intercom",
  "primary_docs_url": "https://developers.intercom.com/docs/build-an-integration/learn-more/authentication/setting-up-oauth",
  "rate_limit_note": "Rate limits are not explicitly detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
