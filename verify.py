"""Auditable blind re-search verification and report metrics.

Automated verification measures reproducibility. It never changes a researched
record or its confidence; a disagreement becomes an adjudication item until a
human accepts or rejects it against official documentation.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import os
from typing import Literal
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pydantic import BaseModel

import config
import docs_research
import normalize
import pipeline
import synthesis

VERIFY_SYSTEM = f"""Independently derive auth_methods and production access from fetched official documentation.

- Use only the supplied evidence and return strict JSON with exactly auth_methods and access_model.
- auth_methods must use only: {normalize.CANONICAL}.
- OAuth2 is the grant scheme; do not add Bearer Token just because an OAuth token uses a Bearer header.
- An OAuth client ID/client secret used only for registration or token exchange is not an API Key; a static client ID/secret required directly on API calls is. Use Personal Access Token for personal/programmatic tokens, Service Account for key-pair auth, and Other Token for OAuth 1.x.
- Include Basic Auth when official docs explicitly require HTTP Basic for API requests.
- Self-Serve means a new developer can obtain credentials usable in production without manual approval, partnership, business verification, or already being a paying customer.
- A sandbox/trial alone is not production Self-Serve. Otherwise use Gated.
- Key generation proves credential mechanics, not production entitlement; use the plan/pricing/production evidence too.
- access_model must be {{"kind":"Self-Serve"|"Gated","note":"..."}}.
- If the evidence cannot establish a field, explain that in the note rather than guessing."""


class VerificationAccess(BaseModel):
    kind: Literal["Self-Serve", "Gated"]
    note: str


class VerificationOutput(BaseModel):
    auth_methods: list[str]
    access_model: VerificationAccess


def _blind_queries(app: str) -> list[str]:
    return [
        f"{app} official API authentication OAuth API key developer documentation",
        f"{app} API production access approval sandbox existing customer official documentation",
        f"{app} official pricing API access free plan trial production plan",
    ]


def _auth_agree(left, right) -> bool:
    """Exact canonical-set equality, used for accuracy/agreement scoring."""
    return normalize.auth_sets_equal(left, right)


def _auth_overlap(left, right) -> bool:
    """A weaker diagnostic only; never presented as exact agreement."""
    return normalize.auth_sets_overlap(left, right)


def _canonical_verdict(parsed: dict) -> dict:
    if set(parsed) != {"auth_methods", "access_model"}:
        raise ValueError("verifier must return exactly auth_methods and access_model")
    if not isinstance(parsed.get("auth_methods"), list):
        raise ValueError("verifier auth_methods must be a list")
    auth = normalize.normalize_auth_list(parsed["auth_methods"], strict=True)
    if not auth:
        raise ValueError("verifier auth_methods must not be empty")
    access = parsed.get("access_model")
    if not isinstance(access, dict) or set(access) != {"kind", "note"}:
        raise ValueError("verifier access_model must contain exactly kind and note")
    kind = str(access.get("kind") or "").strip()
    if kind not in {"Self-Serve", "Gated"}:
        raise ValueError("verifier access_model.kind must be Self-Serve or Gated")
    note = str(access.get("note") or "").strip()
    if not note:
        raise ValueError("verifier access_model.note must explain production access")
    return {"auth_methods": auth, "access_model": {"kind": kind, "note": note}}


def _ground_verdict(verdict: dict, fetched: list[dict]) -> None:
    """Apply the same evidence-grounding rules as first-pass synthesis."""
    auth = verdict["auth_methods"]
    record = {
        "api_type": "None" if auth == ["None / Not Applicable"] else "REST",
        "auth_methods": auth,
        "access_model": verdict["access_model"],
        "evidence_urls": [item["url"] for item in fetched],
    }
    evidence = {"fetched": fetched, "mcp": {"fetched": []}}
    synthesis._validate_auth_grounding(record, evidence)
    synthesis._validate_access_grounding(record, evidence)


def _url_identity(url: str) -> str:
    """Canonical page identity so fragments/trailing slashes cannot bypass exclusion."""
    parsed = urlparse(url)
    query = urlencode(sorted(
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
    ))
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", query, ""))


def _safe_auth_equal(left, right) -> bool:
    try:
        return normalize.auth_sets_equal(left, right, strict=True)
    except ValueError:
        return False


def _rederive(app: str, exclude_urls: set[str], model: str | None,
              lead: str | None = None) -> dict | None:
    """Blindly re-derive two fields and retain the complete evidence trace."""
    queries = _blind_queries(app)
    search_results = docs_research._dedupe_search_results([
        docs_research.search_many(queries, k=8)
    ])
    candidates = docs_research._candidate_urls("", search_results, app=app)
    excluded_identities = {_url_identity(url) for url in exclude_urls}
    candidates = [
        url for url in candidates if _url_identity(url) not in excluded_identities
    ]

    fetched = []
    for url in candidates:
        item = docs_research.fetch(url)
        if item.get("ok"):
            text = item.get("text", "")
            item["support_tags"] = docs_research.support_tags(text, url)
            item["auth_signals"] = docs_research.auth_evidence_signals(text, url)
            item["access_signals"] = docs_research.access_evidence_signals(text, url)
            fetched.append(item)
        if len(fetched) >= 4:
            break
    topics = {tag for item in fetched for tag in item.get("support_tags", [])}
    if (
        not fetched
        or "auth" not in topics
        or not docs_research.access_decision_ready(fetched)
    ):
        return None

    evidence_text = "\n\n".join(
        f"URL: {item['url']}\nTOPICS: {','.join(item['support_tags']) or 'none'}\n"
        f"AUTH_SIGNALS: {','.join(item['auth_signals']) or 'none'}\n"
        f"ACCESS_SIGNALS: {','.join(item['access_signals']) or 'none'}\n"
        f"TEXT: {item['text'][:2800]}"
        for item in fetched
    )
    messages = [
        {"role": "system", "content": VERIFY_SYSTEM},
        {
            "role": "user",
            "content": f"APP: {app}\n\nFETCHED EVIDENCE:\n{evidence_text}\n\nReturn strict JSON now.",
        },
    ]
    try:
        parsed, _ = config.llm_json(
            messages,
            model=model,
            lead=lead,
            max_tokens=3072,
            response_schema=VerificationOutput,
        )
    except config.StructuredOutputError:
        parsed, _ = config.llm_json(
            [
                *messages,
                {
                    "role": "user",
                    "content": "Return one complete JSON object with every required key.",
                },
            ],
            model=model,
            lead=lead,
            thinking_level="low",
            max_tokens=3072,
            response_schema=VerificationOutput,
        )
    try:
        verdict = _canonical_verdict(parsed)
        _ground_verdict(verdict, fetched)
    except ValueError as exc:
        repair_messages = [
            *messages,
            {"role": "assistant", "content": json.dumps(parsed, ensure_ascii=False)},
            {
                "role": "user",
                "content": f"Validation failed: {exc}. Return the complete corrected JSON only.",
            },
        ]
        repaired, _ = config.llm_json(
            repair_messages,
            model=model,
            lead=lead,
            thinking_level="low",
            max_tokens=3072,
            response_schema=VerificationOutput,
        )
        verdict = _canonical_verdict(repaired)
        _ground_verdict(verdict, fetched)
    used_urls = [item["url"] for item in fetched]
    stored_hosts = {urlparse(url).netloc.lower() for url in exclude_urls}
    used_hosts = {urlparse(url).netloc.lower() for url in used_urls}
    return {
        "verdict": verdict,
        "queries": queries,
        "used_urls": used_urls,
        "model": config.last_llm_used() or model or config.PRIMARY_MODEL,
        "source_independence": {
            "no_exact_url_reused": not bool(
                {_url_identity(url) for url in used_urls} & excluded_identities
            ),
            "same_host_as_pass_1": bool(stored_hosts & used_hosts),
            "excluded_url_count": len(exclude_urls),
        },
    }


def _select_sample(results: list[dict], k: int, preseed: dict) -> list[dict]:
    """Risk-biased, category-spread sampling."""
    buckets: dict[str, list] = collections.defaultdict(list)
    for record in sorted(results, key=lambda row: (row["slug"] not in preseed, row["confidence"])):
        buckets[record["category"]].append(record)
    order = list(buckets)
    picked, index = [], 0
    while len(picked) < k and any(buckets.values()):
        category = order[index % len(order)]
        if buckets[category]:
            picked.append(buckets[category].pop(0))
        index += 1
    return picked


def run_verification(sample_size: int | None = None, model: str | None = None) -> dict:
    results = config.load_json(config.RESULTS_PATH) or []
    if not results:
        raise SystemExit("no results.json - run `python research.py --all` first")
    preseed = pipeline.load_preseed_map()
    sample = (
        results
        if not sample_size or sample_size >= len(results)
        else _select_sample(results, sample_size, preseed)
    )

    n = exact_auth_hits = overlap_auth_hits = access_hits = skipped = 0
    disagreements: list[dict] = []
    checks: list[dict] = []

    for record in sample:
        excluded = set(record.get("evidence_urls", []))
        if record.get("primary_docs_url"):
            excluded.add(record["primary_docs_url"])
        try:
            derived = _rederive(record["app"], excluded, model, lead=None)
        except Exception as exc:
            docs_research._log_failure(
                record["slug"], f"verify error: {type(exc).__name__}: {exc}", phase="verify"
            )
            skipped += 1
            continue
        if derived is None:
            docs_research._log_failure(
                record["slug"],
                "blind verification found no independent claim-bearing source",
                phase="verify",
            )
            skipped += 1
            continue

        verifier = derived["verdict"]
        docs_research.resolve_failure(record["slug"], "verify")
        exact_auth = _auth_agree(record.get("auth_methods", []), verifier["auth_methods"])
        overlap_auth = _auth_overlap(record.get("auth_methods", []), verifier["auth_methods"])
        access = record["access_model"]["kind"] == verifier["access_model"]["kind"]
        n += 1
        exact_auth_hits += int(exact_auth)
        overlap_auth_hits += int(overlap_auth)
        access_hits += int(access)

        agreement = {
            "auth_methods_exact": exact_auth,
            "auth_methods_overlap": overlap_auth,
            "access_model": access,
        }
        check = {
            "slug": record["slug"],
            "app": record["app"],
            "model": derived["model"],
            "queries": derived["queries"],
            "used_urls": derived["used_urls"],
            "source_independence": derived["source_independence"],
            "before": {
                "auth_methods": record.get("auth_methods", []),
                "access_model": record["access_model"],
                "confidence": record["confidence"],
            },
            "verifier": verifier,
            "agreement": agreement,
            "adjudication": "Pending" if not (exact_auth and access) else "Not Needed",
        }
        checks.append(check)
        if not exact_auth:
            disagreements.append({
                "slug": record["slug"], "app": record["app"], "field": "auth_methods",
                "before": record.get("auth_methods", []), "verifier": verifier["auth_methods"],
                "status": "Pending adjudication",
            })
        if not access:
            disagreements.append({
                "slug": record["slug"], "app": record["app"], "field": "access_model",
                "before": record["access_model"]["kind"],
                "verifier": verifier["access_model"]["kind"],
                "status": "Pending adjudication",
            })

    verification = {
        "method": (
            "Blind re-search with three fresh queries, independent fetched URLs, and a model blind "
            "to pass-1 values. Automated output is retained as a disagreement, never auto-folded."
        ),
        "n_verified": n,
        "n_skipped_no_independent_source": skipped,
        "auth_methods_exact_agreement_rate": round(exact_auth_hits / n, 3) if n else None,
        "auth_methods_overlap_rate": round(overlap_auth_hits / n, 3) if n else None,
        "auth_methods_agreement_rate": round(exact_auth_hits / n, 3) if n else None,
        "access_model_agreement_rate": round(access_hits / n, 3) if n else None,
        "overall_agreement_rate": round((exact_auth_hits + access_hits) / (2 * n), 3) if n else None,
        "confidence_policy": "Verification does not mutate record confidence or facts before adjudication.",
        "checks": checks,
        "disagreements": disagreements,
        "caveat": (
            "Agreement is reproducibility, not accuracy. Human checks against official docs are the "
            "accuracy measure. Auth scoring uses exact canonical sets."
        ),
        "generated": dt.date.today().isoformat(),
    }
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["verification"] = verification
    config.save_json(config.METRICS_PATH, metrics)
    rebuild_metrics()

    print(
        f"verified {n} (skipped {skipped}); exact auth agree "
        f"{verification['auth_methods_exact_agreement_rate']}, access agree "
        f"{verification['access_model_agreement_rate']}, overall "
        f"{verification['overall_agreement_rate']}; pending disagreements={len(disagreements)}"
    )
    return verification


def _browser_row_comparison(row: dict) -> dict | None:
    first_pass = row.get("first_pass", {})
    browser = row.get("browser", {})
    if browser.get("error"):
        return None
    matches = {
        "api_type": first_pass.get("api_type") == browser.get("api_type"),
        "auth_methods": _safe_auth_equal(
            first_pass.get("auth_methods", []), browser.get("auth_methods", [])
        ),
        "access_model": first_pass.get("access_model") == browser.get("access_model"),
    }
    return {
        "matches": matches,
        "disagreed_fields": [field for field, matched in matches.items() if not matched],
    }


def _browser_use_summary() -> dict:
    data = config.load_json(config.OUT_DIR / "browser_verification.json", default=[]) or []
    if isinstance(data, dict):
        data = data.get("rows", [])
    if not data:
        return {}

    disagreed_apps = []
    field_counts = collections.Counter()
    accepted_apps = []
    n_valid = 0
    for row in data:
        comparison = row.get("comparison") or _browser_row_comparison(row)
        if comparison is None:
            continue
        n_valid += 1
        fields = comparison.get("disagreed_fields", [])
        if fields:
            disagreed_apps.append(row.get("slug"))
            field_counts.update(fields)
        adjudication = row.get("adjudication") or {}
        status = adjudication.get("status") if isinstance(adjudication, dict) else adjudication
        applied = adjudication.get("applied_to_results") if isinstance(adjudication, dict) else False
        if status == "Accepted Correction" and applied is True:
            accepted_apps.append(row.get("slug"))

    return {
        "method": (
            "Independent browser reviews navigated live developer docs and re-derived API type, "
            "canonical auth, and production access. Disagreements require official-doc adjudication."
        ),
        "n_checked": n_valid,
        "n_disagreements": len(disagreed_apps),
        "disagreed_apps": disagreed_apps,
        "field_disagreements": dict(field_counts),
        "n_adjudicated_corrections": len(accepted_apps),
        "adjudicated_correction_apps": accepted_apps,
        # Compatibility keys for the current report renderer. Their meaning is
        # now strictly "accepted correction", never raw model disagreement.
        "n_corrections_found": len(accepted_apps),
        "corrected_apps": accepted_apps,
    }


def rebuild_metrics() -> dict:
    results = config.load_json(config.RESULTS_PATH) or []
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["patterns"] = pipeline.compute_aggregates(results)
    metrics["n_results"] = len(results)
    failure_state = config.load_json(config.FAILURE_STATE_PATH, default={}) or {}
    metrics["unresolved_failures"] = sorted(
        failure_state.values(), key=lambda item: (item.get("slug", ""), item.get("phase", ""))
    )
    browser_summary = _browser_use_summary()
    if browser_summary:
        metrics["browser_use"] = browser_summary
    batch_state = config.load_json(config.BATCH_STATE_PATH, default={}) or {}
    result_slugs = {record.get("slug") for record in results if record.get("slug")}
    completed_slugs = set(batch_state.get("completed_slugs") or [])
    source_audit_complete = bool(
        results
        and batch_state.get("status") == "complete"
        and not batch_state.get("active_job")
        and not batch_state.get("validation_failures")
        and completed_slugs == result_slugs
    )
    # The bulky batch checkpoint is intentionally gitignored after a completed run.
    # Preserve an already-published full audit when rebuilding derived metrics without it.
    prior_quality = metrics.get("quality") or {}
    if not batch_state and prior_quality.get("source_audit_complete"):
        source_audit_complete = prior_quality.get("source_audited_rows") == len(results)
    browser_evidence = config.load_json(config.BROWSER_EVIDENCE_PATH, default={}) or {}
    browser_entries = [
        entry
        for entry in browser_evidence.get("entries", [])
        if entry.get("slug") in result_slugs and entry.get("analyst_summary")
    ]
    metrics["quality"] = {
        "source_audit_complete": source_audit_complete,
        "source_audited_rows": len(results) if source_audit_complete else 0,
        "browser_evidence_pages": len(browser_entries),
        "browser_evidence_apps": len({entry["slug"] for entry in browser_entries}),
    }
    verification = metrics.get("verification", {})
    handcheck = metrics.get("handcheck", {})
    metrics["headline_accuracy"] = {
        "hand_checked_accuracy": {
            "value": handcheck.get("accuracy"),
            "n": handcheck.get("n"),
            "label": "Latest staged official-doc agreement",
        },
        "automated_agreement": {
            "value": verification.get("overall_agreement_rate"),
            "n": verification.get("n_verified"),
            "label": "Automated blind re-search agreement (not accuracy)",
        },
    }
    metrics["repo_url"] = os.getenv(
        "REPO_URL", "https://github.com/dheeraj3587/composio-ai-product-ops"
    )
    metrics["live_url"] = os.getenv(
        "LIVE_URL", "https://composio-ai-product-ops.vercel.app"
    )
    metrics["generated"] = dt.date.today().isoformat()
    config.save_json(config.METRICS_PATH, metrics)
    return metrics
