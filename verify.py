"""Verification (Flag A) + honest metrics (Flag B).

Flag A — BLIND RE-SEARCH FROM SCRATCH (not a re-fetch):
  For a sample of records we independently re-derive the two highest-risk fields
  (auth_methods, access_model) using a FRESH, differently-phrased query, fetching
  pages that EXCLUDE the stored evidence URLs, and asking the LLM blind (it never
  sees pass-1's answer). This catches wrong-PAGE errors, not just wrong-reading —
  re-fetching the stored URL would only re-confirm a correlated error.

Flag B — two clearly-labeled numbers:
  * hand-checked accuracy (ground truth, from handcheck.json)  -> the real accuracy
  * automated blind-re-search AGREEMENT rate (this module)     -> NOT accuracy
"""
from __future__ import annotations

import collections
import datetime as dt
import re

import config
import docs_research
import pipeline
from schema import validate_record

VERIFY_SYSTEM = (
    "You independently determine ONLY two things about an app's API from the "
    "evidence provided: (1) auth_methods (list, e.g. OAuth2, API Key, PAT), and "
    "(2) access_model — whether obtaining API access is 'Self-Serve' (instant "
    "signup/keys) or 'Gated' (approval, business verification, or existing paid "
    "account required). Use ONLY the evidence. Return strict JSON with keys "
    "auth_methods (list) and access_model ({kind:'Self-Serve'|'Gated', note})."
)


def _blind_query(app: str) -> str:
    return (f"How do developers authenticate with the {app} API and is API access "
            f"self-serve or does it require approval or a paid account")


def _norm_auth(items) -> set[str]:
    return {re.sub(r"[^a-z0-9]", "", str(x).lower()) for x in (items or []) if str(x).strip()}


def _auth_agree(a, b) -> bool:
    na, nb = _norm_auth(a), _norm_auth(b)
    if not na and not nb:
        return True
    if not na or not nb:
        return False
    return len(na & nb) > 0 and len(na ^ nb) <= 1


def _rederive(app: str, exclude_urls: set[str], model: str | None, lead: str | None = None):
    """Independent, blind re-derivation. Returns (parsed, used_urls, query) or None."""
    q = _blind_query(app)
    results = docs_research.search(q, k=8)
    cands = [r["url"] for r in results
             if r.get("url", "").startswith("http") and r["url"] not in exclude_urls][:3]
    fetched = [docs_research.fetch(u) for u in cands]
    ok = [f for f in fetched if f["ok"]]
    if not ok:
        return None  # cannot verify blindly -> honestly skip
    ev = "\n\n".join(f"URL: {f['url']}\nTEXT: {f['text'][:2500]}" for f in ok)
    messages = [
        {"role": "system", "content": VERIFY_SYSTEM},
        {"role": "user", "content": f"APP: {app}\n\nEVIDENCE:\n{ev}\n\nReturn the strict JSON now."},
    ]
    parsed, _ = config.llm_json(messages, model=model, lead=lead)
    return parsed, [f["url"] for f in ok], q


def _select_sample(results: list[dict], k: int, preseed: dict) -> list[dict]:
    """Round-robin across categories; within each, preseeded + low-confidence first
    (Flag C triage)."""
    buckets: dict[str, list] = collections.defaultdict(list)
    for r in sorted(results, key=lambda r: (r["slug"] not in preseed, r["confidence"])):
        buckets[r["category"]].append(r)
    order = list(buckets)
    picked, i = [], 0
    while len(picked) < k and any(buckets.values()):
        cat = order[i % len(order)]
        if buckets[cat]:
            picked.append(buckets[cat].pop(0))
        i += 1
        if i > 100_000:
            break
    return picked


