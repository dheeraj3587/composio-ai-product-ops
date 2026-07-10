"""Evidence-grounded LLM synthesis into the locked 19-field schema."""
from __future__ import annotations

import datetime as dt
import json
from typing import Literal

import config
import docs_research
import normalize
from pydantic import BaseModel, Field
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
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 3].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return (cut + "...") if cut else text[:limit]


SYSTEM = f"""You are an API-integration analyst. Produce one STRICT JSON object from the supplied evidence.

Evidence rules:
- Use only fetched documentation. Search-result snippets help discovery but cannot support a final claim by themselves.
- evidence_urls must contain only URLs from ALLOWED_URLS and must cite the pages supporting your decisions.
- If evidence is thin or contradictory, state that in reasoning and lower confidence. Never fill a gap by guessing.
- PRESEED_HYPOTHESIS is an unverified prior. Trust fetched evidence over it.

Controlled vocabularies:
- auth_methods must use ONLY: {json.dumps(normalize.CANONICAL)}.
- OAuth2 means an OAuth grant, including authorization-code and client-credentials flows. Do not also add Bearer Token merely because an OAuth access token is sent in a Bearer header.
- Bearer Token means a static vendor-issued bearer token with no OAuth grant. API Key means a static API key/token. Use Other Token only when official docs identify a distinct credential that fits no other label.
- List only credentials independently accepted by the dominant public API or the recommended official MCP surface. Do not list account IDs, client IDs, scopes, or bearer transport as separate auth methods.
- Prefer the vendor's most specific credential label. A personal access token or bot token sent in an Authorization: Bearer header is one method, not both that label and Bearer Token.
- OAuth2 and a static token may coexist only when official docs show they are independently issued alternatives for API access.
- Use None / Not Applicable only when there is no hosted API/MCP authentication surface.
- api_type: REST | GraphQL | SDK | SOAP | MCP-only | None. Choose the dominant public integration surface; explain additional protocols in notes/reasoning.
- existing_mcp: Official only for a vendor-hosted/published server; Community for a credible third party; None otherwise. Base this primarily on MCP EVIDENCE.

Production access rubric:
- Self-Serve means a new developer can obtain credentials usable in production without manual vendor approval, partnership, business verification, or already being a paying customer.
- A sandbox/trial alone does not make production access Self-Serve.
- Gated means production use needs approval, review, partnership, business verification, or an existing paid account.
- If REST is gated but an official MCP is self-serve, describe both surfaces in access_model.note and base the recommendation on the surface actually proposed.

Decision rubric:
- buildability Easy = self-serve credentials + clear REST/GraphQL docs; Moderate = OAuth/app setup or partial docs; Hard = review/verification or thin docs; Blocked = no usable hosted API/MCP.
- Build Now requires a usable self-serve surface. Needs Outreach means access approval/review. Partner-Gated means no entry point without an existing customer/partner relationship. Blocked means no usable hosted surface.
- one_liner must be a complete sentence of at most 120 characters.

Return EXACTLY these keys:
one_liner, auth_methods, access_model, api_type, api_breadth, existing_mcp, buildability, main_blocker, recommended_next_action, rate_limit_note, evidence_urls, confidence, reasoning.
access_model must be {{"kind":"Self-Serve"|"Gated","note":"..."}}. confidence must be 0..1."""


class SynthesisAccess(BaseModel):
    kind: Literal["Self-Serve", "Gated"]
    note: str


class SynthesisOutput(BaseModel):
    """Native Gemini response schema; deterministic checks remain the final gate."""
    one_liner: str
    auth_methods: list[str]
    access_model: SynthesisAccess
    api_type: Literal["REST", "GraphQL", "SDK", "SOAP", "MCP-only", "None"]
    api_breadth: Literal["Narrow", "Moderate", "Broad"]
    existing_mcp: Literal["Official", "Community", "None"]
    buildability: Literal["Easy", "Moderate", "Hard", "Blocked"]
    main_blocker: str
    recommended_next_action: Literal[
        "Build Now", "Needs Outreach", "Partner-Gated", "Blocked"
    ]
    rate_limit_note: str
    evidence_urls: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


def _pick(value, allowed: list[str], field: str, default: str | None = None) -> str:
    """Return a controlled value; reject invalid non-empty model output."""
    if value is None or not str(value).strip():
        if default is not None:
            return default
        raise ValueError(f"{field} is required; expected one of {allowed}")
    candidate = str(value).strip()
    for item in allowed:
        if candidate.lower() == item.lower():
            return item
    raise ValueError(f"invalid {field}={candidate!r}; expected one of {allowed}")


