#!/usr/bin/env python3
"""One-time correction pass over out/results.json.

Two things:
  1. Normalize every record's auth_methods to the canonical set (normalize.py).
  2. Apply documented per-app overrides sourced from OFFICIAL docs and the
     Browser Use verification loop (each with a real evidence URL). Honest calls:
     WhatsApp Business and Pinterest stay Gated (browser over-called Self-Serve;
     production needs verification/review); weak third-party evidence gets lower
     confidence + an explicit note.

Re-validates every record against the locked schema, then saves results.json.
Run:  python corrections.py
"""
from __future__ import annotations

import config
import normalize
from schema import validate_record

# slug -> partial field overrides (only the fields we change)
OVERRIDES: dict[str, dict] = {
    # --- Otter AI: official MCP server, OAuth-authenticated, no public API key ---
    "otter-ai": {
        "one_liner": "Meeting transcription with an official OAuth-authenticated MCP server (search/fetch/get-user tools).",
        "api_type": "MCP-only",
        "existing_mcp": "Official",
        "auth_methods": ["OAuth2"],
        "access_model": {"kind": "Self-Serve",
                         "note": "MCP connected via OAuth with your Otter account (Claude/ChatGPT/Cursor/Perplexity connectors). No public REST API/key."},
        "buildability": "Moderate",
        "recommended_next_action": "Build Now",
        "main_blocker": "MCP-only (no public REST API/key); usable today via OAuth-authenticated MCP connectors.",
        "primary_docs_url": "https://help.otter.ai/hc/en-us/articles/35287607569687-Otter-MCP-Server",
        "evidence_urls": ["https://help.otter.ai/hc/en-us/articles/35287607569687-Otter-MCP-Server"],
        "confidence": 0.9,
    },
    # --- Empty-auth fills from official docs ---
    "linkedin-ads": {
        "auth_methods": ["OAuth2"],
        "main_blocker": "Marketing API access requires applying for API products + partner approval (3-legged OAuth).",
        "primary_docs_url": "https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication",
        "evidence_urls": ["https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication",
                          "https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access"],
        "confidence": 0.85,
    },
    "ramp": {
        "auth_methods": ["OAuth2"],
        "main_blocker": "OAuth2 (client-credentials / auth-code); API access tied to being a Ramp business customer.",
        "primary_docs_url": "https://docs.ramp.com/developer-api/v1/authorization",
        "evidence_urls": ["https://docs.ramp.com/developer-api/v1/authorization",
                          "https://docs.ramp.com/developer-api/v1/introduction"],
        "confidence": 0.8,
    },
    "ipayx": {
        "api_type": "REST",
        "auth_methods": ["API Key", "Bearer Token"],
        "access_model": {"kind": "Self-Serve",
                         "note": "Create an account and get an API key via the developer portal (browser-verified; small/newer product)."},
        "buildability": "Moderate",
        "recommended_next_action": "Build Now",
        "main_blocker": "",
        "evidence_urls": ["https://www.ipayx.ai/developers?lang=en", "https://www.ipayx.ai/docs/api?lang=en"],
        "confidence": 0.5,
    },
    # --- Non-hosted tools: None / Not Applicable + correct evidence ---
    "sherlock": {
        "api_type": "None",
        "auth_methods": ["None / Not Applicable"],
        "access_model": {"kind": "Self-Serve", "note": "Open-source CLI (username OSINT); not a hosted API service."},
        "buildability": "Blocked",
        "recommended_next_action": "Blocked",
        "main_blocker": "Open-source CLI tool, not a hosted API — nothing to integrate via API (could wrap the CLI).",
        "primary_docs_url": "https://github.com/sherlock-project/sherlock",
        "evidence_urls": ["https://github.com/sherlock-project/sherlock"],
        "confidence": 0.9,
    },
    "mermaid-cli": {
        "api_type": "None",
        "auth_methods": ["None / Not Applicable"],
        "access_model": {"kind": "Self-Serve", "note": "Open-source CLI/library (diagram rendering); not a hosted API service."},
        "buildability": "Blocked",
        "recommended_next_action": "Blocked",
        "main_blocker": "Open-source CLI/library, not a hosted API service.",
        "primary_docs_url": "https://github.com/mermaid-js/mermaid-cli",
        "evidence_urls": ["https://github.com/mermaid-js/mermaid-cli"],
        "confidence": 0.9,
    },
    # --- Browser-verification folds (compared current vs browser vs official docs) ---
    "copper": {
        "api_type": "REST",
        "auth_methods": ["API Key", "OAuth2"],
        "access_model": {"kind": "Self-Serve", "note": "REST API; API key from Settings. Requires a Copper account (14-day trial available)."},
        "buildability": "Easy",
        "recommended_next_action": "Build Now",
        "primary_docs_url": "https://developer.copper.com/introduction/authentication.html",
        "evidence_urls": ["https://developer.copper.com/introduction/authentication.html", "https://developer.copper.com"],
        "confidence": 0.85,
    },
    "plain": {
        "api_type": "GraphQL",
        "auth_methods": ["API Key"],
        "access_model": {"kind": "Self-Serve", "note": "GraphQL API; API key from workspace Settings > API Keys."},
        "buildability": "Easy",
        "recommended_next_action": "Build Now",
        "primary_docs_url": "https://www.plain.com/docs/graphql/authentication",
        "evidence_urls": ["https://www.plain.com/docs/graphql/authentication", "https://docs.plain.com"],
        "confidence": 0.85,
    },
    "salesforce": {
        "api_type": "REST",
        "auth_methods": ["OAuth2"],
        "access_model": {"kind": "Self-Serve", "note": "Free Developer Edition org; REST + OAuth2."},
        "buildability": "Easy",
        "recommended_next_action": "Build Now",
        "primary_docs_url": "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/quickstart_oauth.htm",
        "evidence_urls": ["https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/quickstart_oauth.htm",
                          "https://developer.salesforce.com"],
        "confidence": 0.85,
    },
    "whatsapp-business": {  # browser said Self-Serve; KEEP Gated (production needs verification)
        "api_type": "REST",
        "auth_methods": ["OAuth2", "Bearer Token"],
        "access_model": {"kind": "Gated", "note": "Cloud API; free test number is self-serve, but production requires Meta business verification + app review."},
        "buildability": "Hard",
        "recommended_next_action": "Needs Outreach",
        "main_blocker": "Production access requires Meta business verification + app review.",
        "evidence_urls": ["https://developers.facebook.com/docs/whatsapp",
                          "https://developers.facebook.com/documentation/business-messaging/whatsapp/access-tokens"],
        "confidence": 0.8,
    },
    "google-ads": {
        "api_type": "REST",
        "auth_methods": ["OAuth2", "Service Account"],
        "access_model": {"kind": "Gated", "note": "OAuth2 + an approved developer token (Basic/Standard access)."},
        "buildability": "Hard",
        "recommended_next_action": "Needs Outreach",
        "main_blocker": "Requires an approved Google Ads developer token in addition to OAuth.",
        "evidence_urls": ["https://developers.google.com/google-ads/api/docs/oauth/overview",
                          "https://developers.google.com/google-ads/api/docs/api-policy/developer-token"],
        "confidence": 0.8,
    },
    "pinterest": {  # browser said Self-Serve; KEEP Gated (standard access needs review)
        "api_type": "REST",
        "auth_methods": ["OAuth2"],
        "access_model": {"kind": "Gated", "note": "OAuth2; trial access self-serve, but standard/production access requires app review."},
        "buildability": "Moderate",
        "recommended_next_action": "Needs Outreach",
        "primary_docs_url": "https://developers.pinterest.com/docs/getting-started/set-up-authentication-and-authorization/",
        "evidence_urls": ["https://developers.pinterest.com/docs/getting-started/set-up-authentication-and-authorization/",
                          "https://developers.pinterest.com/docs/getting-started/authentication/"],
        "confidence": 0.8,
    },
    # --- Weak / third-party evidence: prefer official, else lower confidence + note ---
    "pitchbook": {
        "access_model": {"kind": "Gated", "note": "Enterprise/partner-only API (contact sales)."},
        "recommended_next_action": "Partner-Gated",
        "main_blocker": "No public official API docs found; primary evidence is a third-party connector (docs.matia.io). Contact-sales / partner only.",
        "primary_docs_url": "https://pitchbook.com",
        "evidence_urls": ["https://pitchbook.com", "https://docs.matia.io/docs/connectors/etl/pitchbook/api-configuration"],
        "confidence": 0.45,
    },
    "higgsfield": {
        "main_blocker": "Newer product; primary evidence is a third-party blog (apidog.com) — official API docs unconfirmed.",
        "primary_docs_url": "https://higgsfield.ai/cli",
        "evidence_urls": ["https://higgsfield.ai/cli", "https://cloud.higgsfield.ai/", "https://apidog.com/blog/higgsfield-api/"],
        "confidence": 0.5,
    },
    "clay": {
        "main_blocker": "HTTP API documented at university.clay.com; first-pass primary evidence was third-party (apitracker.io).",
        "primary_docs_url": "https://university.clay.com/docs/http-api-integration-overview",
        "evidence_urls": ["https://university.clay.com/docs/http-api-integration-overview", "https://clay.com"],
        "confidence": 0.65,
    },
    "lark": {
        "main_blocker": "Auth corroborated by a third-party wiki (deepwiki); official portal is open.larksuite.com.",
        "primary_docs_url": "https://open.larksuite.com",
        "evidence_urls": ["https://open.larksuite.com", "https://github.com/larksuite/lark-openapi-mcp",
                          "https://deepwiki.com/larksuite/oapi-sdk-go/2.3-authentication-and-token-management"],
        "confidence": 0.78,
    },
    "zoho-crm": {  # official docs exist -> make them primary
        "primary_docs_url": "https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html",
        "evidence_urls": ["https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html",
                          "https://www.zoho.com/crm/developer/docs/api/v8/"],
        "confidence": 0.9,
    },
    # --- existing_mcp corrections (spot-checked 18 of the most-doubtful "Official"
    #     claims vs vendor docs; 16 held up, these 2 did not) ---
    "binance": {"existing_mcp": "Community"},   # only community/third-party MCPs found, no official
    "dealcloud": {  # no DealCloud MCP found; drop the unsupported "MCP preview" claim from the one-liner
        "existing_mcp": "None",
        "one_liner": "Broad REST API with SDKs; API keys require an existing DealCloud site admin (no public signup).",
    },
    # --- Paygent Connect: first pass researched the WRONG product (an LLM-cost SDK at
    #     paygent.to), not the NMI-powered payment gateway. Mark honestly as unconfirmed. ---
    "paygent-connect": {
        "one_liner": "NMI-powered payment gateway; no clear public API docs found (docs.paygent.to looks like a different product).",
        "api_type": "None",
        "auth_methods": ["None / Not Applicable"],
        "access_model": {"kind": "Gated", "note": "Payment gateway; no self-serve public API docs confirmed. Likely partner / contact-sales."},
        "existing_mcp": "None",
        "buildability": "Blocked",
        "recommended_next_action": "Needs Outreach",
        "main_blocker": "Could not confirm the NMI-powered Paygent Connect API; docs found (paygent.to) appear to be a different product.",
        "confidence": 0.3,
    },
}


