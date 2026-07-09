# API Integration Readiness — Research Agent

An autonomous pipeline that researches the **API integration readiness of 100 apps**
(10 categories) into a locked 19-field schema, **independently re-verifies its own
findings**, folds in a hand-checked sample, and renders everything on a **single
static HTML page**.

> **Live report:** https://composio-ai-product-ops.vercel.app · **Repo:** https://github.com/dheeraj3587/composio-ai-product-ops

Built for the accuracy-first grading bar: correct facts about auth/access/API surface
first, clear cross-app patterns second, honest verification third.

---

## What it produces

For each app, one record on this **locked schema** (19 fields):

`app · category · one_liner (≤120) · auth_methods[] · access_model{kind: Self-Serve|Gated, note} ·
api_type (REST|GraphQL|SDK|SOAP|MCP-only|None) · api_breadth (Narrow|Moderate|Broad) ·
existing_mcp (Official|Community|None) · composio_toolkit (Yes|No) ·
buildability (Easy|Moderate|Hard|Blocked) · main_blocker · recommended_next_action
(Build Now|Needs Outreach|Partner-Gated|Blocked) · evidence_urls[] · confidence (0–1) ·
verification_status (Auto|Hand-Checked) · slug · primary_docs_url · rate_limit_note · last_verified`

Outputs land in `out/` (`results.json`, `metrics.json`, `failures.log`, `reasoning/<slug>.md`)
and are baked into `report/` for deploy.

---

## Architecture (lean — single static deploy)

```
research.py (offline CLI = the agent)
  data/apps.json + data/preseed.json
     ├─ composio_lookup.py   composio_toolkit (Yes/No) via Composio catalog/SDK
     ├─ docs_research.py     web SEARCH + direct FETCH  (no browser automation)
     ├─ synthesis.py         GPT via OpenRouter -> locked schema + reasoning log
     │                        (may cite ONLY fetched URLs — no invented sources)
     └─ verify.py            BLIND re-search from scratch -> metrics.json
  handcheck.py               human 2-field check on 15–20 apps -> ground-truth accuracy
        ↓
report/index.html + app.js   renders baked-in data.js  (Patterns → Matrix → Agent → Verification → Proof)
```

**LLM = AgentRouter → ZenMux → OpenRouter fallback chain** (all OpenAI-compatible). Default 3-tier chain:
`claude-opus-4-7` (AgentRouter, OpenAI-compatible `/v1`) → `anthropic/claude-fable-5-free` (ZenMux)
→ `tencent/hy3:free` (Tencent Hy3, OpenRouter) — configurable via
`LLM_PROVIDER`/`LLM_MODEL`/`LLM_FALLBACK_*`/`LLM_FALLBACK2_*` (or a single `LLM_CHAIN`).
`llm_json()` tries each tier until one succeeds. No second backend, no Docker, no headless browser in production.

### Verification you can trust
- **Blind re-search from scratch** — the verify pass issues a *fresh, differently-phrased*
  query and fetches pages that **exclude the stored URLs**, then re-derives `auth_methods` +
  `access_model` **without seeing pass-1's answer**. Catches wrong-*page* errors, not just
  wrong-reading. (Re-fetching the stored URL would only re-confirm a correlated error.)
- **Two clearly-labeled numbers** — *hand-checked accuracy* (ground truth, n≈15–20) vs
  *automated blind re-search agreement* (n=100). Agreement is **not** accuracy.
- **No invented evidence** — `evidence_urls` may contain only URLs actually fetched this run.
- **Confidence is a triage signal**, not an accuracy claim.

---

## Quickstart

```bash
git clone https://github.com/dheeraj3587/composio-ai-product-ops.git && cd composio-ai-product-ops
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env       # then edit .env
```

`.env` keys:

