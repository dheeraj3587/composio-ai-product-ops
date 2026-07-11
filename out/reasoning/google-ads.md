# Google Ads - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Google Ads official API authentication developer documentation", "Google Ads API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developers.google.com/google-ads | HTTP 200 | hint | topics=api
- https://developers.google.com/google-ads/api/docs/oauth/overview | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developers.google.com/google-ads/api/docs/reach-forecasting/authentication | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developers.google.com/google-ads/api/docs/client-libs/dotnet/authentication | HTTP 200 | search_result | topics=api,auth
- https://developer.google.com | HTTP 200 | derived_guess | topics=api,auth,access
- https://developers.google.com | HTTP 200 | derived_guess | topics=api,auth,access

## Model reasoning
The documentation clearly states that OAuth 2.0 and a developer token are required. Production access is gated behind an application review process to obtain the necessary developer token access levels. An official MCP server is documented in the developer toolkit.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Production access requires an approved developer token and an application review to grant appropriate access levels.
- recommended_next_action: **Needs Outreach**
- confidence: **0.95**

## Evidence URLs
- https://developers.google.com/google-ads/api/docs/oauth/overview
- https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server

## Generated record
```json
{
  "app": "Google Ads",
  "category": "Ads/Marketing",
  "one_liner": "The Google Ads API allows developers to programmatically manage and automate Google Ads campaigns and accounts.",
  "auth_methods": [
    "OAuth2",
    "Other Token"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Production access requires an approved developer token and an application review to grant appropriate access levels."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Hard",
  "main_blocker": "Requires an application review and an approved developer token to access production environments.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developers.google.com/google-ads/api/docs/oauth/overview",
    "https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "google-ads",
  "primary_docs_url": "https://developers.google.com/google-ads/api/docs/oauth/overview",
  "rate_limit_note": "Operation limits are determined by the access level granted to the developer token (e.g., Basic Access vs. Standard Access).",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "Requires a developer token approval + OAuth; not instant self-serve."
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current handcheck fold; this supersedes earlier key decisions._

```json
{
  "app": "Google Ads",
  "category": "Ads/Marketing",
  "one_liner": "The Google Ads API allows developers to programmatically manage and automate Google Ads campaigns and accounts.",
  "auth_methods": [
    "OAuth2",
    "API Key",
    "Service Account"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Production access requires an approved developer token and an application review to grant appropriate access levels."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Hard",
  "main_blocker": "Requires an application review and an approved developer token to access production environments.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developers.google.com/google-ads/api/docs/oauth/overview",
    "https://developers.google.com/google-ads/api/docs/api-policy/developer-token",
    "https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Hand-Checked",
  "slug": "google-ads",
  "primary_docs_url": "https://developers.google.com/google-ads/api/docs/oauth/overview",
  "rate_limit_note": "Operation limits are determined by the access level granted to the developer token (e.g., Basic Access vs. Standard Access).",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
