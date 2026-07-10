# LinkedIn Ads - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["LinkedIn Ads official API authentication developer documentation", "LinkedIn Ads API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://learn.microsoft.com/linkedin/marketing | HTTP 200 | hint | topics=api,auth,access
- https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access | HTTP 200 | search_result | topics=api,auth,access
- https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/version/text-ads-integrations?view=li-lms-2026-02 | HTTP 200 | search_result | topics=api,auth,access
- https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access?view=li-lms-2026-05 | HTTP 200 | search_result | topics=api,auth,access
- https://developer.microsoft.com | HTTP 200 | derived_guess | topics=api,access,mcp
- https://developers.microsoft.com | HTTP 200 | derived_guess | topics=api,access,mcp

## Model reasoning
The official documentation confirms that the Advertising API uses OAuth 2.0 and requires explicit approval via the Developer Portal. Community MCPs exist (e.g., linkedin-ads-mcp on PyPI), but there is no official MCP. The gated access model makes buildability Hard.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Access to the Advertising API requires applying for approval through the LinkedIn Developer Portal, which is evaluated by LinkedIn and not guaranteed.
- recommended_next_action: **Needs Outreach**
- confidence: **0.9**

## Evidence URLs
- https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access
- https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access?view=li-lms-2026-05
- https://libraries.io/pypi/linkedin-ads-mcp

## Generated record
```json
{
  "app": "LinkedIn Ads",
  "category": "Ads/Marketing",
  "one_liner": "The LinkedIn Ads API enables developers to manage campaigns, target audiences, and track advertising performance.",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Access to the Advertising API requires applying for approval through the LinkedIn Developer Portal, which is evaluated by LinkedIn and not guaranteed."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "Yes",
  "buildability": "Hard",
  "main_blocker": "Production access requires manual approval for the Advertising API product from LinkedIn, which can take days and is not guaranteed.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access",
    "https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access?view=li-lms-2026-05",
    "https://libraries.io/pypi/linkedin-ads-mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "linkedin-ads",
  "primary_docs_url": "https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access",
  "rate_limit_note": "No specific rate limit details were found in the provided documentation.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "Marketing API access requires LinkedIn Marketing Developer Platform / partner approval."
}
```
