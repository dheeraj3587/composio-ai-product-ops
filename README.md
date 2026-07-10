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
- **Hand-checked accuracy: 95.1% as measured in the published snapshot** (n=27, field-level over api_type + auth + access) —
  the ground-truth number. Four measured auth discrepancies are shown openly: DealCloud, Notion,
  Slack, and Cloudflare. The first three are tracked as historical corrections; Cloudflare remains visible.
- **Accuracy moved 84.0% → 95.1%** on the 27-app hand-check sample *because of the verification loops*
  (5 apps factually corrected: Copper, Plain, WhatsApp Business, LinkedIn Ads, Airtable; 0 regressed).
  Both sides are label-canonicalized, so the delta counts **factual fixes only**; label formatting is
  data hygiene, not accuracy. Misses are shown, not hidden.
- **Blind re-search agreement: ~59%** (n≈21) — labeled as *reproducibility, not accuracy*.
- **Browser-Use Cloud loop:** 12 apps re-checked against live docs. The published snapshot's legacy
  summary recorded **6 API/access disagreements**; hardened runs now retain all three field comparisons
  and require an explicit human adjudication before any disagreement is called a correction.
- **existing_mcp false-negative sweep:** the first batch derived `existing_mcp` from API-reference
  pages (which rarely mention MCP) and marked **30 official MCP servers as "None"** across two
  review sweeps — including GitHub, Stripe, Cloudflare, Slack, Airtable, Ramp, Twilio, Salesforce,
  Snowflake, WooCommerce, Zoho CRM, Consensus, and others. Each fixed row carries the vendor's own MCP page as
  evidence, the corrections are centralized in `corrections.py`, and future runs get a dedicated MCP
  probe in `docs_research.py`. A follow-up false-positive audit also downgraded 3 unsupported
  `Official` claims, and a third targeted sweep re-fixed two rows a prior pass had mis-audited
  (Fathom `None`→`Official`, MrScraper `Community`→`Official`) plus GoHighLevel's dead evidence
  link — so the final official MCP count moved **35 → 64**.
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
     ├─ docs_research.py     two-query SEARCH + balanced/ranked direct FETCH, claim-topic checks,
     │                        + a dedicated "official MCP server" probe for existing_mcp
     ├─ synthesis.py         LLM -> strict semantic validation + one constrained repair
     │                        cites ONLY fetched URLs; invalid enums/contradictions are rejected
     ├─ verify.py            LOOP 1: BLIND re-search -> auditable disagreements (never auto-folded)
     └─ pipeline.py          orchestration: concurrent, resumable, one pinned synthesis model
  browser_verify.py          LOOP 2: Browser Use Cloud agent on live docs (isolated .venv-browser)
  handcheck.py               LOOP 3: current human-check accuracy + separate historical snapshots
  corrections.py             legacy migration used only to reproduce the published reviewed snapshot
        ↓
