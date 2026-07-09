# API Integration Readiness — Research Agent

**Take-home:** AI Product Ops Intern @ Composio
**Goal:** Autonomously research the API/integration readiness of **100 apps** into a locked schema, verify the findings honestly, and present everything on **one static HTML page** a reviewer understands in ~2 minutes.
**Time budget:** 6–8 hours. Speed of submission matters. Correctness > polish.

---

## 1. Grading criteria (priority order — design decisions defer to this)

1. **Accuracy of findings** — wrong/hallucinated facts about auth/access/API surface are the biggest risk.
2. **Clarity of patterns** — insight across the 100 apps, not just a table.
3. **Real verification** — honest first-pass vs post-verification comparison, hand-checked sample, hits **and** misses shown.
4. **A working agent/pipeline** that actually did the research, with an honest account of where a human stepped in.
5. **Presentation** — single self-explanatory page, skimmable in ~2 min.

> Rule of thumb: when in doubt, **cut scope, not accuracy**. Every extra service/tool/test that doesn't serve accuracy or clarity is time stolen from verification.

---

## 2. Locked schema (19 fields — do NOT add/remove/rename without sign-off)

Per app, one record:

| # | Field | Type / enum |
|---|-------|-------------|
| 1 | `app` | string |
| 2 | `category` | enum (10 categories, below) |
| 3 | `one_liner` | string, **≤120 chars** |
| 4 | `auth_methods` | list[string] (e.g. OAuth2, API Key, PAT, Basic, mTLS) |
| 5 | `access_model` | `Self-Serve` \| `Gated` + free-form note (free tier/trial/production nuance) |
| 6 | `api_type` | `REST` \| `GraphQL` \| `SDK` \| `SOAP` \| `MCP-only` \| `None` |
| 7 | `api_breadth` | `Narrow` \| `Moderate` \| `Broad` |
| 8 | `existing_mcp` | `Official` \| `Community` \| `None` |
| 9 | `composio_toolkit` | `Yes` \| `No` |
| 10 | `buildability` | `Easy` \| `Moderate` \| `Hard` \| `Blocked` |
| 11 | `main_blocker` | string ("" if none) |
| 12 | `recommended_next_action` | `Build Now` \| `Needs Outreach` \| `Partner-Gated` \| `Blocked` |
| 13 | `evidence_urls` | list[string] — **only URLs actually fetched this run, each must resolve** |
| 14 | `confidence` | float 0–1 (self-scored; triage signal, NOT an accuracy claim) |
| 15 | `verification_status` | `Auto` \| `Hand-Checked` |
| 16 | `slug` | string (stable key for JSON + HTML anchors) |
| 17 | `primary_docs_url` | string (research anchor) |
| 18 | `rate_limit_note` | string (optional) |
| 19 | `last_verified` | ISO date |

**Categories (10):** CRM · Support · Comms · Ads/Marketing · Commerce · Research/Scraping · DevInfra · Productivity/PM · Fintech · AI/Meeting-tools.
The exact 100 apps live in `data/apps.json` — **use that list verbatim, never substitute apps.**

### Rubrics (keep verdicts consistent & interview-defensible)
- **api_breadth:** Narrow = 1 resource / few endpoints; Moderate = several resources / full CRUD; Broad = many resources across multiple domains.
- **buildability:** Easy = self-serve key + REST/GraphQL + clear docs; Moderate = OAuth app setup or partial docs; Hard = heavy review/verification or thin docs; Blocked = no usable public API / partner-only.
- **recommended_next_action:** Build Now = Easy + Self-Serve; Needs Outreach = API exists but access needs review/business verification; Partner-Gated = good API but no entry point without an existing paid account; Blocked = no public API.

---

## 3. Architecture (lean — single deploy target)

```
Offline Python pipeline (the "agent", runnable via CLI)
  apps.json + preseed.json
        │
        ├─ composio_lookup.py   → composio_toolkit (Yes/No) + existing_mcp hint   [Composio SDK/catalog]
        ├─ docs_research.py     → raw evidence via SEARCH + DIRECT FETCH (not browser automation)
        │                          auth methods · access model · api type/breadth · rate limits · evidence URLs
        └─ synthesis.py         → OpenRouter LLM → schema-conformant record + logged reasoning
        →  pipeline.py          → research_app(app); batch over 100 → out/results.json (+ aggregates, failures.log)
        →  verify.py            → BLIND re-search-from-scratch of auth+access → out/metrics.json (before/after)
        →  handcheck            → 15–20 apps by hand → folded into metrics.json

Single static deploy (Vercel)
  report/index.html  ← renders baked-in results.json + metrics.json  (Patterns → Matrix → Agent → Verification → Proof)
```

