# Consensus - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Consensus official API authentication developer documentation", "Consensus API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://consensus.app | HTTP 200 | hint | topics=none
- https://consensus.app/home/api/ | HTTP 200 | search_result | topics=api,access
- https://developer.zendesk.com/api-reference/introduction/security-and-auth/ | HTTP 200 | search_result | topics=api,auth
- https://developers.konsentus.com/api-reference/fi-authentication.html | HTTP 200 | search_result | topics=api,auth
- https://developer.consensus.app | HTTP 0 | derived_guess | topics=none
- https://developers.consensus.app | HTTP 0 | derived_guess | topics=none

## Model reasoning
The documentation shows that while the traditional REST API is gated behind a 'Request access' form, Consensus provides an official MCP server that is self-serve and uses OAuth2 for authentication. This makes it easy to build integrations for MCP-compatible clients immediately.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - The REST API requires requesting access (Gated), but the official MCP server is self-serve via OAuth2 using a standard Consensus account.
- recommended_next_action: **Build Now**
- confidence: **0.9**

## Evidence URLs
- https://consensus.app/home/api/
- https://docs.consensus.app/docs/mcp

## Generated record
```json
{
  "app": "Consensus",
  "category": "AI/Meeting-tools",
  "one_liner": "Consensus provides an AI-powered search engine for peer-reviewed academic papers, offering both a gated REST API and...",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "The REST API requires requesting access (Gated), but the official MCP server is self-serve via OAuth2 using a standard Consensus account."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Official",
  "composio_toolkit": "No",
  "buildability": "Easy",
  "main_blocker": "None for the MCP server; however, direct REST API access requires manual approval.",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://consensus.app/home/api/",
    "https://docs.consensus.app/docs/mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "consensus",
  "primary_docs_url": "https://consensus.app/home/api/",
  "rate_limit_note": "No specific rate limits are mentioned in the provided documentation.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "'OAuth requested' hint suggests a public API is not yet generally available."
}
```
