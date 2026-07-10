# Devin - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Devin official API authentication developer documentation", "Devin API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://docs.devin.ai | HTTP 200 | hint | topics=api,access,mcp
- https://docs.devin.ai/api-reference/getting-started/enterprise-quickstart | HTTP 200 | search_result | topics=api,auth
- https://docs.devin.ai/api-reference/authentication | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://docs.devin.ai/ja/api-reference/authentication | HTTP 200 | search_result | topics=api,auth,mcp
- https://developer.devin.ai | HTTP 0 | derived_guess | topics=none
- https://developers.devin.ai | HTTP 0 | derived_guess | topics=none

## Model reasoning
The documentation clearly outlines a REST API authenticated via Service User API Keys or Personal Access Tokens. An official Devin MCP server is also documented for programmatic access to platform capabilities.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up, create an organization, and generate Service User API keys for automation.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://docs.devin.ai/api-reference/authentication
- https://docs.devin.ai/work-with-devin/devin-mcp

## Generated record
```json
{
  "app": "Devin",
  "category": "AI/Meeting-tools",
  "one_liner": "Devin is an autonomous AI software engineer offering a REST API and an official MCP server for programmatic access.",
  "auth_methods": [
    "API Key",
    "Personal Access Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up, create an organization, and generate Service User API keys for automation."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.devin.ai/api-reference/authentication",
    "https://docs.devin.ai/work-with-devin/devin-mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "devin",
  "primary_docs_url": "https://docs.devin.ai/api-reference/authentication",
  "rate_limit_note": "Rate limits are not explicitly detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