**Explicitly OUT of scope** (cut for time/accuracy): always-on backend, Docker, headless-browser server in production, public "re-run research" endpoint, heavy TDD suites.
**Browser automation (browser-use):** fallback only for apps whose docs are genuinely un-fetchable — and **disclosed on the report** if used. Not the default.
**Composio usage:** limited to the toolkit lookup + MCP hint. Nothing more unless trivial.

### LLM layer — OpenRouter (OpenAI-compatible)
- Client: OpenAI SDK pointed at `base_url=https://openrouter.ai/api/v1`, key `OPENROUTER_API_KEY`.
- Model configurable via `OPENROUTER_MODEL` (default `openai/gpt-4o-mini` for cost; upgradeable to `openai/gpt-4o`).
- Structured JSON output (response_format / JSON schema) for synthesis + verification.
- Every synthesis call writes an inspectable reasoning log to `out/reasoning/<slug>.md` so **every field can be explained in an interview.**

---

## 4. Verification design (the part that must be real)

- **Flag A (locked, non-negotiable): blind re-search FROM SCRATCH.** The verification pass does NOT re-fetch the stored URL and does NOT see pass-1's answer. It issues a *fresh, differently-phrased* search, fetches independently, and re-derives `auth_methods` + `access_model`, then diffs. This catches *wrong-page* errors (pass 1 read the wrong docs), not only *wrong-reading* errors. Re-fetching the stored URL would just re-confirm a correlated error → verification theater.
- **Flag B (locked): two clearly-labeled numbers.**
  - **Hand-checked accuracy (n≈15–20)** — the real accuracy number, against human-verified ground truth.
  - **Automated agreement rate (n=100)** — pass-1 vs blind-pass-2 agreement. Labeled as *agreement*, never "accuracy".
  - Conflating these is the easiest thing to get called out on in an interview; separating them reads as rigor.
- **Flag C:** `confidence` is self-scored → used only to *triage* which apps to hand-check. Miscalibration risk noted in the report.
- **Flag D (locked, cheap): no invented evidence.** `evidence_urls` may contain only URLs actually returned/fetched this run; each must resolve (HTTP 200) before saving. Any claim with no backing fetched URL → confidence drop + flag.
- **Flag E:** hand-check is time-boxed — verify only the two highest-risk fields (`auth_methods`, `access_model`) + a glance at buildability, ~5 min/app → ~1.5h for ~18 apps.
- **Flag F:** "no accessible public API" is a **valid finding**, not a failure (see preseed).
- **Flag G:** `existing_mcp = Community` is noisy → best-effort (Official = vendor/first-party or Composio/known registry; Community = quick search, low-confidence).
- **Flag H:** the "real agent" proof is the **CLI** (`python research.py --app stripe`). Optional read-only Composio tool-call demo as a CLI (`demo/composio_demo.py`), NOT a public serverless endpoint (avoids hosted secrets/infra).

---

## 5. Preseed = HYPOTHESES, never facts

