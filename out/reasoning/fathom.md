# Fathom - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Fathom official API authentication developer documentation", "Fathom API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://fathom.video | HTTP 200 | hint | topics=api,access,mcp
- https://developers.fathom.ai/sdks/oauth | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developers.fathom.ai/oauth | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developers.fathom.ai/sdks/authentication | HTTP 200 | search_result | topics=api,auth,mcp
- https://developer.fathom.video | HTTP 0 | derived_guess | topics=none
- https://developers.fathom.video | HTTP 0 | derived_guess | topics=none

## Model reasoning
Fathom provides comprehensive developer documentation for its REST API, SDKs, and an official MCP server. Authentication supports API Keys, Bearer Tokens, and OAuth2. Access appears to be self-serve, allowing developers to build integrations immediately.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can register an OAuth app or generate API keys directly from their account settings.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developers.fathom.ai/sdks/authentication
- https://developers.fathom.ai/oauth
- https://developers.fathom.ai/mcp-docs

## Generated record
```json
{
  "app": "Fathom",
  "category": "AI/Meeting-tools",
  "one_liner": "Fathom provides a REST API, SDKs, and an official MCP server to access AI meeting transcripts and summaries.",
  "auth_methods": [
    "API Key",
    "Bearer Token",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can register an OAuth app or generate API keys directly from their account settings."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.fathom.ai/sdks/authentication",
    "https://developers.fathom.ai/oauth",
    "https://developers.fathom.ai/mcp-docs"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "fathom",
  "primary_docs_url": "https://developers.fathom.ai/sdks/oauth",
  "rate_limit_note": "Rate limits are mentioned in the documentation for OAuth and API usage, but specific thresholds are not detailed in the provided text.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "api_type": "None",
  "main_blocker": "May be webhook/Zapier-only; unclear whether a fully public REST API exists — verify against docs, do not trust memory."
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Fathom",
  "category": "AI/Meeting-tools",
  "one_liner": "Fathom provides a REST API, SDKs, and an official MCP server to access AI meeting transcripts and summaries.",
  "auth_methods": [
    "API Key",
    "Bearer Token",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can register an OAuth app or generate API keys directly from their account settings."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.fathom.ai/sdks/authentication",
    "https://developers.fathom.ai/sdks/oauth",
    "https://developers.fathom.ai/mcp-docs"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "fathom",
  "primary_docs_url": "https://developers.fathom.ai/sdks/authentication",
  "rate_limit_note": "Rate limits are mentioned in the documentation for OAuth and API usage, but specific thresholds are not detailed in the provided text.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
