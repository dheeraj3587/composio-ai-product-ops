# WhatsApp Business - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["WhatsApp Business official API authentication developer documentation", "WhatsApp Business API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://developers.facebook.com/docs/whatsapp | HTTP 200 | hint | topics=api,auth,access
- https://developers.facebook.com/docs/whatsapp/on-premises/reference | HTTP 200 | search_result | topics=api,access
- https://developers.facebook.com/docs/whatsapp/business-management-api/get-started/ | HTTP 200 | search_result | topics=api,auth,access
- https://developers.facebook.com/docs/whatsapp/business-management-api/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.facebook.com | HTTP 200 | derived_guess | topics=api,auth,access
- https://developers.facebook.com | HTTP 200 | derived_guess | topics=api,auth,access

## Model reasoning
The WhatsApp Business API (now exclusively Cloud API) is built on Meta's Graph API, utilizing REST and access tokens. Production access is strictly gated behind Meta business verification and App Review. Community MCP servers exist to interface with the API.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - Production access requires Meta business verification, an approved WhatsApp Business account, and App Review.
- recommended_next_action: **Needs Outreach**
- confidence: **0.9**

## Evidence URLs
- https://developers.facebook.com/docs/whatsapp/business-management-api/get-started/
- https://developers.facebook.com/docs/whatsapp/on-premises/reference
- https://github.com/mattcoatsworth/Whatsapp-MCP-Server

## Generated record
```json
{
  "app": "WhatsApp Business",
  "category": "Comms",
  "one_liner": "The WhatsApp Business Platform provides a Cloud API for sending messages, managing templates, and handling business...",
  "auth_methods": [
    "OAuth2",
    "Bearer Token"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Production access requires Meta business verification, an approved WhatsApp Business account, and App Review."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "Requires Meta business verification and App Review before production access is granted.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developers.facebook.com/docs/whatsapp/business-management-api/get-started/",
    "https://developers.facebook.com/docs/whatsapp/on-premises/reference",
    "https://github.com/mattcoatsworth/Whatsapp-MCP-Server"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "whatsapp-business",
  "primary_docs_url": "https://developers.facebook.com/docs/whatsapp/business-management-api/get-started/",
  "rate_limit_note": "Cloud API supports up to 1,000 messages per second, subject to conversation-based pricing and tier limits.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "API exists but requires Meta business verification + app review before production access."
}
```

<!-- final-state:start -->
## Final pipeline state
_Updated 2026-07-11 by current handcheck fold; this supersedes earlier key decisions._

```json
{
  "app": "WhatsApp Business",
  "category": "Comms",
  "one_liner": "The WhatsApp Business Platform provides a Cloud API for sending messages, managing templates, and handling business...",
  "auth_methods": [
    "OAuth2",
    "Bearer Token"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Production access requires Meta business verification, an approved WhatsApp Business account, and App Review."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "Requires Meta business verification and App Review before production access is granted.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started",
    "https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/overview",
    "https://developers.facebook.com/documentation/development/create-an-app/whatsapp-use-case#permissions-and-features",
    "https://github.com/mattcoatsworth/Whatsapp-MCP-Server"
  ],
  "confidence": 0.9,
  "verification_status": "Hand-Checked",
  "slug": "whatsapp-business",
  "primary_docs_url": "https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started",
  "rate_limit_note": "Cloud API supports up to 1,000 messages per second, subject to conversation-based pricing and tier limits.",
  "last_verified": "2026-07-10"
}
```
<!-- final-state:end -->
