# Sherlock - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Sherlock official API authentication developer documentation", "Sherlock API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://github.com/sherlock-project/sherlock | HTTP 200 | hint | topics=access,mcp
- https://developer.ansys.com/docs/sherlock-apis-2025-r2/getting-started.md | HTTP 403 | search_result | topics=none
- https://developer.zendesk.com/documentation/conversations/getting-started/api-authentication/ | HTTP 200 | search_result | topics=api,auth
- https://api-docs.zocdoc.com/guides/authentication | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developer.github.com | HTTP 200 | derived_guess | topics=api,auth
- https://developers.github.com | HTTP 200 | derived_guess | topics=none

## Model reasoning
Sherlock is an open-source Python CLI tool for OSINT, not a hosted API service. While a community MCP server exists to wrap the CLI locally, there is no hosted API surface to integrate with.

## Key decisions
- buildability: **Blocked**
- access_model: **Self-Serve** - Sherlock is a free, open-source CLI tool that does not require API credentials or vendor approval.
- recommended_next_action: **Blocked**
- confidence: **0.95**

## Evidence URLs
- https://github.com/sherlock-project/sherlock
- https://www.mcp-gallery.jp/mcp/github/burnsedia/sherlock-mcp

## Generated record
```json
{
  "app": "Sherlock",
  "category": "Research/Scraping",
  "one_liner": "Sherlock is an open-source CLI tool for hunting social media accounts by username across various social networks.",
  "auth_methods": [
    "None / Not Applicable"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Sherlock is a free, open-source CLI tool that does not require API credentials or vendor approval."
  },
  "api_type": "None",
  "api_breadth": "Narrow",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Blocked",
  "main_blocker": "Sherlock is a local CLI tool, not a hosted API service, meaning there is no cloud API surface to integrate against.",
  "recommended_next_action": "Blocked",
  "evidence_urls": [
    "https://github.com/sherlock-project/sherlock",
    "https://www.mcp-gallery.jp/mcp/github/burnsedia/sherlock-mcp"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "sherlock",
  "primary_docs_url": "https://api-docs.zocdoc.com/guides/authentication",
  "rate_limit_note": "Not applicable as there is no hosted API.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "api_type": "None",
  "access_model": "Self-Serve",
  "recommended_next_action": "Blocked",
  "main_blocker": "Open-source CLI tool (username OSINT), not an API service; nothing to integrate via a hosted API."
}
```
