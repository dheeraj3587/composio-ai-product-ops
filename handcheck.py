"""Risk-biased human hand-check harness and current-vs-historical metrics."""
from __future__ import annotations

import datetime as dt

import config
import normalize
import pipeline
import synthesis
import verify
from schema import validate_record


ACCESS_RUBRIC = (
    "Self-Serve only when a new developer can obtain credentials usable in production without "
    "manual approval, partnership, business verification, or already being a paying customer. "
    "A sandbox or trial alone is not production Self-Serve; otherwise use Gated."
)


def generate_template(n: int = 18) -> dict:
    results = config.load_json(config.RESULTS_PATH) or []
    if not results:
        raise SystemExit("no results.json - run `python research.py --all` first")
    preseed = pipeline.load_preseed_map()
    sample = verify._select_sample(results, n, preseed)

    rows = []
    for record in sample:
        rows.append({
            "slug": record["slug"],
            "app": record["app"],
            "category": record["category"],
            "primary_docs_url": record.get("primary_docs_url", ""),
            "preseeded": record["slug"] in preseed,
            "selection_reason": (
                "preseeded/low-confidence, category-spread risk sample"
                if record["slug"] in preseed or record["confidence"] < 0.7
                else "category-spread control"
            ),
            "agent": {
                "api_type": record.get("api_type"),
                "auth_methods": record.get("auth_methods", []),
                "access_model": record["access_model"]["kind"],
                "recommended_next_action": record["recommended_next_action"],
                "confidence": record["confidence"],
            },
            "truth": {
                "api_type": "",
                "auth_methods": [],
                "access_model": "",
                "existing_mcp": "",
                "evidence_urls": [],
                "notes": "",
            },
            "filled": False,
        })

    payload = {
        "_instructions": (
            "For each row, inspect official docs and fill truth.api_type, canonical auth_methods, "
            "production access_model, existing_mcp, evidence_urls, and notes; then set filled=true. " +
            ACCESS_RUBRIC + " Run: python research.py --fold-handcheck"
        ),
        "auth_vocabulary": normalize.CANONICAL,
        "access_rubric": ACCESS_RUBRIC,
        "selection": "Risk-biased (preseeded + low-confidence) with category spread and controls.",
        "generated": dt.date.today().isoformat(),
        "rows": rows,
    }
    config.ensure_dirs()
    existing = config.load_json(config.HANDCHECK_PATH) or {}
    if any(row.get("filled") for row in existing.get("rows", [])):
        alternate = config.HANDCHECK_PATH.with_name("handcheck.template.json")
        config.save_json(alternate, payload)
        print(f"handcheck.json already contains filled truth - wrote template to {alternate}")
        return payload
    config.save_json(config.HANDCHECK_PATH, payload)
    print(f"wrote {len(rows)} hand-check rows -> {config.HANDCHECK_PATH}")
    return payload


def _validated_truth(row: dict) -> dict:
    truth = row.get("truth") or {}
    auth = normalize.normalize_auth_list(truth.get("auth_methods") or [], strict=True)
    if not auth:
        raise ValueError(f"{row.get('slug')}: filled row has no truth.auth_methods")
    access = truth.get("access_model")
    if access not in {"Self-Serve", "Gated"}:
        raise ValueError(f"{row.get('slug')}: invalid truth.access_model={access!r}")
    api_type = truth.get("api_type")
    if api_type and api_type not in {"REST", "GraphQL", "SDK", "SOAP", "MCP-only", "None"}:
        raise ValueError(f"{row.get('slug')}: invalid truth.api_type={api_type!r}")
    existing_mcp = truth.get("existing_mcp")
    if existing_mcp and existing_mcp not in {"Official", "Community", "None"}:
        raise ValueError(f"{row.get('slug')}: invalid truth.existing_mcp={existing_mcp!r}")
    evidence_urls = truth.get("evidence_urls")
    if not isinstance(evidence_urls, list) or not evidence_urls or any(
        not isinstance(url, str) or not url.startswith(("http://", "https://"))
        for url in evidence_urls
    ):
        raise ValueError(f"{row.get('slug')}: truth.evidence_urls needs at least one official URL")
    if not str(truth.get("notes") or "").strip():
        raise ValueError(f"{row.get('slug')}: truth.notes must explain the check")
    return {**truth, "auth_methods": auth, "access_model": access}


def _require_current_rubric(payload: dict) -> None:
    if payload.get("access_rubric") != ACCESS_RUBRIC:
        raise SystemExit(
            "handcheck.json uses the legacy trial-access rubric. Generate/fill a fresh template "
            "before computing current metrics. The old score remains historical evidence."
        )