_API_TYPE = [item.value for item in ApiType]
_BREADTH = [item.value for item in ApiBreadth]
_MCP = [item.value for item in ExistingMcp]
_BUILD = [item.value for item in Buildability]
_NEXT = [item.value for item in NextAction]
_KIND = [item.value for item in AccessKind]
_YN = [item.value for item in YesNo]


def _ranked_fetched(evidence: dict) -> list[dict]:
    fetched = [item for item in evidence.get("fetched", []) if item.get("ok") and item.get("text")]
    return sorted(
        fetched,
        key=lambda item: (
            len(set(item.get("support_tags", [])) & {"api", "auth", "access"}),
            item.get("relevance_score", 0),
        ),
        reverse=True,
    )


def _evidence_block(evidence: dict, per_source: int = 2800, max_sources: int = 6):
    blocks = []
    for item in _ranked_fetched(evidence)[:max_sources]:
        topics = ", ".join(item.get("support_tags", [])) or "unclassified"
        blocks.append(
            f"URL: {item['url']}\nSOURCE: {item.get('source_kind', 'unknown')}\n"
            f"TOPICS: {topics}\nTEXT: {item['text'][:per_source]}"
        )
    snippets = [
        f"- {result.get('title', '')} ({result.get('url', '')}): {result.get('snippet', '')[:200]}"
        for result in evidence.get("search_results", [])[:8]
    ]
    return "\n\n".join(blocks), "\n".join(snippets)


def _mcp_block(evidence: dict, per_source: int = 1800) -> str:
    mcp = evidence.get("mcp") or {}
    snippets = [
        f"- {result.get('title', '')} ({result.get('url', '')}): {result.get('snippet', '')[:200]}"
        for result in mcp.get("search_results", [])[:5]
    ]
    blocks = [
        f"URL: {item['url']}\nTEXT: {item['text'][:per_source]}"
        for item in mcp.get("fetched", [])
        if item.get("ok") and item.get("text")
    ]
    return "\n\n".join([part for part in ("\n".join(snippets), "\n\n".join(blocks)) if part])


def build_messages(evidence: dict, composio_signal: dict, preseed: dict | None = None):
    evidence_text, snippets = _evidence_block(evidence)
    mcp_text = _mcp_block(evidence)
    preseed_text = (
        json.dumps(preseed.get("hypothesis"), ensure_ascii=False)
        if preseed and preseed.get("hypothesis")
        else "none"
    )
    user = f"""APP: {evidence['app']} (category: {evidence.get('category', '')})
COMPOSIO_TOOLKIT (deterministic; do not change): {composio_signal.get('composio_toolkit')}
PRESEED_HYPOTHESIS: {preseed_text}
RESEARCH_QUERIES: {json.dumps(evidence.get('queries') or [evidence.get('query')])}
EVIDENCE_QUALITY: {evidence.get('evidence_quality', 'unknown')}

ALLOWED_URLS:
{json.dumps(evidence.get('fetched_urls', []), ensure_ascii=False)}

SEARCH RESULTS (discovery only):
{snippets or '(none)'}

FETCHED DOCUMENTATION:
{evidence_text or '(none)'}

MCP EVIDENCE:
{mcp_text or '(none found)'}

Return the strict JSON object now."""
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def _primary_docs_url(evidence: dict, fallback: str = "") -> str:
    ranked = _ranked_fetched(evidence)
    if ranked:
        return ranked[0]["url"]
    mcp_ok = [item for item in (evidence.get("mcp") or {}).get("fetched", []) if item.get("ok")]
    if mcp_ok:
        return mcp_ok[0]["url"]
    return fallback


def _validate_citations(record: dict, evidence: dict) -> None:
    """Require cited pages to cover every high-risk claim family."""
    by_url = {}
    for item in [
        *evidence.get("fetched", []),
        *(evidence.get("mcp") or {}).get("fetched", []),
    ]:
        if item.get("ok"):
            by_url[item.get("url")] = set(item.get("support_tags", []))
    cited_topics = set()
    for url in record["evidence_urls"]:
        cited_topics.update(by_url.get(url, set()))

    required = set()
    if record["api_type"] != "None":
        required.update({"auth", "access"})
        required.add("mcp" if record["api_type"] == "MCP-only" else "api")
    if record["existing_mcp"] != "None":
        required.add("mcp")
    missing = required - cited_topics
    if missing:
        raise ValueError(
            "evidence_urls do not support all high-risk claims; "
            f"missing topics={sorted(missing)}, cited topics={sorted(cited_topics)}"
        )


