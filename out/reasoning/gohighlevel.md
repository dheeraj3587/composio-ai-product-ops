# GoHighLevel - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["GoHighLevel official API authentication developer documentation", "GoHighLevel API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://highlevel.stoplight.io | HTTP 200 | hint | topics=none
- https://marketplace.gohighlevel.com/docs/oauth/Authorization/index.html | HTTP 200 | search_result | topics=auth
- https://marketplace.gohighlevel.com/docs/oauth/ExternalAuthentication/index.html | HTTP 200 | search_result | topics=api,auth,mcp
- https://marketplace.gohighlevel.com/docs/Authorization/DeveloperGlossary/ | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developer.stoplight.io | HTTP 200 | derived_guess | topics=none
- https://developers.stoplight.io | HTTP 200 | derived_guess | topics=none

## Model reasoning
GoHighLevel offers extensive REST APIs and recently launched an official LeadConnector MCP server. Authentication supports OAuth 2.0 for marketplace apps and API keys for self-serve private integrations.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Private integrations and API keys are self-serve; public Marketplace apps require a review process.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://marketplace.gohighlevel.com/docs/Authorization/DeveloperGlossary/
- https://marketplace.gohighlevel.com/docs/oauth/ExternalAuthentication/index.html
- https://help.gohighlevel.com/support/solutions/articles/155000005741-how-to-use-the-highlevel-mcp-server
- https://www.gohighlevel.com/post/introducing-the-mcp-server
- https://marketplace.gohighlevel.com/docs/2021-07-28/other/mcp/index.html

## Generated record
```json
{
  "app": "GoHighLevel",
  "category": "Ads/Marketing",
  "one_liner": "GoHighLevel provides a comprehensive REST API and an official MCP server for CRM, marketing, and automation workflows.",
  "auth_methods": [
    "OAuth2",
    "API Key",
    "Basic Auth"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Private integrations and API keys are self-serve; public Marketplace apps require a review process."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None for private integrations. Public marketplace distribution requires app review.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://marketplace.gohighlevel.com/docs/Authorization/DeveloperGlossary/",
    "https://marketplace.gohighlevel.com/docs/oauth/ExternalAuthentication/index.html",
    "https://help.gohighlevel.com/support/solutions/articles/155000005741-how-to-use-the-highlevel-mcp-server",
    "https://www.gohighlevel.com/post/introducing-the-mcp-server",
    "https://marketplace.gohighlevel.com/docs/2021-07-28/other/mcp/index.html"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "gohighlevel",
  "primary_docs_url": "https://marketplace.gohighlevel.com/docs/Authorization/DeveloperGlossary/",
  "rate_limit_note": "Not explicitly detailed in the provided evidence.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Self-Serve",
  "recommended_next_action": "Build Now",
  "main_blocker": "Sub-account API keys are self-serve; public marketplace app listing needs review (public-vs-private app distinction)."
}
```