def fold() -> dict:
    """Score the current results only; never substitute historical agent values."""
    payload = config.load_json(config.HANDCHECK_PATH) or {}
    _require_current_rubric(payload)
    rows = [row for row in payload.get("rows", []) if row.get("filled")]
    results = config.load_json(config.RESULTS_PATH) or []
    by_slug = {record["slug"]: record for record in results}

    n = api_n = api_hits = mcp_n = mcp_hits = auth_hits = access_hits = 0
    misses, checked = [], []
    for row in rows:
        slug = row["slug"]
        record = by_slug.get(slug)
        if not record:
            continue
        truth = _validated_truth(row)
        n += 1
        current_auth = normalize.normalize_auth_list(record.get("auth_methods", []), strict=True)
        auth_ok = verify._auth_agree(current_auth, truth["auth_methods"])
        current_access = (record.get("access_model") or {}).get("kind")
        access_ok = current_access == truth["access_model"]
        auth_hits += int(auth_ok)
        access_hits += int(access_ok)

        api_ok = None
        if truth.get("api_type"):
            api_n += 1
            api_ok = record.get("api_type") == truth["api_type"]
            api_hits += int(api_ok)
            if not api_ok:
                misses.append({
                    "slug": slug, "app": row.get("app", slug), "field": "api_type",
                    "current": record.get("api_type"), "truth": truth["api_type"],
                    "notes": truth.get("notes", ""),
                })
        mcp_ok = None
        if truth.get("existing_mcp"):
            mcp_n += 1
            mcp_ok = record.get("existing_mcp") == truth["existing_mcp"]
            mcp_hits += int(mcp_ok)
            if not mcp_ok:
                misses.append({
                    "slug": slug, "app": row.get("app", slug), "field": "existing_mcp",
                    "current": record.get("existing_mcp"), "truth": truth["existing_mcp"],
                    "notes": truth.get("notes", ""),
                })
        if not auth_ok:
            misses.append({
                "slug": slug, "app": row.get("app", slug), "field": "auth_methods",
                "current": current_auth, "truth": truth["auth_methods"],
                "notes": truth.get("notes", ""),
            })
        if not access_ok:
            misses.append({
                "slug": slug, "app": row.get("app", slug), "field": "access_model",
                "current": current_access, "truth": truth["access_model"],
                "notes": truth.get("notes", ""),
            })
        record["verification_status"] = "Hand-Checked"
        validate_record(record)
        synthesis.append_final_state(record, reason="current handcheck fold")
        checked.append({
            "slug": slug,
            "app": row.get("app", slug),
            "api_ok": api_ok,
            "mcp_ok": mcp_ok,
            "auth_ok": auth_ok,
            "access_ok": access_ok,
        })

    order = {app["slug"]: index for index, app in enumerate(pipeline.load_apps())}
    config.save_json(
        config.RESULTS_PATH,
        sorted(by_slug.values(), key=lambda record: order.get(record["slug"], 10_000)),
    )

    total = 2 * n + api_n + mcp_n
    handcheck = {
        "metric_scope": "Staged cumulative official-doc check at fold time",
        "method": (
            "Analyst adjudication against official docs for api_type, exact canonical auth set, "
            "production access, and MCP ownership. No historical agent values are substituted."
        ),
        "access_rubric": payload.get("access_rubric") or ACCESS_RUBRIC,
        "selection": payload.get("selection") or "Risk-biased, category-spread sample.",
        "n": n,
        "api_type_accuracy": round(api_hits / api_n, 3) if api_n else None,
        "mcp_accuracy": round(mcp_hits / mcp_n, 3) if mcp_n else None,
        "auth_accuracy": round(auth_hits / n, 3) if n else None,
        "access_accuracy": round(access_hits / n, 3) if n else None,
        "accuracy": round((api_hits + auth_hits + access_hits + mcp_hits) / total, 3) if total else None,
        "misses": misses,
        "checked": checked,
        "generated": dt.date.today().isoformat(),
        "note": (
            "This is the latest staged pre-fold agreement. Earlier checked batches may already "
            "have been corrected before later batches are added; it is not a blind first-pass estimate."
        ),
    }
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    previous = metrics.get("handcheck")
    if previous and previous != handcheck and "handcheck_historical" not in metrics:
        metrics["handcheck_historical"] = {
            "label": "Prior published hand-check snapshot",
            "snapshot": previous,
        }
    metrics["handcheck"] = handcheck
    config.save_json(config.METRICS_PATH, metrics)
    verify.rebuild_metrics()
    print(
        f"handcheck CURRENT n={n}: api_type={handcheck['api_type_accuracy']} "
        f"auth={handcheck['auth_accuracy']} access={handcheck['access_accuracy']} "
        f"mcp={handcheck['mcp_accuracy']} "
        f"overall={handcheck['accuracy']} misses={len(misses)}"
    )
    return handcheck


