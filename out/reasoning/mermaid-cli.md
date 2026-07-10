# Mermaid CLI - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Mermaid CLI official API authentication developer documentation", "Mermaid CLI API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://github.com/mermaid-js/mermaid-cli | HTTP 200 | search_result | topics=api,access,mcp
- https://github.com/data-mermaid/mermaid-api | HTTP 200 | search_result | topics=api,auth,access,mcp
- https://github.com/mermaid-js/mermaid-cli/blob/master/building.md | HTTP 200 | search_result | topics=auth,access,mcp
- https://developer.github.com | HTTP 200 | derived_guess | topics=api,auth
- https://developers.github.com | HTTP 200 | derived_guess | topics=none
- https://docs.github.com | HTTP 200 | derived_guess | topics=api,auth

## Model reasoning
Mermaid CLI is a local command-line tool for rendering Mermaid diagrams. It does not offer a hosted API service, making standard API integration impossible, though several community MCP servers exist to wrap the local CLI.

## Key decisions
- buildability: **Blocked**
- access_model: **Self-Serve** - Open-source local CLI tool; no hosted API credentials required.
- recommended_next_action: **Blocked**
- confidence: **0.95**

## Evidence URLs
- https://github.com/mermaid-js/mermaid-cli
- https://github.com/peng-shawn/mermaid-mcp-server

## Generated record
```json
{
  "app": "Mermaid CLI",
  "category": "AI/Meeting-tools",
  "one_liner": "Mermaid CLI is an open-source command-line tool for generating diagrams, lacking a hosted API but supported by...",
  "auth_methods": [
    "None / Not Applicable"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Open-source local CLI tool; no hosted API credentials required."
  },
  "api_type": "None",
  "api_breadth": "Narrow",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Blocked",
  "main_blocker": "Mermaid CLI is a local open-source tool, not a hosted API service.",
  "recommended_next_action": "Blocked",
  "evidence_urls": [
    "https://github.com/mermaid-js/mermaid-cli",
    "https://github.com/peng-shawn/mermaid-mcp-server"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "mermaid-cli",
  "primary_docs_url": "https://github.com/data-mermaid/mermaid-api",
  "rate_limit_note": "Not applicable as it is a local tool.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "api_type": "None",
  "access_model": "Self-Serve",
  "recommended_next_action": "Blocked",
  "main_blocker": "Open-source CLI/library (diagram rendering), not a hosted API service."
}
```