def apply() -> None:
    rows = config.load_json(config.RESULTS_PATH) or []
    if not rows:
        raise SystemExit("out/results.json missing")
    changed_auth = 0
    # first-pass synthesis self-scores, used to undo the weak blind-re-search confidence
    # penalty on solid, NON-corrected apps (e.g. Vercel/Airtable/Neo4j were 0.9 -> 0.576).
    fp = {r["slug"]: r.get("confidence")
          for r in (config.load_json(config.OUT_DIR / "results_firstpass.json") or [])}
    for r in rows:
        # 1) normalize auth on EVERY record
        before = list(r.get("auth_methods", []))
        r["auth_methods"] = normalize.normalize_auth_list(before)
        if r["auth_methods"] != before:
            changed_auth += 1
        # 2) per-app overrides
        ov = OVERRIDES.get(r["slug"])
        if ov:
            for k, v in ov.items():
                r[k] = v
        # undo the weak-model verify penalty: restore first-pass self-score where an
        # app that has NO manual override was dragged down by the blind re-search pass.
        if r["slug"] not in OVERRIDES and fp.get(r["slug"]) and fp[r["slug"]] > r.get("confidence", 0):
            r["confidence"] = fp[r["slug"]]
        # cap over-confident self-scores (nothing from doc-scraping is 100% certain)
        r["confidence"] = round(min(float(r.get("confidence", 0.5)), 0.95), 3)
        # re-validate against the locked schema
        validate_record(r)

    config.save_json(config.RESULTS_PATH, rows)
    print(f"normalized auth on {changed_auth} records; applied {len(OVERRIDES)} per-app overrides; "
          f"{len(rows)} records re-validated + saved.")


if __name__ == "__main__":
    apply()
