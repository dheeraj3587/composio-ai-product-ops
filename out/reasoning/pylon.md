# Pylon - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Pylon official API authentication developer documentation", "Pylon API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://usepylon.com | HTTP 200 | hint | topics=api,auth,access
- https://docs.usepylon.com/pylon-docs/developer/api/authentication | HTTP 200 | search_result | topics=api,auth,mcp
- https://docs.usepylon.com/pylon-docs/developer/api/api-reference/me | HTTP 200 | search_result | topics=api,auth,mcp
- https://docs.usepylon.com/pylon-docs/developer/api/api-reference | HTTP 200 | search_result | topics=api,auth,mcp
- https://developer.usepylon.com | HTTP 0 | derived_guess | topics=none
- https://developers.usepylon.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
The documentation clearly details a REST API using Bearer token authentication and an official MCP server that uses OAuth. The API covers a moderate breadth of support-related resources, and rate limits are explicitly stated. Access appears to be self-serve via a free trial.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - API tokens can be generated in the Pylon dashboard. A free trial is available to get started, though production use may require a paid plan.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://usepylon.com
- https://docs.usepylon.com/pylon-docs/developer/api/authentication
- https://docs.usepylon.com/pylon-docs/developer/api/api-reference/me
- https://docs.usepylon.com/pylon-docs/integrations/pylon-mcp

## Generated record
```json
{
  "app": "Pylon",
  "category": "Support",
  "one_liner": "Pylon is an AI-native B2B support platform offering a REST API and an official MCP server for omnichannel workflows.",
  "auth_methods": [
    "Bearer Token",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "API tokens can be generated in the Pylon dashboard. A free trial is available to get started, though production use may require a paid plan."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://usepylon.com",
    "https://docs.usepylon.com/pylon-docs/developer/api/authentication",
    "https://docs.usepylon.com/pylon-docs/developer/api/api-reference/me",
    "https://docs.usepylon.com/pylon-docs/integrations/pylon-mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "pylon",
  "primary_docs_url": "https://usepylon.com",
  "rate_limit_note": "60 requests per minute as documented on the /me endpoint.",
  "last_verified": "2026-07-10"
}
```