def _validate_source_quality(record: dict, evidence: dict, app_meta: dict) -> None:
    """Reject wrong-app evidence and overconfident third-party-only conclusions."""
    by_url = {
        item.get("url"): item
        for item in [
            *evidence.get("fetched", []),
            *(evidence.get("mcp") or {}).get("fetched", []),
        ]
        if item.get("ok") and item.get("url")
    }
    cited = []
    for url in record["evidence_urls"]:
        item = by_url.get(url, {})
        first_party = docs_research.is_first_party(
            url, app_meta.get("hint_url") or "", app_meta["slug"]
        )
        identity_match = docs_research.identity_matches(
            url,
            item.get("text", ""),
            app_meta["app"],
            app_meta["slug"],
            app_meta.get("hint_url") or "",
        )
        cited.append({
            "url": url,
            "tags": set(item.get("support_tags", [])),
            "first_party": first_party,
            "identity_match": identity_match,
        })

    if not any(item["identity_match"] for item in cited):
        raise ValueError("evidence_urls do not identify the requested app")
    first_party = [item for item in cited if item["first_party"]]
    if not first_party:
        if docs_research.ACCESS_OFFICIAL_SEEDS.get(app_meta["slug"]):
            raise ValueError("known first-party evidence exists but was not cited")
        if record["confidence"] > 0.5:
            raise ValueError("third-party-only evidence requires confidence <= 0.5")
        disclosure = " ".join([
            record.get("one_liner", ""),
            (record.get("access_model") or {}).get("note", ""),
            record.get("main_blocker", ""),
        ]).lower()
        if not any(
            marker in disclosure
            for marker in ("third-party", "no official", "official documentation")
        ):
            raise ValueError("third-party-only evidence must be disclosed in the record")
    if record["existing_mcp"] == "Official" and not any(
        item["first_party"] and "mcp" in item["tags"] for item in cited
    ):
        raise ValueError("existing_mcp=Official requires first-party MCP evidence")
    if record["confidence"] > 0.5 and record["api_type"] != "None":
        first_party_topics = {
            tag for item in first_party for tag in item["tags"]
        }
        required = {"auth", "access"}
        required.add("mcp" if record["api_type"] == "MCP-only" else "api")
        missing = required - first_party_topics
        if missing:
            raise ValueError(
                "high-confidence core claims need first-party coverage; "
                f"missing topics={sorted(missing)}"
            )


def _validate_semantics(record: dict) -> None:
    api_type = record["api_type"]
    buildability = record["buildability"]
    action = record["recommended_next_action"]
    access = record["access_model"]["kind"]
    auth = set(record["auth_methods"])

    if not record["access_model"]["note"].strip():
        raise ValueError("access_model.note must explain how production credentials are obtained")
    if api_type == "None":
        if auth != {"None / Not Applicable"}:
            raise ValueError("api_type=None requires auth_methods=['None / Not Applicable']")
        if buildability != "Blocked" or action != "Blocked":
            raise ValueError("api_type=None requires buildability=Blocked and next_action=Blocked")
    elif "None / Not Applicable" in auth:
        raise ValueError("a usable API/MCP cannot use None / Not Applicable authentication")
    if "Bearer Token" in auth and auth & {"Personal Access Token", "Bot Token"}:
        raise ValueError("specific token credentials must not also be labeled Bearer Token")
    if api_type == "MCP-only" and record["existing_mcp"] == "None":
        raise ValueError("api_type=MCP-only requires an Official or Community MCP")
    if action == "Build Now" and (access != "Self-Serve" or buildability == "Blocked"):
        raise ValueError("Build Now requires a non-blocked Self-Serve production surface")
    if action in {"Needs Outreach", "Partner-Gated"} and access != "Gated":
        raise ValueError(f"{action} requires access_model.kind=Gated")
    partner_text = (
        record["access_model"]["note"] + " " + record["main_blocker"]
    ).lower()
    if action == "Partner-Gated" and not any(
        marker in partner_text
        for marker in ("partner", "customer", "paid", "license", "contract")
    ):
        raise ValueError("Partner-Gated must identify the partner/existing-customer requirement")
    if buildability == "Easy" and access != "Self-Serve":
        raise ValueError("buildability=Easy requires Self-Serve production access")
    if buildability == "Blocked" and action != "Blocked":
        raise ValueError("buildability=Blocked requires recommended_next_action=Blocked")
    if action == "Blocked" and buildability != "Blocked":
        raise ValueError("recommended_next_action=Blocked requires buildability=Blocked")
    if access == "Gated" and not record["main_blocker"].strip():
        raise ValueError("Gated access requires a concrete main_blocker")


