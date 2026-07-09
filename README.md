# API Integration Readiness — Research Agent

An autonomous pipeline that researches the **API integration readiness of 100 apps**
(10 categories) into a **locked 19-field schema**, **independently re-verifies its own
findings through three loops** (blind re-search + a live-browser agent + a human
hand-check), and renders everything on a **single static HTML page**.

> **Live report:** https://composio-ai-product-ops.vercel.app · **Repo:** https://github.com/dheeraj3587/composio-ai-product-ops

Built for the accuracy-first bar: correct facts about auth/access/API surface first,
clear cross-app patterns second, honest verification third.

---

## Headline results (current run)

- **100 / 100 apps** researched, schema-valid, every row backed by a real, resolving evidence URL.
- **Hand-checked accuracy: 94.1% as measured** (n=17, field-level over api_type + auth + access) —
  the ground-truth number. The 3 auth misses it caught (DealCloud, Notion, Slack) have since been
  folded back into the matrix via `corrections.py`, so the shipped rows carry the verified truth.
- **Accuracy moved 78.4% → 94.1%** on the hand-check sample *because of the verification loops*
  (4 apps factually corrected: Copper, Plain, WhatsApp Business, LinkedIn Ads; 0 regressed).
  Scored with both sides label-canonicalized so the delta counts **factual fixes only** — the raw
  scorer previously reported 62.7% → 94.1%, but 8 of those first-pass "misses" were label-format
  artifacts ("OAuth 2.0" vs "OAuth2"), which is data hygiene, not accuracy. Misses shown, not hidden.
- **Blind re-search agreement: ~59%** (n≈21) — labeled as *reproducibility, not accuracy*.
- **Browser-Use Cloud loop:** 12 apps re-checked against live docs; caught **6** first-pass errors
  static fetch missed (e.g. Copper and Plain, which the first pass had wrongly marked "no API").
- **existing_mcp false-negative sweep:** the first batch derived `existing_mcp` from API-reference
  pages (which rarely mention MCP) and marked **30 official MCP servers as "None"** across two
  review sweeps — including GitHub, Stripe, Cloudflare, Slack, Airtable, Ramp, Twilio, Salesforce,
  Snowflake, WooCommerce, Zoho CRM, Consensus, and others. Each fixed row carries the vendor's own MCP page as
  evidence, the corrections are centralized in `corrections.py`, and future runs get a dedicated MCP
  probe in `docs_research.py`. A follow-up false-positive audit also downgraded 3 unsupported
  `Official` claims, so the final official MCP count moved **35 → 62**.
- **Two named patterns:** *"API exists ≠ API is accessible"* (WhatsApp/Meta/LinkedIn/Google Ads have
  APIs but gate access behind review/verification) and *"good API, no entry point"* (DealCloud-style:
  solid API, but keys require being an existing paying customer → Partner-Gated).
- **Composio overlap surfaced:** 49 of the 100 requested apps have **no Composio toolkit yet**; the
  self-serve Build Now subset of those is the immediate build queue (own column + insight on the report).

Full live matrix + pattern charts are on the report.

---

## What it produces

For each app, one record on this **locked schema** (19 fields):

`app · category · one_liner (≤120) · auth_methods[] · access_model{kind: Self-Serve|Gated, note} ·
api_type (REST|GraphQL|SDK|SOAP|MCP-only|None) · api_breadth (Narrow|Moderate|Broad) ·
existing_mcp (Official|Community|None) · composio_toolkit (Yes|No) ·
buildability (Easy|Moderate|Hard|Blocked) · main_blocker · recommended_next_action
(Build Now|Needs Outreach|Partner-Gated|Blocked) · evidence_urls[] · confidence (0–1) ·
verification_status (Auto|Hand-Checked) · slug · primary_docs_url · rate_limit_note · last_verified`

Auth labels are normalized to a canonical set (`normalize.py`): `OAuth2 · API Key · Bearer Token ·
Basic Auth · Personal Access Token · Service Account · Bot Token · Other Token · None / Not Applicable`.

Generated outputs land in `out/` and are baked into `report/` for deploy.

---

## Architecture (lean — single static deploy)

```
research.py (offline CLI = the agent)
  data/apps.json + data/preseed.json
     ├─ composio_lookup.py   composio_toolkit (Yes/No) via Composio SDK / public catalog
     ├─ docs_research.py     web SEARCH + direct FETCH (+ developer-subdomain probing,
     │                        + a dedicated "official MCP server" probe for existing_mcp)
     ├─ synthesis.py         LLM (OpenAI-compatible) -> locked schema + reasoning log
     │                        cites ONLY fetched, resolving URLs — no invented sources
     ├─ verify.py            LOOP 1: BLIND re-search from scratch -> agreement + metrics.json
     └─ pipeline.py          orchestration: concurrent, resumable, optional provider sharding
  browser_verify.py          LOOP 2: Browser Use Cloud agent on live docs (isolated .venv-browser)
  handcheck.py               LOOP 3: human check on ~17 apps -> ground-truth accuracy + movement
  corrections.py             documented, re-runnable migration: auth normalization + per-app fixes
        ↓
report/index.html + app.js   renders baked-in data.js  (Findings → Matrix → Agent → Verification → Proof)
```

