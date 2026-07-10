# Pinterest - synthesis reasoning
_generated 2026-07-11 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Pinterest official API authentication developer documentation", "Pinterest API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developers.pinterest.com | HTTP 200 | hint | topics=api,access
- https://github.com/pinterest/api-quickstart/blob/main/nodejs/README.md | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://www.youtube.com/watch?v=16ns1L5UySI | HTTP 200 | search_result | topics=none
- https://community.n8n.io/t/pinterest-api-trial-standard-any-success-stories-tips-for-standard-access-approval/257516?tl=en | HTTP 200 | search_result | topics=api,auth,access
- https://developer.pinterest.com | HTTP 200 | derived_guess | topics=api,access
- https://docs.pinterest.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
First-party documentation snippets lack explicit details on authentication methods and access gating, though the quickstart repo mentions application ID and secret. Relying on a detailed third-party community post for OAuth2 and the video demo requirement, which lowers confidence.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Trial access is self-serve, but Standard (production) access requires submitting a video demo of the OAuth flow and core actions for manual approval.
- recommended_next_action: **Needs Outreach**
- confidence: **0.5**

## Evidence URLs
- https://community.n8n.io/t/pinterest-api-trial-standard-any-success-stories-tips-for-standard-access-approval/257516?tl=en
- https://developers.pinterest.com
- https://github.com/clugtu/pinterest-mcp
- https://github.com/pinterest/api-quickstart/blob/main/nodejs/README.md

## Generated record
```json
{
  "app": "Pinterest",
  "category": "Ads/Marketing",
  "one_liner": "Pinterest provides a REST API for managing pins, boards, ads, and catalogs, with production access requiring a video...",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Trial access is self-serve, but Standard (production) access requires submitting a video demo of the OAuth flow and core actions for manual approval."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "Upgrading from Trial to Standard access requires recording and submitting a video demo of the application for vendor approval.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://community.n8n.io/t/pinterest-api-trial-standard-any-success-stories-tips-for-standard-access-approval/257516?tl=en",
    "https://developers.pinterest.com",
    "https://github.com/clugtu/pinterest-mcp",
    "https://github.com/pinterest/api-quickstart/blob/main/nodejs/README.md"
  ],
  "confidence": 0.5,
  "verification_status": "Auto",
  "slug": "pinterest",
  "primary_docs_url": "https://github.com/pinterest/api-quickstart/blob/main/nodejs/README.md",
  "rate_limit_note": "Trial access restricts certain POST endpoints; Standard access lifts these restrictions upon approval.",
  "last_verified": "2026-07-11"
}
```
