# Composio API Integration Readiness

Reproducible research pipeline and static decision dashboard for the Composio AI Product Ops take-home. It evaluates 100 requested apps across API shape, authentication, production access, MCP ownership, Composio coverage, and implementation readiness.

- Live report: https://composio-ai-product-ops.vercel.app
- Repository: https://github.com/dheeraj3587/composio-ai-product-ops

## Results

- 100 / 100 apps pass schema, citation, app-identity, and source-quality checks.
- Composio SDK coverage: 50 active toolkits, 1 catalog-only entry (Front), and 49 missing apps.
- The active catalog exposes 6,902 tools in total (median 97); 16 toolkits expose triggers.
- Recommended action: 63 `Build Now`, 19 `Needs Outreach`, 16 `Partner-Gated`, and 2 `Blocked`.
- The immediate uncovered queue contains 29 build-ready apps. Front is tracked separately as a toolkit-expansion opportunity.
- 45 priority apps were adjudicated against official docs; 16 additional apps were independently checked in a live browser.

## Reviewer Artifacts

Each committed artifact has one role:

| Artifact | Purpose |
| --- | --- |
| `out/results.json` | Canonical current 100-app dataset. |
| `out/results_firstpass.json` | Immutable first-pass snapshot used for before/after accuracy. |
| `out/metrics.json` | Derived patterns, verification summaries, and report metadata. |
| `out/composio_coverage.json` | Authoritative SDK-only `Active` / `Catalog-only` / `Missing` audit. |
| `out/reasoning/*.md` | Original evidence trace, model rationale, and final adjudicated state for each app. |
| `handcheck/handcheck.json` | Analyst-reviewed official-doc truth and correction notes. |
| `out/browser_evidence.json` | Browser-read pages added when direct fetching could not recover usable content. |
| `out/browser_verification.json` | Independent Browser Use verdicts and adjudication status. |
| `report/data.js` | Generated static bundle consumed by the reviewer dashboard. |

`report/data.js` is the only publication copy. Canonical research remains in `out/`; the report does not keep a second JSON tree.

## Data Contract

Every app uses the same locked 19-field schema:

`app · category · one_liner · auth_methods[] · access_model · api_type · api_breadth · existing_mcp · composio_toolkit · buildability · main_blocker · recommended_next_action · evidence_urls[] · confidence · verification_status · slug · primary_docs_url · rate_limit_note · last_verified`

Metric labels are intentionally narrow:

- `handcheck.accuracy` is the latest staged pre-fold agreement, not a population-wide accuracy estimate.
- `accuracy_movement` compares the archived first pass with the corrected dataset against the same 45-app truth set.
- The archived first pass scored 80%; replaying the verified corrections scores 100%.
- The latest staged agreement is 91.7%. Earlier batches had already been corrected, so it is not a blind 45-app first-pass score.
- `confidence` is a triage signal, not an accuracy claim.

## Architecture

```text
research.py                         one public CLI
  -> composio_lookup.py             toolkit overlap during research
  -> docs_research.py               official API/auth/access/MCP evidence
  -> synthesis.py                   strict Gemini record synthesis
  -> schema.py                      locked enums and semantic validation
  -> pipeline.py                    synchronous resumable execution
  -> batch_pipeline.py              asynchronous Gemini Batch execution
  -> verify.py                      metrics and blind re-search checks
  -> handcheck.py                   official-doc adjudication
  -> out/                            canonical evidence and datasets
  -> report/data.js                 generated static dashboard bundle

Independent checks
  -> browser_verify.py              Browser Use Cloud verification
  -> composio_agent.py              one-app read-only Composio Session diagnostic
```

Fresh research fails closed when authentication or production-access evidence is incomplete. Historical preseeds only prioritize risky apps; their hypotheses are never shown to the synthesis model.

## Composio SDK Usage

`python research.py --composio-audit` queries all 100 apps through the Composio SDK only. It atomically writes `out/composio_coverage.json` and fails without replacing the previous snapshot if any SDK profile is incomplete.

`python research.py --composio-agent otter-ai` creates a scoped Composio Session with Gemini, the no-auth `browser_tool`, and three preloaded local tools. It loads one current record, performs one bounded first-party documentation task, and compares the cached verdict deterministically. It is read-only: disagreements require human adjudication and never mutate published research.

The locked dataset's original `composio_toolkit` field is preserved. The SDK sidecar adds current executable depth without rewriting historical research.

## Reproduce

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Provider keys:

| Key | Used for |
| --- | --- |
| `PERPLEXITY_API_KEY` | Documentation search. |
| `GOOGLE_GENAI_API_KEY` | Synthesis, blind verification, and Session reasoning. |
| `COMPOSIO_API_KEY` | Toolkit audit and Composio Session. |
| `BROWSER_USE_API_KEY` | Optional independent browser verification. |

Run a fresh paid pipeline:

```bash
python research.py --batch-submit --fresh-run --model gemini-3.1-pro-preview
python research.py --batch-status
python research.py --batch-collect
python research.py --batch-audit-sources
python research.py --metrics
```

Run independent checks and rebuild the report:

```bash
python browser_verify.py --sample 12
python research.py --handcheck-template 24
# Review official docs and fill handcheck/handcheck.json.
python research.py --fold-handcheck
python research.py --apply-handcheck
python research.py --accuracy-movement
python research.py --composio-audit
python research.py --composio-agent otter-ai
python research.py --build-report
```

## View And Test

```bash
cd report
python -m http.server 8000
```

Open http://localhost:8000.

```bash
python -m unittest discover -s tests -v
ruff check *.py tests
python -m compileall -q *.py tests
node --check report/app.js
git diff --check
```

Deploy the static report with `cd report && vercel deploy --prod`.

## Repository Layout

```text
composio/
├── research.py                  CLI
├── pipeline.py                  synchronous runner
├── batch_pipeline.py            asynchronous batch runner
├── docs_research.py             evidence acquisition
├── synthesis.py                 structured model synthesis
├── schema.py                    locked record contract
├── normalize.py                 canonical auth labels
├── verify.py                    automated verification and metrics
├── handcheck.py                 human adjudication
├── browser_verify.py            independent browser checks
├── composio_lookup.py           toolkit lookup and coverage audit
├── composio_agent.py            read-only Session diagnostic
├── config.py                    environment and atomic JSON I/O
├── usage_tracker.py             paid-provider budget ledger
├── data/                         assignment catalog and risk preseeds
├── handcheck/                    official-doc truth
├── out/                          canonical results and evidence
├── report/                       static reviewer dashboard
├── tests/                        quality and regression suite
├── requirements.txt
└── requirements-dev.txt
```