def _record_from_parsed(app_meta: dict, evidence: dict, composio_signal: dict,
                        parsed: dict) -> tuple[object, str]:
    expected_keys = {
        "one_liner", "auth_methods", "access_model", "api_type", "api_breadth",
        "existing_mcp", "buildability", "main_blocker", "recommended_next_action",
        "rate_limit_note", "evidence_urls", "confidence", "reasoning",
    }
    extra = set(parsed) - expected_keys
    missing = expected_keys - set(parsed)
    if extra or missing:
        raise ValueError(f"wrong JSON keys; missing={sorted(missing)}, extra={sorted(extra)}")

    one_liner = _clip120(str(parsed.get("one_liner") or ""))
    if not one_liner:
        raise ValueError("one_liner is required")
    if not isinstance(parsed.get("auth_methods"), list):
        raise ValueError("auth_methods must be a list")
    auth_methods = normalize.normalize_auth_list(parsed["auth_methods"], strict=True)
    if not auth_methods:
        raise ValueError("auth_methods must not be empty")

    access_model = parsed.get("access_model")
    if not isinstance(access_model, dict):
        raise ValueError("access_model must be an object")
    if set(access_model) != {"kind", "note"}:
        raise ValueError("access_model must contain exactly kind and note")

    allowed = set(evidence.get("fetched_urls", []))
    if not allowed:
        raise ValueError("no fetched documentation URL is available; refusing to synthesize a guess")
    requested_urls = parsed.get("evidence_urls")
    if not isinstance(requested_urls, list):
        raise ValueError("evidence_urls must be a list")
    if any(not isinstance(url, str) for url in requested_urls):
        raise ValueError("every evidence URL must be a string")
    invented = [url for url in requested_urls if url not in allowed]
    if invented:
        raise ValueError(f"evidence_urls contains non-fetched URLs: {invented}")
    evidence_urls = list(dict.fromkeys(requested_urls))
    if not evidence_urls:
        raise ValueError("at least one fetched evidence URL must support the record")

    try:
        confidence = float(parsed["confidence"])
    except (TypeError, ValueError) as exc:
        raise ValueError("confidence must be numeric") from exc
    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")
    confidence = min(confidence, 0.95)
    if evidence.get("degraded"):
        confidence = min(confidence, 0.35)

    record = {
        "app": app_meta["app"],
        "category": app_meta["category"],
        "one_liner": one_liner,
        "auth_methods": auth_methods,
        "access_model": {
            "kind": _pick(access_model.get("kind"), _KIND, "access_model.kind"),
            "note": str(access_model.get("note") or "").strip(),
        },
        "api_type": _pick(parsed.get("api_type"), _API_TYPE, "api_type"),
        "api_breadth": _pick(parsed.get("api_breadth"), _BREADTH, "api_breadth"),
        "existing_mcp": _pick(parsed.get("existing_mcp"), _MCP, "existing_mcp"),
        "composio_toolkit": _pick(
            composio_signal.get("composio_toolkit"), _YN, "composio_toolkit"
        ),
        "buildability": _pick(parsed.get("buildability"), _BUILD, "buildability"),
        "main_blocker": str(parsed.get("main_blocker") or "").strip(),
        "recommended_next_action": _pick(
            parsed.get("recommended_next_action"), _NEXT, "recommended_next_action"
        ),
        "evidence_urls": evidence_urls,
        "confidence": confidence,
        "verification_status": "Auto",
        "slug": app_meta["slug"],
        "primary_docs_url": _primary_docs_url(evidence, app_meta.get("hint_url") or ""),
        "rate_limit_note": str(parsed.get("rate_limit_note") or "").strip(),
        "last_verified": dt.date.today().isoformat(),
    }
    _validate_citations(record, evidence)
    _validate_source_quality(record, evidence, app_meta)
    _validate_semantics(record)
    reasoning = str(parsed.get("reasoning") or "").strip()
    if not reasoning:
        raise ValueError("reasoning is required")
    return validate_record(record), reasoning


