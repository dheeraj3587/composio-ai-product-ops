# higgsfield - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["higgsfield official API authentication developer documentation", "higgsfield API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://higgsfield.ai/cli | HTTP 200 | hint | topics=api,auth,access,mcp
- https://mindcloud.co/docs/universal/rest/higgsfield-ai/latest/introduction/authentication | HTTP 200 | search_result | topics=api,auth,access
- https://www.scribd.com/document/992401211/Higgsfield-API-Documentation | HTTP 200 | search_result | topics=api
- https://mindcloud.co/docs/universal/rest/higgsfield-ai/latest | HTTP 200 | search_result | topics=api,auth,access
- https://developer.higgsfield.ai | HTTP 0 | derived_guess | topics=none
- https://developers.higgsfield.ai | HTTP 0 | derived_guess | topics=none

## Model reasoning
Official documentation confirms a self-serve access model with an official MCP server available at mcp.higgsfield.ai/mcp. Authentication is handled via a browser-based login flow for the MCP/CLI, and API keys for the SDKs.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up and authenticate via the CLI or MCP using a browser-based login, or generate API keys for SDK use.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://higgsfield.ai/mcp
- https://higgsfield.ai/cli
- https://github.com/geopopos/higgsfield_ai_mcp

## Generated record
```json
{
  "app": "higgsfield",
  "category": "AI/Meeting-tools",
  "one_liner": "Higgsfield provides an AI video and image generation platform with an official MCP server and REST API.",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up and authenticate via the CLI or MCP using a browser-based login, or generate API keys for SDK use."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://higgsfield.ai/mcp",
    "https://higgsfield.ai/cli",
    "https://github.com/geopopos/higgsfield_ai_mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "higgsfield",
  "primary_docs_url": "https://higgsfield.ai/cli",
  "rate_limit_note": "Not explicitly detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "main_blocker": "Newer product; plausibly invite/beta-gated (low confidence either way)."
}
```