report/index.html + app.js   renders baked-in data.js  (Findings → Matrix → Agent → Verification → Proof)
```

No second hosted backend, no Docker, no live headless-browser server in production — the report is a
static page rendering baked-in JSON.

### Paid research layer — Perplexity Search + native Google Gen AI

`docs_research.py` uses the official Perplexity Search SDK to discover candidate documentation. It
batches related queries into one request, caches responses for seven days, and then fetches pages
directly before they can enter the citation whitelist. Search snippets alone are never accepted as
evidence.

`config.py` uses the native Google Gen AI SDK with Pydantic response schemas. The fresh-run model is
`gemini-3.1-pro-preview` with medium thinking: one pinned model keeps judgments comparable across all
100 apps, while deterministic validators remain the final authority for schema, semantics, and
citations. There is intentionally no gateway fallback or cross-model sharding.

Every paid call is recorded in `out/usage.json`. Default run caps are $2 for Perplexity and $8 for
Google; the pipeline refuses a call whose conservative estimate would cross its provider cap.

---

## Verification (three loops + honest numbers)

1. **Blind re-search from scratch** (`verify.py`) — issues two fresh queries, fetches pages that
   **exclude the stored URLs**, then re-derives canonical `auth_methods` + production `access_model`
   **without seeing pass-1's answer**. Every check stores its queries, fetched URLs, answering model,
   before/verifier values, and source-independence metadata. It never mutates records or confidence.
2. **Browser Use Cloud** (`browser_verify.py`) — a cloud browser agent independently navigates each
   app's live developer docs and re-derives api_type/auth/access. Output uses the same controlled
   vocabulary and production-access rule; disagreements remain `Pending` until human adjudication.
3. **Human hand-check** (`handcheck.py`) — a person verifies api_type + exact canonical auth set +
   production access against official docs. This is the **ground-truth accuracy** number. Current and
   historical snapshots are stored separately; scoring never swaps in old agent values.

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
| `PERPLEXITY_API_KEY` | Perplexity Search API for documentation discovery |
| `GOOGLE_GENAI_API_KEY` | Native Google Gen AI synthesis and verification |
| `GOOGLE_GENAI_MODEL` | Pinned synthesis model; default `gemini-3.1-pro-preview` |
| `PERPLEXITY_RUN_BUDGET_USD` / `GOOGLE_RUN_BUDGET_USD` | Per-run safety caps; defaults `$2` / `$8` |
| `COMPOSIO_API_KEY` | Composio toolkit lookup (recommended; HTTP-catalog fallback if absent) |
| `BROWSER_USE_API_KEY` | *optional* — Browser Use Cloud verification loop (`browser_verify.py`) |

### Fresh run end-to-end

```bash
python research.py --app stripe             # 1) live sanity check; does not merge a results row
python research.py --all --fresh-run         # 2) archive old state, research all 100
# If any app failed: rerun --all, then capture the complete snapshot once:
python research.py --snapshot-first-pass        # 3) only needed after an interrupted fresh run
python research.py --verify --sample 24         # 4) blind re-search; facts remain unchanged
.venv-browser/bin/python browser_verify.py --sample 12 --batch-size 6  # 5) live-doc loop
python research.py --handcheck-template 24      # 6) create risk-biased worksheet
# Fill official-doc truth + evidence URLs in handcheck/handcheck.json.
python research.py --fold-handcheck             # 7) current ground-truth metric
python research.py --accuracy-movement          # 8) first-pass vs current on same truth
python research.py --metrics                    # 9) rebuild all derived metrics
python research.py --build-report               # 10) publish only after review
```

- **Safe fresh state:** `--fresh-run` archives generated results, metrics, reasoning, browser output,
  and hand-check truth under ignored `out/archive/<timestamp>/`; it deliberately leaves `report/`
  unchanged until `--build-report`.
- **Immutable baseline:** a complete fresh run writes `results_firstpass.json` automatically. If the
  run was interrupted, resume it and call `--snapshot-first-pass`; that command refuses to overwrite.
- **Resumable:** `--all` skips apps already in `results.json`; re-run after interruption.
- **Honest failures:** current unresolved failures live in `out/failures.json`; append-only
  `out/failures.log` keeps failed/resolved history. Ambiguous apps are never guessed.
- **No automatic correction fold:** verification outputs disagreements for adjudication. `corrections.py`
  is retained only to reproduce the legacy published snapshot and is not part of a fresh run.

### Loop 2 — Browser Use Cloud (isolated env)

Kept in a separate venv so its heavy deps don't touch the pipeline:

```bash
python -m venv .venv-browser && .venv-browser/bin/pip install browser-use
.venv-browser/bin/python browser_verify.py --sample 12 --batch-size 6   # ~2 cloud tasks
```
Writes `out/browser_verification.json` with field comparisons and adjudication state; `--metrics`
summarizes disagreements separately from accepted corrections.

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
| `--recheck a,b,c` | re-research given slugs and **merge** into results.json (keeps all other rows) |
| `--fresh-run` | with `--all`, archive generated state and start clean without touching `report/` |
| `--snapshot-first-pass` | capture a complete baseline once; refuses incomplete data or overwrite |
| `--verify [--sample N]` | blind re-search audit; writes evidence/provenance but never changes rows |
| `--handcheck-template [N]` | generate a hand-check worksheet (default 18) |
| `--fold-handcheck` | LOOP 3: fold filled hand-check truth into metrics (per-field accuracy + misses) |
| `--accuracy-movement` | score first-pass snapshot vs post-verification results vs hand truth |
| `--metrics` | rebuild `metrics.json` (patterns + headline numbers) |
| `--build-report` | copy results/metrics into `report/` and write `data.js` |
| `--workers N` · `--model M` · `--no-resume` | execution knobs (`--no-shard` is compatibility-only) |

---

## Regression checks

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
ruff check *.py tests demo
python -m compileall -q *.py tests demo
```

