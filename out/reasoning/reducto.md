# Reducto - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Reducto official API authentication developer documentation", "Reducto API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://reducto.ai | HTTP 200 | hint | topics=api,auth,access,mcp
- https://docs.reducto.ai/quickstart | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://docs.reducto.ai/api-reference/legacy/pipeline | HTTP 200 | search_result | topics=api,auth
- https://docs.reducto.ai/api-reference/webhook-portal | HTTP 200 | search_result | topics=api,auth
- https://developer.reducto.ai | HTTP 0 | derived_guess | topics=none
- https://developers.reducto.ai | HTTP 0 | derived_guess | topics=none

## Model reasoning
The official documentation clearly details a REST API that uses Bearer Token authentication. An official MCP server is also provided and documented. The quickstart guide indicates a self-serve onboarding process where developers can generate an API key and begin processing documents.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up, obtain an API key, and start using the API or MCP server immediately.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://docs.reducto.ai/quickstart
- https://docs.reducto.ai/api-reference/legacy/pipeline
- https://docs.reducto.ai/mcp-server

## Generated record
```json
{
  "app": "Reducto",
  "category": "AI/Meeting-tools",
  "one_liner": "Reducto provides a REST API and an official MCP server for AI-driven document parsing, extraction, and processing.",
  "auth_methods": [
    "Bearer Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up, obtain an API key, and start using the API or MCP server immediately."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.reducto.ai/quickstart",
    "https://docs.reducto.ai/api-reference/legacy/pipeline",
    "https://docs.reducto.ai/mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "reducto",
  "primary_docs_url": "https://docs.reducto.ai/quickstart",
  "rate_limit_note": "Rate limits and concurrency throttles exist and are documented in the API reference, though specific limits depend on the account tier.",
  "last_verified": "2026-07-10"
}
```
