"""Hand-check harness (Flag E — time-boxed to the two highest-risk fields).

generate_template(n):
  pick n apps biased to preseeded + low-confidence, spread across categories,
  and write handcheck/handcheck.json with the AGENT's values + blank TRUTH fields
  for a human to fill (auth_methods, access_model) in ~5 min/app.

fold():
  compare human truth vs agent for the filled rows, compute hand-checked accuracy
  (the ground-truth number, Flag B), mark those records verification_status=
  'Hand-Checked' in results.json, and write metrics['handcheck'].
"""
from __future__ import annotations

import datetime as dt

import config
import normalize
import pipeline
import verify
from schema import validate_record


def generate_template(n: int = 18) -> dict:
    results = config.load_json(config.RESULTS_PATH) or []
    if not results:
        raise SystemExit("no results.json — run `python research.py --all` first")
    preseed = pipeline.load_preseed_map()
    sample = verify._select_sample(results, n, preseed)  # preseed + low-conf + category spread

    rows = []
    for r in sample:
        rows.append({
            "slug": r["slug"], "app": r["app"], "category": r["category"],
            "primary_docs_url": r.get("primary_docs_url", ""),
            "preseeded": r["slug"] in preseed,
            "agent": {
                "auth_methods": r.get("auth_methods", []),
                "access_model": r["access_model"]["kind"],
                "recommended_next_action": r["recommended_next_action"],
                "confidence": r["confidence"],
            },
            "truth": {"auth_methods": [], "access_model": "", "next_action": "", "notes": ""},
            "filled": False,
        })

    payload = {
        "_instructions": ("For each row, open primary_docs_url and verify (~5 min). Fill "
                          "truth.auth_methods (list) and truth.access_model ('Self-Serve' or "
                          "'Gated'); add notes for any miss; set filled=true. Then run: "
                          "python research.py --fold-handcheck"),
        "generated": dt.date.today().isoformat(),
        "rows": rows,
    }
    config.ensure_dirs()
    config.save_json(config.HANDCHECK_PATH, payload)
    print(f"wrote {len(rows)} hand-check rows -> {config.HANDCHECK_PATH}")
    return payload


def fold() -> dict:
    """Score CURRENT results.json against hand-verified truth (per field) + list misses."""
    payload = config.load_json(config.HANDCHECK_PATH) or {}
    rows = [r for r in payload.get("rows", []) if r.get("filled")]
    results = config.load_json(config.RESULTS_PATH) or []
    by_slug = {r["slug"]: r for r in results}

    n = api_n = api_hits = auth_hits = access_hits = 0
    misses = []
    checked = []
    for row in rows:
        slug, truth = row["slug"], row["truth"]
        rec = by_slug.get(slug)
        if not rec:
            continue
        n += 1
        rec["verification_status"] = "Hand-Checked"
        cur_auth = rec.get("auth_methods", [])
        truth_auth = normalize.normalize_auth_list(truth.get("auth_methods") or [])
        aa = verify._auth_agree(cur_auth, truth_auth)
        cur_access = (rec.get("access_model") or {}).get("kind")
        ac = (cur_access == truth.get("access_model"))
        auth_hits += int(aa)
        access_hits += int(ac)
        if truth.get("api_type"):
            api_n += 1
            ok = rec.get("api_type") == truth.get("api_type")
            api_hits += int(ok)
            if not ok:
                misses.append({"slug": slug, "app": row.get("app", slug), "field": "api_type",
                               "current": rec.get("api_type"), "truth": truth.get("api_type"),
                               "notes": truth.get("notes", "")})
        if not aa:
            misses.append({"slug": slug, "app": row.get("app", slug), "field": "auth_methods",
                           "current": cur_auth, "truth": truth_auth, "notes": truth.get("notes", "")})
        if not ac:
            misses.append({"slug": slug, "app": row.get("app", slug), "field": "access_model",
                           "current": cur_access, "truth": truth.get("access_model"), "notes": truth.get("notes", "")})
        checked.append({"slug": slug, "app": row.get("app", slug),
                        "api_ok": (rec.get("api_type") == truth.get("api_type")) if truth.get("api_type") else None,
                        "auth_ok": bool(aa), "access_ok": bool(ac)})

    order = {a["slug"]: i for i, a in enumerate(pipeline.load_apps())}
    config.save_json(config.RESULTS_PATH, sorted(by_slug.values(), key=lambda r: order.get(r["slug"], 10_000)))

    total = 2 * n + api_n
    hc = {
        "method": ("Human cross-check vs official docs on api_type + auth_methods + access_model "
                   "(truth auth normalized to canonical labels before comparison). Misses shown, not hidden."),
        "n": n,
        "api_type_accuracy": round(api_hits / api_n, 3) if api_n else None,
        "auth_accuracy": round(auth_hits / n, 3) if n else None,
        "access_accuracy": round(access_hits / n, 3) if n else None,
        "accuracy": round((api_hits + auth_hits + access_hits) / total, 3) if total else None,
        "misses": misses,
        "checked": checked,
        "generated": dt.date.today().isoformat(),
    }
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["handcheck"] = hc
    config.save_json(config.METRICS_PATH, metrics)
    verify.rebuild_metrics()
    print(f"handcheck n={n}: api_type={hc['api_type_accuracy']} auth={hc['auth_accuracy']} "
          f"access={hc['access_accuracy']} overall={hc['accuracy']} misses={len(misses)}")
    return hc


