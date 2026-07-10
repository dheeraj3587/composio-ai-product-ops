# iPayX - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["iPayX official API authentication developer documentation", "iPayX API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://ipayx.ai/docs | HTTP 200 | hint | topics=none
- https://docs.i-pay.io/ | HTTP 200 | search_result | topics=api,auth,access
- https://docs.i-pay.io/testing-and-faqs/FAQ/ | HTTP 200 | search_result | topics=api,auth
- https://documentation.ixopay.com/api/transaction/transaction-api | HTTP 200 | search_result | topics=api,auth
- https://developer.ipayx.ai | HTTP 0 | derived_guess | topics=none
- https://developers.ipayx.ai | HTTP 0 | derived_guess | topics=none

## Model reasoning
Changed existing_mcp to Community because the MCP server is hosted on a personal Cloudflare worker (ybolduc.workers.dev) and listed on a community registry, lacking definitive first-party documentation.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - REST API requires a self-serve account and API key. The community MCP server requires no authentication or signup.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://docs.i-pay.io/
- https://docs.i-pay.io/testing-and-faqs/FAQ/
- https://mcpservers.org/servers/ipayx-technologies/mcp-fx-audit

## Generated record
```json
{
  "app": "iPayX",
  "category": "Fintech",
  "one_liner": "iPayX provides a REST API for fiat-to-crypto payments and a community MCP server for forensic FX auditing.",
  "auth_methods": [
    "API Key"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "REST API requires a self-serve account and API key. The community MCP server requires no authentication or signup."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.i-pay.io/",
    "https://docs.i-pay.io/testing-and-faqs/FAQ/",
    "https://mcpservers.org/servers/ipayx-technologies/mcp-fx-audit"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "ipayx",
  "primary_docs_url": "https://docs.i-pay.io/",
  "rate_limit_note": "The MCP audit_transaction tool is limited to 3 free requests per month per IP.",
  "last_verified": "2026-07-10"
}
```
