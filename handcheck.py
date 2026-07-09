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
    payload = config.load_json(config.HANDCHECK_PATH) or {}
    rows = [r for r in payload.get("rows", []) if r.get("filled")]
    results = config.load_json(config.RESULTS_PATH) or []
    by_slug = {r["slug"]: r for r in results}

    n = len(rows)
    auth_hits = access_hits = 0
    misses = []
    for row in rows:
        agent, truth = row["agent"], row["truth"]
        aa = verify._auth_agree(agent.get("auth_methods", []), truth.get("auth_methods") or [])
        ac = (agent.get("access_model") == truth.get("access_model"))
        auth_hits += int(aa)
        access_hits += int(ac)
        if row["slug"] in by_slug:
            by_slug[row["slug"]]["verification_status"] = "Hand-Checked"
        if not aa:
            misses.append({"slug": row["slug"], "app": row["app"], "field": "auth_methods",
                           "agent": agent.get("auth_methods"), "truth": truth.get("auth_methods"),
                           "notes": truth.get("notes", "")})
        if not ac:
            misses.append({"slug": row["slug"], "app": row["app"], "field": "access_model",
                           "agent": agent.get("access_model"), "truth": truth.get("access_model"),
                           "notes": truth.get("notes", "")})

    if results:  # persist verification_status flips
        updated = [validate_record(by_slug[r["slug"]]).model_dump(mode="json") for r in results]
        config.save_json(config.RESULTS_PATH, updated)

    hc = {
        "method": ("Human verification of the two highest-risk fields (auth_methods, "
                   "access_model) against primary docs; ~5 min/app (Flag E)."),
        "n": n,
        "auth_accuracy": round(auth_hits / n, 3) if n else None,
        "access_accuracy": round(access_hits / n, 3) if n else None,
        "accuracy": round((auth_hits + access_hits) / (2 * n), 3) if n else None,
        "misses": misses,
        "generated": dt.date.today().isoformat(),
    }
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["handcheck"] = hc
    config.save_json(config.METRICS_PATH, metrics)
    verify.rebuild_metrics()

    if n:
        print(f"folded {n} hand-checked rows; accuracy={hc['accuracy']} "
              f"(auth {hc['auth_accuracy']}, access {hc['access_accuracy']}), misses={len(misses)}")
    else:
        print("no filled rows yet — fill handcheck/handcheck.json, then re-run --fold-handcheck")
    return hc


def _score_record(rec: dict, truth: dict):
    """Field-level match of a record against hand truth (api_type + auth + access)."""
    checks = [
        ("auth_methods", verify._auth_agree(rec.get("auth_methods", []), truth.get("auth_methods") or [])),
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
    metrics.setdefault("handcheck", {})
    metrics["handcheck"]["n"] = len(rows)
    metrics["handcheck"]["accuracy"] = mv["post_verification_accuracy"]
    config.save_json(config.METRICS_PATH, metrics)
    verify.rebuild_metrics()
    print(f"ACCURACY MOVEMENT | first-pass {mv['first_pass_accuracy']} -> "
          f"post-verification {mv['post_verification_accuracy']} (n={len(rows)}) | improved: {improved}")
    return mv
