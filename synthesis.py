"""Evidence-grounded LLM synthesis into the locked 19-field schema."""
from __future__ import annotations

import datetime as dt
import json
import re
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
- Historical preseeds are deliberately withheld from synthesis to avoid anchoring. Decide only from fetched evidence.

Controlled vocabularies:
- auth_methods must use ONLY: {json.dumps(normalize.CANONICAL)}.
- OAuth2 means an OAuth grant, including authorization-code and client-credentials flows. Do not also add Bearer Token merely because an OAuth access token is sent in a Bearer header.
- Bearer Token means a static vendor-issued bearer token with no OAuth grant. API Key means a static API key/token. Use Other Token only when official docs identify a distinct credential that fits no other label.
- An OAuth client ID/client secret used only for registration or token exchange is not an independent API Key method. If vendor docs require a client ID/secret directly on every API request, treat that static pair as API Key.
- Map personal/programmatic access tokens to Personal Access Token, key-pair/private-key auth to Service Account, and OAuth 1.x to Other Token.
- Include Basic Auth when official docs explicitly require HTTP Basic for API requests, even when the username is an API key.
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
- A key-generation page proves credential mechanics, not production entitlement. Check plan/pricing/production evidence before choosing Self-Serve.
- If free access expires and continued API use needs a paid plan, classify Gated. Do not treat a temporary trial as a free production tier.
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
        content_source = item.get("content_url") or item["url"]
        auth_signals = ", ".join(
            item.get("auth_signals")
            or docs_research.auth_evidence_signals(item.get("text", ""), item["url"])
        ) or "none"
        access_signals = ", ".join(
            item.get("access_signals")
            or docs_research.access_evidence_signals(item.get("text", ""), item["url"])
        ) or "none"
        blocks.append(
            f"URL: {item['url']}\nSOURCE: {item.get('source_kind', 'unknown')}\n"
            f"CONTENT_URL: {content_source}\n"
            f"TOPICS: {topics}\nAUTH_SIGNALS: {auth_signals}\n"
            f"ACCESS_SIGNALS: {access_signals}\nTEXT: {item['text'][:per_source]}"
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
        f"URL: {item['url']}\n"
        f"CONTENT_URL: {item.get('content_url') or item['url']}\n"
        f"AUTH_SIGNALS: {', '.join(item.get('auth_signals') or docs_research.auth_evidence_signals(item.get('text', ''), item['url'])) or 'none'}\n"
        f"ACCESS_SIGNALS: {', '.join(item.get('access_signals') or docs_research.access_evidence_signals(item.get('text', ''), item['url'])) or 'none'}\n"
        f"TEXT: {item['text'][:per_source]}"
        for item in mcp.get("fetched", [])
        if item.get("ok") and item.get("text")
    ]
    return "\n\n".join([part for part in ("\n".join(snippets), "\n\n".join(blocks)) if part])