def _score_record(rec: dict, truth: dict):
    """Field-level match of a record against hand truth (api_type + auth + access)."""
    checks = [
        ("auth_methods", verify._auth_agree(rec.get("auth_methods", []),
                                            normalize.normalize_auth_list(truth.get("auth_methods") or []))),
        ("access_model", (rec.get("access_model", {}) or {}).get("kind") == truth.get("access_model")),
    ]
    if truth.get("api_type"):
        checks.append(("api_type", rec.get("api_type") == truth.get("api_type")))
    hits = sum(1 for _, ok in checks if ok)
    return hits, len(checks)


def accuracy_movement() -> dict:
    """Score first-pass snapshot vs post-verification results against hand truth,
    to show accuracy moved up because of the verification loops (Flag B / rubric)."""
    hc = config.load_json(config.HANDCHECK_PATH) or {}
    rows = [r for r in hc.get("rows", []) if r.get("filled")]
    fp = {r["slug"]: r for r in (config.load_json(config.OUT_DIR / "results_firstpass.json") or [])}
    cur = {r["slug"]: r for r in (config.load_json(config.RESULTS_PATH) or [])}
    if not rows or not fp:
        raise SystemExit("need filled handcheck.json + out/results_firstpass.json")

    fh = ft = ch = ct = 0
    per_app, improved, regressed = [], [], []
    for row in rows:
        slug, truth = row["slug"], row["truth"]
        if slug not in fp or slug not in cur:
            continue
        h1, t1 = _score_record(fp[slug], truth)
        h2, t2 = _score_record(cur[slug], truth)
        fh += h1; ft += t1; ch += h2; ct += t2
        per_app.append({"slug": slug, "first_pass": f"{h1}/{t1}", "post_verification": f"{h2}/{t2}"})
        if h2 > h1:
            improved.append(slug)
        elif h2 < h1:
            regressed.append(slug)
        cur[slug]["verification_status"] = "Hand-Checked"

    order = {a["slug"]: i for i, a in enumerate(pipeline.load_apps())}
    config.save_json(config.RESULTS_PATH, sorted(cur.values(), key=lambda r: order.get(r["slug"], 10_000)))

    mv = {
        "method": ("Field-level accuracy (api_type + auth_methods + access_model) vs hand-verified "
                   "truth, comparing the first-pass snapshot to the post-verification results."),
        "n": len(rows),
        "first_pass_accuracy": round(fh / ft, 3) if ft else None,
        "post_verification_accuracy": round(ch / ct, 3) if ct else None,
        "improved_apps": improved,
        "regressed_apps": regressed,
        "per_app": per_app,
    }
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["accuracy_movement"] = mv
    config.save_json(config.METRICS_PATH, metrics)
    verify.rebuild_metrics()
    print(f"ACCURACY MOVEMENT | first-pass {mv['first_pass_accuracy']} -> "
          f"post-verification {mv['post_verification_accuracy']} (n={len(rows)}) | improved: {improved}")
    return mv
