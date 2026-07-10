#!/usr/bin/env python3
"""Legacy migration that reproduces the currently published reviewed snapshot.

Four things:
  1. Normalize every record's auth_methods to the canonical set (normalize.py).
  2. Apply documented per-app overrides sourced from OFFICIAL docs and the
     Browser Use verification loop (each with a real evidence URL). Honest calls:
     WhatsApp Business and Pinterest stay Gated (browser over-called Self-Serve;
     production needs verification/review); weak third-party evidence gets lower
     confidence + an explicit note.
  3. Fix existing_mcp FALSE NEGATIVES (MCP_OFFICIAL_FIXES): the first batch
     derived existing_mcp from API-reference pages, which rarely mention MCP,
     so many official servers were marked "None". Each fix below was
     re-verified against the vendor's own MCP page (URL appended as evidence).
     docs_research.gather_mcp_evidence() now probes for this at research time.
  4. Fold the three auth misses the human hand-check found (DealCloud, Notion,
     Slack) back into the matrix. metrics['handcheck'] keeps the pre-fix 94.1%
     as the honest as-measured number; the shipped rows carry the truth.

Re-validates every record against the locked schema, then saves results.json.
This is not part of a fresh research run. New runs should use the hardened
pipeline, retain verification disagreements, and fold only adjudicated fixes.
Run only when reproducing the legacy snapshot: python corrections.py
"""
from __future__ import annotations

