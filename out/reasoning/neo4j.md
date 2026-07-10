# Neo4j - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Neo4j official API authentication developer documentation", "Neo4j API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://neo4j.com/docs/api | HTTP 404 | hint | topics=none
- https://neo4j.com/developer/kb/a-lightweight-approach-to-testing-the-neo4j-rest-api-with-authentication/ | HTTP 200 | search_result | topics=api,auth,access
- https://neo4j.com/docs/aura/api/authentication/ | HTTP 200 | search_result | topics=api,auth,access
- https://neo4j.com/docs/http-api/current/authentication-authorization/ | HTTP 200 | search_result | topics=api,auth,access
- https://developer.neo4j.com | HTTP 0 | derived_guess | topics=none
- https://developers.neo4j.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
Neo4j provides an official MCP server hosted on their GitHub organization, and their Aura API supports OAuth2 and Basic Auth with self-serve access.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - All Aura tiers, including free/trial, can create API credentials. Self-managed instances also support basic auth.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://neo4j.com/docs/aura/api/authentication/
- https://neo4j.com/docs/http-api/current/authentication-authorization/
- https://github.com/neo4j/mcp
- https://neo4j.com/blog/developer/model-context-protocol/

## Generated record
```json
{
  "app": "Neo4j",
  "category": "DevInfra",
  "one_liner": "Neo4j is a leading graph database offering an HTTP API, Aura cloud API, and an official MCP server for AI integrations.",
  "auth_methods": [
    "OAuth2",
    "Basic Auth"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "All Aura tiers, including free/trial, can create API credentials. Self-managed instances also support basic auth."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://neo4j.com/docs/aura/api/authentication/",
    "https://neo4j.com/docs/http-api/current/authentication-authorization/",
    "https://github.com/neo4j/mcp",
    "https://neo4j.com/blog/developer/model-context-protocol/"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "neo4j",
  "primary_docs_url": "https://neo4j.com/developer/kb/a-lightweight-approach-to-testing-the-neo4j-rest-api-with-authentication/",
  "rate_limit_note": "Not explicitly detailed in the provided snippets.",
  "last_verified": "2026-07-10"
}
```