The focused suite covers evidence-slot starvation, claim-topic detection, strict auth normalization,
LLM repair, non-mutating verification, browser disagreement semantics, fresh-run archival, failure
recovery state, and current-only hand-check scoring.

---

## Where a human steps in (honest)

- **Preseed priors** (`data/preseed.json`, ~20 apps): human hypotheses (e.g. Amazon SP-API is gated;
  DealCloud is "good API, no entry point"). They are **hypotheses only** — the pipeline re-confirms each
  with a fresh search and **trusts evidence over the prior**, logging contradictions.
- **Hand-check** (27 apps): a human verifies api_type + auth + access against real docs; hits and
  misses are shown in the report and `metrics.json`, not hidden.
- **Browser adjudication:** Browser Use Cloud flags disagreements; a human must accept/reject each
  against official docs. New output stores that decision explicitly. The published legacy snapshot
  used `corrections.py`; fresh runs do not auto-apply that migration.
- **Thin/unfetchable docs:** retained in current failure state; synthesized degraded records cap
  confidence, while no-fetched-source cases fail instead of guessing.

## Honest limitations

- `composio_toolkit` via the public catalog is a **heuristic** when the SDK isn't available; the SDK path is authoritative.
- `existing_mcp` is an automated signal (not part of the formal 27-app hand-check), and it burned us
  in **both** directions: the first audit stress-checked the 18 most-doubtful `Official` claims
  (16 held up; Binance → Community, DealCloud → None) but never audited the `None` claims. Two
  follow-up sweeps found 29 false negatives with official vendor MCP pages. Root cause:
  API-reference evidence rarely mentions MCP. Fixed in `corrections.py` with vendor evidence, and
  prevented going forward by the dedicated MCP probe in `docs_research.py`. Remaining
  `None`/`Community` rows have not all been re-swept by hand — treat that field as verified-on-fix,
  not hand-checked.
- Self-scored `confidence` can be miscalibrated. Automated verification no longer changes it; the
  **hand-checked** number, not confidence, is the accuracy claim.
- The published snapshot was produced by a mix of models. The next fresh run pins
  `gemini-3.1-pro-preview`; every reasoning/check artifact records the exact model used. Because this
  model is a preview, a later rerun should first repeat the one-app smoke test.
- The published hand-check file used a looser trial-access rule. New templates define access by
  production usability and keep current metrics separate from historical snapshots.

## Repo layout

```
composio/
├── research.py            CLI (the agent entry point)
├── config.py  schema.py   native Google Gen AI + paths; locked Pydantic schema
├── usage_tracker.py       paid-call ledger and per-provider run caps
├── normalize.py           canonical auth-label normalization
├── composio_lookup.py  docs_research.py  synthesis.py  pipeline.py  verify.py  handcheck.py
├── corrections.py         legacy migration for reproducing the published reviewed snapshot
├── browser_verify.py      Browser Use Cloud verification loop (runs in .venv-browser)
├── data/       apps.json  preseed.json
├── handcheck/  handcheck.json                                       (hand-verified truth)
├── out/        results.json  metrics.json  usage.json  browser_verification.json  archive/ (ignored)
│               results_firstpass.json  failures.json  failures.log  reasoning/<slug>.md
├── report/     index.html  app.js  data.js  vercel.json             (static site)
├── demo/       composio_demo.py                                     (optional read-only tool-call)
└── plan.md  requirements.txt  .env.example  .gitignore
```
