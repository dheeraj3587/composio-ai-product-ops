# Otter AI - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Otter AI official API authentication developer documentation", "Otter AI API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://help.otter.ai | HTTP 200 | hint | topics=access
- https://help.otter.ai/hc/en-us/articles/4412365535895-Does-Otter-offer-an-open-API | HTTP 200 | search_result | topics=api
- https://otter.ai/terms-of-service | HTTP 200 | search_result | topics=auth,access
- https://otter.ai/software-services-agreement | HTTP 200 | search_result | topics=auth,access
- https://developer.otter.ai | HTTP 0 | derived_guess | topics=none
- https://developers.otter.ai | HTTP 0 | derived_guess | topics=none

## Model reasoning
Otter's help center explicitly states that the public API is only available for Enterprise customers who contact their account manager. Recent blog posts confirm the launch of an official MCP server, which is also tied to the Enterprise offering. Authentication relies on OAuth2.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - API and MCP access is restricted to Enterprise customers and requires contacting an account manager to enable.
- recommended_next_action: **Needs Outreach**
- confidence: **0.9**

## Evidence URLs
- https://help.otter.ai/hc/en-us/articles/4412365535895-Does-Otter-offer-an-open-API
- https://otter.ai/blog/otter-for-enterprise-connect-ai-to-ai-with-otters-mcp
- https://otter.ai/software-services-agreement

## Generated record
```json
{
  "app": "Otter AI",
  "category": "AI/Meeting-tools",
  "one_liner": "Otter AI provides a REST API and an official MCP server for meeting transcripts, gated behind Enterprise plans.",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "API and MCP access is restricted to Enterprise customers and requires contacting an account manager to enable."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "Access requires an Enterprise plan and manual approval from an account manager.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://help.otter.ai/hc/en-us/articles/4412365535895-Does-Otter-offer-an-open-API",
    "https://otter.ai/blog/otter-for-enterprise-connect-ai-to-ai-with-otters-mcp",
    "https://otter.ai/software-services-agreement"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "otter-ai",
  "primary_docs_url": "https://otter.ai/terms-of-service",
  "rate_limit_note": "Not explicitly documented in the provided public sources.",
  "last_verified": "2026-07-10"
}
```
