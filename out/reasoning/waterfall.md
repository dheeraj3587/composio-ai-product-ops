# Waterfall.io - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Waterfall.io official API authentication developer documentation", "Waterfall.io API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://waterfall.io | HTTP 200 | hint | topics=api,auth,access
- https://docs.waterfall.io/v1/authentication | HTTP 200 | search_result | topics=api,auth
- https://docs.waterfall.io/v1/introduction | HTTP 200 | search_result | topics=api,auth
- https://www.waterfall.io/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.waterfall.io | HTTP 0 | derived_guess | topics=none
- https://developers.waterfall.io | HTTP 0 | derived_guess | topics=none

## Model reasoning
The documentation clearly shows a REST API using an API key in the x-api-key header. However, the main website and docs point to 'Book a Call' and 'Get API & Sales Support', indicating that production access is gated behind a sales process. Evidence for the access model is thin as no dedicated access/pricing page was fetched, lowering confidence.

## Key decisions
- buildability: **Moderate**
- access_model: **Gated** - Requires booking a call or contacting sales to obtain an API key. Explicit self-serve access documentation is missing, inferred from 'Book a Call' and 'Get API & Sales Support' links.
- recommended_next_action: **Needs Outreach**
- confidence: **0.7**

## Evidence URLs
- https://docs.waterfall.io/v1/authentication
- https://docs.waterfall.io/v1/introduction
- https://waterfall.io
- https://www.waterfall.io/

## Generated record
```json
{
  "app": "Waterfall.io",
  "category": "Research/Scraping",
  "one_liner": "Waterfall.io provides a REST API for B2B contact and company enrichment, prospecting, and email verification.",
  "auth_methods": [
    "API Key"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Requires booking a call or contacting sales to obtain an API key. Explicit self-serve access documentation is missing, inferred from 'Book a Call' and 'Get API & Sales Support' links."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "None",
  "composio_toolkit": "No",
  "buildability": "Moderate",
  "main_blocker": "No self-serve sign-up; developers must book a call or contact sales to get API credentials.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://docs.waterfall.io/v1/authentication",
    "https://docs.waterfall.io/v1/introduction",
    "https://waterfall.io",
    "https://www.waterfall.io/"
  ],
  "confidence": 0.7,
  "verification_status": "Auto",
  "slug": "waterfall",
  "primary_docs_url": "https://waterfall.io",
  "rate_limit_note": "Rate limit documentation exists but specific limits are not detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
