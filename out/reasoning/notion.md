# Notion - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Notion official API authentication developer documentation", "Notion API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developers.notion.com | HTTP 200 | hint | topics=api,auth,access,mcp
- https://developers.notion.com/reference/authentication | HTTP 200 | search_result | topics=api,auth
- https://developers.notion.com/guides/get-started/authorization | HTTP 200 | search_result | topics=api,auth,mcp
- https://developers.notion.com/cli/get-started/authentication | HTTP 200 | search_result | topics=api,auth
- https://developer.notion.com | HTTP 0 | derived_guess | topics=none
- https://docs.notion.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
Notion provides a REST API and an official MCP server. Auth methods include OAuth2, Personal Access Tokens, and static API tokens (API Key). Removed Bearer Token to comply with the rule against labeling specific tokens as Bearer Token.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can create internal connections or public OAuth apps directly from the Notion Developer Portal without manual approval.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developers.notion.com
- https://developers.notion.com/reference/authentication
- https://developers.notion.com/guides/get-started/authorization
- https://developers.notion.com/guides/mcp/overview

## Generated record
```json
{
  "app": "Notion",
  "category": "Productivity/PM",
  "one_liner": "Notion provides a comprehensive REST API and an official hosted MCP server for integrating AI tools and external apps.",
  "auth_methods": [
    "OAuth2",
    "Personal Access Token",
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can create internal connections or public OAuth apps directly from the Notion Developer Portal without manual approval."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.notion.com",
    "https://developers.notion.com/reference/authentication",
    "https://developers.notion.com/guides/get-started/authorization",
    "https://developers.notion.com/guides/mcp/overview"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "notion",
  "primary_docs_url": "https://developers.notion.com",
  "rate_limit_note": "Request limits exist and are documented in the API reference, though specific thresholds are not detailed in the fetched snippets.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Notion",
  "category": "Productivity/PM",
  "one_liner": "Notion provides a comprehensive REST API and an official hosted MCP server for integrating AI tools and external apps.",
  "auth_methods": [
    "OAuth2",
    "Personal Access Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can create internal connections or public OAuth apps directly from the Notion Developer Portal without manual approval."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.notion.com/reference/authentication",
    "https://developers.notion.com/guides/get-started/personal-access-tokens",
    "https://developers.notion.com/guides/mcp/overview"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "notion",
  "primary_docs_url": "https://developers.notion.com/reference/authentication",
  "rate_limit_note": "Request limits exist and are documented in the API reference, though specific thresholds are not detailed in the fetched snippets.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