import config
import normalize
import synthesis
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
        "evidence_urls": [
            "https://www.plain.com/docs/graphql/authentication",
            "https://www.plain.com/docs/graphql/introduction",
            "https://help.plain.com/article/mcp-server",
        ],
        "confidence": 0.9,
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
                          "https://developers.google.com/google-ads/api/docs/api-policy/developer-token",
                          "https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server"],
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
        "auth_methods": ["API Key"],
        "access_model": {"kind": "Gated", "note": "Enterprise/partner-only API (contact sales)."},
        "recommended_next_action": "Partner-Gated",
        "main_blocker": "Official API exists, but access requires requesting an API connection through PitchBook Direct Data.",
        "primary_docs_url": "https://pitchbook.com/help/PitchBook-api",
        "evidence_urls": [
            "https://pitchbook.com/help/PitchBook-api",
            "https://pitchbook.com/products/direct-access-data/api",
            "https://pitchbook.com/products/direct-access-data",
        ],
        "confidence": 0.72,
    },
    "higgsfield": {  # Grok 4.5 re-research found the OFFICIAL docs.higgsfield.ai (replaced the apidog blog)
        "main_blocker": "Newer product, but official REST API + CLI docs now confirmed at docs.higgsfield.ai.",
        "primary_docs_url": "https://docs.higgsfield.ai",
        "evidence_urls": ["https://higgsfield.ai/mcp", "https://higgsfield.ai/cli", "https://docs.higgsfield.ai"],
        "confidence": 0.72,
    },
    "clay": {  # Grok 4.5 re-research found official developers.clay.com / docs.clay.com (better than university.clay)
        "auth_methods": ["API Key"],
        "main_blocker": "Public REST API + official MCP; developer docs at developers.clay.com / docs.clay.com.",
        "primary_docs_url": "https://developers.clay.com",
        "evidence_urls": [
            "https://developers.clay.com",
            "https://docs.clay.com",
            "https://www.clay.com/mcp",
            "https://www.clay.com/changelog/clay-mcp-in-codex",
        ],
        "confidence": 0.72,
    },
    "lark": {
        "main_blocker": "",
        "primary_docs_url": "https://open.larksuite.com/document",
        "evidence_urls": [
            "https://open.larksuite.com/document",
            "https://open.larksuite.com/document/home/introduction-to-scope-and-authorization/overview",
            "https://github.com/larksuite/lark-openapi-mcp",
        ],
        "confidence": 0.84,
    },
    "zoho-crm": {  # official docs exist -> make them primary
        "primary_docs_url": "https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html",
        "evidence_urls": ["https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html",
                          "https://www.zoho.com/crm/developer/docs/api/v8/"],
        "confidence": 0.9,
    },
    "gorgias": {
        "auth_methods": ["API Key", "Basic Auth", "OAuth2"],
        "primary_docs_url": "https://developers.gorgias.com/",
        "evidence_urls": [
            "https://developers.gorgias.com/",
            "https://developers.gorgias.com/reference/introduction",
            "https://docs.gorgias.com/en-US/rest-api-208286",
            "https://developers.gorgias.com/docs/oauth2-authentication-for-creating-apps-with-gorgias",
            "https://docs.gorgias.com/en-US/connect-your-ai-assistant-to-the-gorgias-mcp-6310546",
        ],
        "confidence": 0.9,
    },
    "vonage": {
        "primary_docs_url": "https://developer.vonage.com/en/getting-started/concepts/authentication",
        "evidence_urls": [
            "https://developer.vonage.com/en/getting-started/concepts/authentication",
            "https://developer.vonage.com/en/verify/concepts/authentication",
            "https://developer.vonage.com/en/mcp-server/overview",
        ],
        "confidence": 0.9,
    },
    "systeme-io": {
        "primary_docs_url": "https://help.systeme.io/article/2329-how-to-use-systeme-io-public-api",
        "evidence_urls": [
            "https://help.systeme.io/article/2329-how-to-use-systeme-io-public-api",
            "https://help.systeme.io/article/9489-how-to-use-systeme-ios-mcp",
        ],
        "confidence": 0.9,
    },
    "woocommerce": {
        "primary_docs_url": "https://developer.woocommerce.com/docs/apis/rest-api/",
        "evidence_urls": [
            "https://developer.woocommerce.com/docs/apis/rest-api/",
            "https://woocommerce.com/document/woocommerce-rest-api",
            "https://developer.woocommerce.com/docs/features/mcp/",
        ],
        "confidence": 0.95,
    },
    "dataforseo": {
        "primary_docs_url": "https://docs.dataforseo.com/v3/auth/",
        "evidence_urls": [
            "https://docs.dataforseo.com/v3/auth/",
            "https://docs.dataforseo.com/v3/",
            "https://dataforseo.com/model-context-protocol",
            "https://dataforseo.com/help-center/setting-up-the-official-dataforseo-mcp-server-simple-guide",
        ],
        "confidence": 0.95,
    },
    "vercel": {
        "primary_docs_url": "https://vercel.com/docs/rest-api",
        "evidence_urls": [
            "https://vercel.com/docs/rest-api",
            "https://vercel.com/docs/integrations/create-integration/vercel-api-integrations",
            "https://vercel.com/docs/agent-resources/vercel-mcp",
        ],
        "confidence": 0.92,
    },
    "supabase": {
        "auth_methods": ["API Key", "Bearer Token", "Personal Access Token"],
        "primary_docs_url": "https://supabase.com/docs/guides/api",
        "evidence_urls": [
            "https://supabase.com/docs/guides/api",
            "https://supabase.com/docs/guides/getting-started/api-keys",
            "https://supabase.com/docs/reference/api/introduction",
            "https://supabase.com/docs/guides/ai-tools/mcp",
        ],
        "confidence": 0.95,
    },
    "neo4j": {
        "primary_docs_url": "https://neo4j.com/docs/",
        "evidence_urls": [
            "https://neo4j.com/docs/",
            "https://neo4j.com/developer/genai-ecosystem/model-context-protocol-mcp/",
            "https://github.com/neo4j-contrib/mcp-neo4j",
        ],
        "confidence": 0.9,
    },
    "datadog": {
        "primary_docs_url": "https://docs.datadoghq.com/api/latest/",
        "evidence_urls": [
            "https://docs.datadoghq.com/api/latest/",
            "https://docs.datadoghq.com/account_management/api-app-keys/",
            "https://docs.datadoghq.com/mcp_server/",
        ],
        "confidence": 0.92,
    },
    "jira": {
        "primary_docs_url": "https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/",
        "evidence_urls": [
            "https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/",
            "https://developer.atlassian.com/cloud/jira/software/oauth-2-3lo-apps/",
            "https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/",
        ],
        "confidence": 0.95,
    },
    "quickbooks": {
        "primary_docs_url": "https://developer.intuit.com/app/developer/qbo/docs/develop",
        "evidence_urls": [
            "https://developer.intuit.com/app/developer/qbo/docs/develop",
            "https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0",
            "https://github.com/intuit/quickbooks-online-mcp-server",
        ],
        "confidence": 0.92,
    },
    "zendesk": {
        "primary_docs_url": "https://developer.zendesk.com/api-reference/introduction/security-and-auth/",
        "evidence_urls": [
            "https://developer.zendesk.com/api-reference/introduction/security-and-auth/",
            "https://developer.zendesk.com/api-reference/",
            "https://developer.zendesk.com/documentation/api-basics/best-practices/best-practices-for-avoiding-rate-limiting/",
        ],
        "confidence": 0.92,
    },
    "stripe": {
        "primary_docs_url": "https://docs.stripe.com/api/authentication",
        "evidence_urls": [
            "https://docs.stripe.com/api/authentication",
            "https://docs.stripe.com/api",
            "https://docs.stripe.com/mcp",
        ],
        "confidence": 0.95,
    },
    "xero": {
        "primary_docs_url": "https://developer.xero.com/documentation/getting-started-guide/",
        "evidence_urls": [
            "https://developer.xero.com/documentation/getting-started-guide/",
            "https://github.com/xeroapi/xero-mcp-server",
            "https://developer.xero.com/faq/AI-Toolkit",
        ],
        "confidence": 0.92,
    },
    "attio": {
        "primary_docs_url": "https://docs.attio.com/rest-api/overview",
        "evidence_urls": [
            "https://docs.attio.com/rest-api/overview",
            "https://docs.attio.com/rest-api/guides/authentication",
            "https://docs.attio.com/mcp/overview",
        ],
        "confidence": 0.92,
    },
    "close": {
        "primary_docs_url": "https://developer.close.com/api/overview/api-key-authentication",
        "evidence_urls": [
            "https://developer.close.com/api/overview/api-key-authentication",
            "https://help.close.com/docs/mcp-server",
            "https://close.com/integrations/close-mcp",
        ],
        "confidence": 0.92,
    },
    "intercom": {
        "primary_docs_url": "https://developers.intercom.com/docs/build-an-integration/learn-more/authentication",
        "evidence_urls": [
            "https://developers.intercom.com/docs/build-an-integration/learn-more/authentication",
            "https://developers.intercom.com/docs/references/rest-api/api.intercom.io",
            "https://developers.intercom.com/docs/guides/mcp",
            "https://github.com/intercom/intercom-mcp-server",
        ],
        "confidence": 0.9,
    },
    "front": {
        "existing_mcp": "Official",
        "primary_docs_url": "https://dev.frontapp.com/docs/core-api-getting-started",
        "evidence_urls": [
            "https://dev.frontapp.com/docs/core-api-getting-started",
            "https://dev.frontapp.com/docs/mcp-server",
        ],
        "confidence": 0.9,
    },
    "pylon": {
        "primary_docs_url": "https://docs.usepylon.com/pylon-docs/developer/api/authentication",
        "evidence_urls": [
            "https://docs.usepylon.com/pylon-docs/developer/api/authentication",
            "https://docs.usepylon.com/pylon-docs/integrations/pylon-mcp",
            "https://support.usepylon.com/articles/2407390554-connecting-to-the-pylon-mcp-server",
        ],
        "confidence": 0.88,
    },
    "bigcommerce": {
        "existing_mcp": "Community",
        "primary_docs_url": "https://developer.bigcommerce.com/docs/start/about",
        "evidence_urls": [
            "https://developer.bigcommerce.com/docs/start/about",
            "https://docs.bigcommerce.com/developer/api-reference/about-our-apis",
            "https://github.com/CDataSoftware/bigcommerce-mcp-server-by-cdata",
        ],
        "confidence": 0.82,
    },
    "se-ranking": {
        "primary_docs_url": "https://seranking.com/api/data/getting-started/",
        "evidence_urls": [
            "https://seranking.com/api/data/getting-started/",
            "https://seranking.com/api/integrations/mcp/",
            "https://seranking.com/mcp.html",
        ],
        "confidence": 0.9,
    },
    "ahrefs": {
        "primary_docs_url": "https://docs.ahrefs.com/en/api/docs/introduction",
        "evidence_urls": [
            "https://docs.ahrefs.com/en/api/docs/introduction",
            "https://docs.ahrefs.com/en/mcp/docs/introduction",
            "https://github.com/ahrefs/ahrefs-mcp-server",
        ],
        "confidence": 0.92,
    },
    "mrscraper": {  # OFFICIAL first-party, cloud-hosted MCP server at mcp.mrscraper.com/mcp
                    # (docs.mrscraper.com/docs/getting-started/mcp-server). The prior check saw only
                    # the third-party Zapier wrapper and missed the vendor's own MCP subpage.
        "existing_mcp": "Official",
        "one_liner": "AI web-scraping platform with a scraper API and an official cloud-hosted MCP server (mcp.mrscraper.com/mcp).",
        "primary_docs_url": "https://docs.mrscraper.com/docs/getting-started/mcp-server",
        "evidence_urls": [
            "https://docs.mrscraper.com/docs/getting-started/mcp-server",
            "https://docs.mrscraper.com",
            "https://mrscraper.com/",
        ],
        "confidence": 0.85,
    },
    "apify": {
        "primary_docs_url": "https://docs.apify.com/api/v2",
        "evidence_urls": [
            "https://docs.apify.com/api/v2",
            "https://docs.apify.com/platform/integrations/mcp",
        ],
        "confidence": 0.95,
    },
    "firecrawl": {
        "primary_docs_url": "https://docs.firecrawl.dev/api-reference/introduction",
        "evidence_urls": [
            "https://docs.firecrawl.dev/api-reference/introduction",
            "https://docs.firecrawl.dev/use-cases/developers-mcp",
            "https://github.com/firecrawl/firecrawl-mcp-server",
        ],
        "confidence": 0.95,
    },
    "bright-data": {
        "primary_docs_url": "https://docs.brightdata.com/api-reference/authentication",
        "evidence_urls": [
            "https://docs.brightdata.com/api-reference/authentication",
            "https://brightdata.com/ai/mcp-server",
        ],
        "confidence": 0.92,
    },
    "asana": {
        "primary_docs_url": "https://developers.asana.com/docs/authentication",
        "evidence_urls": [
            "https://developers.asana.com/docs/authentication",
            "https://developers.asana.com/docs/using-asanas-mcp-server",
            "https://developers.asana.com/docs/mcp-clients",
        ],
        "confidence": 0.92,
    },
    "monday": {
        "primary_docs_url": "https://developer.monday.com/api-reference/docs/authentication",
        "evidence_urls": [
            "https://developer.monday.com/api-reference/docs/authentication",
            "https://developer.monday.com/api-reference/docs/monday-mcp-security-overview",
            "https://monday.com/w/mcp",
        ],
        "confidence": 0.9,
    },
    "clickup": {
        "primary_docs_url": "https://developer.clickup.com/docs/authentication",
        "evidence_urls": [
            "https://developer.clickup.com/docs/authentication",
            "https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server",
            "https://help.clickup.com/hc/en-us/articles/33335772678423-What-is-ClickUp-MCP",
        ],
        "confidence": 0.9,
    },
    "coda": {
        "primary_docs_url": "https://coda.io/developers",
        "evidence_urls": [
            "https://coda.io/developers",
            "https://coda.io/resources/guides/getting_started_with_coda_mcp",
        ],
        "confidence": 0.9,
    },
    "smartsheet": {
        "primary_docs_url": "https://developers.smartsheet.com/api/smartsheet/guides/basics/authentication",
        "evidence_urls": [
            "https://developers.smartsheet.com/api/smartsheet/guides/basics/authentication",
            "https://developers.smartsheet.com/ai-mcp/smartsheet/mcp-server",
            "https://help.smartsheet.com/articles/2483670-smartsheet-mcp-server",
        ],
        "confidence": 0.92,
    },
    "brex": {
        "primary_docs_url": "https://developer.brex.com/guides/authentication",
        "evidence_urls": [
            "https://developer.brex.com/guides/authentication",
            "https://developer.brex.com/docs/mcp",
            "https://www.brex.com/journal/brex-mcp-connect-brex-to-ai-tools",
        ],
        "confidence": 0.92,
    },
    "gohighlevel": {  # Official MCP is real (LeadConnector ships it), but the old evidence
                      # URL (…/articles/155000007981-…) now 404s. Replace it with the live
                      # LeadConnector MCP developer docs + the current help-center walkthrough.
        "evidence_urls": [
            "https://marketplace.gohighlevel.com/docs/other/mcp/",
            "https://marketplace.gohighlevel.com/docs/",
            "https://help.gohighlevel.com/support/solutions/articles/155000005741-how-to-use-the-highlevel-mcp-server",
            "https://help.gohighlevel.com/support/solutions/articles/48001060529-highlevel-api-documentation",
            "https://github.com/GoHighLevel/highlevel-api-docs",
        ],
    },
    "fathom": {  # OFFICIAL vendor-hosted MCP server at api.fathom.ai/mcp
                 # (docs: developers.fathom.ai/mcp-docs, confirmed at help.fathom.video/en/articles/11497793).
                 # The "deepen audit" pass wrongly downgraded this to None — a generic
                 # "does Fathom have an official MCP?" search missed the dedicated MCP subpage.
        "existing_mcp": "Official",
        "one_liner": "Fathom offers a public REST API plus an official OAuth-authenticated MCP server for meeting data & summaries.",
        "primary_docs_url": "https://developers.fathom.ai/mcp-docs",
        "evidence_urls": [
            "https://developers.fathom.ai/mcp-docs",
            "https://developers.fathom.ai/sdks/authentication",
            "https://help.fathom.video/en/articles/11497793",
        ],
        "confidence": 0.9,
    },
    "reducto": {
        "primary_docs_url": "https://docs.reducto.ai/quickstart",
        "evidence_urls": [
            "https://docs.reducto.ai/quickstart",
            "https://docs.reducto.ai/mcp-server",
            "https://reducto.ai/developers",
        ],
        "confidence": 0.95,
    },
    "devin": {
        "primary_docs_url": "https://docs.devin.ai/api-reference/authentication",
        "evidence_urls": [
            "https://docs.devin.ai/api-reference/authentication",
            "https://docs.devin.ai/work-with-devin/devin-mcp",
            "https://docs.devin.ai/api-reference/overview",
        ],
        "confidence": 0.92,
    },
    "youtube-transcript": {
        "primary_docs_url": "https://transcriptapi.com/docs/api/",
        "evidence_urls": [
            "https://transcriptapi.com/docs/api/",
            "https://transcriptapi.com/blog/youtube-mcp-server-setup-connect-claude",
            "https://transcriptapi.com/docs/",
        ],
        "confidence": 0.9,
    },
    "consensus": {
        "one_liner": "Consensus offers an official OAuth MCP server for peer-reviewed paper search; enterprise REST API is gated.",
        "auth_methods": ["OAuth2", "Bearer Token"],
        "access_model": {"kind": "Self-Serve",
                         "note": "Official MCP can be connected directly; free/pro accounts expand results. Enterprise API-key access requires contacting Consensus."},
        "api_type": "REST",
        "api_breadth": "Moderate",
        "existing_mcp": "Official",
        "buildability": "Moderate",
        "recommended_next_action": "Build Now",
        "main_blocker": "Enterprise REST API access is gated, but the official MCP server is usable now via OAuth or bearer token.",
        "primary_docs_url": "https://docs.consensus.app/docs/mcp",
        "evidence_urls": [
            "https://docs.consensus.app/docs/mcp",
            "https://consensus.app/home/api/",
        ],
        "confidence": 0.93,
    },
    # --- existing_mcp false-positive corrections (verified against vendor docs;
    #     do not count third-party MCP wrappers as first-party official servers) ---
    "binance": {"existing_mcp": "Community"},   # only community/third-party MCPs found, no official
    "dealcloud": {  # no DealCloud MCP found; drop the unsupported "MCP preview" claim from the one-liner
        "existing_mcp": "None",
        "one_liner": "Broad REST API with SDKs; API keys require an existing DealCloud site admin (no public signup).",
        # hand-check fold: docs describe OAuth-style token issuance alongside keys,
        # not a bespoke "Other Token" (handcheck/handcheck.json truth).
        "auth_methods": ["API Key", "OAuth2"],
    },
    # --- Hand-check auth folds (LOOP 3 truth, handcheck/handcheck.json). The
    #     hand-check MEASURED these as misses (that stays in metrics.handcheck,
    #     as-measured, 94.1%); the shipped matrix should still carry the truth. ---
    "notion": {  # internal integration secret is an API key, not a generic bearer
        "auth_methods": ["OAuth2", "API Key"],
        "evidence_urls": [
            "https://developers.notion.com/reference/authentication",
            "https://developers.notion.com/guides/get-started/overview",
            "https://developers.notion.com/guides/mcp/overview",
        ],
    },
    "slack": {  # apps are created + installed via OAuth; tokens are OAuth artifacts
        "auth_methods": ["OAuth2"],
    },
    # --- Stale auth facts caught in external review ---
    "airtable": {  # legacy API keys were deprecated (Feb 2024) in favor of PATs + OAuth
        "auth_methods": ["Personal Access Token", "OAuth2"],
    },
    "hubspot": {  # developer API keys were sunset in 2022; private-app tokens + OAuth remain
        "auth_methods": ["OAuth2", "Bearer Token"],
        "evidence_urls": [
            "https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview",
            "https://developers.hubspot.com/docs/api/private-apps",
            "https://developers.hubspot.com/docs/apps/developer-platform/build-apps/integrate-with-the-remote-hubspot-mcp-server",
        ],
        "confidence": 0.9,
    },
    "help-scout": {
        "auth_methods": ["OAuth2", "API Key", "Basic Auth"],
        "primary_docs_url": "https://developer.helpscout.com/mailbox-api/overview/authentication/",
        "evidence_urls": [
            "https://developer.helpscout.com/mailbox-api/overview/authentication/",
            "https://developer.helpscout.com/docs-api/",
        ],
        "confidence": 0.9,
    },
    "plaid": {
        "auth_methods": ["API Key", "Other Token"],
        "access_model": {"kind": "Gated",
                         "note": "Sandbox signup is self-serve, but Production API access must be requested in the Plaid Dashboard."},
        "buildability": "Moderate",
        "recommended_next_action": "Needs Outreach",
        "main_blocker": "Production access requires a Plaid approval/review process.",
        "evidence_urls": ["https://plaid.com/docs/api/", "https://plaid.com/docs/resources/mcp/"],
        "confidence": 0.88,
    },
    "pumble": {
        "one_liner": "Pumble provides a self-serve API-key addon and official MCP server for workspace messaging.",
        "access_model": {"kind": "Self-Serve", "note": "API addon is available on all plans; keys are generated inside Pumble."},
        "primary_docs_url": "https://pumble.com/help/integrations/automation-workflow-integrations/api-keys-integration/",
        "evidence_urls": [
            "https://pumble.com/help/integrations/automation-workflow-integrations/api-keys-integration/",
            "https://pumble.com/help/integrations/automation-workflow-integrations/how-to-use-the-pumble-mcp-server/",
        ],
        "confidence": 0.82,
    },
    "twilio": {
        "auth_methods": ["Basic Auth", "API Key"],
        "existing_mcp": "Official",
        "evidence_urls": [
            "https://www.twilio.com/docs/iam/api-keys",
            "https://www.twilio.com/docs/iam/api/authtoken",
            "https://www.twilio.com/docs/ai/mcp",
        ],
        "confidence": 0.93,
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

# --- existing_mcp FALSE-NEGATIVE fixes (verified 2026-07-09 against vendor pages;
#     every URL below returned HTTP 200 at verification time and is appended to the
#     row's evidence_urls). Root cause: existing_mcp was derived from API-reference
#     evidence, which rarely mentions MCP — absence there proves nothing. The
#     original audit only stress-checked "Official" claims (false positives),
#     never "None" claims, so these slipped through in one direction. ---
MCP_OFFICIAL_FIXES: dict[str, str] = {
    "github": "https://github.com/github/github-mcp-server",
    "cloudflare": "https://github.com/cloudflare/mcp-server-cloudflare",
    "stripe": "https://docs.stripe.com/mcp",
    "linear": "https://linear.app/docs/mcp",
    "sentry": "https://mcp.sentry.dev",
    "netlify": "https://docs.netlify.com/build/build-with-ai/netlify-mcp-server/",
    "vercel": "https://vercel.com/docs/agent-resources/vercel-mcp",
    "mongodb-atlas": "https://www.mongodb.com/docs/mcp-server/",
    "jira": "https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/",
    "hubspot": "https://developers.hubspot.com/mcp",
    "klaviyo": "https://developers.klaviyo.com/en/docs/klaviyo_mcp_server",
    "shopify": "https://shopify.dev/docs/apps/build/storefront-mcp",
    # Second sweep: current vendor pages now show first-party MCP support.
    "slack": "https://docs.slack.dev/ai/slack-mcp-server/",
    "airtable": "https://support.airtable.com/docs/using-the-airtable-mcp-server",
    "ramp": "https://docs.ramp.com/developer-api/v1/developer-mcp",
    "twilio": "https://www.twilio.com/docs/ai/mcp",
    "vonage": "https://developer.vonage.com/en/mcp-server/overview",
    "dataforseo": "https://dataforseo.com/help-center/setting-up-the-official-dataforseo-mcp-server-simple-guide",
    # NOTE on MCP maturity: most rows here are official + GA (e.g. GitHub, Stripe,
    # Twilio, Salesforce). A few are official but vendor-labeled Beta/EAP — still
    # first-party/"Official", just not yet GA. Flagged inline below.
    "freshdesk": "https://support.freshdesk.com/support/solutions/articles/50000012670-model-context-protocol-mcp-integration-in-freshdesk-eap-",  # official, vendor-labeled EAP (beta)
    "gohighlevel": "https://marketplace.gohighlevel.com/docs/other/mcp/",  # was …/155000007981-… (404); now the live LeadConnector MCP dev docs
    "gorgias": "https://docs.gorgias.com/en-US/connect-your-ai-assistant-to-the-gorgias-mcp-6310546",  # official, vendor-labeled Beta
    "podio": "https://docs.sharefile.com/en-us/podio/using-podio/general-features/podio-mcp-server.html",
    "quickbooks": "https://github.com/intuit/quickbooks-online-mcp-server",
    "salesforce": "https://developer.salesforce.com/docs/platform/hosted-mcp-servers/overview",
    "snowflake": "https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp",
    "woocommerce": "https://developer.woocommerce.com/docs/features/mcp/",
    "zoho-crm": "https://www.zoho.com/crm/developer/docs/mcp/overview.html",
    "zoho-cliq": "https://www.zoho.com/cliq/help/platform/zoho-cliq-mcp.html",
    "systeme-io": "https://help.systeme.io/article/9489-how-to-use-systeme-ios-mcp",
    "consensus": "https://docs.consensus.app/docs/mcp",
    # Third sweep: the "deepen audit" over-corrected two rows the wrong way — a generic
    # "does X have an official MCP?" search returned "no" when the real answer was "yes,
    # on a subpage the search missed". Re-verified against the vendor's own MCP page.
    "fathom": "https://developers.fathom.ai/mcp-docs",        # was None; official server at api.fathom.ai/mcp
    "mrscraper": "https://docs.mrscraper.com/docs/getting-started/mcp-server",  # was Community; official server at mcp.mrscraper.com/mcp
}

# Evidence URLs to APPEND (never replace) for rows whose fix is sourced from a
# specific page not already in the row's evidence list.
EVIDENCE_APPENDS: dict[str, list[str]] = {
    "notion": ["https://developers.notion.com/reference/authentication"],
    "slack": ["https://docs.slack.dev/authentication/"],
    "airtable": ["https://airtable.com/developers/web/api/authentication"],
    "hubspot": ["https://developers.hubspot.com/docs/api/private-apps"],
    "plaid": ["https://plaid.com/docs/api/"],
}

# Full, accurate one-liners (<=120 chars) that REPLACE 9 the old synthesis hard-truncated
# mid-word via [:120]. Complete sentences, written within the limit.
ONE_LINERS = {
    "copper": "Copper provides a comprehensive REST CRM API for leads, people, companies, and opportunities.",
    "whatsapp-business": "WhatsApp Business Cloud API: broad REST messaging with a free sandbox; production needs Meta verification + app review.",
    "threads": "Meta's Threads API supports automated posting, media retrieval, reply management, and insights for creators/brands.",
    "amazon-selling-partner": "REST API for Amazon sellers to manage catalogs, orders, and fulfillment; gated developer registration required.",
    "smartsheet": "Smartsheet offers a comprehensive REST API with SDKs and an official MCP server for project management.",
    "harvest": "Harvest offers a comprehensive REST API for time tracking, invoicing, and projects, with OAuth2 and PAT support.",
    "ipayx": "iPayX exposes an FX Audit API, but public endpoint documentation is thin and not fully verifiable.",
    "reducto": "Agentic document API for parsing, extraction, classification, splitting, and editing across 30+ file types.",
    "higgsfield": "Higgsfield offers a self-serve REST API with API-key auth for integrating generative AI models.",
    # Precision: these two ship an OFFICIAL (vendor-hosted) MCP server, but the vendors
    # themselves label it Beta/EAP — distinct from official + GA (GitHub, Stripe). Still "Official".
    "freshdesk": "Broad self-serve REST API for tickets, conversations & fields; official MCP integration is in EAP/beta.",
    "gorgias": "Self-serve REST API (Basic Auth/API key) for private apps; official MCP server is currently in beta.",
}


def apply() -> None:
    rows = config.load_json(config.RESULTS_PATH) or []
    if not rows:
        raise SystemExit("out/results.json missing")
    changed_auth = 0
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
        # 2b) existing_mcp false-negative fixes (+ their evidence)
        if r["slug"] in MCP_OFFICIAL_FIXES:
            r["existing_mcp"] = "Official"
            url = MCP_OFFICIAL_FIXES[r["slug"]]
            if url not in r.get("evidence_urls", []):
                r["evidence_urls"] = list(r.get("evidence_urls", [])) + [url]
        # 2c) appended (never replacing) evidence for targeted fixes
        for url in EVIDENCE_APPENDS.get(r["slug"], []):
            if url not in r.get("evidence_urls", []):
                r["evidence_urls"] = list(r.get("evidence_urls", [])) + [url]
        # replace one-liners the OLD synthesis truncated mid-word with full sentences
        if r["slug"] in ONE_LINERS:
            r["one_liner"] = ONE_LINERS[r["slug"]]
        # cap over-confident self-scores (nothing from doc-scraping is 100% certain)
        r["confidence"] = round(min(float(r.get("confidence", 0.5)), 0.95), 3)
        # re-validate against the locked schema
        validate_record(r)
        synthesis.append_final_state(r, reason="legacy corrections.py migration")

    config.save_json(config.RESULTS_PATH, rows)
    print(f"normalized auth on {changed_auth} records; applied {len(OVERRIDES)} per-app overrides; "
          f"{len(MCP_OFFICIAL_FIXES)} existing_mcp false-negative fixes; "
          f"{len(rows)} records re-validated + saved.")


if __name__ == "__main__":
    apply()
