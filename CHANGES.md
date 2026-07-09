# Fix pass — 2026-07-09

External review pass over the submitted repo + live page. Every fix below was verified
before shipping (evidence URLs curl-checked to HTTP 200, dataset re-validated against the
locked schema, page re-render asserted). Numbers on the report regenerate from data — no
hand-edited HTML stats.

## 1. Data: `existing_mcp` false negatives (29 rows) — the big one

The first batch derived `existing_mcp` from API-reference evidence. API reference pages
almost never mention MCP, so multiple apps with **official** MCP servers were marked
`None`. The first sweep caught GitHub, Stripe, Cloudflare, Linear, Sentry, Netlify,
Vercel, MongoDB Atlas, Jira (Atlassian), HubSpot, Klaviyo, and Shopify; a deeper
official-doc sweep added Slack, Airtable, Ramp, Twilio, Vonage, DataForSEO, Freshdesk,
GoHighLevel, Gorgias, Podio, QuickBooks, Salesforce, Snowflake, WooCommerce, Zoho CRM,
Zoho Cliq, and systeme.io. The original audit stress-checked only "Official" claims
(false positives), never "None" claims — a one-directional audit.

- Fixed in `corrections.py` → `MCP_OFFICIAL_FIXES` (each row gets the vendor's own MCP
  page appended as evidence).
- Re-checked unsupported `Official` claims too: BigCommerce and MrScraper are
  third-party/community MCP only; Fathom has no confirmed first-party MCP. Those were
  downgraded instead of inflating the metric.
- Prevented at the source: `docs_research.gather_mcp_evidence()` now runs a dedicated
  `"<app> official MCP server"` search + fetch per app, and `synthesis.py` instructs the
  model to base `existing_mcp` on that block (absence in API docs proves nothing).
- Headline stat moved **35 → 61 official MCP** after adding 29 false negatives and removing
  3 unsupported official claims.

## 2. Data: hand-check auth folds + stale auth facts (5 rows)

The hand-check honestly *reported* 3 auth misses but the shipped matrix still displayed
the known-wrong values. Folded the truth back in (`corrections.py`), keeping
`metrics.handcheck` as the as-measured 94.1% snapshot with an explanatory note:

- **DealCloud** `API Key, Other Token` → `API Key, OAuth2`
- **Notion** `OAuth2, Bearer Token` → `OAuth2, API Key`
- **Slack** `OAuth2, Bot Token, Other Token` → `OAuth2`

Plus two stale facts caught in review (evidence appended):

- **Airtable** `API Key` → `Personal Access Token, OAuth2` (legacy keys deprecated Feb 2024)
- **HubSpot** `OAuth2, Bearer Token, API Key` → `OAuth2, Bearer Token` (dev API keys sunset 2022)

## 3. Code: accuracy-movement scoring bug (`handcheck.py`)

`_score_record()`/`fold()` compared canonicalized truth against **raw** record labels
through `verify._auth_agree`'s string-squash, so first-pass rows were penalized for
spellings ("OAuth 2.0" vs "OAuth2", "API Token" vs "API Key"). 8 of the 19 counted
first-pass misses were label artifacts, inflating the movement headline.

- Both sides are now canonicalized before comparison.
- Honest movement: **78.4% → 94.1%** (4 apps factually corrected: Copper, Plain,
  WhatsApp Business, LinkedIn Ads; 0 regressed). The old 62.7% figure conflated
  normalization with accuracy; metrics now carry a note separating the two.

## 4. Code: smaller bugs

- `handcheck.generate_template()` could silently overwrite human-filled ground truth in
  `handcheck/handcheck.json`; it now refuses and writes `handcheck.template.json` instead.
- `report/app.js` `width()` rendered a 3% bar for zero-count values (e.g. DevInfra's 0
  gated apps showed a sliver); zero now renders zero.
- `report/app.js` `renderInsights()` had a latent TypeError when `avg_confidence` was
  missing (`(x || 0).toFixed` guard evaluated the wrong object).
- Reasoning logs stamped the *configured* primary model instead of the model that
  actually answered (fallback chains + sharding make these differ). `config.llm_json()`
  now records the winning tier (thread-local) and `synthesis.py` logs it.
- `requirements.txt`: `composio>=0.5` is now guarded with `; python_version >= "3.10"` —
  unguarded, `pip install -r requirements.txt` hits ResolutionImpossible on older
  interpreters, killing the README quickstart for reviewers. README notes Python 3.10+.

## 5. Report page (`report/index.html`, `report/app.js`)

- **New "03 / Agent" section** — the assignment requires the page itself to explain the
  agent and where a human was needed. Five pipeline stages (each named after its file),
  "where a human was needed" (preseeds, hand-check, loop adjudication, MCP sweep), and
  "what defeated the agent" (Paygent, thin docs, free-tier failures). Sections renumbered,
  nav + reviewer route updated.
- **Composio overlap surfaced** — new matrix column (Yes/No toolkit), a 7th headline tile
  ("49 · no Composio toolkit yet"), and a 4th findings card naming the whitespace: the
  no-toolkit ∩ Build Now set is the immediate build queue.
- Verification cards now render the honest post-fix notes (as-measured accuracy vs
  folded matrix; factual movement vs label normalization).

## Verification of this fix pass

- All Python files compile; `corrections.py` re-validates all 100 records against the
  locked schema (0 errors).
- Independent re-score of the final dataset vs `handcheck/handcheck.json` truth: **51/51**.
- New targeted evidence URLs were checked during the fix pass; rows re-validate against
  the locked schema and the report regenerates from `out/results.json`.
- Full page render asserted headlessly (metrics tiles, matrix pills, verification notes,
  100 rows, no warnings).

Rebuild artifacts after any data change: `python corrections.py && python research.py --metrics && python research.py --build-report`.
