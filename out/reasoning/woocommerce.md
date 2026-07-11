# WooCommerce - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["WooCommerce official API authentication developer documentation", "WooCommerce API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://woocommerce.com/document/woocommerce-rest-api | HTTP 200 | hint | topics=api,auth,access
- https://developer.woocommerce.com/docs/apis/rest-api/authentication/ | HTTP 200 | search_result | topics=api,auth
- https://developer.woocommerce.com/2015/08/07/api-settings-and-the-api-authentication-endpoint-in-2-4/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.woocommerce.com/docs/apis/rest-api/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.woocommerce.com | HTTP 200 | derived_guess | topics=api,access,mcp
- https://developers.woocommerce.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
WooCommerce offers a well-documented REST API using Consumer Key/Secret (API Key) authentication. It is self-serve as any store owner can generate keys. Additionally, official documentation confirms a native MCP integration is available in developer preview.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - API keys can be generated directly from the WooCommerce admin dashboard by any store owner.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://developer.woocommerce.com/docs/apis/rest-api/
- https://developer.woocommerce.com/docs/apis/rest-api/authentication/
- https://developer.woocommerce.com/docs/features/mcp/

## Generated record
```json
{
  "app": "WooCommerce",
  "category": "Commerce",
  "one_liner": "WooCommerce provides a comprehensive REST API and native MCP integration for managing store data and operations.",
  "auth_methods": [
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "API keys can be generated directly from the WooCommerce admin dashboard by any store owner."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developer.woocommerce.com/docs/apis/rest-api/",
    "https://developer.woocommerce.com/docs/apis/rest-api/authentication/",
    "https://developer.woocommerce.com/docs/features/mcp/"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "woocommerce",
  "primary_docs_url": "https://developer.woocommerce.com/2015/08/07/api-settings-and-the-api-authentication-endpoint-in-2-4/",
  "rate_limit_note": "Rate limits depend on the underlying WordPress hosting environment.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current handcheck fold; this supersedes earlier key decisions._

```json
{
  "app": "WooCommerce",
  "category": "Commerce",
  "one_liner": "WooCommerce provides a comprehensive REST API and native MCP integration for managing store data and operations.",
  "auth_methods": [
    "API Key",
    "Basic Auth"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "API keys can be generated directly from the WooCommerce admin dashboard by any store owner."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developer.woocommerce.com/docs/apis/rest-api/authentication/",
    "https://developer.woocommerce.com/docs/features/mcp/"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "woocommerce",
  "primary_docs_url": "https://developer.woocommerce.com/docs/apis/rest-api/authentication/",
  "rate_limit_note": "Rate limits depend on the underlying WordPress hosting environment.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
