# QuickBooks - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["QuickBooks official API authentication developer documentation", "QuickBooks API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developer.intuit.com | HTTP 200 | hint | topics=none
- https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/faq | HTTP 200 | search_result | topics=auth
- https://developer.intuit.com/app/developer/qbpayments/docs/develop/authentication-and-authorization/oauth-2.0 | HTTP 200 | search_result | topics=auth
- https://developer.intuit.com/app/developer/qbo/docs/develop/sdks-and-samples-collections/php/authorization | HTTP 200 | search_result | topics=auth
- https://developers.intuit.com | HTTP 200 | derived_guess | topics=none
- https://docs.intuit.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
Search results confirm QuickBooks uses OAuth 2.0 for API authentication and developers can self-serve credentials via the Intuit Developer Portal. An official MCP server is available under the Intuit GitHub organization.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can create an app on the Intuit Developer Portal to get credentials. Publicly listing an app requires a publishing review.
- recommended_next_action: **Build Now**
- confidence: **0.85**

## Evidence URLs
- https://developer.intuit.com/app/developer/qbpayments/docs/develop/authentication-and-authorization/oauth-2.0
- https://github.com/intuit/quickbooks-online-mcp-server

## Generated record
```json
{
  "app": "QuickBooks",
  "category": "Fintech",
  "one_liner": "QuickBooks provides a REST API and an official MCP server for integrating with its accounting and financial software.",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can create an app on the Intuit Developer Portal to get credentials. Publicly listing an app requires a publishing review."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developer.intuit.com/app/developer/qbpayments/docs/develop/authentication-and-authorization/oauth-2.0",
    "https://github.com/intuit/quickbooks-online-mcp-server"
  ],
  "confidence": 0.85,
  "verification_status": "Auto",
  "slug": "quickbooks",
  "primary_docs_url": "https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/faq",
  "rate_limit_note": "Standard API rate limits apply; specific limits are not detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
