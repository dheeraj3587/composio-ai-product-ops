# Amazon Selling Partner - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Amazon Selling Partner official API authentication developer documentation", "Amazon Selling Partner API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developer-docs.amazon.com/sp-api | HTTP 200 | hint | topics=api,auth,access
- https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-gen-ai-selling-partner-api/integrating-sp-api.html | HTTP 200 | search_result | topics=api,auth,access
- https://developer-docs.amazon.com/sp-api/lang-ja_JP/docs/onboarding-step-8-call-the-sp-api-in-production | HTTP 200 | search_result | topics=api,auth,access
- https://developer.amazonservices.com/register | HTTP 200 | search_result | topics=api,auth,access
- https://developer.amazon.com | HTTP 200 | derived_guess | topics=api,access
- https://developers.amazon.com | HTTP 200 | derived_guess | topics=api,access

## Model reasoning
The SP-API is a comprehensive REST API using Login with Amazon (OAuth 2.0). Access is strictly gated behind developer registration and identity verification. AWS provides an official Partner Central MCP server, and there are official sample MCP implementations for SP-API.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Requires creating a Solution Provider Portal account, completing identity verification, and submitting a profile for approval.
- recommended_next_action: **Needs Outreach**
- confidence: **0.85**

## Evidence URLs
- https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-gen-ai-selling-partner-api/integrating-sp-api.html
- https://developer.amazonservices.com/register
- https://developer-docs.amazon.com/sp-api
- https://docs.aws.amazon.com/partner-central/latest/APIReference/partner-central-mcp-server.html

## Generated record
```json
{
  "app": "Amazon Selling Partner",
  "category": "Commerce",
  "one_liner": "The Amazon Selling Partner API (SP-API) provides programmatic access to Amazon Seller Central data for orders...",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Requires creating a Solution Provider Portal account, completing identity verification, and submitting a profile for approval."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "Developers must complete a gated identity verification and profile approval process before obtaining production credentials.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-gen-ai-selling-partner-api/integrating-sp-api.html",
    "https://developer.amazonservices.com/register",
    "https://developer-docs.amazon.com/sp-api",
    "https://docs.aws.amazon.com/partner-central/latest/APIReference/partner-central-mcp-server.html"
  ],
  "confidence": 0.85,
  "verification_status": "Auto",
  "slug": "amazon-selling-partner",
  "primary_docs_url": "https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-gen-ai-selling-partner-api/integrating-sp-api.html",
  "rate_limit_note": "Rate limits apply and vary by endpoint, such as specific limits for the Catalog Items and Customer Feedback APIs.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "Requires a paid Professional Seller account ($39.99/mo) plus a developer approval process (days to weeks)."
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current handcheck fold; this supersedes earlier key decisions._

```json
{
  "app": "Amazon Selling Partner",
  "category": "Commerce",
  "one_liner": "The Amazon Selling Partner API (SP-API) provides programmatic access to Amazon Seller Central data for orders...",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Requires creating a Solution Provider Portal account, completing identity verification, and submitting a profile for approval."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "None",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "Developers must complete a gated identity verification and profile approval process before obtaining production credentials.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developer-docs.amazon.com/sp-api/docs/onboarding-overview",
    "https://developer-docs.amazon.com/sp-api/lang-en_EN/docs/sp-api-registration-overview",
    "https://developer-docs.amazon.com/sp-api/lang-US/docs/onboarding-step-8-call-the-sp-api-in-production"
  ],
  "confidence": 0.85,
  "verification_status": "Hand-Checked",
  "slug": "amazon-selling-partner",
  "primary_docs_url": "https://developer-docs.amazon.com/sp-api/docs/onboarding-overview",
  "rate_limit_note": "Rate limits apply and vary by endpoint, such as specific limits for the Catalog Items and Customer Feedback APIs.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
