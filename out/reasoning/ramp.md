# Ramp - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Ramp official API authentication developer documentation", "Ramp API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://docs.ramp.com | HTTP 200 | hint | topics=api
- https://docs.ramp.com/developer-api/v1/authorization | HTTP 200 | search_result | topics=api,auth
- https://support.ramp.com/accessing-the-developer-api/ | HTTP 200 | search_result | topics=api,auth,access
- https://docs.ramp.com/ | HTTP 200 | search_result | topics=api
- https://developer.ramp.com | HTTP 200 | derived_guess | topics=api,auth,access,mcp
- https://developers.ramp.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
Ramp provides a Developer API and an official MCP server. Authentication is handled via OAuth2 Client Credentials. However, access is gated because generating credentials requires Admin access to an active Ramp business account, and sandbox environments must be requested through an account manager.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Requires Admin access to an existing Ramp business account. Sandbox access is not self-serve and requires contacting an account manager.
- recommended_next_action: **Needs Outreach**
- confidence: **0.9**

## Evidence URLs
- https://support.ramp.com/accessing-the-developer-api/
- https://support.ramp.com/ramp-mcp/
- https://github.com/ramp-public/ramp_mcp

## Generated record
```json
{
  "app": "Ramp",
  "category": "Fintech",
  "one_liner": "Ramp provides a Developer API and an official MCP server for programmatic access to corporate cards and spend...",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Requires Admin access to an existing Ramp business account. Sandbox access is not self-serve and requires contacting an account manager."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Hard",
  "main_blocker": "API access requires an existing Ramp business account with Admin privileges, and sandbox access is manually provisioned by an account manager.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://support.ramp.com/accessing-the-developer-api/",
    "https://support.ramp.com/ramp-mcp/",
    "https://github.com/ramp-public/ramp_mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "ramp",
  "primary_docs_url": "https://support.ramp.com/accessing-the-developer-api/",
  "rate_limit_note": "Not explicitly detailed in the provided text, though MCP docs mention ETL operation limits.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "API access is tied to being a Ramp business customer; not self-serve for a solo developer testing."
}
```
