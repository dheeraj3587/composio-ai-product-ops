"""Asynchronous Gemini Batch API path for quota-safe, homogeneous synthesis."""
from __future__ import annotations

import concurrent.futures as cf
import datetime as dt
import json

import composio_lookup
import config
import docs_research
import pipeline
import synthesis
import usage_tracker


TERMINAL_STATES = {
    "JOB_STATE_SUCCEEDED",
    "JOB_STATE_FAILED",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_EXPIRED",
}


def _batch_request(messages: list[dict]) -> dict:
    system = "\n\n".join(
        str(message.get("content", ""))
        for message in messages
        if message.get("role") == "system"
    )
    contents = []
    for message in messages:
        if message.get("role") == "system":
            continue
        role = "model" if message.get("role") == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": str(message.get("content", ""))}],
        })
    return {
        "contents": contents,
        "config": {
            "system_instruction": {"parts": [{"text": system}]},
            "temperature": 0,
            "max_output_tokens": 4096,
            "response_mime_type": "application/json",
            "response_schema": synthesis.SynthesisOutput,
            "thinking_config": {"thinking_level": config.GOOGLE_THINKING_LEVEL},
        },
    }


def _prepare_one(app: dict) -> dict:
    meta = {
        "app": app["app"],
        "slug": app["slug"],
        "category": app["category"],
        "hint_url": app.get("hint_url") or "",
    }
    signal = composio_lookup.lookup(meta["app"], meta["slug"])
    evidence = docs_research.gather_evidence(
        meta["app"],
        meta["slug"],
        hint_url=meta["hint_url"],
        category=meta["category"],
    )
    if not evidence.get("fetched_urls"):
        raise ValueError("no fetched documentation URL is available")
    return {
        "app_meta": meta,
        "evidence": evidence,
        "composio_signal": signal,
        "preseed": pipeline.load_preseed_map().get(meta["slug"]),
    }


def _first_party_tagged_sources(entry: dict) -> list[str]:
    app = entry["app_meta"]
    evidence = entry["evidence"]
    fetched = [
        *(evidence.get("fetched") or []),
        *((evidence.get("mcp") or {}).get("fetched") or []),
    ]
    sources = []
    seen = set()
    for item in fetched:
        url = item.get("url", "")
        tags = item.get("support_tags") or []
        if (
            not item.get("ok")
            or not tags
            or url in seen
            or not docs_research.is_first_party(
                url, app.get("hint_url", ""), app["slug"]
            )
        ):
            continue
        seen.add(url)
        sources.append(f"- {url} [supports: {', '.join(tags)}]")
    return sources


def _messages(entry: dict, failure: dict | None = None) -> list[dict]:
    messages = synthesis.build_messages(
        entry["evidence"], entry["composio_signal"], entry.get("preseed")
    )
    if not failure:
        return messages
    raw = failure.get("raw") or ""
    if raw:
        messages.append({"role": "assistant", "content": raw})
    official_sources = _first_party_tagged_sources(entry)
    source_hint = ""
    if official_sources:
        source_hint = (
            "\nFirst-party evidence candidates and their deterministic claim-family "
            "tags:\n" + "\n".join(official_sources)
            + "\nCite the first-party candidates that cover every required claim family."
        )
    messages.append({
        "role": "user",
        "content": (
            "The previous batch response failed deterministic validation: "
            f"{failure['error']}. Correct it using only the supplied evidence and return "
            f"the complete strict JSON object.{source_hint}"
        ),
    })
    return messages


def _estimate_batch_cost(requests: list[dict], model: str) -> float:
    input_price, output_price = config._google_token_prices(model)
    prompt_chars = sum(len(json.dumps(request, default=str)) for request in requests)
    prompt_tokens = prompt_chars / 4
    output_tokens = len(requests) * 4096
    return 0.5 * (
        prompt_tokens * input_price / 1_000_000
        + output_tokens * output_price / 1_000_000
    )


def _submit_job(state: dict, slugs: list[str], kind: str) -> None:
    entries = {entry["app_meta"]["slug"]: entry for entry in state["entries"]}
    failures = {item["slug"]: item for item in state.get("validation_failures", [])}
    requests = [
        _batch_request(_messages(entries[slug], failures.get(slug)))
        for slug in slugs
    ]
    usage_tracker.ensure_budget(
        "google", _estimate_batch_cost(requests, state["model"])
    )
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    job = config.get_client().batches.create(
        model=state["model"],
        src=requests,
        config={"display_name": f"composio-{kind}-{stamp}"},
    )
    state["active_job"] = {
        "name": job.name,
        "kind": kind,
        "slugs": slugs,
        "state": job.state.name,
    }
    state["status"] = f"{kind}_submitted"
    config.save_json(config.BATCH_STATE_PATH, state)
    print(f"submitted {kind} batch: {job.name} ({len(slugs)} requests)")