`data/preseed.json` holds prior beliefs to *narrow* research, tagged by confidence + a `must_reconfirm` flag. Rules:
1. A preseeded app **still gets one fresh search + ≥1 resolving evidence URL** (Flag D applies to everything). Preseed only skips the *broad multi-page crawl*.
2. If the fresh search **contradicts** the hypothesis, **the search wins** and the contradiction is logged (a caught stale assumption is a good report story).
3. Preseeded apps are **priority hand-check targets** (that's where a stale memory would silently bake in a wrong fact).

### Seed hypotheses
**Confirmed by search (2026-07-09):**
- Amazon Selling Partner API (#49) → **Gated** — paid Professional Seller ($39.99/mo) + developer approval (days–weeks).
- DealCloud (#10) → **Partner-Gated** — broad, well-documented REST/OAuth2 API, but keys only issuable by an admin on an existing paid site; no public trial. Archetype of the **"good API, no entry point"** pattern.

**High-confidence (verify fast):** PitchBook #90 → Partner-Gated · SF Commerce Cloud #44 → Gated (enterprise sales; ≠ core Salesforce free dev org) · Plaid #82 → Self-Serve sandbox + note "production gated by review" · Brex #88 / Ramp #89 → Gated (must be a business customer) · **Binance #83 → Self-Serve easy-win** (API key on signup, no OAuth/partner gate).

**Low-confidence (pipeline decides):** Ahrefs #53 → maybe paid-tier gated · GoHighLevel #34 → Self-Serve sub-account keys + "marketplace listing needs review" · Fathom #93 → maybe webhook/Zapier-only · Higgsfield #97 → maybe invite/beta.

**Non-API / platform-gated (Flag F):** Sherlock #58, Mermaid CLI #98 → OSS CLI (`api_type` None/SDK) · NotebookLM #91 → no public API (Gemini Enterprise workaround) · Consensus #94 → "OAuth requested" = not yet GA · WhatsApp #28 / Meta Ads #32 / LinkedIn Ads #33 / Google Ads #31 → API exists but behind business verification + app review.

### Report-worthy patterns to surface
- **"API exists ≠ API is accessible"** (WhatsApp/Meta/LinkedIn/Google Ads).
- **"Good API, no entry point"** — Partner-Gated with `main_blocker = "requires existing paid account; no public trial/signup"` (DealCloud; likely Brex/Ramp).
- Dominant auth method; self-serve vs gated by category; most common blocker; count of Build-Now easy wins.

---

## 6. Tasks (build in order; each works before the next; time-boxed)

| # | Task | Output / demo | ~time |
|---|------|---------------|-------|
| 1 | Scaffold + `config.py` (OpenRouter) + `.env.example` + `requirements.txt` | repo runs, env loads | 30m |
| 2 | `data/apps.json` (exact 100 + categories) + `data/preseed.json` + `schema.py` (Pydantic, enums, ≤120, JSON-schema export) | sample record validates; bad enum fails | 40m |
| 3 | `composio_lookup.py` — toolkit Yes/No + MCP hint, cached | `lookup("github") → Yes` | 30m |
| 4 | `docs_research.py` — search + fetch, evidence extraction, fetched-URL whitelist, fallback + logging | Stripe → evidence + real URLs | 60–75m |
| 5 | `synthesis.py` — OpenRouter structured JSON → full record + reasoning log | one complete record + reasoning | 45–60m |
| 6 | `pipeline.py` + `research.py` CLI — `research_app()`, single-app CLI | `--app notion` → one record | 30m |
| 7 | Batch all 100 → `out/results.json` + `failures.log` + aggregates (concurrency, resumable cache; 3-app dry run first) | results.json + stats | 45–60m (mostly unattended) |
| 8 | `verify.py` — blind re-search verification → `out/metrics.json` (before/after, agreement rate) | corrected record + agreement summary | 45–60m |
| 9 | Hand-check harness (15–20 apps, biased to preseed + low-confidence) → fold into metrics | hit/miss table + real accuracy | 90m |
| 10 | `report/index.html` (Patterns → Matrix → Agent → Verification → Proof) + README + Vercel deploy + smoke | live URL renders report | 90m + 40m |

### Cut-order if time runs short (never cut accuracy)
optional Composio demo → hand-check 20→15 → UI polish (keep filter/sort, drop animations) → `existing_mcp` Community depth.
**Keep Flags A, B, D intact regardless.**

---

## 7. Report page (single scroll, ~2 min, no narration)
1. **Patterns** — data-driven headline stats first (auth distribution, self-serve vs gated by category, top blocker, easy-win count, the two named patterns). The payoff, not buried.
2. **Matrix** — all 100 apps, filterable/sortable/searchable, clean.
3. **Agent** — what the pipeline does + specific apps where a human stepped in.
4. **Verification** — hand-checked accuracy vs automated agreement (two labeled numbers), the hand-check sample, named hits/misses.
5. **Proof** — repo link, `python research.py --app <slug>` command, optional Composio demo output.

---

## 8. Human-intervention log (tracked as we go, surfaced in README + report)
Record specifically: which apps needed a browser-use fallback (if any), which preseed hypotheses the pipeline contradicted, which docs were un-fetchable, and every hand-check disagreement (app, field, agent value, true value, why).

---

## 9. Repo layout
```
composio/
├── plan.md  README.md  requirements.txt  .env.example  .gitignore
├── config.py            # env + OpenRouter client factory + model config
├── schema.py            # Pydantic models, enums, validation, JSON-schema export
├── research.py          # CLI: --app | --all | --verify | --handcheck-template | --fold-handcheck | --build-report
├── composio_lookup.py docs_research.py synthesis.py pipeline.py verify.py handcheck.py
├── data/    apps.json  preseed.json
├── demo/    composio_demo.py            # optional read-only Composio tool call
├── out/     results.json  metrics.json  failures.log  reasoning/<slug>.md
└── report/  index.html  app.js  data.js  vercel.json   (data.js regenerated by --build-report)
```
(Flattened to project root — no `research/` package — so the `research.py` CLI name is free.)

## 10. Keys required (never committed; `.env`)
- `OPENROUTER_API_KEY` (+ `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL`)
- `COMPOSIO_API_KEY`
- (optional demo) a Composio connected account for GitHub or Notion, read-only.
