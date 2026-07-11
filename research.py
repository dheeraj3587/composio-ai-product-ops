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
import datetime as dt
import importlib
import json
import shutil
import sys
import time as _t

import config
import docs_research
import pipeline


def _print_record(rec: dict, info: dict | None = None) -> None:
    print(json.dumps(rec, indent=2, ensure_ascii=False))
    if info:
        print("\ninfo:", json.dumps(info, ensure_ascii=False))
    print(f"reasoning log: out/reasoning/{rec['slug']}.md")


def cmd_app(slug: str, model: str | None) -> None:
    rec, info = pipeline.research_app(pipeline.get_app(slug), model=model)
    _print_record(rec.model_dump(mode="json"), info)


def _preflight_paid_runtime(workers: int) -> None:
    """Fail before archiving when this interpreter cannot run the paid pipeline."""
    errors = []
    if not config.PERPLEXITY_API_KEY:
        errors.append("PERPLEXITY_API_KEY is not set")
    if not config.GOOGLE_API_KEY:
        errors.append("GOOGLE_GENAI_API_KEY/GOOGLE_API_KEY is not set")
    for module, package in (("perplexity", "perplexityai"), ("google.genai", "google-genai")):
        try:
            importlib.import_module(module)
        except ImportError:
            errors.append(f"{package} is not installed in {sys.executable}")
    if workers < 1 or workers > config.GOOGLE_MAX_WORKERS:
        errors.append(
            f"--workers must be 1..{config.GOOGLE_MAX_WORKERS}; the configured preview "
            "model was unstable above that concurrency"
        )
    if errors:
        raise SystemExit("paid-run preflight failed:\n- " + "\n- ".join(errors))


def _archive_current_run() -> None:
    """Archive generated state while preserving report/ and human-authored truth."""
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    archive = config.OUT_DIR / "archive" / stamp
    archive.mkdir(parents=True, exist_ok=False)
    generated_files = [
        config.RESULTS_PATH,
        config.METRICS_PATH,
        config.OUT_DIR / "results_firstpass.json",
        config.OUT_DIR / "browser_verification.json",
        config.FAILURES_PATH,
        config.FAILURE_STATE_PATH,
        config.USAGE_PATH,
        config.BATCH_STATE_PATH,
    ]
    for path in generated_files:
        if path.exists():
            shutil.copy2(path, archive / path.name)
            path.unlink()
    if config.REASONING_DIR.exists():
        shutil.copytree(config.REASONING_DIR, archive / "reasoning")
        shutil.rmtree(config.REASONING_DIR)
    if config.HANDCHECK_PATH.exists():
        shutil.copy2(config.HANDCHECK_PATH, archive / "handcheck.json")
    if config.BROWSER_EVIDENCE_PATH.exists():
        shutil.copy2(config.BROWSER_EVIDENCE_PATH, archive / "browser_evidence.json")
    config.ensure_dirs()
    print(f"archived prior run -> {archive} (published report files were not changed)")


def cmd_batch(slugs, limit, workers, model, resume, shard, fresh_run=False) -> None:
    _preflight_paid_runtime(workers)
    if fresh_run:
        _archive_current_run()
        resume = False
    if limit and not slugs:
        slugs = [a["slug"] for a in pipeline.load_apps()[:limit]]
    try:
        results = pipeline.run_batch(
            slugs=slugs, workers=workers, resume=resume, model=model, shard=shard
        )
    except (config.ProviderQuotaExhausted, config.ProviderCapacityUnavailable) as exc:
        raise SystemExit(
            f"batch paused safely: {exc}\n"
            "completed rows are checkpointed; rerun the same command without --fresh-run"
        ) from exc
    agg = pipeline.compute_aggregates(results)
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["patterns"] = agg
    metrics["n_results"] = len(results)
    config.save_json(config.METRICS_PATH, metrics)
    if fresh_run:
        expected = len(pipeline.load_apps())
        if len(results) == expected:
            config.save_json(config.OUT_DIR / "results_firstpass.json", results)
            print(f"captured immutable first-pass snapshot ({len(results)} rows)")
        else:
            print(
                f"fresh run incomplete ({len(results)}/{expected}); first-pass snapshot not written. "
                "Resume the run, then use --snapshot-first-pass."
            )
    print(f"\nwrote {len(results)} records -> {config.RESULTS_PATH}")
    print(
        f"patterns -> {config.METRICS_PATH}: build_now={agg.get('build_now')} "
        f"partner_gated={agg.get('partner_gated')} access={agg.get('access_model')}"
    )


