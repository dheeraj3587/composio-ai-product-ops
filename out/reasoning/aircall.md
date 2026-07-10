# Aircall - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Aircall official API authentication developer documentation", "Aircall API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://aircall.io | HTTP 200 | hint | topics=api,access
- https://developer.aircall.io/tutorials/how-aircall-oauth-flow-works/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.aircall.io/tutorials/basic-authentication/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.aircall.io/api-references/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.aircall.io | HTTP 200 | derived_guess | topics=api,auth,access
- https://developers.aircall.io | HTTP 0 | derived_guess | topics=none

## Model reasoning
The documentation clearly outlines Basic Auth for single-tenant use (self-serve) and OAuth for multi-tenant apps (gated). The REST API is extensive, covering calls, users, teams, and conversation intelligence. Multiple community MCP servers exist, explicitly marked as unofficial.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Basic Auth credentials (API ID and Token) can be generated directly in the Aircall dashboard. OAuth for multi-tenant apps requires contacting the marketplace team for approval.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developer.aircall.io/tutorials/basic-authentication/
- https://developer.aircall.io/tutorials/how-aircall-oauth-flow-works/
- https://developer.aircall.io/api-references/
- https://lobehub.com/mcp/themobilefirstco-aircall-mcp-server

## Generated record
```json
{
  "app": "Aircall",
  "category": "Comms",
  "one_liner": "Aircall provides a comprehensive REST API for managing calls, contacts, and users, supported by community MCP servers.",
  "auth_methods": [
    "Basic Auth",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Basic Auth credentials (API ID and Token) can be generated directly in the Aircall dashboard. OAuth for multi-tenant apps requires contacting the marketplace team for approval."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None for single-tenant integrations using Basic Auth. Multi-tenant OAuth applications require vendor outreach and approval.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developer.aircall.io/tutorials/basic-authentication/",
    "https://developer.aircall.io/tutorials/how-aircall-oauth-flow-works/",
    "https://developer.aircall.io/api-references/",
    "https://lobehub.com/mcp/themobilefirstco-aircall-mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "aircall",
  "primary_docs_url": "https://developer.aircall.io/tutorials/how-aircall-oauth-flow-works/",
  "rate_limit_note": "Rate limiting is listed in the API references menu, though specific limits are not detailed in the provided text.",
  "last_verified": "2026-07-10"
}
```
