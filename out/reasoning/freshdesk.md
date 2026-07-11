# Freshdesk - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Freshdesk official API authentication developer documentation", "Freshdesk API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://freshdesk.com | HTTP 200 | hint | topics=access
- https://developers.freshdesk.com/api/ | HTTP 200 | search_result | topics=api,auth,access
- https://support.freshdesk.com/support/solutions/articles/215517-how-to-find-your-api-key | HTTP 200 | search_result | topics=api,auth,access
- https://environdec.freshdesk.com/support/solutions/articles/103000332352-where-can-i-find-the-api-documentation- | HTTP 404 | search_result | topics=none
- https://developer.freshdesk.com | HTTP 200 | derived_guess | topics=api,access
- https://developers.freshdesk.com | HTTP 200 | derived_guess | topics=api,access

## Model reasoning
Freshdesk offers a well-documented REST API accessible via an API key, which can be obtained by signing up for a free trial. An official MCP server is also available in Early Access (EAP), making integration straightforward.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up for a free trial and access their API key directly from their profile settings.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developers.freshdesk.com/api/
- https://support.freshdesk.com/support/solutions/articles/215517-how-to-find-your-api-key
- https://support.freshdesk.com/support/solutions/articles/50000012670-model-context-protocol-mcp-integration-in-freshdesk-eap-

## Generated record
```json
{
  "app": "Freshdesk",
  "category": "Support",
  "one_liner": "Freshdesk provides a comprehensive REST API and an official MCP server for managing customer support tickets and...",
  "auth_methods": [
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up for a free trial and access their API key directly from their profile settings."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developers.freshdesk.com/api/",
    "https://support.freshdesk.com/support/solutions/articles/215517-how-to-find-your-api-key",
    "https://support.freshdesk.com/support/solutions/articles/50000012670-model-context-protocol-mcp-integration-in-freshdesk-eap-"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "freshdesk",
  "primary_docs_url": "https://developers.freshdesk.com/api/",
  "rate_limit_note": "Rate limits are enforced based on the number of API calls per hour, varying by subscription plan.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Freshdesk",
  "category": "Support",
  "one_liner": "Freshdesk provides a comprehensive REST API and an official MCP server for managing customer support tickets and...",
  "auth_methods": [
    "API Key",
    "Basic Auth"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Freshdesk Free currently permits zero API calls; production API use requires a paid Growth, Pro, or Enterprise account."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Moderate",
  "main_blocker": "Production API credentials require an existing paid Freshdesk customer account.",
  "recommended_next_action": "Partner-Gated",
  "evidence_urls": [
    "https://developers.freshdesk.com/api/",
    "https://partnersupport.freshworks.com/support/solutions/articles/225439-what-are-the-rate-limits-for-the-api-calls-to-freshdesk-",
    "https://support.freshdesk.com/support/solutions/articles/50000012670-model-context-protocol-mcp-integration-in-freshdesk-eap-"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "freshdesk",
  "primary_docs_url": "https://developers.freshdesk.com/api/",
  "rate_limit_note": "Rate limits are enforced based on the number of API calls per hour, varying by subscription plan.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
