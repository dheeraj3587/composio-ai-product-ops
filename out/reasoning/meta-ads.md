# Meta Ads - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Meta Ads official API authentication developer documentation", "Meta Ads API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developers.facebook.com/docs/marketing-apis | HTTP 200 | hint | topics=api,auth,access
- https://developers.facebook.com/docs/marketing-api/get-started/authorization/ | HTTP 200 | search_result | topics=api,auth,access
- https://developers.facebook.com/docs/marketing-api/get-started/authentication/ | HTTP 200 | search_result | topics=api,auth,access
- https://developers.facebook.com/docs/marketing-api/get-started/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.facebook.com | HTTP 200 | derived_guess | topics=api,auth,access
- https://developers.facebook.com | HTTP 200 | derived_guess | topics=api,auth,access

## Model reasoning
The REST API requires app review and business verification for production access. While a third-party blog mentions an official MCP, there is no first-party documentation in the allowed URLs to confirm it, so existing_mcp is set to Community based on the pipeboard-co repository, which itself requires gated API credentials.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Production access to the Marketing API requires app review and business verification. Community MCPs exist but require these same gated credentials.
- recommended_next_action: **Needs Outreach**
- confidence: **0.9**

## Evidence URLs
- https://developers.facebook.com/docs/marketing-api/get-started/authorization/
- https://www.augmentcode.com/mcp/meta-ads-mcp

## Generated record
```json
{
  "app": "Meta Ads",
  "category": "Ads/Marketing",
  "one_liner": "Meta Ads provides a Marketing API for managing campaigns, though production access requires app review and business...",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Production access to the Marketing API requires app review and business verification. Community MCPs exist but require these same gated credentials."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "Yes",
  "buildability": "Hard",
  "main_blocker": "Marketing API is behind Meta app review and business verification.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developers.facebook.com/docs/marketing-api/get-started/authorization/",
    "https://www.augmentcode.com/mcp/meta-ads-mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "meta-ads",
  "primary_docs_url": "https://developers.facebook.com/docs/marketing-api/get-started/authorization/",
  "rate_limit_note": "Rate limiting is applied dynamically based on the app and account tier.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "Marketing API is behind Meta app review + business verification."
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current human handcheck correction; this supersedes earlier key decisions._

```json
{
  "app": "Meta Ads",
  "category": "Ads/Marketing",
  "one_liner": "Meta Ads provides a Marketing API for managing campaigns, though production access requires app review and business...",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Production access to the Marketing API requires app review and business verification. Community MCPs exist but require these same gated credentials."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "Yes",
  "buildability": "Hard",
  "main_blocker": "Marketing API is behind Meta app review and business verification.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developers.facebook.com/documentation/ads-commerce/marketing-api/get-started/authorization",
    "https://www.augmentcode.com/mcp/meta-ads-mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Hand-Checked",
  "slug": "meta-ads",
  "primary_docs_url": "https://developers.facebook.com/documentation/ads-commerce/marketing-api/get-started/authorization",
  "rate_limit_note": "Rate limiting is applied dynamically based on the app and account tier.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
