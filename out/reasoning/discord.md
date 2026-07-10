# Discord - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["Discord official API authentication developer documentation", "Discord API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://discord.com | HTTP 200 | hint | topics=none
- https://docs.discord.com/developers/topics/oauth2 | HTTP 200 | search_result | topics=api,auth,access
- https://docs.discord.com/developers/reference | HTTP 200 | search_result | topics=api,auth
- https://discord.com/developers/docs/social-sdk/authentication.html | HTTP 200 | search_result | topics=api,auth,access
- https://developer.discord.com | HTTP 0 | derived_guess | topics=none
- https://developers.discord.com | HTTP 0 | derived_guess | topics=none

## Model reasoning
Discord's official documentation clearly outlines a self-serve REST API utilizing OAuth2 and Bot Tokens. Multiple community MCP servers exist on GitHub.

## Key decisions
- buildability: **Easy**
- access_model: **Self-Serve** - Developers can freely create applications and bots in the Discord Developer Portal to obtain credentials.
- recommended_next_action: **Build Now**
- confidence: **0.95**

## Evidence URLs
- https://docs.discord.com/developers/topics/oauth2
- https://docs.discord.com/developers/reference
- https://github.com/IQAIcom/mcp-discord

## Generated record
```json
{
  "app": "Discord",
  "category": "Comms",
  "one_liner": "Discord provides a comprehensive REST API and WebSocket gateway for building bots, apps, and integrations.",
  "auth_methods": [
    "OAuth2",
    "Bot Token"
  ],
  "access_model": {
    "kind": "Self-Serve",
    "note": "Developers can freely create applications and bots in the Discord Developer Portal to obtain credentials."
  },
  "api_type": "REST",
  "api_breadth": "Broad",
  "existing_mcp": "Community",
  "composio_toolkit": "Yes",
  "buildability": "Easy",
  "main_blocker": "None",
  "recommended_next_action": "Build Now",
  "evidence_urls": [
    "https://docs.discord.com/developers/topics/oauth2",
    "https://docs.discord.com/developers/reference",
    "https://github.com/IQAIcom/mcp-discord"
  ],
  "confidence": 0.95,
  "verification_status": "Auto",
  "slug": "discord",
  "primary_docs_url": "https://docs.discord.com/developers/topics/oauth2",
  "rate_limit_note": "Rate limits are enforced and documented in the API reference, with specific limits varying by endpoint.",
  "last_verified": "2026-07-10"
}
```
