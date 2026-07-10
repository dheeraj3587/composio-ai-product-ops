# Shopify - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Shopify official API authentication developer documentation", "Shopify API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://shopify.dev | HTTP 200 | hint | topics=api,access
- https://shopify.dev/docs/api/usage/authentication | HTTP 200 | search_result | topics=api,auth,access
- https://shopify.dev/docs/storefronts/headless/building-with-the-storefront-api/getting-started | HTTP 200 | search_result | topics=api,auth,access
- https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developer.shopify.dev | HTTP 0 | derived_guess | topics=none
- https://developers.shopify.dev | HTTP 0 | derived_guess | topics=none

## Model reasoning
Shopify offers extensive, self-serve developer documentation. They provide modern GraphQL APIs for Admin and Storefront, authenticated via OAuth2 and access tokens. They also officially support MCP with the Storefront MCP and Shopify Dev MCP server.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can create a Partner account, scaffold apps, and generate client credentials or Storefront access tokens directly from the Dev Dashboard.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://shopify.dev/docs/api/usage/authentication
- https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets
- https://shopify.dev/docs/apps/build/storefront-mcp
- https://tenten.co/shopifymcp/docs/mcp-resources/official-mcp-servers

## Generated record
```json
{
  "app": "Shopify",
  "category": "Commerce",
  "one_liner": "Shopify provides a comprehensive commerce platform with GraphQL APIs and official MCP support for AI integrations.",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can create a Partner account, scaffold apps, and generate client credentials or Storefront access tokens directly from the Dev Dashboard."
  },
  "api_type": "GraphQL",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://shopify.dev/docs/api/usage/authentication",
    "https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets",
    "https://shopify.dev/docs/apps/build/storefront-mcp",
    "https://tenten.co/shopifymcp/docs/mcp-resources/official-mcp-servers"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "shopify",
  "primary_docs_url": "https://shopify.dev/docs/api/usage/authentication",
  "rate_limit_note": "Apps can have a maximum of 100 active storefront access tokens per shop.",
  "last_verified": "2026-07-10"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Shopify",
  "category": "Commerce",
  "one_liner": "Shopify provides a comprehensive commerce platform with GraphQL APIs and official MCP support for AI integrations.",
  "auth_methods": [
    "OAuth2",
    "Bearer Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can create a Partner account, scaffold apps, and generate client credentials or Storefront access tokens directly from the Dev Dashboard."
  },
  "api_type": "GraphQL",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://shopify.dev/docs/api/usage/authentication",
    "https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/authorization-code-grant",
    "https://shopify.dev/docs/apps/launch/distribution",
    "https://shopify.dev/docs/apps/build/storefront-mcp"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "shopify",
  "primary_docs_url": "https://shopify.dev/docs/api/usage/authentication",
  "rate_limit_note": "Apps can have a maximum of 100 active storefront access tokens per shop.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
