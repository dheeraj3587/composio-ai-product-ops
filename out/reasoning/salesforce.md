# Salesforce - synthesis reasoning
_generated 2026-07-11 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Salesforce official API authentication developer documentation", "Salesforce API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://salesforce.com | HTTP 200 | hint | topics=access
- https://developer.salesforce.com/docs/marketing/pardot/guide/authentication.html | HTTP 403 | search_result | topics=none
- https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/authentication.htm | HTTP 403 | search_result | topics=none
- https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/authentication.htm | HTTP 403 | search_result | topics=none
- https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_using_oauth.html | HTTP 200 | browser_verified_summary | topics=api,auth
- https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest_compatible_editions.htm | HTTP 200 | browser_verified_summary | topics=api,access

## Model reasoning
Salesforce provides a REST API accessible via OAuth2. Developer Edition orgs offer self-serve access. Official MCP servers are available.

## Key decisions
- buildability: **Moderate**
- access_model: **Self-Serve** - Developer Edition orgs are free and have API access enabled by default.
- recommended_next_action: **Build Now**
- confidence: **0.8**

## Evidence URLs
- https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_using_oauth.html
- https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest_compatible_editions.htm
- https://github.com/salesforcecli/mcp

## Generated record
```json
{
  "app": "Salesforce",
  "category": "CRM",
  "one_liner": "Salesforce is a leading CRM platform offering extensive REST APIs and official MCP servers for AI agents.",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developer Edition orgs are free and have API access enabled by default."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Moderate",
  "main_blocker": "Requires setting up a connected app and OAuth flow.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_using_oauth.html",
    "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest_compatible_editions.htm",
    "https://github.com/salesforcecli/mcp"
  ],
  "confidence": 0.8,
  "verification_status": "Auto",
  "slug": "salesforce",
  "primary_docs_url": "https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_using_oauth.html",
  "rate_limit_note": "API limits are typically based on the Salesforce edition and user licenses.",
  "last_verified": "2026-07-11"
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Salesforce",
  "category": "CRM",
  "one_liner": "Salesforce is a leading CRM platform offering extensive REST APIs and official MCP servers for AI agents.",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Free Developer Edition supports development and testing; production API access requires a supported paid edition or API add-on."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Hard",
  "main_blocker": "Production API access requires an existing customer on a supported paid edition or an API access add-on.",
  "recommended_next_action": "Partner-Gated",
  "evidence_urls": [
    "https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_using_oauth.html",
    "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest_compatible_editions.htm",
    "https://github.com/salesforcecli/mcp"
  ],
  "confidence": 0.8,
  "verification_status": "Hand-Checked",
  "slug": "salesforce",
  "primary_docs_url": "https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_using_oauth.html",
  "rate_limit_note": "API limits are typically based on the Salesforce edition and user licenses.",
  "last_verified": "2026-07-11"
}
```
<!-- final-state:end -->
