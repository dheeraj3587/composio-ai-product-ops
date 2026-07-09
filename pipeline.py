"""Pipeline: wire Composio lookup + docs research + LLM synthesis into one
``research_app()``, plus a concurrent, resumable batch runner and the pattern
aggregates the report leads with.
"""
from __future__ import annotations

import collections
import concurrent.futures as cf
import threading
from functools import lru_cache

import composio_lookup
import config
import docs_research
import synthesis


@lru_cache(maxsize=1)
def load_apps() -> list[dict]:
    return (config.load_json(config.APPS_PATH) or {}).get("apps", [])


@lru_cache(maxsize=1)
def load_preseed_map() -> dict:
    seeds = (config.load_json(config.PRESEED_PATH) or {}).get("seeds", [])
    return {s["slug"]: s for s in seeds}


def get_app(slug: str) -> dict:
    for a in load_apps():
        if a["slug"] == slug:
            return a
    raise KeyError(f"unknown app slug: {slug!r}")


# --------------------------------------------------------------------------- #
# single app
# --------------------------------------------------------------------------- #
def research_app(app: dict, model: str | None = None, log: bool = True,
                 lead: str | None = None):
    """app: a record from apps.json. Returns (AppRecord, info)."""
    meta = {"app": app["app"], "slug": app["slug"],
            "category": app["category"], "hint_url": app.get("hint_url") or ""}
    composio_signal = composio_lookup.lookup(meta["app"], meta["slug"])
    preseed = load_preseed_map().get(meta["slug"])
    evidence = docs_research.gather_evidence(
        meta["app"], meta["slug"], hint_url=meta["hint_url"], category=meta["category"])
    rec, reasoning = synthesis.synthesize(
        meta, evidence, composio_signal, preseed=preseed, model=model, write_log=log, lead=lead)
    info = {"preseed_used": bool(preseed), "degraded": evidence["degraded"],
            "n_fetched": len(evidence["fetched_urls"]), "query": evidence["query"]}
    return rec, info


# --------------------------------------------------------------------------- #
# batch (concurrent + resumable)
# --------------------------------------------------------------------------- #
_write_lock = threading.Lock()


def _ordered(results_by_slug: dict) -> list[dict]:
    order = {a["slug"]: i for i, a in enumerate(load_apps())}
    return sorted(results_by_slug.values(), key=lambda r: order.get(r["slug"], 10_000))


def _save(results_by_slug: dict) -> None:
    config.save_json(config.RESULTS_PATH, _ordered(results_by_slug))


def run_batch(slugs: list[str] | None = None, workers: int = 6,
              resume: bool = True, model: str | None = None,
              shard: bool = True) -> list[dict]:
    config.ensure_dirs()
    apps = load_apps()
    if slugs:
        want = set(slugs)
        apps = [a for a in apps if a["slug"] in want]

    existing = {}
    if resume:
        existing = {r["slug"]: r for r in (config.load_json(config.RESULTS_PATH) or [])}
    todo = [a for a in apps if a["slug"] not in existing]
    results = dict(existing)

    providers = config.keyed_shard_providers() if shard else []
    sharding = len(providers) > 1 and not model
    mode = ("shard across " + "+".join(providers)) if sharding else f"model={model or config.OPENROUTER_MODEL}"
    print(f"batch: {len(apps)} requested, {len(existing)} cached, {len(todo)} to run "
          f"(workers={workers}, {mode})")

    def work(a: dict, idx: int):
        lead = providers[idx % len(providers)] if sharding else None
        rec, info = research_app(a, model=model, lead=lead)
        return a["slug"], rec.model_dump(mode="json"), info, lead

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(work, a, i): a for i, a in enumerate(todo)}
        for fut in cf.as_completed(futs):
            a = futs[fut]
            try:
                slug, rec, info, lead = fut.result()
                results[slug] = rec
                with _write_lock:
                    _save(results)
                flag = " [degraded]" if info["degraded"] else ""
                via = f" via {lead}" if lead else ""
                print(f"[ok] {slug}: {rec['buildability']}/{rec['recommended_next_action']} "
                      f"conf={rec['confidence']}{via}{flag}")
            except Exception as e:  # honest failure log — never silently guess
                docs_research._log_failure(a["slug"], f"pipeline error: {type(e).__name__}: {e}")
                print(f"[FAIL] {a['slug']}: {type(e).__name__}: {e}")

    ordered = _ordered(results)
    _save(results)
    return ordered


# --------------------------------------------------------------------------- #
# pattern aggregates (the report headline)
# --------------------------------------------------------------------------- #
def compute_aggregates(results: list[dict]) -> dict:
    n = len(results)
    if not n:
        return {"n": 0}

    def count(get):
        return dict(collections.Counter(get(r) for r in results))

    auth = collections.Counter()
    for r in results:
        for a in r.get("auth_methods", []):
            auth[a] += 1

    access_by_cat: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in results:
        access_by_cat[r["category"]][r["access_model"]["kind"]] += 1

    blockers = collections.Counter(r["main_blocker"] for r in results if r.get("main_blocker"))

    return {
        "n": n,
        "buildability": count(lambda r: r["buildability"]),
        "recommended_next_action": count(lambda r: r["recommended_next_action"]),
        "access_model": count(lambda r: r["access_model"]["kind"]),
        "api_type": count(lambda r: r["api_type"]),
        "existing_mcp": count(lambda r: r["existing_mcp"]),
        "composio_toolkit": count(lambda r: r["composio_toolkit"]),
        "auth_methods_top": auth.most_common(8),
        "access_by_category": {k: dict(v) for k, v in access_by_cat.items()},
        "top_blockers": blockers.most_common(6),
        "build_now": sum(1 for r in results if r["recommended_next_action"] == "Build Now"),
        "partner_gated": sum(1 for r in results if r["recommended_next_action"] == "Partner-Gated"),
        "avg_confidence": round(sum(r["confidence"] for r in results) / n, 3),
    }
