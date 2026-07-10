# Magento (Adobe Commerce) - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Magento (Adobe Commerce) official API authentication developer documentation", "Magento (Adobe Commerce) API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developer.adobe.com/commerce | HTTP 200 | hint | topics=api,access
- https://developer.adobe.com/commerce/webapi/get-started/authentication/gs-authentication-oauth/ | HTTP 404 | search_result | topics=none
- https://developer.adobe.com/commerce/webapi/get-started/authentication/ | HTTP 200 | search_result | topics=api,auth
- https://developer.adobe.com/commerce/webapi/get-started/authentication/gs-authentication-session/ | HTTP 404 | search_result | topics=none
- https://developer.adobe.com | HTTP 200 | derived_guess | topics=api
- https://developers.adobe.com | HTTP 200 | derived_guess | topics=api

## Model reasoning
The official documentation details REST and GraphQL APIs with token-based and OAuth authentication. Multiple community MCP servers exist for Magento/Adobe Commerce. Because Magento Open Source is freely available to install and test, developers can self-serve API credentials without needing an enterprise Adobe contract.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Magento Open Source can be downloaded and installed freely to generate API credentials, though Adobe Commerce cloud hosting requires a paid contract.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://developer.adobe.com/commerce/webapi/get-started/authentication/
- https://developer.adobe.com/commerce
- https://lobehub.com/mcp/codexpect-adobe-commerce-mcp
- https://conare.ai/marketplace/mcp/magento-mcp

## Generated record
```json
{
  "app": "Magento (Adobe Commerce)",
  "category": "Commerce",
  "one_liner": "Adobe Commerce and Magento Open Source provide comprehensive REST and GraphQL APIs for headless commerce integrations.",
  "auth_methods": [
    "Bearer Token",
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Magento Open Source can be downloaded and installed freely to generate API credentials, though Adobe Commerce cloud hosting requires a paid contract."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developer.adobe.com/commerce/webapi/get-started/authentication/",
    "https://developer.adobe.com/commerce",
    "https://lobehub.com/mcp/codexpect-adobe-commerce-mcp",
    "https://conare.ai/marketplace/mcp/magento-mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "magento",
  "primary_docs_url": "https://developer.adobe.com/commerce/webapi/get-started/authentication/",
  "rate_limit_note": "Rate limits depend on the specific hosting environment and infrastructure configuration of the Magento instance.",
  "last_verified": "2026-07-10"
}
```