def cmd_batch_submit(model: str | None, workers: int, fresh_run: bool) -> None:
    import batch_pipeline

    _preflight_paid_runtime(workers)
    if fresh_run:
        _archive_current_run()
    batch_pipeline.submit(model or config.PRIMARY_MODEL, workers=workers)


def cmd_batch_status() -> None:
    import batch_pipeline

    batch_pipeline.status()


def cmd_batch_recover(job_name: str, model: str | None, workers: int) -> None:
    import batch_pipeline

    _preflight_paid_runtime(workers)
    batch_pipeline.recover(
        job_name, model or config.PRIMARY_MODEL, workers=workers
    )


def cmd_batch_collect() -> None:
    import batch_pipeline

    batch_pipeline.collect()


def cmd_batch_retry_failures(workers: int) -> None:
    import batch_pipeline

    _preflight_paid_runtime(workers)
    batch_pipeline.retry_failures(workers=workers)


def cmd_batch_audit_sources() -> None:
    import batch_pipeline

    batch_pipeline.audit_sources()


def cmd_recheck(slugs_csv, model) -> None:
    slugs = [s.strip() for s in slugs_csv.split(",") if s.strip()]
    existing = {r["slug"]: r for r in (config.load_json(config.RESULTS_PATH) or [])}
    order = {a["slug"]: i for i, a in enumerate(pipeline.load_apps())}
    done = 0
    for s in slugs:
        try:
            rec, info = pipeline.research_app(pipeline.get_app(s), model=model, lead=None)
        except Exception as e:  # rate limit / transient -> keep existing record, continue
            print(f"[recheck] {s}: FAILED ({type(e).__name__}) — kept existing record")
            continue
        d = rec.model_dump(mode="json")
        existing[s] = d
        docs_research.resolve_failure(s, "pipeline")
        if not info["degraded"]:
            docs_research.resolve_failure(s, "evidence")
        done += 1
        # incremental save so a mid-run failure never discards completed rechecks
        config.save_json(config.RESULTS_PATH,
                         sorted(existing.values(), key=lambda r: order.get(r["slug"], 10_000)))
        print(f"[recheck] {s}: {d['api_type']}/{d['access_model']['kind']}/"
              f"{d['recommended_next_action']} conf={d['confidence']}  (saved)")
        _t.sleep(2)  # pace requests to avoid provider rate limits
    print(f"merged {done}/{len(slugs)} rechecked -> {config.RESULTS_PATH}")


def cmd_verify(sample: int, model: str | None) -> None:
    import verify  # lazy import (module added in the verification task)

    verify.run_verification(sample_size=sample, model=model)


def cmd_metrics() -> None:
    import verify

    verify.rebuild_metrics()


def cmd_apply_handcheck() -> None:
    import handcheck

    handcheck.apply_corrections()


def cmd_build_report() -> None:
    dst = config.REPORT_DIR / "data"
    dst.mkdir(parents=True, exist_ok=True)
    results = config.load_json(config.RESULTS_PATH, default=[]) or []
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    reasoning = {}
    for record in results:
        slug = record.get("slug")
        path = config.REASONING_DIR / f"{slug}.md"
        if slug and path.exists():
            reasoning[slug] = path.read_text(encoding="utf-8")
    for src in (config.RESULTS_PATH, config.METRICS_PATH):
        if src.exists():
            shutil.copy(src, dst / src.name)
            print(f"copied {src.name} -> report/data/")
        else:
            print(f"WARN: {src} missing (run --all first)")
    config.save_json(dst / "reasoning.json", reasoning)
    # data.js sets globals so the static page works from file://, http.server, or Vercel.
    with open(config.REPORT_DIR / "data.js", "w", encoding="utf-8") as fh:
        fh.write("window.RESULTS = " + json.dumps(results, ensure_ascii=False) + ";\n")
        fh.write("window.METRICS = " + json.dumps(metrics, ensure_ascii=False) + ";\n")
        fh.write("window.REASONING = " + json.dumps(reasoning, ensure_ascii=False) + ";\n")
    print(
        f"wrote {len(results)} records + metrics + {len(reasoning)} reasoning traces "
        "-> report/data.js"
    )


