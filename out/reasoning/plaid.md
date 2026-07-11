# Plaid - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Plaid official API authentication developer documentation", "Plaid API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://plaid.com/docs | HTTP 200 | hint | topics=api,auth,access,mcp
- https://plaid.com/docs/api/products/auth/ | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://plaid.com/products/auth/ | HTTP 200 | search_result | topics=api,auth,access
- https://plaid.com/plaid-exchange/docs/authentication/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.plaid.com | HTTP 0 | derived_guess | topics=none
- https://developers.plaid.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
Plaid offers a comprehensive REST API authenticated via client_id and secret (API Key), with OAuth2 used for Plaid Exchange. They have officially released MCP servers for dashboard diagnostics and local development. While sandbox testing is accessible, production access is gated behind an approval process.

## Key decisions
- buildability: **Moderate**
- access_model: **Gated** - Sandbox access is self-serve, but production access requires passing validation and a formal approval process from Plaid.
- recommended_next_action: **Needs Outreach**
- confidence: **0.9**

## Evidence URLs
- https://plaid.com/docs/api/products/auth/
- https://plaid.com/plaid-exchange/docs/authentication/
- https://plaid.com/docs/resources/mcp/

## Generated record
```json
{
  "app": "Plaid",
  "category": "Fintech",
  "one_liner": "Plaid provides APIs for connecting financial accounts, verifying identity, and moving money, along with official MCP...",
  "auth_methods": [
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Sandbox access is self-serve, but production access requires passing validation and a formal approval process from Plaid."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Moderate",
  "main_blocker": "Production access requires passing endpoint validation and requesting approval from Plaid.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://plaid.com/docs/api/products/auth/",
    "https://plaid.com/plaid-exchange/docs/authentication/",
    "https://plaid.com/docs/resources/mcp/"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "plaid",
  "primary_docs_url": "https://plaid.com/docs/api/products/auth/",
  "rate_limit_note": "Not explicitly detailed in the provided evidence.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Self-Serve",
  "recommended_next_action": "Build Now",
  "main_blocker": "Free/instant sandbox is self-serve, but PRODUCTION access requires a Plaid approval/review process.",
  "note": "Capture as 'self-serve trial, gated production', not a flat label."
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current handcheck fold; this supersedes earlier key decisions._

```json
{
  "app": "Plaid",
  "category": "Fintech",
  "one_liner": "Plaid provides APIs for connecting financial accounts, verifying identity, and moving money, along with official MCP...",
  "auth_methods": [
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Sandbox access is self-serve, but production access requires passing validation and a formal approval process from Plaid."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Moderate",
  "main_blocker": "Production access requires passing endpoint validation and requesting approval from Plaid.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://plaid.com/docs/api/",
    "https://plaid.com/docs/link/oauth/",
    "https://plaid.com/docs/resources/mcp/"
  ],
  "confidence": 0.9,
  "verification_status": "Hand-Checked",
  "slug": "plaid",
  "primary_docs_url": "https://plaid.com/docs/api/",
  "rate_limit_note": "Not explicitly detailed in the provided evidence.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