def _score_record(record: dict, truth: dict) -> tuple[int, int]:
    canonical_truth = normalize.normalize_auth_list(truth.get("auth_methods") or [], strict=True)
    checks = [
        ("auth_methods", verify._auth_agree(record.get("auth_methods", []), canonical_truth)),
        ("access_model", (record.get("access_model") or {}).get("kind") == truth.get("access_model")),
    ]
    if truth.get("api_type"):
        checks.append(("api_type", record.get("api_type") == truth.get("api_type")))
    if truth.get("existing_mcp"):
        checks.append(("existing_mcp", record.get("existing_mcp") == truth.get("existing_mcp")))
    return sum(int(ok) for _, ok in checks), len(checks)


def apply_corrections() -> int:
    """Apply only filled current-rubric truth after recording the hand-check score."""
    payload = config.load_json(config.HANDCHECK_PATH) or {}
    _require_current_rubric(payload)
    rows = [row for row in payload.get("rows", []) if row.get("filled")]
    if not rows:
        raise SystemExit("handcheck.json has no filled rows")

    results = config.load_json(config.RESULTS_PATH) or []
    by_slug = {record["slug"]: record for record in results}
    allowed_overrides = {
        "one_liner", "api_breadth", "buildability", "main_blocker",
        "recommended_next_action", "rate_limit_note", "confidence",
    }
    corrected = 0
    for row in rows:
        slug = row["slug"]
        record = by_slug.get(slug)
        if not record:
            continue
        truth = _validated_truth(row)
        correction = row.get("correction") or {}
        unknown = set(correction) - allowed_overrides - {"access_note"}
        if unknown:
            raise ValueError(f"{slug}: unsupported correction fields={sorted(unknown)}")

        record["api_type"] = truth["api_type"]
        record["auth_methods"] = truth["auth_methods"]
        record["access_model"] = {
            "kind": truth["access_model"],
            "note": str(
                correction.get("access_note")
                or record.get("access_model", {}).get("note")
                or truth["notes"]
            ).strip(),
        }
        if truth.get("existing_mcp"):
            record["existing_mcp"] = truth["existing_mcp"]
        record["evidence_urls"] = list(dict.fromkeys(truth["evidence_urls"]))
        record["primary_docs_url"] = record["evidence_urls"][0]
        for key in allowed_overrides:
            if key in correction:
                record[key] = correction[key]
        record["verification_status"] = "Hand-Checked"
        validate_record(record)
        synthesis._validate_semantics(record)
        synthesis.append_final_state(record, reason="current human handcheck correction")
        corrected += 1

    order = {app["slug"]: index for index, app in enumerate(pipeline.load_apps())}
    config.save_json(
        config.RESULTS_PATH,
        sorted(by_slug.values(), key=lambda record: order.get(record["slug"], 10_000)),
    )
    verify.rebuild_metrics()
    print(f"applied current human handcheck truth to {corrected} rows")
    return corrected


def accuracy_movement() -> dict:
    """Compare archived first-pass and current results against the same hand truth."""
    payload = config.load_json(config.HANDCHECK_PATH) or {}
    _require_current_rubric(payload)
    rows = [row for row in payload.get("rows", []) if row.get("filled")]
    first_pass = {
        record["slug"]: record
        for record in (config.load_json(config.OUT_DIR / "results_firstpass.json") or [])
    }
    current = {record["slug"]: record for record in (config.load_json(config.RESULTS_PATH) or [])}
    if not rows or not first_pass:
        raise SystemExit("need filled handcheck.json + out/results_firstpass.json")

    first_hits = first_total = current_hits = current_total = 0
    per_app, improved, regressed = [], [], []
    for row in rows:
        slug = row["slug"]
        if slug not in first_pass or slug not in current:
            continue
        truth = _validated_truth(row)
        before_hits, before_total = _score_record(first_pass[slug], truth)
        after_hits, after_total = _score_record(current[slug], truth)
        first_hits += before_hits
        first_total += before_total
        current_hits += after_hits
        current_total += after_total
        per_app.append({
            "slug": slug,
            "first_pass": f"{before_hits}/{before_total}",
            "current": f"{after_hits}/{after_total}",
        })
        if after_hits > before_hits:
            improved.append(slug)
        elif after_hits < before_hits:
            regressed.append(slug)

    movement = {
        "method": (
            "Field-level accuracy against one hand-verified truth set, comparing the archived "
            "first pass to current results. Auth uses exact canonical-set equality."
        ),
        "n": len(per_app),
        "first_pass_accuracy": round(first_hits / first_total, 3) if first_total else None,
        "post_verification_accuracy": round(current_hits / current_total, 3) if current_total else None,
        "improved_apps": improved,
        "regressed_apps": regressed,
        "per_app": per_app,
        "generated": dt.date.today().isoformat(),
    }
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["accuracy_movement"] = movement
    config.save_json(config.METRICS_PATH, metrics)
    verify.rebuild_metrics()
    print(
        f"ACCURACY MOVEMENT | first-pass {movement['first_pass_accuracy']} -> "
        f"current {movement['post_verification_accuracy']} (n={len(per_app)}) | "
        f"improved: {improved}; regressed: {regressed}"
    )
    return movement
