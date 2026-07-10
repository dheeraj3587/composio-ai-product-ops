# Linear - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Linear official API authentication developer documentation", "Linear API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developers.linear.app | HTTP 200 | hint | topics=api,auth,access
- https://linear.app/developers/oauth-2-0-authentication | HTTP 200 | search_result | topics=api,auth,access
- https://linear.app/developers/file-storage-authentication | HTTP 200 | search_result | topics=api,auth,access
- https://linear.app/developers | HTTP 200 | search_result | topics=api,auth,access
- https://developer.linear.app | HTTP 200 | derived_guess | topics=api,auth,access
- https://docs.linear.app | HTTP 200 | derived_guess | topics=access

## Model reasoning
Linear offers comprehensive developer documentation for its GraphQL API and an official, centrally hosted remote MCP server. Authentication is self-serve via OAuth 2.0 or personal API keys.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up and generate personal API keys or create OAuth2 applications without manual approval.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developers.linear.app
- https://linear.app/developers/oauth-2-0-authentication
- https://linear.app/docs/mcp

## Generated record
```json
{
  "app": "Linear",
  "category": "Productivity/PM",
  "one_liner": "Linear provides a GraphQL API, TypeScript SDK, and an official MCP server for managing issues, projects, and workflows.",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up and generate personal API keys or create OAuth2 applications without manual approval."
  },
  "api_type": "GraphQL",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.linear.app",
    "https://linear.app/developers/oauth-2-0-authentication",
    "https://linear.app/docs/mcp"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "linear",
  "primary_docs_url": "https://linear.app/developers/oauth-2-0-authentication",
  "rate_limit_note": "Rate limiting is enforced on the GraphQL API; specific limits are detailed in the developer documentation.",
  "last_verified": "2026-07-10"
}
```
