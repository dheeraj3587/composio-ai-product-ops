# Threads (Meta) - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Threads (Meta) official API authentication developer documentation", "Threads (Meta) API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developers.facebook.com/docs/threads | HTTP 200 | hint | topics=api,auth
- https://developers.facebook.com/docs/threads/get-started/ | HTTP 200 | search_result | topics=api,auth,access
- https://developers.facebook.com/docs/threads/ | HTTP 200 | search_result | topics=api,auth
- https://developers.facebook.com/docs/threads/get-started/get-access-tokens-and-permissions/ | HTTP 200 | search_result | topics=api,auth
- https://developer.facebook.com | HTTP 200 | derived_guess | topics=api,auth,access
- https://developers.facebook.com | HTTP 200 | derived_guess | topics=api,auth,access

## Model reasoning
The official documentation clearly outlines an OAuth2 flow for user access tokens and explicitly states that App Review is required for public users to grant permissions. The API covers a broad range of features including publishing, replies, and insights. Multiple community MCP servers exist.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Requires Meta App Review for production access to permissions for users without a role on the app.
- recommended_next_action: **Needs Outreach**
- confidence: **0.9**

## Evidence URLs
- https://developers.facebook.com/docs/threads/get-started/
- https://developers.facebook.com/docs/threads/get-started/get-access-tokens-and-permissions/
- https://github.com/quinnjr/threads-mcp
- https://lobehub.com/ru/mcp/metathreads-meta-threads-mcp

## Generated record
```json
{
  "app": "Threads (Meta)",
  "category": "Ads/Marketing",
  "one_liner": "The Threads API by Meta allows developers to publish content, manage replies, and retrieve insights via a REST API.",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Requires Meta App Review for production access to permissions for users without a role on the app."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "Production access requires passing Meta's App Review process to get permissions approved for public users.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developers.facebook.com/docs/threads/get-started/",
    "https://developers.facebook.com/docs/threads/get-started/get-access-tokens-and-permissions/",
    "https://github.com/quinnjr/threads-mcp",
    "https://lobehub.com/ru/mcp/metathreads-meta-threads-mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "threads",
  "primary_docs_url": "https://developers.facebook.com/docs/threads/get-started/",
  "rate_limit_note": "Rate limits and publishing quotas apply, though specific limits are not detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
