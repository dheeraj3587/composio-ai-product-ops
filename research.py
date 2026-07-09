#!/usr/bin/env python3
"""CLI for the API Integration Readiness agent.

python research.py --app stripe           # research one app, print the record
python research.py --all                  # research all 100 (concurrent + resumable)
python research.py --slugs stripe,notion  # research a subset
python research.py --limit 5              # research the first 5 apps (quick dry run)
python research.py --verify               # blind re-search verification -> metrics.json
python research.py --metrics              # rebuild metrics.json (patterns + verify + handcheck)
python research.py --build-report         # copy results.json + metrics.json into report/data/
"""

from __future__ import annotations

import argparse
import json
import shutil

import config
import pipeline


def _print_record(rec: dict, info: dict | None = None) -> None:
    print(json.dumps(rec, indent=2, ensure_ascii=False))
    if info:
        print("\ninfo:", json.dumps(info, ensure_ascii=False))
    print(f"reasoning log: out/reasoning/{rec['slug']}.md")


def cmd_app(slug: str, model: str | None) -> None:
    rec, info = pipeline.research_app(pipeline.get_app(slug), model=model)
    _print_record(rec.model_dump(mode="json"), info)


def cmd_batch(slugs, limit, workers, model, resume, shard) -> None:
    if limit and not slugs:
        slugs = [a["slug"] for a in pipeline.load_apps()[:limit]]
    results = pipeline.run_batch(
        slugs=slugs, workers=workers, resume=resume, model=model, shard=shard
    )
    agg = pipeline.compute_aggregates(results)
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["patterns"] = agg
    metrics["n_results"] = len(results)
    config.save_json(config.METRICS_PATH, metrics)
    print(f"\nwrote {len(results)} records -> {config.RESULTS_PATH}")
    print(
        f"patterns -> {config.METRICS_PATH}: build_now={agg.get('build_now')} "
        f"partner_gated={agg.get('partner_gated')} access={agg.get('access_model')}"
    )


def cmd_recheck(slugs_csv, model) -> None:
    slugs = [s.strip() for s in slugs_csv.split(",") if s.strip()]
    existing = {r["slug"]: r for r in (config.load_json(config.RESULTS_PATH) or [])}
    providers = config.keyed_shard_providers()
    for i, s in enumerate(slugs):
        lead = providers[i % len(providers)] if len(providers) > 1 else None
        rec, _ = pipeline.research_app(pipeline.get_app(s), model=model, lead=lead)
        d = rec.model_dump(mode="json")
        existing[s] = d
        print(f"[recheck] {s}: {d['api_type']}/{d['access_model']['kind']}/"
              f"{d['recommended_next_action']} conf={d['confidence']}")
    order = {a["slug"]: i for i, a in enumerate(pipeline.load_apps())}
    merged = sorted(existing.values(), key=lambda r: order.get(r["slug"], 10_000))
    config.save_json(config.RESULTS_PATH, merged)
    print(f"merged {len(slugs)} rechecked -> {config.RESULTS_PATH} ({len(merged)} total)")


def cmd_verify(sample: int, model: str | None) -> None:
    import verify  # lazy import (module added in the verification task)

    verify.run_verification(sample_size=sample, model=model)


def cmd_metrics() -> None:
    import verify

    verify.rebuild_metrics()


def cmd_build_report() -> None:
    dst = config.REPORT_DIR / "data"
    dst.mkdir(parents=True, exist_ok=True)
    results = config.load_json(config.RESULTS_PATH, default=[]) or []
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    for src in (config.RESULTS_PATH, config.METRICS_PATH):
        if src.exists():
            shutil.copy(src, dst / src.name)
            print(f"copied {src.name} -> report/data/")
        else:
            print(f"WARN: {src} missing (run --all first)")
    # data.js sets globals so the static page works from file://, http.server, or Vercel.
    with open(config.REPORT_DIR / "data.js", "w", encoding="utf-8") as fh:
        fh.write("window.RESULTS = " + json.dumps(results, ensure_ascii=False) + ";\n")
        fh.write("window.METRICS = " + json.dumps(metrics, ensure_ascii=False) + ";\n")
    print(f"wrote {len(results)} records + metrics -> report/data.js")


def main() -> None:
    p = argparse.ArgumentParser(description="API Integration Readiness research agent")
    p.add_argument("--app", help="research a single app by slug")
    p.add_argument("--all", action="store_true", help="research all 100 apps")
    p.add_argument("--slugs", help="comma-separated slugs to research")
    p.add_argument("--limit", type=int, help="research only the first N apps (dry run)")
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--model", help="override OPENROUTER_MODEL")
    p.add_argument(
        "--no-resume", action="store_true", help="ignore cached results.json"
    )
    p.add_argument(
        "--no-shard", action="store_true",
        help="disable round-robin provider sharding (use the fallback chain)"
    )
    p.add_argument(
        "--verify", action="store_true", help="run blind re-search verification"
    )
    p.add_argument(
        "--sample",
        type=int,
        default=None,
        help="verification sample size (default: all records)",
    )
    p.add_argument("--metrics", action="store_true", help="rebuild metrics.json")
    p.add_argument(
        "--handcheck-template",
        nargs="?",
        type=int,
        const=18,
        default=None,
        metavar="N",
        help="generate a hand-check worksheet for N apps (default 18)",
    )
    p.add_argument(
        "--fold-handcheck",
        action="store_true",
        help="fold filled hand-check truth into metrics.json",
    )
    p.add_argument("--build-report", action="store_true", help="copy data into report/")
    p.add_argument("--recheck", help="comma-separated slugs to re-research and MERGE into results.json")
    p.add_argument("--accuracy-movement", action="store_true",
                   help="score first-pass vs post-verification accuracy against hand truth")
    args = p.parse_args()

    if args.app:
        cmd_app(args.app, args.model)
    elif args.recheck:
        cmd_recheck(args.recheck, args.model)
    elif args.all or args.slugs or args.limit:
        slugs = args.slugs.split(",") if args.slugs else None
        cmd_batch(slugs, args.limit, args.workers, args.model, not args.no_resume, not args.no_shard)
    elif args.verify:
        cmd_verify(args.sample, args.model)
    elif args.handcheck_template is not None:
        import handcheck

        handcheck.generate_template(args.handcheck_template)
    elif args.fold_handcheck:
        import handcheck

        handcheck.fold()
    elif args.accuracy_movement:
        import handcheck

        handcheck.accuracy_movement()
    elif args.metrics:
        cmd_metrics()
    elif args.build_report:
        cmd_build_report()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
