# Gorgias - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Gorgias official API authentication developer documentation", "Gorgias API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://gorgias.com | HTTP 200 | hint | topics=api,access
- https://docs.gorgias.com/en-US/rest-api-208286 | HTTP 200 | search_result | topics=api,auth,access
- https://developers.gorgias.com/docs/create-a-ticket-using-api | HTTP 200 | search_result | topics=api,auth,access
- https://updates.gorgias.com/publications/oauth2-authentication-for-http-integrations | HTTP 200 | search_result | topics=api,auth
- https://developer.gorgias.com | HTTP 200 | derived_guess | topics=none
- https://developers.gorgias.com | HTTP 200 | derived_guess | topics=api,access

## Model reasoning
Gorgias provides comprehensive REST API documentation with self-serve API keys via Basic Auth for private apps, and OAuth2 for public apps. An official MCP server is also available and documented on their main help center.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - API keys can be generated directly from the helpdesk settings for private apps. Public apps require developer portal registration and review.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://docs.gorgias.com/en-US/rest-api-208286
- https://developers.gorgias.com/docs/create-a-ticket-using-api
- https://docs.gorgias.com/en-US/connect-your-ai-assistant-to-the-gorgias-mcp-6310546

## Generated record
```json
{
  "app": "Gorgias",
  "category": "Support",
  "one_liner": "Gorgias provides a REST API and an official MCP server for managing e-commerce helpdesk tickets and customer data.",
  "auth_methods": [
    "Basic Auth",
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "API keys can be generated directly from the helpdesk settings for private apps. Public apps require developer portal registration and review."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.gorgias.com/en-US/rest-api-208286",
    "https://developers.gorgias.com/docs/create-a-ticket-using-api",
    "https://docs.gorgias.com/en-US/connect-your-ai-assistant-to-the-gorgias-mcp-6310546"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "gorgias",
  "primary_docs_url": "https://docs.gorgias.com/en-US/rest-api-208286",
  "rate_limit_note": "Not explicitly detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Gorgias",
  "category": "Support",
  "one_liner": "Gorgias provides a REST API and an official MCP server for managing e-commerce helpdesk tickets and customer data.",
  "auth_methods": [
    "Basic Auth",
    "API Key",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Gorgias provides a seven-day trial; continued production API and MCP use requires a paid plan."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Moderate",
  "main_blocker": "Production credentials require an existing paid customer account.",
  "recommended_next_action": "Partner-Gated",
  "evidence_urls": [
    "https://developers.gorgias.com/reference/authentication",
    "https://developers.gorgias.com/docs/access-tokens-api-keys",
    "https://www.gorgias.com/pricing/choose-your-plan",
    "https://docs.gorgias.com/en-US/connect-your-ai-assistant-to-the-gorgias-mcp-6310546"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "gorgias",
  "primary_docs_url": "https://developers.gorgias.com/reference/authentication",
  "rate_limit_note": "Not explicitly detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
