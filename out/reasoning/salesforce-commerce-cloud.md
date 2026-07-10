# Salesforce Commerce Cloud - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Salesforce Commerce Cloud official API authentication developer documentation", "Salesforce Commerce Cloud API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developer.salesforce.com/docs/commerce | HTTP 403 | hint | topics=none
- https://developer.salesforce.com/docs/commerce/account-manager/guide/account-manager-get-started.html | HTTP 403 | derived_guess | topics=none
- https://developer.salesforce.com/docs/commerce/b2c-commerce/references/b2c-commerce-ocapi/oauth.html | HTTP 403 | search_result | topics=none
- https://developer.salesforce.com/docs/commerce/commerce-api/guide/authorization-for-admin-apis.html | HTTP 403 | search_result | topics=none
- https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_oauth_and_connected_apps.htm | HTTP 403 | search_result | topics=none
- https://developer.salesforce.com/docs/commerce/commerce-api/guide/authorization.html | HTTP 200 | browser_verified_summary | topics=api,auth,access

## Model reasoning
The fetched documentation confirms OAuth 2.1 is used for B2C Commerce APIs and requires an API client in Account Manager, which aligns with the preseed hypothesis that it is a gated enterprise platform.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Requires an enterprise Salesforce Commerce Cloud account and Account Manager access to create API clients.
- recommended_next_action: **Partner-Gated**
- confidence: **0.8**

## Evidence URLs
- https://developer.salesforce.com/docs/commerce/commerce-api/guide/authorization.html

## Generated record
```json
{
  "app": "Salesforce Commerce Cloud",
  "category": "Commerce",
  "one_liner": "Salesforce Commerce Cloud provides REST APIs for building headless commerce experiences.",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Requires an enterprise Salesforce Commerce Cloud account and Account Manager access to create API clients."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "None",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "Requires an existing customer relationship or partner account; enterprise commerce platform sold via sales with no self-serve signup.",
  "recommended_next_action": "Partner-Gated",
  "evidence_urls": [
    "https://developer.salesforce.com/docs/commerce/commerce-api/guide/authorization.html"
  ],
  "confidence": 0.8,
  "verification_status": "Auto",
  "slug": "salesforce-commerce-cloud",
  "primary_docs_url": "https://developer.salesforce.com/docs/commerce/commerce-api/guide/authorization.html",
  "rate_limit_note": "Not explicitly detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "Enterprise commerce platform sold via sales; no self-serve signup (distinct from core Salesforce CRM's free dev org)."
}
```