def build_messages(evidence: dict, composio_signal: dict, preseed: dict | None = None):
    evidence_text, snippets = _evidence_block(evidence)
    mcp_text = _mcp_block(evidence)
    preseed_status = "withheld (available for risk sampling only)" if preseed else "none"
    user = f"""APP: {evidence['app']} (category: {evidence.get('category', '')})
COMPOSIO_TOOLKIT (deterministic; do not change): {composio_signal.get('composio_toolkit')}
PRESEED_STATUS: {preseed_status}
RESEARCH_QUERIES: {json.dumps(evidence.get('queries') or [evidence.get('query')])}
EVIDENCE_QUALITY: {evidence.get('evidence_quality', 'unknown')}
AGGREGATE_AUTH_SIGNALS: {json.dumps(evidence.get('supported_auth_signals', []))}
AGGREGATE_ACCESS_SIGNALS: {json.dumps(evidence.get('supported_access_signals', []))}

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


def _cited_items(record: dict, evidence: dict) -> list[dict]:
    wanted = set(record["evidence_urls"])
    return [
        item
        for item in [
            *evidence.get("fetched", []),
            *(evidence.get("mcp") or {}).get("fetched", []),
        ]
        if item.get("ok") and item.get("url") in wanted
    ]


def _auth_signals(items: list[dict]) -> set[str]:
    return {
        signal
        for item in items
        for signal in (
            item.get("auth_signals")
            or docs_research.auth_evidence_signals(
                item.get("text", ""), item.get("url", "")
            )
        )
    }


def _access_signals(items: list[dict]) -> set[str]:
    return {
        signal
        for item in items
        for signal in (
            item.get("access_signals")
            or docs_research.access_evidence_signals(
                item.get("text", ""), item.get("url", "")
            )
        )
    }


def _explicit_basic_for_api_requests(item: dict) -> bool:
    text = re.sub(
        r"\s+", " ", f"{item.get('url', '')} {item.get('text', '')}".lower()
    )
    if re.search(
        r"basic (?:auth(?:entication)?|transport).{0,80}not (?:an? )?independent|"
        r"basic auth(?:entication)?.{0,50}(?:deprecated|not supported|no longer supported)",
        text,
    ):
        return False
    return bool(
        "basic-auth" in text
        or "basic_auth" in text
        or re.search(
            r"(?:api key|api token).{0,160}(?:basic auth|http basic)|"
            r"(?:basic auth|http basic).{0,160}(?:api key|api token|api requests?)|"
            r"authenticate (?:your )?(?:api )?requests?.{0,100}(?:basic auth|http basic)",
            text,
        )
    )


def _validate_auth_grounding(record: dict, evidence: dict) -> None:
    """Reject auth labels that are unsupported or less specific than the docs."""
    if record["api_type"] == "None":
        return
    items = _cited_items(record, evidence)
    signals = _auth_signals(items)
    auth = set(record["auth_methods"])

    if (
        "Personal Access Token" in signals
        and "Bearer Token" in auth
        and "Personal Access Token" not in auth
    ):
        raise ValueError(
            "cited evidence names a personal/programmatic access token; use the specific canonical label"
        )
    if (
        "Service Account" in signals
        and "Other Token" in auth
        and "Service Account" not in auth
    ):
        raise ValueError(
            "cited evidence names key-pair/service-account auth; use Service Account"
        )
    if "Other Token" in signals and "Other Token" not in auth:
        raise ValueError("cited evidence names OAuth 1.x; represent it as Other Token")

    for label in auth & {
        "OAuth2", "API Key", "Basic Auth", "Personal Access Token",
        "Service Account", "Bot Token", "Bearer Token", "Other Token",
    }:
        if label not in signals:
            raise ValueError(
                f"auth_methods includes {label!r}, but cited evidence does not name that scheme"
            )
    if any(_explicit_basic_for_api_requests(item) for item in items):
        if "Basic Auth" not in auth:
            raise ValueError(
                "cited evidence explicitly requires HTTP Basic for API requests; include Basic Auth"
            )

    if {"OAuth2", "Bearer Token"} <= auth:
        static_bearer = any(
            re.search(
                r"private integration token|static (?:access )?token|"
                r"independent bearer token|bearer[ -](?:api )?token|"
                r"independently issued.{0,60}access token|"
                r"storefront access token|service keys?.{0,80}bearer|"
                r"(?:customer|admin|integration) token|"
                r"api key.{0,80}bearer",
                f"{item.get('url', '')} {item.get('text', '')}".lower(),
            )
            for item in items
        )
        if not static_bearer:
            raise ValueError(
                "OAuth2 plus Bearer Token needs evidence for an independently issued static token"
            )


def _validate_access_grounding(record: dict, evidence: dict) -> None:
    """Require cited evidence to resolve production entitlement, not just signup."""
    if record["api_type"] == "None":
        return
    items = _cited_items(record, evidence)
    signals = _access_signals(items)
    if not docs_research.access_decision_ready(items):
        raise ValueError(
            "cited evidence does not resolve production access; fetch a plan, pricing, "
            "approval, production, or official hosted-connection page"
        )

    kind = record["access_model"]["kind"]
    note = record["access_model"]["note"].lower()
    gate_signals = signals & {"manual_gate", "commercial_gate"}
    if kind == "Gated" and not gate_signals:
        raise ValueError("Gated access requires cited approval, customer, or paid-plan evidence")
    if kind != "Self-Serve":
        return

    free_production = "self_serve_production" in signals
    hosted_mcp = "hosted_connection" in signals and "mcp" in note
    free_api_path = "free_api_account" in signals
    if not (free_production or hosted_mcp or free_api_path):
        raise ValueError(
            "Self-Serve requires explicit free production credentials or a self-serve "
            "official MCP connection; signup/key generation alone is insufficient"
        )
    if gate_signals:
        free_exception = bool(
            re.search(r"\bfree (?:plan|tier|edition)\b", note)
            and not re.search(r"\b(?:free )?trial\b", note)
        )
        split_surface = hosted_mcp and bool(
            re.search(r"(?:rest|api).{0,80}gat|gat.{0,80}(?:rest|api)", note)
        )
        if not (free_exception or split_surface):
            raise ValueError(
                "Self-Serve conflicts with cited paid/approval evidence and no distinct "
                "free production or MCP path is explained"
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
    if access == "Self-Serve":
        access_text = " ".join([
            record["access_model"]["note"], record["main_blocker"]
        ]).lower()
        contradictory_gate = re.search(
            r"requires?.{0,60}(?:paid (?:plan|account)|existing customer|approval|review)|"
            r"after (?:the )?(?:free )?trial|trial (?:ends|expires)|"
            r"contact sales|business verification|partner approval",
            access_text,
        )
        if contradictory_gate and not re.search(
            r"\bfree (?:plan|tier|edition)\b|official mcp", access_text
        ):
            raise ValueError(
                "Self-Serve contradicts the record's own paid/trial/approval requirement"
            )


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
    _validate_auth_grounding(record, evidence)
    _validate_access_grounding(record, evidence)
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
    if evidence.get("degraded"):
        raise ValueError(
            f"{app_meta['slug']}: evidence is degraded; production access and auth "
            "must be resolved before synthesis"
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
        content_note = ""
        if item.get("content_url") and item["content_url"] != item.get("url"):
            content_note = f" | content={item['content_url']}"
        fetched_lines.append(
            f"- {item.get('url')} | HTTP {status} | {item.get('source_kind', 'unknown')} "
            f"| topics={topics}{content_note}"
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
            "## Risk seed (withheld from synthesis)",
            "This prior was retained only for audit sampling and was not shown to the model.",
            "```json",
            json.dumps(preseed["hypothesis"], indent=2, ensure_ascii=False),
            "```",
        ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