def synthesize(app_meta: dict, evidence: dict, composio_signal: dict,
               preseed: dict | None = None, model: str | None = None,
               write_log: bool = True, lead: str | None = None):
    """Synthesize one record and repair one invalid model response."""
    if not evidence.get("fetched_urls"):
        raise ValueError(
            f"{app_meta['slug']}: no fetched evidence; pipeline will log a failure instead of guessing"
        )
    messages = build_messages(evidence, composio_signal, preseed)
    try:
        parsed, _ = config.llm_json(
            messages,
            model=model,
            lead=lead,
            max_tokens=4096,
            response_schema=SynthesisOutput,
        )
    except config.StructuredOutputError:
        parsed, _ = config.llm_json(
            [
                *messages,
                {
                    "role": "user",
                    "content": (
                        "Return the complete JSON object. Keep reasoning concise so no field is "
                        "truncated. Do not omit any required key."
                    ),
                },
            ],
            model=model,
            lead=lead,
            thinking_level="low",
            max_tokens=4096,
            response_schema=SynthesisOutput,
        )
    first_error = ""
    for attempt in range(2):
        try:
            record, reasoning = _record_from_parsed(app_meta, evidence, composio_signal, parsed)
            if write_log:
                _write_reasoning(app_meta, reasoning, record.model_dump(mode="json"), evidence, preseed)
            return record, reasoning
        except ValueError as exc:
            if attempt == 1:
                raise ValueError(
                    f"invalid synthesis after one repair; first={first_error}; final={exc}"
                ) from exc
            first_error = str(exc)
            repair_messages = [
                *messages,
                {"role": "assistant", "content": json.dumps(parsed, ensure_ascii=False)},
                {
                    "role": "user",
                    "content": (
                        "Your JSON failed deterministic validation: " + first_error +
                        ". Correct only the JSON using the same evidence and return the complete object."
                    ),
                },
            ]
            parsed, _ = config.llm_json(
                repair_messages,
                model=model,
                lead=lead,
                thinking_level="low",
                max_tokens=4096,
                response_schema=SynthesisOutput,
            )
    raise AssertionError("unreachable")


_FINAL_START = "<!-- final-state:start -->"
_FINAL_END = "<!-- final-state:end -->"


def append_final_state(record: dict, reason: str = "post-processing") -> None:
    """Make a reasoning log's final state match any later adjudicated migration."""
    path = config.REASONING_DIR / f"{record['slug']}.md"
    if not path.exists():
        return
    current = path.read_text(encoding="utf-8")
    if _FINAL_START in current:
        current = current.split(_FINAL_START, 1)[0].rstrip() + "\n"
    block = [
        "",
        _FINAL_START,
        "## Final pipeline state",
        f"_Updated {dt.date.today().isoformat()} by {reason}; this supersedes earlier key decisions._",
        "",
        "```json",
        json.dumps(record, indent=2, ensure_ascii=False),
        "```",
        _FINAL_END,
        "",
    ]
    path.write_text(current + "\n".join(block), encoding="utf-8")


def _write_reasoning(
    app_meta, reasoning, record, evidence, preseed, model_used: str | None = None
) -> None:
    config.ensure_dirs()
    path = config.REASONING_DIR / f"{app_meta['slug']}.md"
    confidence_note = " (capped because evidence was degraded)" if evidence.get("degraded") else ""
    fetched_lines = []
    for item in evidence.get("fetched", []):
        status = item.get("status", 0)
        topics = ",".join(item.get("support_tags", [])) or "none"
        fetched_lines.append(
            f"- {item.get('url')} | HTTP {status} | {item.get('source_kind', 'unknown')} | topics={topics}"
        )
    lines = [
        f"# {app_meta['app']} - synthesis reasoning",
        f"_generated {record['last_verified']} | model "
        f"{config.last_llm_used() or model_used or config.PRIMARY_MODEL}_",
        "",
        "## Research trace",
        f"- queries: {json.dumps(evidence.get('queries') or [evidence.get('query')])}",
        f"- evidence quality: **{evidence.get('evidence_quality', 'unknown')}**",
        *fetched_lines,
        "",
        "## Model reasoning",
        reasoning,
        "",
        "## Key decisions",
        f"- buildability: **{record['buildability']}**",
        f"- access_model: **{record['access_model']['kind']}** - {record['access_model']['note']}",
        f"- recommended_next_action: **{record['recommended_next_action']}**",
        f"- confidence: **{record['confidence']}**{confidence_note}",
        "",
        "## Evidence URLs",
        *([f"- {url}" for url in record["evidence_urls"]] or ["- (none)"]),
        "",
        "## Generated record",
        "```json",
        json.dumps(record, indent=2, ensure_ascii=False),
        "```",
    ]
    if preseed and preseed.get("hypothesis"):
        lines.extend([
            "",
            "## Preseed hypothesis (unverified prior)",
            "```json",
            json.dumps(preseed["hypothesis"], indent=2, ensure_ascii=False),
            "```",
        ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
