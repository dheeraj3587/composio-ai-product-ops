# BigCommerce - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["BigCommerce official API authentication developer documentation", "BigCommerce API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developer.bigcommerce.com | HTTP 200 | hint | topics=api,auth,access
- https://docs.bigcommerce.com/developer/api-reference/rest/b2b/management/authentication | HTTP 200 | search_result | topics=api,auth,mcp
- https://docs.bigcommerce.com/developer/docs/b2b-edition/getting-started/authentication | HTTP 200 | search_result | topics=api,auth,access
- https://developer.bigcommerce.com/b2b-edition/apis/rest-management/authentication?ajs_aid=8dd01c7b-0541-4a4c-8075-ed18887a7547 | HTTP 200 | search_result | topics=api,auth,mcp
- https://developers.bigcommerce.com | HTTP 0 | derived_guess | topics=none
- https://docs.bigcommerce.com | HTTP 200 | derived_guess | topics=api,auth,access

## Model reasoning
BigCommerce offers extensive REST and GraphQL APIs with self-serve sandbox access. They also officially support a Storefront MCP server, making it highly buildable.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can sign up for a free sandbox store to generate API credentials and build integrations.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://docs.bigcommerce.com
- https://docs.bigcommerce.com/developer/api-reference/mcp/overview
- https://www.bigcommerce.com/blog/storefront-mcp/

## Generated record
```json
{
  "app": "BigCommerce",
  "category": "Commerce",
  "one_liner": "BigCommerce provides comprehensive REST and GraphQL APIs, along with an official MCP server, for e-commerce management.",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can sign up for a free sandbox store to generate API credentials and build integrations."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.bigcommerce.com",
    "https://docs.bigcommerce.com/developer/api-reference/mcp/overview",
    "https://www.bigcommerce.com/blog/storefront-mcp/"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "bigcommerce",
  "primary_docs_url": "https://docs.bigcommerce.com/developer/docs/b2b-edition/getting-started/authentication",
  "rate_limit_note": "Rate limits apply and are documented in the API Fundamentals section.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by official-doc adjudication of independent browser verification; this supersedes earlier key decisions._

```json
{
  "app": "BigCommerce",
  "category": "Commerce",
  "one_liner": "BigCommerce provides comprehensive REST and GraphQL APIs, along with an official MCP server, for e-commerce management.",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "A sandbox can be created for testing, but production API credentials require an active BigCommerce store or partner/customer relationship."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Moderate",
  "main_blocker": "Production credentials require an active paid store or an existing BigCommerce partner/customer relationship.",
  "recommended_next_action": "Partner-Gated",
  "evidence_urls": [
    "https://docs.bigcommerce.com/developer/docs/overview/quick-start",
    "https://docs.bigcommerce.com/developer/docs/overview/api-fundamentals/api-accounts",
    "https://docs.bigcommerce.com",
    "https://docs.bigcommerce.com/developer/api-reference/mcp/overview",
    "https://www.bigcommerce.com/blog/storefront-mcp/"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "bigcommerce",
  "primary_docs_url": "https://docs.bigcommerce.com/developer/docs/overview/quick-start",
  "rate_limit_note": "Rate limits apply and are documented in the API Fundamentals section.",
  "last_verified": "2026-07-11"
}
```
<!-- final-state:end -->
