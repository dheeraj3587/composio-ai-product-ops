# PitchBook - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["PitchBook official API authentication developer documentation", "PitchBook API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://pitchbook.com | HTTP 403 | hint | topics=none
- https://pitchbook.com/products/direct-access-data/api | HTTP 403 | search_result | topics=none
- https://documenter.getpostman.com/view/5190535/TzCV1iRc | HTTP 200 | search_result | topics=none
- https://developer.pitchbook.com | HTTP 0 | derived_guess | topics=none
- https://developers.pitchbook.com | HTTP 0 | derived_guess | topics=none
- https://pitchbook.com/help/PitchBook-api | HTTP 200 | browser_verified_summary | topics=api,auth,access
- https://pitchbook.com/media/press-releases/pitchbook-announces-new-essential-mcp-integration-with-perplexity-expanding-access-to-ai-powered-verifiable-market-intelligence | HTTP 200 | browser_verified_summary | topics=access,mcp

## Model reasoning
First-party documentation confirms the REST API requires a standalone contract (Gated). Press releases and official MCP directories confirm an official MCP server exists but requires premium access and OAuth.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Access to the PitchBook API and Premium MCP server requires a standalone enterprise contract agreement.
- recommended_next_action: **Partner-Gated**
- confidence: **0.8**

## Evidence URLs
- https://pitchbook.com/help/PitchBook-api
- https://pitchbook.com/media/press-releases/pitchbook-announces-new-essential-mcp-integration-with-perplexity-expanding-access-to-ai-powered-verifiable-market-intelligence
- https://apigene.ai/mcp/official/pitchbook
- https://mcpservers.org/remote-mcp-servers/pitchbook

## Generated record
```json
{
  "app": "PitchBook",
  "category": "Fintech",
  "one_liner": "PitchBook provides an enterprise REST API and an official MCP server for accessing private and public capital market...",
  "auth_methods": [
    "OAuth2",
    "API Key"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Access to the PitchBook API and Premium MCP server requires a standalone enterprise contract agreement."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "Requires an enterprise contract and licensed user account to obtain API credentials or access the Premium MCP server.",
  "recommended_next_action": "Partner-Gated",
  "evidence_urls": [
    "https://pitchbook.com/help/PitchBook-api",
    "https://pitchbook.com/media/press-releases/pitchbook-announces-new-essential-mcp-integration-with-perplexity-expanding-access-to-ai-powered-verifiable-market-intelligence",
    "https://apigene.ai/mcp/official/pitchbook",
    "https://mcpservers.org/remote-mcp-servers/pitchbook"
  ],
  "confidence": 0.8,
  "verification_status": "Auto",
  "slug": "pitchbook",
  "primary_docs_url": "https://pitchbook.com/help/PitchBook-api",
  "rate_limit_note": "Each request incurs a credit cost according to the enterprise contract.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Partner-Gated",
  "main_blocker": "Enterprise research platform; API is contact-sales / partner-only, no public self-serve tier."
}
```
