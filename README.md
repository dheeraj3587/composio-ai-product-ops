# API Integration Readiness Research Agent

Research pipeline and static report for the Composio AI Product Ops take-home.

Live report: https://composio-ai-product-ops.vercel.app

Repository: https://github.com/dheeraj3587/composio-ai-product-ops

The project researches 100 apps across 10 categories and scores whether each one is ready for an API/toolkit integration. The output is a locked 19-field dataset plus a reviewer-friendly dashboard.

## Current Snapshot

- 100 apps researched and rendered in the final report.
- 100 / 100 rows pass schema, citation, app identity, and source-quality checks.
- 49 apps have no Composio toolkit yet.
- 63 apps are marked `Build Now`; 19 need outreach; 16 are partner-gated; 2 are blocked.
- 69 apps have an official MCP server signal; 25 community; 6 none.
- 45 reviewer-priority apps were hand-checked against official docs across all 10 categories.
- The latest pre-fold hand-check measured 91.7% across API type, exact auth, production access, and MCP ownership.
- After applying the same verified truth set, the checked sample scores 100%.
- All 15 pre-correction field misses across 12 apps remain disclosed in the report.

## What The Agent Produces

Each app is written to a locked 19-field schema:

`app · category · one_liner · auth_methods[] · access_model · api_type · api_breadth · existing_mcp · composio_toolkit · buildability · main_blocker · recommended_next_action · evidence_urls[] · confidence · verification_status · slug · primary_docs_url · rate_limit_note · last_verified`

The important distinction is deliberate:

- `handcheck.accuracy` is the human-verified accuracy score.
- `accuracy_movement` compares the archived first pass against the corrected current dataset.
- `confidence` is only a triage signal, not an accuracy claim.
- Browser evidence is evidence acquisition, not a separate accuracy number.
- Every app keeps its original research trace, model rationale, source fetches, and final decision record. The dashboard exposes these through the per-app `Reasoning` drawer.

## Architecture

```text
research.py
  data/apps.json
  data/preseed.json       risk sampling only; hypotheses are withheld from the model
    -> composio_lookup.py   checks Composio toolkit coverage
    -> docs_research.py     fetches balanced auth + pricing/production evidence
    -> synthesis.py         asks the pinned LLM for a strict, evidence-grounded record
    -> schema.py            validates enums, required fields, and semantic dependencies
    -> verify.py            rebuilds metrics and source-quality checks
    -> handcheck.py         scores and applies official-doc human checks
    -> out/reasoning/*.md   preserves the per-app research and synthesis trace
    -> report/data.js       bakes results, metrics, and reasoning into the static dashboard
```

The production report is static: no backend, no live headless browser, and no runtime model calls.

Fresh research has a fail-closed evidence gate. It reserves fetch slots for auth,
API shape, and plan/production entitlement; extracts conservative auth and access
signals; follows official Markdown variants when an HTML docs shell advertises
one; and rejects unresolved rows before a paid synthesis call. A signup or
key-generation page alone cannot prove production access. Historical preseeds
still prioritize risky apps for verification, but their values are never shown
to the synthesis model.

## Composio Usage

Composio is used for the `composio_toolkit` field. The pipeline checks whether Composio already has coverage for each app through the SDK when available, with a public-catalog fallback.

The research task itself evaluates external app APIs, so Composio is used as the source of truth for toolkit overlap rather than as the LLM orchestration layer. A minimal read-only SDK demo lives at `demo/composio_demo.py`.

## Verification Model

The project separates automated checks from human judgment:

1. Source audit validates schema shape, URL quality, app identity, and first-party coverage.
2. Browser evidence stores official pages that needed live browser reading.
3. Human handcheck verifies selected high-usage apps against official vendor docs.
4. Corrections are applied only after the handcheck score is preserved.

Current human-check fields:

- API type: 100%
- Auth methods: 84.4%
- Production access: 82.2%
- MCP ownership: 100%
- Overall pre-fold snapshot: 91.7%

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Required keys for fresh research:

| Key | Purpose |
| --- | --- |
| `PERPLEXITY_API_KEY` | Documentation search |
| `GOOGLE_GENAI_API_KEY` | Synthesis and verification |
| `COMPOSIO_API_KEY` | Composio toolkit lookup |
| `BROWSER_USE_API_KEY` | Optional browser verification loop |

## Fresh Run

```bash
python research.py --app stripe
python research.py --batch-submit --fresh-run --model gemini-3.1-pro-preview
python research.py --batch-status
python research.py --batch-collect
python research.py --verify --sample 24
python research.py --handcheck-template 24
# Fill handcheck/handcheck.json from official docs.
python research.py --fold-handcheck
python research.py --apply-handcheck
python research.py --accuracy-movement
python research.py --metrics
python research.py --build-report
```

Generated runtime state such as provider usage ledgers, batch state, failures, cache files, and previous archives is ignored. The committed evidence is the final dataset, metrics, reasoning logs, browser evidence summary, and handcheck file.

## View The Report

```bash
cd report
python -m http.server 8000
```

Open http://localhost:8000.

Deploy from `report/`:

```bash
cd report
vercel deploy --prod
```

## Tests

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
ruff check *.py tests demo
python -m compileall -q *.py tests demo
node --check report/app.js
```

## Repo Layout

```text
composio/
├── research.py
├── batch_pipeline.py
├── composio_lookup.py
├── docs_research.py
├── synthesis.py
├── verify.py
├── handcheck.py
├── schema.py
├── normalize.py
├── data/
├── handcheck/handcheck.json
├── out/
│   ├── results.json
│   ├── results_firstpass.json
│   ├── metrics.json
│   ├── browser_evidence.json
│   └── reasoning/
├── report/
│   ├── index.html
│   ├── app.js
│   ├── theme.css
│   ├── data.js
│   ├── data/reasoning.json
│   └── vercel.json
├── tests/
├── demo/
├── requirements.txt
└── requirements-dev.txt
```
