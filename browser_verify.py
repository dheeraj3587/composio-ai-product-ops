#!/usr/bin/env python3
"""Verification LOOP 2 — Browser Use Cloud (batched).

An INDEPENDENT verification channel: a cloud browser agent NAVIGATES the live
developer docs for a set of apps and re-derives whether a public API exists, its
type, the auth method(s), and Self-Serve vs Gated access. Independent of the
pipeline's static search+fetch pass (catches JS-rendered docs / marketing-homepage
misses like copper/plain) and uses the cloud's OWN browser model — so it's
independent of the pipeline's ZenMux/OpenRouter/Gemini LLMs too.

Quota-savvy: one browser agent can research many sites per task, so we batch
`--batch-size` apps into a single cloud instance.

Runs in the isolated .venv-browser. Reads out/results.json, writes
out/browser_verification.json.

Usage (from repo root):
  .venv-browser/bin/python browser_verify.py --sample 12 --batch-size 6
  .venv-browser/bin/python browser_verify.py --slugs copper,plain,dealcloud --batch-size 15
  .venv-browser/bin/python browser_verify.py --slugs copper,plain --recover-task-id TASK_ID
Needs BROWSER_USE_API_KEY in .env.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel

from browser_use_sdk import BrowserUse

import normalize

load_dotenv()
ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "out" / "results.json"
OUT = ROOT / "out" / "browser_verification.json"
DEFAULT_LLM = "browser-use-2.0"


class AppVerdict(BaseModel):
    slug: str
    app: str
    has_public_api: bool
    api_type: Literal["REST", "GraphQL", "SDK", "SOAP", "MCP-only", "None"]
    auth_methods: list[str]
    access_model: Literal["Self-Serve", "Gated"]
    evidence_url: str
    notes: str


class BatchVerdict(BaseModel):
    verdicts: list[AppVerdict]


def pick_sample(rows: list[dict], n: int) -> list[dict]:
    """Bias to highest-value apps: low-confidence first, then gated, then controls."""
    low = sorted([r for r in rows if r["confidence"] < 0.6], key=lambda r: r["confidence"])
    gated = [r for r in rows if r["access_model"]["kind"] == "Gated"]
    control = sorted([r for r in rows if r["confidence"] >= 0.9], key=lambda r: -r["confidence"])
    seen, out = set(), []
    for bucket in (low, gated, control):
        for r in bucket:
            if r["slug"] not in seen:
                seen.add(r["slug"])
                out.append(r)
            if len(out) >= n:
                return out[:n]
    return out[:n]


def build_batch_task(chunk: list[dict]) -> str:
    lines = [f"- slug={r['slug']} | {r['app']} | start: {r.get('primary_docs_url') or r.get('hint_url') or '(search)'}"
             for r in chunk]
    return (
        "You are verifying developer-API facts. For EACH app below, find its official "
        "API documentation (navigate past the marketing homepage to the real docs), then "
        "determine: has_public_api (bool), api_type (REST/GraphQL/SDK/SOAP/MCP-only/None), "
        f"auth_methods (use only {normalize.CANONICAL}), access_model ('Self-Serve' only if a "
        "new developer can obtain credentials usable in PRODUCTION without approval, partnership, "
        "business verification, or already being a paying customer; a sandbox alone is not "
        "Self-Serve; otherwise use 'Gated'), the exact "
        "evidence_url you used, and a short note.\n\nApps:\n" + "\n".join(lines) +
        "\n\nOAuth2 is a grant scheme: do not also add Bearer Token merely because an OAuth "
        "access token uses a Bearer header. Return one verdict per app, reusing the exact slug."
    )


def _comparison(first_pass: dict, browser: dict) -> dict:
    matches = {
        "api_type": first_pass.get("api_type") == browser.get("api_type"),
        "auth_methods": normalize.auth_sets_equal(
            first_pass.get("auth_methods", []), browser.get("auth_methods", []), strict=True
        ),
        "access_model": first_pass.get("access_model") == browser.get("access_model"),
    }
    return {
        "matches": matches,
        "disagreed_fields": [field for field, matched in matches.items() if not matched],
    }


def _to_dict(out) -> dict:
    if out is None:
        return {}
    if isinstance(out, dict):
        return out
    if isinstance(out, str):
        try:
            return json.loads(out)
        except Exception:
            return {"raw": out[:400]}
    # SDK 3.x returns a TaskView whose `output` contains the structured JSON.
    # Unwrap that before model_dump(), which would otherwise hide verdicts one level down.
    for attr in ("parsed", "output", "structured_output", "result", "data"):
        v = getattr(out, attr, None)
        if v is not None:
            return _to_dict(v)
    if hasattr(out, "model_dump"):
        return out.model_dump()
    return {"raw": str(out)[:400]}


def main() -> None:
    ap = argparse.ArgumentParser(description="Browser Use Cloud verification (batched)")
    ap.add_argument("--sample", type=int, default=12, help="how many apps total")
    ap.add_argument("--slugs", help="comma-separated slugs to force (overrides --sample)")
    ap.add_argument("--batch-size", type=int, default=6, help="apps per cloud task/instance")
    ap.add_argument("--llm", default=DEFAULT_LLM, help=f"cloud model (default {DEFAULT_LLM})")
    ap.add_argument("--max-steps", type=int, default=60)
    ap.add_argument(
        "--recover-task-id",
        help="parse an existing completed Browser Use task instead of spending a new task credit",
    )
    args = ap.parse_args()

    key = os.getenv("BROWSER_USE_API_KEY")
    if not key:
        raise SystemExit("BROWSER_USE_API_KEY not set — add it to .env")
    if not RESULTS.exists():
        raise SystemExit("out/results.json missing — run `python research.py --all` first")

    rows = json.loads(RESULTS.read_text())
    by = {r["slug"]: r for r in rows}
    sample = ([by[s] for s in args.slugs.split(",") if s in by] if args.slugs
              else pick_sample(rows, args.sample))

    chunks = [sample[i:i + args.batch_size] for i in range(0, len(sample), args.batch_size)]
    print(f"Browser Use Cloud: {len(sample)} apps in {len(chunks)} task(s) "
          f"(batch-size={args.batch_size}, llm={args.llm})")

    client = BrowserUse(api_key=key)
    fp = {r["slug"]: r for r in sample}
    # preserve prior verdicts so browser coverage ACCUMULATES across runs (keyed by slug)
    prior = {}
    if OUT.exists():
        try:
            prior = {x["slug"]: x for x in json.loads(OUT.read_text()) if x.get("slug")}
        except Exception:
            prior = {}
    results: list[dict] = []
    for ci, chunk in enumerate(chunks, 1):
        slugs = [r["slug"] for r in chunk]
        print(f"[task {ci}/{len(chunks)}] {slugs} ...")
        try:
            if args.recover_task_id:
                if len(chunks) != 1:
                    raise ValueError("--recover-task-id requires one batch")
                print(f"   recovering completed task {args.recover_task_id}")
                out = client.tasks.get(args.recover_task_id)
            else:
                out = client.run(task=build_batch_task(chunk), schema=BatchVerdict,
                                 llm=args.llm, max_steps=args.max_steps)
            data = _to_dict(out)
            verdicts = data.get("verdicts", []) if isinstance(data, dict) else []
            expected = {r["slug"] for r in chunk}
            seen, invalid = set(), {}
            for raw_verdict in verdicts:
                raw_slug = raw_verdict.get("slug", "") if isinstance(raw_verdict, dict) else ""
                try:
                    verdict = AppVerdict.model_validate(raw_verdict).model_dump()
                    verdict["auth_methods"] = normalize.normalize_auth_list(
                        verdict.get("auth_methods", []), strict=True
                    )
                    slug = verdict["slug"]
                    if slug not in expected:
                        raise ValueError(f"unexpected slug {slug!r}")
                    if slug in seen:
                        raise ValueError(f"duplicate verdict for {slug}")
                    if not verdict["auth_methods"]:
                        raise ValueError(f"{slug}: empty auth_methods")
                    if not verdict["evidence_url"].startswith(("http://", "https://")):
                        raise ValueError(f"{slug}: evidence_url must be absolute HTTP(S)")
                    if not verdict["notes"].strip():
                        raise ValueError(f"{slug}: notes must explain the decision")
                    if verdict["api_type"] == "None":
                        if verdict["has_public_api"]:
                            raise ValueError(f"{slug}: api_type=None contradicts has_public_api=true")
                        if verdict["auth_methods"] != ["None / Not Applicable"]:
                            raise ValueError(f"{slug}: api_type=None requires not-applicable auth")
                    elif "None / Not Applicable" in verdict["auth_methods"]:
                        raise ValueError(f"{slug}: usable surface cannot have not-applicable auth")

                    r = fp[slug]
                    first_pass = {
                        "api_type": r.get("api_type"),
                        "auth_methods": r.get("auth_methods"),
                        "access_model": (r.get("access_model") or {}).get("kind"),
                        "recommended_next_action": r.get("recommended_next_action"),
                        "confidence": r.get("confidence"),
                    }
                    comparison = _comparison(first_pass, verdict)
                    results.append({
                        "slug": slug, "app": verdict.get("app") or r.get("app", ""),
                        "first_pass": first_pass,
                        "browser": verdict,
                        "comparison": comparison,
                        "adjudication": {
                            "status": "Pending" if comparison["disagreed_fields"] else "Not Needed",
                            "notes": "",
                            "evidence_urls": [],
                            "applied_to_results": False,
                        },
                        "browser_model": args.llm,
                        "generated": dt.date.today().isoformat(),
                    })
                    seen.add(slug)
                    print(f"   {slug}: api={verdict.get('api_type')} "
                          f"access={verdict.get('access_model')} auth={verdict.get('auth_methods')} "
                          f"disagrees={comparison['disagreed_fields']}")
                except Exception as verdict_error:
                    invalid[raw_slug] = str(verdict_error)[:200]
                    print(f"   invalid verdict {raw_slug or '(unknown)'}: {verdict_error}")
            for r in chunk:
                if r["slug"] not in seen:
                    error = invalid.get(r["slug"], "No valid verdict returned for this app")
                    results.append({
                        "slug": r["slug"], "app": r["app"],
                        "first_pass": {
                            "api_type": r["api_type"],
                            "auth_methods": r.get("auth_methods", []),
                            "access_model": r["access_model"]["kind"],
                        },
                        "browser": {"error": error},
                        "generated": dt.date.today().isoformat(),
                    })
        except Exception as e:
            print(f"   TASK ERROR: {str(e)[:200]}")
            for r in chunk:
                results.append({"slug": r["slug"], "app": r["app"],
                                "first_pass": {"api_type": r["api_type"],
                                               "auth_methods": r.get("auth_methods", []),
                                               "access_model": r["access_model"]["kind"]},
                                "browser": {"error": str(e)[:200]},
                                "generated": dt.date.today().isoformat()})
        OUT.parent.mkdir(parents=True, exist_ok=True)
        # merge prior + this run's verdicts (new overrides prior for the same slug)
        merged = {**prior, **{x["slug"]: x for x in results if x.get("slug")}}
        OUT.write_text(json.dumps(list(merged.values()), indent=2, ensure_ascii=False))

    total_now = len({**prior, **{x["slug"]: x for x in results if x.get("slug")}})
    print(f"\nwrote {len(results)} new verdicts; {total_now} total in {OUT}")


if __name__ == "__main__":
    main()
