# Meta Ads — synthesis reasoning
_generated 2026-07-09 · model x-ai/grok-4.5-free_

## Model reasoning
Official Marketing API docs show a large surface (campaigns, ad sets, creatives, ads, insights, Instagram/Threads/Lead/Partnership/Advantage+ ads, etc.) → api_breadth Broad and api_type REST (HTTP programmatic interface per third-party guide). Auth is clearly required via dedicated Authentication and Authorization get-started pages, so not a simple API-key self-serve path → access_model Gated and buildability at least Moderate; treating as Hard because production Marketing API use is characteristically review/verification-heavy, matching the preseed. Preseed access_model=Gated and recommended_next_action=Needs Outreach are consistent with Authorization as a first-class gate and with Needs Outreach rubric (API exists, access needs review/business verification). Preseed main_blocker wording (app review + business verification) is NOT explicitly present in the fetched page bodies (auth/authorization fetches are mostly nav chrome; Vohrtech covers setup/auth at a high level only), so that blocker is retained as a weakly supported prior and confidence is lowered. No MCP mentioned → existing_mcp None. Rate limiting is only evidenced as a documented topic, not with numeric limits. COMPOSIO_TOOLKIT=Yes does not change public API readiness.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** — Public Marketing API docs plus dedicated Authentication and Authorization get-started guides; production ad access is not a simple self-serve key.
- recommended_next_action: **Needs Outreach**
- confidence: **0.58**

## Evidence URLs (whitelist-enforced)
- https://developers.facebook.com/docs/marketing-apis
- https://developers.facebook.com/documentation/ads-commerce/marketing-api/get-started/authentication/
- https://developers.facebook.com/documentation/ads-commerce/marketing-api/get-started/authorization/
- https://vohrtech.com/blog/meta-ads-api-integration-guide-for-developers

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "Marketing API is behind Meta app review + business verification."
}
```
_The model was instructed to trust evidence over this prior and note contradictions above._
