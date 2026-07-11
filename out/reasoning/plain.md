# Plain - synthesis reasoning
_generated 2026-07-11 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Plain official API authentication developer documentation", "Plain API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://plain.com | HTTP 200 | hint | topics=api
- https://developers.kit.com/api-reference/authentication | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://docs.plainid.io/apidocs/authorization-apis | HTTP 200 | search_result | topics=api,auth,access
- https://docs.plainid.io/docs/developer-portal | HTTP 200 | search_result | topics=api,auth,access
- https://developer.plain.com | HTTP 0 | derived_guess | topics=none
- https://help.plain.com/article/api-quickstart | HTTP 200 | browser_verified_summary | topics=api,auth,access

## Model reasoning
Plain provides a GraphQL API authenticated via API Key and an official MCP server authenticated via OAuth2. Both are self-serve, allowing developers to generate credentials directly from their workspace settings.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can generate API keys from their workspace settings or use OAuth for the official MCP server.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://help.plain.com/article/api-quickstart
- https://help.plain.com/article/mcp-server

## Generated record
```json
{
  "app": "Plain",
  "category": "Support",
  "one_liner": "Plain is an AI-first support infrastructure platform that enables B2B teams to build custom support workflows.",
  "auth_methods": [
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can generate API keys from their workspace settings or use OAuth for the official MCP server."
  },
  "api_type": "GraphQL",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://help.plain.com/article/api-quickstart",
    "https://help.plain.com/article/mcp-server"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "plain",
  "primary_docs_url": "https://help.plain.com/article/api-quickstart",
  "rate_limit_note": "Rate limits exist but specific details are not provided in the quickstart.",
  "last_verified": "2026-07-11"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Plain",
  "category": "Support",
  "one_liner": "Plain is an AI-first support infrastructure platform that enables B2B teams to build custom support workflows.",
  "auth_methods": [
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Plain provides a seven-day trial; production API and MCP use requires a paid Foundation, Horizon, or Frontier workspace."
  },
  "api_type": "GraphQL",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Moderate",
  "main_blocker": "Production credentials require an existing paid customer account.",
  "recommended_next_action": "Partner-Gated",
  "evidence_urls": [
    "https://help.plain.com/article/api-quickstart",
    "https://help.plain.com/article/mcp-server",
    "https://www.plain.com/pricing"
  ],
  "confidence": 0.9,
  "verification_status": "Hand-Checked",
  "slug": "plain",
  "primary_docs_url": "https://help.plain.com/article/api-quickstart",
  "rate_limit_note": "Rate limits exist but specific details are not provided in the quickstart.",
  "last_verified": "2026-07-11"
}
```
<!-- final-state:end -->