No second hosted backend, no Docker, no live headless-browser server in production — the report is a
static page rendering baked-in JSON.

### LLM layer — configurable, OpenAI-compatible, multi-provider

`config.py` supports any OpenAI-compatible provider and an **ordered fallback chain** (`llm_json()`
tries each tier until one succeeds), with optional **round-robin sharding** across providers to beat
free-tier rate limits.

**Current / recommended config (`.env`):** OpenRouter with a paid model —
`anthropic/claude-opus-4.8` → `openai/gpt-5-mini` → `google/gemini-2.5-flash`.
Providers wired: `openrouter`, `zenmux`, `google` (Gemini), `agentrouter`. Configure via
`LLM_PROVIDER` / `LLM_MODEL` / `LLM_FALLBACK_*` / `LLM_FALLBACK2_*`, `LLM_SHARD_PROVIDERS`,
or a single `LLM_CHAIN="provider:model, provider:model"`. Permanent 4xx (e.g. a 402 "needs
balance") are not retried; a tier that returns empty output falls through to the next.

---

## Verification (three loops + honest numbers)

1. **Blind re-search from scratch** (`verify.py`) — issues a *fresh, differently-phrased* query and
   fetches pages that **exclude the stored URLs**, then re-derives `auth_methods` + `access_model`
   **without seeing pass-1's answer**. Catches wrong-*page* errors, not just wrong-reading.
   (Re-fetching the stored URL would only re-confirm a correlated error.)
2. **Browser Use Cloud** (`browser_verify.py`) — a cloud browser agent independently navigates each
   app's live developer docs and re-derives api_type/auth/access. Independent of the pipeline's own
   search+fetch *and* LLM, so it catches JS-rendered docs and marketing-homepage misses.
3. **Human hand-check** (`handcheck.py`) — a person verifies api_type + auth + access on ~17 apps
   against real docs. This is the **ground-truth accuracy** number; misses are listed in `metrics.json`.

Two clearly-labeled numbers: **hand-checked accuracy** (ground truth) vs **automated blind re-search
agreement** (reproducibility). `confidence` is a self-scored triage signal, **not** an accuracy claim.

---

## Composio usage

Composio is used as the authoritative **toolkit-existence signal** (`composio_toolkit` Yes/No, via the
Composio SDK with a public-catalog HTTP fallback). Scope choice: the research agent's job is to evaluate
100 *other* apps' APIs, so Composio is the ground-truth source for "does a toolkit already exist," not
the calling layer of the research itself. A read-only Composio tool-call demo lives in `demo/composio_demo.py`.

---

## Quickstart

Requires **Python 3.10+** (the optional Composio SDK's dependency tree needs it; the
requirement is version-guarded so installs on older interpreters still resolve).

```bash
git clone https://github.com/dheeraj3587/composio-ai-product-ops.git && cd composio-ai-product-ops
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # then edit .env
```

`.env` keys:

| Key | Purpose |
|-----|---------|
| `OPENROUTER_API_KEY` | LLM provider (recommended primary). Default model `anthropic/claude-opus-4.8` |
| `LLM_MODEL` / `LLM_FALLBACK_MODEL` / `LLM_FALLBACK2_MODEL` | chain, e.g. `anthropic/claude-opus-4.8` → `openai/gpt-5-mini` → `gemini-2.5-flash` |
| `COMPOSIO_API_KEY` | Composio toolkit lookup (recommended; HTTP-catalog fallback if absent) |
| `GOOGLE_API_KEY` / `ZENMUX_API_KEY` / `AGENTROUTER_API_KEY` | *optional* extra providers for the chain / sharding |
| `BROWSER_USE_API_KEY` | *optional* — Browser Use Cloud verification loop (`browser_verify.py`) |
| `TAVILY_API_KEY` / `SERPER_API_KEY` | *optional* better search; keyless DuckDuckGo is the default |

### Run end-to-end

```bash
python research.py --app stripe        # 1) sanity-check one app live (prints record; no writes)
python research.py --limit 5           # 2) small dry run
python research.py --all               # 3) research all 100 (concurrent + resumable)
python research.py --verify            # 4) LOOP 1: blind re-search -> metrics.json
python research.py --handcheck-template 18   # 5) generate hand-check worksheet
#    ...fill truth in handcheck/handcheck.json (~5 min/app)...
python research.py --fold-handcheck    # 6) LOOP 3: fold hand-checked ground truth
python research.py --accuracy-movement # 7) first-pass vs post-verification accuracy delta
python research.py --build-report      # 8) bake data into report/ (writes data.js)
```

- **Resumable:** `--all` skips apps already in `results.json`; re-run after interruption.
- **Honest failures:** unresearched/ambiguous apps are logged to `out/failures.log`, never guessed.
- **Corrections migration:** `python corrections.py` re-applies auth normalization + the documented,
  evidence-backed per-app fixes (Otter MCP, Copper/Plain APIs, Binance/DealCloud MCP, weak-evidence
  confidence, etc.) and re-validates all 100 against the locked schema. Re-run it after any `--no-resume`.

### Loop 2 — Browser Use Cloud (isolated env)

Kept in a separate venv so its heavy deps don't touch the pipeline:

```bash
python -m venv .venv-browser && .venv-browser/bin/pip install browser-use
.venv-browser/bin/python browser_verify.py --sample 12 --batch-size 6   # ~2 cloud tasks
```
Writes `out/browser_verification.json`; `--build-report` folds its summary into the report.

### View locally / deploy

```bash
cd report && python -m http.server 8000       # open http://localhost:8000
cd report && vercel --prod                    # deploy report/ as a static site
```
or point a Vercel project at the repo with **Root Directory = `report`** (no build step).

---

## CLI reference (`research.py`)

| Command | Does |
|---------|------|
| `--app <slug>` | research one app, print the record + reasoning-log path (no file writes) |
| `--all` | research all 100 (concurrent, resumable) |
| `--slugs a,b,c` | research a subset |
| `--limit N` | research the first N apps |
| `--recheck a,b,c` | re-research given slugs and **merge** into results.json (keeps the rest + corrections) |
| `--verify [--sample N]` | LOOP 1 blind re-search verification (default: all records) |
| `--handcheck-template [N]` | generate a hand-check worksheet (default 18) |
| `--fold-handcheck` | LOOP 3: fold filled hand-check truth into metrics (per-field accuracy + misses) |
| `--accuracy-movement` | score first-pass snapshot vs post-verification results vs hand truth |
| `--metrics` | rebuild `metrics.json` (patterns + headline numbers) |
| `--build-report` | copy results/metrics into `report/` and write `data.js` |
| `--workers N` · `--model M` · `--no-resume` · `--no-shard` | knobs |

---

## Where a human steps in (honest)

- **Preseed priors** (`data/preseed.json`, ~20 apps): human hypotheses (e.g. Amazon SP-API is gated;
  DealCloud is "good API, no entry point"). They are **hypotheses only** — the pipeline re-confirms each
  with a fresh search and **trusts evidence over the prior**, logging contradictions.
- **Hand-check** (~17 apps): a human verifies api_type + auth + access against real docs; hits and
  misses are shown in the report and `metrics.json`, not hidden.
- **Browser-verification fold:** the Browser Use Cloud loop flagged disagreements; a human adjudicated
  each against official docs (e.g. WhatsApp/Pinterest kept **Gated** despite the browser calling them
  self-serve, because production needs verification/review) and folded corrections via `corrections.py`.
- **Thin/unfetchable docs:** logged to `failures.log`; those records get capped confidence.

## Honest limitations

- `composio_toolkit` via the public catalog is a **heuristic** when the SDK isn't available; the SDK path is authoritative.
- `existing_mcp` is an automated signal (not part of the formal 17-app hand-check), and it burned us
  in **both** directions: the first audit stress-checked the 18 most-doubtful `Official` claims
  (16 held up; Binance → Community, DealCloud → None) but never audited the `None` claims. Two
  follow-up sweeps found 29 false negatives with official vendor MCP pages. Root cause:
  API-reference evidence rarely mentions MCP. Fixed in `corrections.py` with vendor evidence, and
  prevented going forward by the dedicated MCP probe in `docs_research.py`. Remaining
  `None`/`Community` rows have not all been re-swept by hand — treat that field as verified-on-fix,
  not hand-checked.
- Self-scored `confidence` can be miscalibrated — that's exactly why the **hand-checked** number, not
  confidence, is the accuracy claim.
- The dataset was produced by a mix of models (free-tier during the batch, plus targeted re-checks); it
  is trustworthy because it was **verified**, not because of the model that produced it.

## Repo layout

```
composio/
├── research.py            CLI (the agent entry point)
├── config.py  schema.py   multi-provider LLM chain + paths; locked Pydantic schema
├── normalize.py           canonical auth-label normalization
├── composio_lookup.py  docs_research.py  synthesis.py  pipeline.py  verify.py  handcheck.py
├── corrections.py         documented, re-runnable per-app corrections migration
├── browser_verify.py      Browser Use Cloud verification loop (runs in .venv-browser)
├── data/       apps.json  preseed.json
├── handcheck/  handcheck.json                                       (hand-verified truth)
├── out/        results.json  metrics.json  browser_verification.json
│               results_firstpass.json  failures.log  reasoning/<slug>.md   (generated)
├── report/     index.html  app.js  data.js  vercel.json             (static site)
├── demo/       composio_demo.py                                     (optional read-only tool-call)
└── plan.md  requirements.txt  .env.example  .gitignore
```