def _prepare_state(state: dict, workers: int) -> list[str]:
    state.setdefault("version", 1)
    state.setdefault("created_at", dt.datetime.now(dt.timezone.utc).isoformat())
    state.setdefault("entries", [])
    state.setdefault("preparation_failures", [])
    state["status"] = "preparing"
    config.save_json(config.BATCH_STATE_PATH, state)

    existing = {entry["app_meta"]["slug"] for entry in state["entries"]}
    apps = [app for app in pipeline.load_apps() if app["slug"] not in existing]
    order = {app["slug"]: index for index, app in enumerate(pipeline.load_apps())}
    failures = {
        item["slug"]: item for item in state.get("preparation_failures", [])
    }
    print(f"batch preparation: {len(existing)} cached, {len(apps)} to research")

    with cf.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_prepare_one, app): app for app in apps}
        for future in cf.as_completed(futures):
            app = futures[future]
            try:
                entry = future.result()
                state["entries"].append(entry)
                failures.pop(app["slug"], None)
                print(
                    f"[prepared] {app['slug']}: "
                    f"{len(entry['evidence'].get('fetched_urls', []))} fetched URLs"
                )
            except Exception as exc:
                failures[app["slug"]] = {
                    "slug": app["slug"],
                    "error": f"{type(exc).__name__}: {exc}",
                }
                print(f"[PREP FAIL] {app['slug']}: {type(exc).__name__}: {exc}")
            state["entries"].sort(
                key=lambda entry: order.get(entry["app_meta"]["slug"], 10_000)
            )
            state["preparation_failures"] = list(failures.values())
            config.save_json(config.BATCH_STATE_PATH, state)

    if failures:
        raise SystemExit(
            f"batch preparation incomplete: {len(state['entries'])}/100 ready, "
            f"{len(failures)} failed; rerun --batch-submit to retry only failed apps"
        )
    slugs = [entry["app_meta"]["slug"] for entry in state["entries"]]
    expected = len(pipeline.load_apps())
    if len(slugs) != expected:
        raise SystemExit(f"refusing incomplete batch submission: {len(slugs)}/{expected}")
    return slugs


def submit(model: str, workers: int = 2) -> None:
    """Prepare evidence with checkpoints, then submit one Pro synthesis batch."""
    config.ensure_dirs()
    state = config.load_json(config.BATCH_STATE_PATH, default={}) or {}
    if state.get("active_job"):
        raise SystemExit(
            "a batch job is already active; use --batch-status or --batch-collect"
        )
    if state and state.get("model") != model:
        raise SystemExit(
            f"existing batch state uses {state.get('model')}; archive it before using {model}"
        )
    state.setdefault("model", model)
    slugs = _prepare_state(state, workers)
    _submit_job(state, slugs, "initial")


