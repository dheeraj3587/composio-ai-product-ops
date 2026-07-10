# NotebookLM - synthesis reasoning
_generated 2026-07-10 | model gemini-3.1-pro-preview_

## Research trace
- queries: ["NotebookLM official API authentication developer documentation", "NotebookLM API production access approval credentials official documentation"]
- evidence quality: **adequate**
- https://cloud.google.com/gemini | HTTP 200 | hint | topics=api,auth,access
- https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/set-up-notebooklm | HTTP 200 | search_result | topics=api,auth,access
- https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks | HTTP 200 | search_result | topics=api,auth
- https://support.google.com/notebooklm/answer/16164461?hl=en&co=GENIE.Platform=Desktop | HTTP 200 | search_result | topics=none
- https://developer.google.com | HTTP 200 | derived_guess | topics=api,auth,access
- https://developers.google.com | HTTP 200 | derived_guess | topics=api,auth,access

## Model reasoning
The official REST API is documented under NotebookLM Enterprise, which requires specific licenses and Google Cloud identity setup (OAuth2 via gcloud auth). Standard NotebookLM lacks a public API, leading to community MCPs that rely on unsupported cookie extraction. Confidence is set to 0.8 due to the gated nature of the Enterprise API.

## Key decisions
- buildability: **Hard**
- access_model: **Gated** - The official REST API is restricted to NotebookLM Enterprise, requiring Google Cloud setup, licenses, and an identity provider. Community MCPs exist but use unsupported browser cookie extraction.
- recommended_next_action: **Needs Outreach**
- confidence: **0.8**

## Evidence URLs
- https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks
- https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/set-up-notebooklm
- https://cloud.google.com/gemini
- https://github.com/jacob-bd/notebooklm-mcp-cli
- https://mcp.directory/servers/notebooklm

## Generated record
```json
{
  "app": "NotebookLM",
  "category": "AI/Meeting-tools",
  "one_liner": "NotebookLM offers a gated Enterprise REST API for managing notebooks, while community MCPs rely on browser cookies.",
  "auth_methods": [
    "OAuth2"
  ],
  "access_model": {
    "kind": "Gated",
    "note": "The official REST API is restricted to NotebookLM Enterprise, requiring Google Cloud setup, licenses, and an identity provider. Community MCPs exist but use unsupported browser cookie extraction."
  },
  "api_type": "REST",
  "api_breadth": "Moderate",
  "existing_mcp": "Community",
  "composio_toolkit": "No",
  "buildability": "Hard",
  "main_blocker": "No public self-serve API for standard NotebookLM; the official API requires NotebookLM Enterprise licenses and Google Cloud identity setup.",
  "recommended_next_action": "Needs Outreach",
  "evidence_urls": [
    "https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks",
    "https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/set-up-notebooklm",
    "https://cloud.google.com/gemini",
    "https://github.com/jacob-bd/notebooklm-mcp-cli",
    "https://mcp.directory/servers/notebooklm"
  ],
  "confidence": 0.8,
  "verification_status": "Auto",
  "slug": "notebooklm",
  "primary_docs_url": "https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/set-up-notebooklm",
  "rate_limit_note": "Not explicitly documented in the provided snippets.",
  "last_verified": "2026-07-10"
}
```

## Preseed hypothesis (unverified prior)
```json
{
  "api_type": "None",
  "access_model": "Gated",
  "recommended_next_action": "Needs Outreach",
  "main_blocker": "No public NotebookLM API; the closest workaround is the Gemini Enterprise API."
}
```
