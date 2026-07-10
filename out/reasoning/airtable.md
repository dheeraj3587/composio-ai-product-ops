# Airtable - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Airtable official API authentication developer documentation", "Airtable API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://airtable.com/developers | HTTP 200 | hint | topics=none
- https://airtable.com/developers/web/api/oauth-reference | HTTP 200 | search_result | topics=api,auth
- https://airtable.com/developers/web/api/authentication | HTTP 200 | search_result | topics=api,auth
- https://community.airtable.com/announcements-6/new-beta-new-api-authentication-methods-endpoints-and-public-api-docs-1442 | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://developer.airtable.com | HTTP 0 | derived_guess | topics=none
- https://developers.airtable.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
The evidence clearly demonstrates that Airtable offers a Web API supporting Personal Access Tokens and OAuth2, alongside an official MCP server documented on their support site. Access to these credentials is self-serve.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Personal access tokens and OAuth integrations can be created by users without manual approval.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://community.airtable.com/announcements-6/new-beta-new-api-authentication-methods-endpoints-and-public-api-docs-1442
- https://support.airtable.com/docs/using-the-airtable-mcp-server

## Generated record
```json
{
  "app": "Airtable",
  "category": "Productivity/PM",
  "one_liner": "Airtable provides a REST API and an official MCP server for managing bases, tables, and records.",
  "auth_methods": [
    "Personal Access Token",
    "OAuth2",
    "Service Account"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Personal access tokens and OAuth integrations can be created by users without manual approval."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://community.airtable.com/announcements-6/new-beta-new-api-authentication-methods-endpoints-and-public-api-docs-1442",
    "https://support.airtable.com/docs/using-the-airtable-mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "airtable",
  "primary_docs_url": "https://community.airtable.com/announcements-6/new-beta-new-api-authentication-methods-endpoints-and-public-api-docs-1442",
  "rate_limit_note": "Not explicitly detailed in the provided evidence.",
  "last_verified": "2026-07-10"
}
```
