"""LLM synthesis (OpenRouter).

Raw evidence + Composio signal + preseed hypothesis  ->  one schema-conformant
AppRecord, plus an inspectable reasoning log written to out/reasoning/<slug>.md.

Division of labour (keeps hallucination surface small):
  * The LLM owns the ANALYTICAL fields (auth, access, api type/breadth, mcp,
    buildability, blocker, next action, confidence, reasoning).
  * Code owns the DETERMINISTIC fields (app, category, slug, composio_toolkit,
    verification_status, last_verified, primary_docs_url) and ENFORCES Flag D by
    intersecting evidence_urls with the fetched-URL whitelist.
"""

from __future__ import annotations

import datetime as dt
import json

import config
import normalize
from schema import (
    AccessKind,
    ApiBreadth,
    ApiType,
    Buildability,
    ExistingMcp,
    NextAction,
    YesNo,
    validate_record,
)


def _clip120(text: str, limit: int = 120) -> str:
    """Fit within `limit` chars WITHOUT chopping mid-word (cut at the last space)."""
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return (cut + "\u2026") if cut else text[:limit]

SYSTEM = """You are an API-integration analyst. From the evidence provided, produce a STRICT JSON record about ONE app's API integration readiness.

Hard rules:
- Use ONLY the evidence provided. Do NOT invent facts or URLs.
- evidence_urls MUST be a subset of ALLOWED_URLS. If none apply, return [].
- If evidence is thin/ambiguous, SAY SO in reasoning and LOWER confidence.
- The PRESEED hypothesis is an UNVERIFIED prior. If the evidence confirms it, use it. If the evidence contradicts it or is silent, TRUST THE EVIDENCE and note the contradiction in reasoning.
- one_liner <= 120 characters.

Rubrics (apply consistently):
- api_breadth: Narrow = one resource / a few endpoints; Moderate = several resources / full CRUD; Broad = many resources across multiple domains.
- buildability: Easy = self-serve key + REST/GraphQL + clear docs; Moderate = OAuth app setup or partial docs; Hard = heavy review/verification or thin docs; Blocked = no usable public API.
- recommended_next_action: Build Now = Easy + Self-Serve; Needs Outreach = API exists but access needs review/business verification; Partner-Gated = good API but NO entry point without an existing paid account; Blocked = no public API.

Return JSON with EXACTLY these keys:
one_liner, auth_methods (list of strings), access_model (object {kind:"Self-Serve"|"Gated", note:string}), api_type ("REST"|"GraphQL"|"SDK"|"SOAP"|"MCP-only"|"None"), api_breadth ("Narrow"|"Moderate"|"Broad"), existing_mcp ("Official"|"Community"|"None"), buildability ("Easy"|"Moderate"|"Hard"|"Blocked"), main_blocker (string, "" if none), recommended_next_action ("Build Now"|"Needs Outreach"|"Partner-Gated"|"Blocked"), rate_limit_note (string), evidence_urls (list, subset of ALLOWED_URLS), confidence (float 0-1), reasoning (string: justify buildability/blocker/next_action/confidence and whether the preseed was confirmed or contradicted)."""


# --------------------------------------------------------------------------- #
# enum normalisation (reduce validation failures on a 100-app batch)
# --------------------------------------------------------------------------- #
def _pick(value, allowed: list[str], default: str) -> str:
    if value is None:
        return default
    v = str(value).strip()
    for a in allowed:
        if v.lower() == a.lower():
            return a
    return default


_API_TYPE = [e.value for e in ApiType]
_BREADTH = [e.value for e in ApiBreadth]
_MCP = [e.value for e in ExistingMcp]
_BUILD = [e.value for e in Buildability]
_NEXT = [e.value for e in NextAction]
_KIND = [e.value for e in AccessKind]
_YN = [e.value for e in YesNo]


# --------------------------------------------------------------------------- #
# prompt
# --------------------------------------------------------------------------- #
def _evidence_block(evidence: dict, per_source: int = 3000, max_sources: int = 4):
    blocks = []
    for f in evidence.get("fetched", [])[:max_sources]:
        if f.get("ok") and f.get("text"):
            blocks.append(f"URL: {f['url']}\nTEXT: {f['text'][:per_source]}")
    snips = [
        f"- {r.get('title', '')} ({r.get('url', '')}): {r.get('snippet', '')[:200]}"
        for r in evidence.get("search_results", [])[:6]
    ]
    return "\n\n".join(blocks), "\n".join(snips)


