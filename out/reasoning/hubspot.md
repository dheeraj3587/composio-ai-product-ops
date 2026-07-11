# HubSpot - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["HubSpot official API authentication developer documentation", "HubSpot API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://hubspot.com | HTTP 200 | hint | topics=access
- https://developers.hubspot.com/docs/api-reference/latest/authentication/manage-oauth-tokens | HTTP 200 | search_result | topics=api,auth,access
- https://developers.hubspot.com/docs/apps/legacy-apps/authentication/oauth-quickstart-guide | HTTP 200 | search_result | topics=api,auth,access
- https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys | HTTP 200 | search_result | topics=api,auth,access
- https://developer.hubspot.com | HTTP 200 | derived_guess | topics=api,access
- https://developers.hubspot.com | HTTP 200 | derived_guess | topics=api,access

## Model reasoning
HubSpot's developer documentation clearly outlines self-serve access to OAuth2 and Service Keys (API Keys) for their REST APIs. Furthermore, HubSpot has officially released an MCP server (in public beta) to allow AI tools to securely interact with CRM data, making it highly buildable.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can freely create a developer account to build apps, generate OAuth credentials, or create service keys for API access.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developers.hubspot.com/docs/api-reference/latest/authentication/manage-oauth-tokens
- https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys
- https://developers.hubspot.com/mcp
- https://developers.hubspot.com/docs/apps/developer-platform/build-apps/integrate-with-the-remote-hubspot-mcp-server

## Generated record
```json
{
  "app": "HubSpot",
  "category": "CRM",
  "one_liner": "HubSpot provides a comprehensive CRM platform with robust REST APIs and an official MCP server for AI integrations.",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can freely create a developer account to build apps, generate OAuth credentials, or create service keys for API access."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.hubspot.com/docs/api-reference/latest/authentication/manage-oauth-tokens",
    "https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys",
    "https://developers.hubspot.com/mcp",
    "https://developers.hubspot.com/docs/apps/developer-platform/build-apps/integrate-with-the-remote-hubspot-mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "hubspot",
  "primary_docs_url": "https://developers.hubspot.com/docs/api-reference/latest/authentication/manage-oauth-tokens",
  "rate_limit_note": "Service keys and OAuth apps are subject to standard API limits based on the developer platform version.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current handcheck fold; this supersedes earlier key decisions._

```json
{
  "app": "HubSpot",
  "category": "CRM",
  "one_liner": "HubSpot provides a comprehensive CRM platform with robust REST APIs and an official MCP server for AI integrations.",
  "auth_methods": [
    "OAuth2",
    "Bearer Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can freely create a developer account to build apps, generate OAuth credentials, or create service keys for API access."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.hubspot.com/docs/api-reference/latest/authentication/manage-oauth-tokens",
    "https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys",
    "https://developers.hubspot.com/docs/getting-started/account-types",
    "https://developers.hubspot.com/ai-tools/mcp"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "hubspot",
  "primary_docs_url": "https://developers.hubspot.com/docs/api-reference/latest/authentication/manage-oauth-tokens",
  "rate_limit_note": "Service keys and OAuth apps are subject to standard API limits based on the developer platform version.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
