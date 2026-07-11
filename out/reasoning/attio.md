# Attio - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Attio official API authentication developer documentation", "Attio API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://attio.com | HTTP 200 | hint | topics=api,access,mcp
- https://docs.attio.com/rest-api/tutorials/connect-an-app-through-oauth | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://docs.attio.com/docs/oauth/authorize | HTTP 200 | search_result | topics=api,auth,mcp
- https://docs.attio.com/rest-api/guides/authentication | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developer.attio.com | HTTP 0 | derived_guess | topics=none
- https://developers.attio.com | HTTP 200 | derived_guess | topics=api,mcp

## Model reasoning
Attio provides clear, self-serve documentation for its REST API, supporting both OAuth 2.0 for multi-tenant apps and API keys for single workspaces. Furthermore, Attio officially hosts and maintains an MCP server, making it highly accessible for AI integrations.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can create apps, configure OAuth 2.0, and generate single-workspace API keys directly from the developer dashboard.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://docs.attio.com/rest-api/guides/authentication
- https://docs.attio.com/rest-api/tutorials/connect-an-app-through-oauth
- https://docs.attio.com/mcp/overview
- https://attio.com/engineering/blog/building-the-attio-mcp-server

## Generated record
```json
{
  "app": "Attio",
  "category": "CRM",
  "one_liner": "Attio is an AI-native CRM platform offering a comprehensive REST API and an official hosted MCP server for AI agents.",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can create apps, configure OAuth 2.0, and generate single-workspace API keys directly from the developer dashboard."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.attio.com/rest-api/guides/authentication",
    "https://docs.attio.com/rest-api/tutorials/connect-an-app-through-oauth",
    "https://docs.attio.com/mcp/overview",
    "https://attio.com/engineering/blog/building-the-attio-mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "attio",
  "primary_docs_url": "https://docs.attio.com/rest-api/tutorials/connect-an-app-through-oauth",
  "rate_limit_note": "The documentation includes a section on 'Handling rate limits', though specific limits are not detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Attio",
  "category": "CRM",
  "one_liner": "Attio is an AI-native CRM platform offering a comprehensive REST API and an official hosted MCP server for AI agents.",
  "auth_methods": [
    "OAuth2",
    "API Key",
    "Basic Auth"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can create apps, configure OAuth 2.0, and generate single-workspace API keys directly from the developer dashboard."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.attio.com/rest-api/guides/authentication",
    "https://docs.attio.com/mcp/overview",
    "https://docs.attio.com/share/the-publication-lifecycle"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "attio",
  "primary_docs_url": "https://docs.attio.com/rest-api/guides/authentication",
  "rate_limit_note": "The documentation includes a section on 'Handling rate limits', though specific limits are not detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