def build_messages(evidence: dict, composio_signal: dict, preseed: dict | None = None):
    ev_text, snips = _evidence_block(evidence)
    allowed = evidence.get("fetched_urls", [])
    preseed_txt = (
        json.dumps(preseed.get("hypothesis"), ensure_ascii=False)
        if preseed and preseed.get("hypothesis")
        else "none"
    )
    user = f"""APP: {evidence["app"]}  (category: {evidence.get("category", "")})
COMPOSIO_TOOLKIT (already determined; do not change): {composio_signal.get("composio_toolkit")}
PRESEED_HYPOTHESIS (UNVERIFIED prior — confirm or refute from evidence): {preseed_txt}

ALLOWED_URLS (evidence_urls must be a subset of these):
{json.dumps(allowed, ensure_ascii=False)}

SEARCH RESULTS:
{snips or "(none)"}

FETCHED DOCUMENTATION TEXT:
{ev_text or "(no pages fetched successfully — evidence is thin; lower confidence)"}

Return the STRICT JSON record now."""
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


# --------------------------------------------------------------------------- #
# synthesis
# --------------------------------------------------------------------------- #
def synthesize(
    app_meta: dict,
    evidence: dict,
    composio_signal: dict,
    preseed: dict | None = None,
    model: str | None = None,
    write_log: bool = True,
    lead: str | None = None,
):
    """app_meta: {app, slug, category, hint_url}. Returns (AppRecord, reasoning)."""
    messages = build_messages(evidence, composio_signal, preseed)
    parsed, raw = config.llm_json(messages, model=model, lead=lead)

    allowed = set(evidence.get("fetched_urls", []))
    ev_urls = [u for u in (parsed.get("evidence_urls") or []) if u in allowed]  # Flag D

    primary = evidence.get("fetched_urls") or []
    primary = primary[0] if primary else (app_meta.get("hint_url") or "")

    am = parsed.get("access_model")
    if isinstance(am, str):
        am = {"kind": "Gated" if "gat" in am.lower() else "Self-Serve", "note": am}
    elif not isinstance(am, dict):
        am = {"kind": "Gated", "note": ""}

    conf = parsed.get("confidence", 0.4)
    try:
        conf = float(conf)
    except (TypeError, ValueError):
        conf = 0.4
    conf = max(0.0, min(1.0, conf))
    if evidence.get("degraded"):
        conf = min(conf, 0.35)  # thin evidence can't earn high confidence

    record = {
        "app": app_meta["app"],
        "category": app_meta["category"],
        "one_liner": _clip120(
            parsed.get("one_liner")
            or f"{app_meta['app']}: readiness assessed from public docs."
        ),
        "auth_methods": normalize.normalize_auth_list(parsed.get("auth_methods") or []),
        "access_model": {
            "kind": _pick(am.get("kind"), _KIND, "Gated"),
            "note": am.get("note", "") or "",
        },
        "api_type": _pick(parsed.get("api_type"), _API_TYPE, "None"),
        "api_breadth": _pick(parsed.get("api_breadth"), _BREADTH, "Narrow"),
        "existing_mcp": _pick(parsed.get("existing_mcp"), _MCP, "None"),
        "composio_toolkit": _pick(composio_signal.get("composio_toolkit"), _YN, "No"),
        "buildability": _pick(parsed.get("buildability"), _BUILD, "Hard"),
        "main_blocker": parsed.get("main_blocker") or "",
        "recommended_next_action": _pick(
            parsed.get("recommended_next_action"), _NEXT, "Needs Outreach"
        ),
        "evidence_urls": ev_urls,
        "confidence": conf,
        "verification_status": "Auto",
        "slug": app_meta["slug"],
        "primary_docs_url": primary,
        "rate_limit_note": parsed.get("rate_limit_note") or "",
        "last_verified": dt.date.today().isoformat(),
    }

    rec = validate_record(record)
    reasoning = parsed.get("reasoning") or "(model returned no reasoning)"
    if write_log:
        _write_reasoning(app_meta, reasoning, record, evidence, preseed)
    return rec, reasoning


def _write_reasoning(app_meta, reasoning, record, evidence, preseed) -> None:
    config.ensure_dirs()
    path = config.REASONING_DIR / f"{app_meta['slug']}.md"
    conf_note = "  _(capped: evidence was thin)_" if evidence.get("degraded") else ""
    ev_lines = [f"- {u}" for u in record["evidence_urls"]] or ["- (none)"]
    lines = [
        f"# {app_meta['app']} — synthesis reasoning",
        f"_generated {record['last_verified']} · model {config.PRIMARY_MODEL}_",
        "",
        "## Model reasoning",
        reasoning,
        "",
        "## Key decisions",
        f"- buildability: **{record['buildability']}**",
        f"- access_model: **{record['access_model']['kind']}** — {record['access_model']['note']}",
        f"- recommended_next_action: **{record['recommended_next_action']}**",
        f"- confidence: **{record['confidence']}**" + conf_note,
        "",
        "## Evidence URLs (whitelist-enforced)",
        *ev_lines,
    ]
    if preseed and preseed.get("hypothesis"):
        lines += [
            "",
            "## Preseed hypothesis (unverified prior)",
            "```json",
            json.dumps(preseed["hypothesis"], indent=2, ensure_ascii=False),
            "```",
            "_The model was instructed to trust evidence over this prior and note contradictions above._",
        ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