def cmd_snapshot_first_pass() -> None:
    results = config.load_json(config.RESULTS_PATH) or []
    expected = len(pipeline.load_apps())
    if len(results) != expected:
        raise SystemExit(f"refusing snapshot: results has {len(results)}/{expected} apps")
    destination = config.OUT_DIR / "results_firstpass.json"
    if destination.exists():
        raise SystemExit("results_firstpass.json already exists; refusing to overwrite it")
    config.save_json(destination, results)
    print(f"captured immutable first-pass snapshot -> {destination}")


def main() -> None:
    p = argparse.ArgumentParser(description="API Integration Readiness research agent")
    p.add_argument("--app", help="research a single app by slug")
    p.add_argument("--all", action="store_true", help="research all 100 apps")
    p.add_argument("--slugs", help="comma-separated slugs to research")
    p.add_argument("--limit", type=int, help="research only the first N apps (dry run)")
    p.add_argument("--workers", type=int, default=config.GOOGLE_MAX_WORKERS)
    p.add_argument("--model", help="override the native Google Gemini model")
    p.add_argument(
        "--no-resume", action="store_true", help="ignore cached results.json"
    )
    p.add_argument(
        "--fresh-run", action="store_true",
        help="archive generated state, research all apps from scratch, and preserve report/"
    )
    p.add_argument(
        "--batch-submit",
        action="store_true",
        help="prepare all evidence and submit asynchronous Gemini batch synthesis",
    )
    p.add_argument(
        "--batch-status", action="store_true", help="show current Gemini batch state"
    )
    p.add_argument(
        "--batch-recover",
        metavar="JOB_NAME",
        help="rebuild local evidence state for an existing Gemini batch job",
    )
    p.add_argument(
        "--batch-collect",
        action="store_true",
        help="collect and validate a completed Gemini batch",
    )
    p.add_argument(
        "--batch-retry-failures",
        action="store_true",
        help="refresh evidence and resubmit only final batch validation failures",
    )
    p.add_argument(
        "--batch-audit-sources",
        action="store_true",
        help="revalidate completed rows against app-identity and official-source rules",
    )
    p.add_argument(
        "--snapshot-first-pass", action="store_true",
        help="capture complete results as results_firstpass.json (refuses overwrite)"
    )
    p.add_argument(
        "--no-shard", action="store_true",
        help="compatibility flag; provider sharding is disabled"
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
    p.add_argument(
        "--apply-handcheck",
        action="store_true",
        help="apply filled current-rubric truth after recording the hand-check score",
    )
    p.add_argument("--build-report", action="store_true", help="copy data into report/")
    p.add_argument("--recheck", help="comma-separated slugs to re-research and MERGE into results.json")
    p.add_argument("--accuracy-movement", action="store_true",
                   help="score first-pass vs post-verification accuracy against hand truth")
    args = p.parse_args()

    if args.fresh_run and not (args.all or args.batch_submit):
        p.error("--fresh-run must be used with --all or --batch-submit")
    if args.fresh_run and len(config.configured_model_chain(args.model)) != 1:
        p.error(
            "--fresh-run requires the single native Google model policy."
        )

    if args.batch_submit:
        cmd_batch_submit(args.model, args.workers, args.fresh_run)
    elif args.batch_recover:
        cmd_batch_recover(args.batch_recover, args.model, args.workers)
    elif args.batch_status:
        cmd_batch_status()
    elif args.batch_collect:
        cmd_batch_collect()
    elif args.batch_retry_failures:
        cmd_batch_retry_failures(args.workers)
    elif args.batch_audit_sources:
        cmd_batch_audit_sources()
    elif args.app:
        cmd_app(args.app, args.model)
    elif args.recheck:
        cmd_recheck(args.recheck, args.model)
    elif args.all or args.slugs or args.limit:
        slugs = args.slugs.split(",") if args.slugs else None
        cmd_batch(
            slugs, args.limit, args.workers, args.model,
            not args.no_resume, not args.no_shard, fresh_run=args.fresh_run,
        )
    elif args.verify:
        cmd_verify(args.sample, args.model)
    elif args.handcheck_template is not None:
        import handcheck

        handcheck.generate_template(args.handcheck_template)
    elif args.fold_handcheck:
        import handcheck

        handcheck.fold()
    elif args.apply_handcheck:
        cmd_apply_handcheck()
    elif args.accuracy_movement:
        import handcheck

        handcheck.accuracy_movement()
    elif args.metrics:
        cmd_metrics()
    elif args.build_report:
        cmd_build_report()
    elif args.snapshot_first_pass:
        cmd_snapshot_first_pass()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