def run_verification(sample_size: int | None = None, model: str | None = None) -> dict:
    results = config.load_json(config.RESULTS_PATH) or []
    if not results:
        raise SystemExit("no results.json — run `python research.py --all` first")
    by_slug = {r["slug"]: r for r in results}
    preseed = pipeline.load_preseed_map()

    if not sample_size or sample_size >= len(results):
        sample = results  # verify everything -> agreement rate n = len(results)
    else:
        sample = _select_sample(results, sample_size, preseed)

    n = auth_hits = access_hits = 0
    skipped = 0
    conf_before = conf_after = 0.0
    disagreements: list[dict] = []
    providers = config.keyed_shard_providers()

    for i, r in enumerate(sample):
        exclude = set(r.get("evidence_urls", []))
        if r.get("primary_docs_url"):
            exclude.add(r["primary_docs_url"])
        lead = providers[i % len(providers)] if len(providers) > 1 else None
        try:
            out = _rederive(r["app"], exclude, model, lead=lead)
        except Exception as e:  # a bad app shouldn't crash the whole pass
            docs_research._log_failure(r["slug"], f"verify error: {type(e).__name__}: {e}")
            skipped += 1
            continue
        if out is None:
            skipped += 1
            continue
        parsed, _used, _q = out
        n += 1

        after_auth = parsed.get("auth_methods") or []
        after_access = parsed.get("access_model") or {}
        if isinstance(after_access, str):
            after_access = {"kind": "Gated" if "gat" in after_access.lower() else "Self-Serve"}
        after_kind = after_access.get("kind")

        aa = _auth_agree(r.get("auth_methods", []), after_auth)
        ac = (r["access_model"]["kind"] == after_kind)
        auth_hits += int(aa)
        access_hits += int(ac)

        # recalibrate confidence from the independent second opinion
        conf_before += r["confidence"]
        if aa and ac:
            newc = min(0.98, round(r["confidence"] + 0.05, 3))
        elif not aa and not ac:
            newc = round(r["confidence"] * 0.6, 3)
        else:
            newc = round(r["confidence"] * 0.8, 3)
        conf_after += newc
        by_slug[r["slug"]]["confidence"] = newc

        if not aa:
            disagreements.append({"slug": r["slug"], "app": r["app"], "field": "auth_methods",
                                  "before": r.get("auth_methods", []), "after": after_auth})
        if not ac:
            disagreements.append({"slug": r["slug"], "app": r["app"], "field": "access_model",
                                  "before": r["access_model"]["kind"], "after": after_kind})

    # persist confidence-adjusted, re-validated records
    updated = [validate_record(by_slug[r["slug"]]).model_dump(mode="json") for r in results]
    config.save_json(config.RESULTS_PATH, updated)

    verification = {
        "method": ("Blind re-search from scratch: fresh differently-phrased query, "
                   "independent fetch EXCLUDING stored evidence URLs, LLM blind to the "
                   "pass-1 answer. Re-derived fields: auth_methods, access_model."),
        "n_verified": n,
        "n_skipped_no_independent_source": skipped,
        "auth_methods_agreement_rate": round(auth_hits / n, 3) if n else None,
        "access_model_agreement_rate": round(access_hits / n, 3) if n else None,
        "overall_agreement_rate": round((auth_hits + access_hits) / (2 * n), 3) if n else None,
        "avg_confidence_before": round(conf_before / n, 3) if n else None,
        "avg_confidence_after": round(conf_after / n, 3) if n else None,
        "disagreements": disagreements,
        "caveat": ("Agreement rate is NOT accuracy — it measures whether an independent "
                   "second pass reproduced pass 1. True accuracy is the hand-checked number."),
        "generated": dt.date.today().isoformat(),
    }
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["verification"] = verification
    config.save_json(config.METRICS_PATH, metrics)
    rebuild_metrics()

    print(f"verified {n} (skipped {skipped}); auth agree "
          f"{verification['auth_methods_agreement_rate']}, access agree "
          f"{verification['access_model_agreement_rate']}, overall "
          f"{verification['overall_agreement_rate']}; disagreements={len(disagreements)}")
    return verification


def _browser_use_summary() -> dict:
    """Summarize the Browser Use Cloud verification loop (out/browser_verification.json),
    if present, so the report can name it as a distinct, real loop."""
    data = config.load_json(config.OUT_DIR / "browser_verification.json", default=[]) or []
    if not data:
        return {}
    corrected = []
    for row in data:
        fp, b = row.get("first_pass", {}), row.get("browser", {})
        if fp.get("api_type") != b.get("api_type") or fp.get("access_model") != b.get("access_model"):
            corrected.append(row.get("slug"))
    return {
        "method": ("A cloud browser agent (Browser Use Cloud) independently navigated each app's "
                   "live developer docs and re-derived API type, auth, and access model — a channel "
                   "independent of the pipeline's own search+fetch and LLM synthesis."),
        "n_checked": len(data),
        "n_corrections_found": len(corrected),
        "corrected_apps": corrected,
    }


def rebuild_metrics() -> dict:
    """Recompute patterns from current results.json and assemble the two labeled numbers."""
    results = config.load_json(config.RESULTS_PATH) or []
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["patterns"] = pipeline.compute_aggregates(results)
    metrics["n_results"] = len(results)
    bu = _browser_use_summary()
    if bu:
        metrics["browser_use"] = bu
    ver = metrics.get("verification", {})
    hc = metrics.get("handcheck", {})
    metrics["headline_accuracy"] = {
        "hand_checked_accuracy": {
            "value": hc.get("accuracy"), "n": hc.get("n"),
            "label": "Hand-checked accuracy (ground truth)"},
        "automated_agreement": {
            "value": ver.get("overall_agreement_rate"), "n": ver.get("n_verified"),
            "label": "Automated blind re-search agreement (not accuracy)"},
    }
    import os
    metrics["repo_url"] = os.getenv("REPO_URL", "https://github.com/dheeraj3587/composio-ai-product-ops")
    metrics["live_url"] = os.getenv("LIVE_URL", "https://composio-ai-product-ops.vercel.app")
    metrics["generated"] = dt.date.today().isoformat()
    config.save_json(config.METRICS_PATH, metrics)
    return metrics