| Key | Purpose |
|-----|---------|
| `AGENTROUTER_API_KEY` | preferred LLM provider for Claude Opus via OpenAI-compatible `https://agentrouter.org/v1`; `ANTHROPIC_AUTH_TOKEN` is also accepted as a fallback env name |
| `ZENMUX_API_KEY` | fallback LLM provider (Claude Fable 5) |
| `OPENROUTER_API_KEY` | last-resort fallback provider (Tencent Hy3) — recommended |
| `LLM_MODEL` / `LLM_FALLBACK_MODEL` / `LLM_FALLBACK2_MODEL` | default `claude-opus-4-7` → `anthropic/claude-fable-5-free` → `tencent/hy3:free` |
| `COMPOSIO_API_KEY` | Composio toolkit lookup (recommended; HTTP-catalog fallback if absent) |
| `TAVILY_API_KEY` / `SERPER_API_KEY` | *optional* better search; keyless DuckDuckGo is the default |

### Run end-to-end

```bash
python research.py --app stripe        # 1) sanity-check one app live
python research.py --limit 5           # 2) 5-app dry run
python research.py --all               # 3) research all 100 (concurrent + resumable)
python research.py --verify            # 4) blind re-search verification -> metrics.json
python research.py --handcheck-template 18   # 5) generate hand-check worksheet
#    ...fill truth in handcheck/handcheck.json (~5 min/app, 2 fields)...
python research.py --fold-handcheck    # 6) fold ground-truth accuracy
python research.py --build-report      # 7) bake data into report/
```

Resumable: `--all` skips apps already in `results.json`; re-run after an interruption.
Honest failures: unresearched/ambiguous apps are logged to `out/failures.log`, never guessed.

### View the report locally
```bash
cd report && python -m http.server 8000   # open http://localhost:8000
```

### Deploy (Vercel, static)
```bash
cd report && vercel --prod        # deploy the report/ folder as a static site
```
or point a Vercel project at the repo with **Root Directory = `report`** (no build step).

---

## CLI reference

| Command | Does |
|---------|------|
| `--app <slug>` | research one app, print the record + reasoning-log path |
| `--all` | research all 100 (concurrent, resumable) |
| `--slugs a,b,c` | research a subset |
| `--limit N` | research the first N apps |
| `--verify [--sample N]` | blind re-search verification (default: all records) |
| `--handcheck-template [N]` | generate a hand-check worksheet (default 18) |
| `--fold-handcheck` | fold filled hand-check truth into metrics |
| `--metrics` | rebuild `metrics.json` |
| `--build-report` | copy results/metrics into `report/` (writes `data.js`) |
| `--workers N` · `--model M` · `--no-resume` | knobs |

Optional Composio tool-call demo: `python demo/composio_demo.py` (read-only GitHub/Notion).

---

## Where a human steps in (honest)

- **Preseed priors** (`data/preseed.json`, ~20 apps): human hypotheses (e.g. Amazon SP-API is
  gated; DealCloud is "good API, no entry point"). They are **hypotheses only** — the pipeline
  re-confirms each with a fresh search and **trusts evidence over the prior**, logging contradictions.
- **Hand-check** (15–20 apps): a human verifies `auth_methods` + `access_model` against real docs;
  hits and misses are shown in the report, not hidden.
- **Thin/unfetchable docs**: logged to `failures.log`; those records get capped confidence.
- **Browser automation**: not used by default — search + direct fetch was sufficient. If ever used
  for an inaccessible doc, it is disclosed on the report.

## Honest limitations
- `composio_toolkit` via the public catalog is a **heuristic** when the SDK isn't available; the
  Composio SDK path is authoritative.
- `existing_mcp` is an automated signal (not part of the 17-app formal hand-check). I stress-checked
  the 18 most-doubtful `Official` claims against vendor docs — 16 held up, 2 were corrected
  (Binance → Community, DealCloud → None). `Community` is the noisiest value.
- Self-scored `confidence` can be miscalibrated — that's exactly why the hand-checked number, not
  confidence, is the accuracy claim.

## Repo layout
```
composio/
├── research.py            CLI (the agent entry point)
├── config.py schema.py    OpenRouter client + paths; locked Pydantic schema
├── composio_lookup.py docs_research.py synthesis.py pipeline.py verify.py handcheck.py
├── data/      apps.json  preseed.json
├── out/       results.json  metrics.json  failures.log  reasoning/<slug>.md   (generated)
├── report/    index.html  app.js  data.js  vercel.json                        (static site)
├── demo/      composio_demo.py                                                (optional)
└── plan.md  requirements.txt  .env.example
```
