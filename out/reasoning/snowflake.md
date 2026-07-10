# Snowflake - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Snowflake official API authentication developer documentation", "Snowflake API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://docs.snowflake.com | HTTP 200 | hint | topics=api
- https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/authentication | HTTP 200 | search_result | topics=api,auth
- https://signup.snowflake.com/ | HTTP 200 | derived_guess | topics=access
- https://docs.snowflake.com/ja/developer-guide/snowflake-rest-api/authentication | HTTP 200 | search_result | topics=api,auth
- https://docs.snowflake.com/en/user-guide/api-authentication | HTTP 200 | search_result | topics=api,auth
- https://developer.snowflake.com | HTTP 200 | derived_guess | topics=api,access

## Model reasoning
Snowflake's REST APIs support OAuth, PATs, and Key-Pair authentication (Other Token). An official MCP server is available for Cortex AI and object management. Production access requires a paid account, making it Gated.

## Key decisions
- buildability: **Moderate**
- access_model: **Gated** - Production use requires a paid Snowflake account; trial accounts are available for testing.
- recommended_next_action: **Needs Outreach**
- confidence: **0.9**

## Evidence URLs
- https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/authentication
- https://developer.snowflake.com
- https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp
- https://github.com/Snowflake-Labs/mcp

## Generated record
```json
{
  "app": "Snowflake",
  "category": "DevInfra",
  "one_liner": "Snowflake provides extensive REST APIs and an official MCP server for data management, analytics, and Cortex AI.",
  "auth_methods": [
    "OAuth2",
    "Personal Access Token",
    "Other Token"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "Production use requires a paid Snowflake account; trial accounts are available for testing."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Official",
  "composio_toolkit": "Yes",
  "buildability": "Moderate",
  "main_blocker": "Production access requires an active, paid Snowflake enterprise account.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/authentication",
    "https://developer.snowflake.com",
    "https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp",
    "https://github.com/Snowflake-Labs/mcp"
  ],
  "confidence": 0.9,
  "verification_status": "Auto",
  "slug": "snowflake",
  "primary_docs_url": "https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/authentication",
  "rate_limit_note": "Rate limits depend on warehouse sizing and account tier.",
  "last_verified": "2026-07-10"
}
```