def recover(job_name: str, model: str, workers: int = 2) -> None:
    """Rebuild a lost local evidence map and attach an existing remote job."""
    config.ensure_dirs()
    state = config.load_json(config.BATCH_STATE_PATH, default={}) or {}
    if state.get("active_job"):
        raise SystemExit("local batch state already has an active job")
    if state and state.get("model") not in (None, model):
        raise SystemExit(
            f"existing batch state uses {state.get('model')}; cannot recover {model}"
        )
    job = config.get_client().batches.get(name=job_name)
    if job.state.name in {"JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}:
        raise SystemExit(f"cannot recover terminal batch {job_name}: {job.state.name}")
    state.setdefault("model", model)
    slugs = _prepare_state(state, workers)
    state["active_job"] = {
        "name": job.name,
        "kind": "initial",
        "slugs": slugs,
        "state": job.state.name,
    }
    state["status"] = "recovered"
    config.save_json(config.BATCH_STATE_PATH, state)
    print(f"recovered {job.name}: {job.state.name} ({len(slugs)} requests)")


def retry_failures(workers: int = 2) -> None:
    """Refresh evidence and submit only rows that failed the repair batch."""
    state = config.load_json(config.BATCH_STATE_PATH, default={}) or {}
    if state.get("active_job"):
        raise SystemExit("a batch job is already active")
    failures = state.get("validation_failures", [])
    if not failures:
        raise SystemExit("there are no batch validation failures to retry")
    slugs = [item["slug"] for item in failures]
    entries = {entry["app_meta"]["slug"]: entry for entry in state["entries"]}
    print(f"refreshing evidence for {len(slugs)} failed rows: {', '.join(slugs)}")

    with cf.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(_prepare_one, pipeline.get_app(slug)): slug
            for slug in slugs
        }
        for future in cf.as_completed(futures):
            slug = futures[future]
            try:
                entry = future.result()
            except Exception as exc:
                raise SystemExit(
                    f"targeted evidence refresh failed for {slug}: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            entries[slug] = entry
            topics = entry["evidence"].get("supported_topics", [])
            print(
                f"[refreshed] {slug}: {len(entry['evidence'].get('fetched_urls', []))} "
                f"URLs, topics={topics}"
            )

    order = {app["slug"]: index for index, app in enumerate(pipeline.load_apps())}
    state["entries"] = sorted(
        entries.values(), key=lambda entry: order[entry["app_meta"]["slug"]]
    )
    config.save_json(config.BATCH_STATE_PATH, state)
    _submit_job(state, slugs, "targeted")


def _raw_from_record(record: dict) -> str:
    keys = [
        "one_liner",
        "auth_methods",
        "access_model",
        "api_type",
        "api_breadth",
        "existing_mcp",
        "buildability",
        "main_blocker",
        "recommended_next_action",
        "rate_limit_note",
        "evidence_urls",
        "confidence",
    ]
    parsed = {key: record[key] for key in keys}
    parsed["reasoning"] = "Prior generated record; revise it against stronger source-quality rules."
    return json.dumps(parsed, ensure_ascii=False)


def audit_sources() -> None:
    """Revalidate completed rows after source-quality rules are strengthened."""
    state = config.load_json(config.BATCH_STATE_PATH, default={}) or {}
    if state.get("active_job"):
        raise SystemExit("cannot audit sources while a batch job is active")
    entries = {entry["app_meta"]["slug"]: entry for entry in state.get("entries", [])}
    results = config.load_json(config.RESULTS_PATH, default=[]) or []
    result_slugs = {record["slug"] for record in results}
    valid = {}
    failures = [
        failure
        for failure in state.get("validation_failures", [])
        if failure["slug"] not in result_slugs
    ]
    for record in results:
        slug = record["slug"]
        entry = entries.get(slug)
        if not entry:
            failures.append({
                "slug": slug,
                "error": "missing stored evidence entry",
                "raw": _raw_from_record(record),
            })
            continue
        try:
            synthesis._validate_citations(record, entry["evidence"])
            synthesis._validate_source_quality(
                record, entry["evidence"], entry["app_meta"]
            )
            synthesis._validate_semantics(record)
            valid[slug] = record
        except ValueError as exc:
            failures.append({
                "slug": slug,
                "error": f"ValueError: {exc}",
                "raw": _raw_from_record(record),
            })
            print(f"[SOURCE INVALID] {slug}: {exc}")

    ordered = pipeline._ordered(valid)
    config.save_json(config.RESULTS_PATH, ordered)
    _refresh_metrics(ordered)
    state["validation_failures"] = failures
    state["completed_slugs"] = [record["slug"] for record in ordered]
    state["status"] = "incomplete" if failures else "complete"
    config.save_json(config.BATCH_STATE_PATH, state)
    print(f"source audit: {len(ordered)}/100 valid, {len(failures)} need rerun")


def _record_batch_usage(job, model: str) -> None:
    ledger = usage_tracker.snapshot()
    if any(
        event.get("metadata", {}).get("batch_job") == job.name
        for event in ledger.get("events", [])
    ):
        return
    prompt_tokens = answer_tokens = thought_tokens = 0
    for item in job.dest.inlined_responses or []:
        if not item.response:
            continue
        usage = item.response.usage_metadata
        prompt_tokens += int(getattr(usage, "prompt_token_count", 0) or 0)
        answer_tokens += int(getattr(usage, "candidates_token_count", 0) or 0)
        thought_tokens += int(getattr(usage, "thoughts_token_count", 0) or 0)
    input_price, output_price = config._google_token_prices(model)
    cost = 0.5 * (
        prompt_tokens * input_price / 1_000_000
        + (answer_tokens + thought_tokens) * output_price / 1_000_000
    )
    usage_tracker.record("google", "batch_generate_content", cost, {
        "batch_job": job.name,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "answer_tokens": answer_tokens,
        "thought_tokens": thought_tokens,
        "batch_discount": 0.5,
    })


def _refresh_metrics(results: list[dict]) -> None:
    metrics = config.load_json(config.METRICS_PATH, default={}) or {}
    metrics["patterns"] = pipeline.compute_aggregates(results)
    metrics["n_results"] = len(results)
    config.save_json(config.METRICS_PATH, metrics)


def status() -> str:
    state = config.load_json(config.BATCH_STATE_PATH, default={}) or {}
    active = state.get("active_job")
    if not active:
        current = state.get("status", "none")
        print(f"batch state: {current}")
        return current
    job = config.get_client().batches.get(name=active["name"])
    active["state"] = job.state.name
    state["status"] = job.state.name
    config.save_json(config.BATCH_STATE_PATH, state)
    print(
        f"{active['kind']} batch {active['name']}: {job.state.name} "
        f"({len(active['slugs'])} requests)"
    )
    return job.state.name


def collect() -> None:
    """Validate a completed job; submit one repair batch for invalid rows."""
    state = config.load_json(config.BATCH_STATE_PATH, default={}) or {}
    active = state.get("active_job")
    if not active:
        raise SystemExit("no active batch job; use --batch-submit first")
    job = config.get_client().batches.get(name=active["name"])
    job_state = job.state.name
    if job_state not in TERMINAL_STATES:
        print(f"batch not finished: {job_state}")
        return
    if job_state != "JOB_STATE_SUCCEEDED":
        raise SystemExit(f"batch ended as {job_state}: {job.error}")

    responses = list(job.dest.inlined_responses or [])
    slugs = active["slugs"]
    if len(responses) != len(slugs):
        raise SystemExit(
            f"batch response mismatch: {len(responses)} responses for {len(slugs)} slugs"
        )
    entries = {entry["app_meta"]["slug"]: entry for entry in state["entries"]}
    results = {
        record["slug"]: record
        for record in (config.load_json(config.RESULTS_PATH, default=[]) or [])
    }
    failures = []
    for slug, item in zip(slugs, responses, strict=True):
        entry = entries[slug]
        raw = item.response.text if item.response else ""
        try:
            if item.error:
                raise ValueError(f"provider batch error: {item.error}")
            parsed = config._extract_json_object(raw)
            record, reasoning = synthesis._record_from_parsed(
                entry["app_meta"],
                entry["evidence"],
                entry["composio_signal"],
                parsed,
            )
            payload = record.model_dump(mode="json")
            results[slug] = payload
            synthesis._write_reasoning(
                entry["app_meta"],
                reasoning,
                payload,
                entry["evidence"],
                entry.get("preseed"),
                model_used=state["model"],
            )
            docs_research.resolve_failure(slug, "pipeline")
            if not entry["evidence"].get("degraded"):
                docs_research.resolve_failure(slug, "evidence")
            print(
                f"[collected] {slug}: {payload['buildability']}/"
                f"{payload['recommended_next_action']} conf={payload['confidence']}"
            )
        except Exception as exc:
            failures.append({
                "slug": slug,
                "error": f"{type(exc).__name__}: {exc}",
                "raw": raw,
            })
            docs_research._log_failure(
                slug,
                f"batch validation error: {type(exc).__name__}: {exc}",
                phase="pipeline",
            )
            print(f"[INVALID] {slug}: {type(exc).__name__}: {exc}")
        ordered = pipeline._ordered(results)
        config.save_json(config.RESULTS_PATH, ordered)

    _record_batch_usage(job, state["model"])
    ordered = pipeline._ordered(results)
    _refresh_metrics(ordered)
    state["validation_failures"] = failures
    state["completed_slugs"] = [record["slug"] for record in ordered]
    state["active_job"] = None
    config.save_json(config.BATCH_STATE_PATH, state)

    if failures and active["kind"] == "initial":
        print(f"submitting one repair batch for {len(failures)} invalid rows")
        _submit_job(state, [item["slug"] for item in failures], "repair")
        return

    expected = len(pipeline.load_apps())
    if failures or len(ordered) != expected:
        state["status"] = "incomplete"
        config.save_json(config.BATCH_STATE_PATH, state)
        raise SystemExit(
            f"batch remains incomplete: {len(ordered)}/{expected} valid, "
            f"{len(failures)} final failures"
        )

    snapshot = config.OUT_DIR / "results_firstpass.json"
    if not snapshot.exists():
        config.save_json(snapshot, ordered)
    state["status"] = "complete"
    config.save_json(config.BATCH_STATE_PATH, state)
    print(f"batch complete: {len(ordered)}/{expected} valid rows")
