#!/usr/bin/env python3
"""Verification LOOP 2 — Browser Use Cloud (batched).

An INDEPENDENT verification channel: a cloud browser agent NAVIGATES the live
developer docs for a set of apps and re-derives whether a public API exists, its
type, the auth method(s), and Self-Serve vs Gated access. Independent of the
pipeline's static search+fetch pass (catches JS-rendered docs / marketing-homepage
misses like copper/plain) and uses the cloud's OWN model (default Opus) — so it's
independent of the pipeline's ZenMux/OpenRouter/Gemini LLMs too.

Quota-savvy: one browser agent can research MANY sites per task, so we batch
`--batch-size` apps into a single cloud instance (Browser Use Cloud free = 10/mo).

Runs in the isolated .venv-browser. Reads out/results.json, writes
out/browser_verification.json.

Usage (from repo root):
  .venv-browser/bin/python browser_verify.py --sample 12 --batch-size 6
  .venv-browser/bin/python browser_verify.py --slugs copper,plain,dealcloud --batch-size 15
Needs BROWSER_USE_API_KEY in .env.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel

from browser_use_sdk import BrowserUse

load_dotenv()
ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "out" / "results.json"
OUT = ROOT / "out" / "browser_verification.json"
DEFAULT_LLM = "claude-opus-4-7"  # newest Opus-tier model Browser Use Cloud currently accepts
                                  # (verified live against the tasks API; gpt-5.5 / opus-4.8
                                  # are rejected with a 422 as of this writing — not yet onboarded)


class AppVerdict(BaseModel):
    slug: str
    app: str
    has_public_api: bool
    api_type: str  # REST | GraphQL | SDK | SOAP | MCP-only | None
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
        "determine: has_public_api (bool), api_type (REST/GraphQL/SDK/SOAP/None), "
        "auth_methods (list, e.g. OAuth2/API key/token), access_model ('Self-Serve' if a "
        "developer can self-issue free credentials, else 'Gated' if it needs approval / a "
        "paid plan / business verification / being an existing customer), the exact "
        "evidence_url you used, and a short note.\n\nApps:\n" + "\n".join(lines) +
        "\n\nReturn one verdict per app, reusing the exact slug given."
    )


def _to_dict(out) -> dict:
    if out is None:
        return {}
    if hasattr(out, "model_dump"):
        return out.model_dump()
    if isinstance(out, dict):
        return out
    if isinstance(out, str):
        try:
            return json.loads(out)
        except Exception:
            return {"raw": out[:400]}
    for attr in ("parsed", "output", "structured_output", "result", "data"):
        v = getattr(out, attr, None)
        if v is not None:
            return _to_dict(v)
    return {"raw": str(out)[:400]}


def main() -> None:
    ap = argparse.ArgumentParser(description="Browser Use Cloud verification (batched)")
    ap.add_argument("--sample", type=int, default=12, help="how many apps total")
    ap.add_argument("--slugs", help="comma-separated slugs to force (overrides --sample)")
    ap.add_argument("--batch-size", type=int, default=6, help="apps per cloud task/instance")
    ap.add_argument("--llm", default=DEFAULT_LLM, help="cloud model (default Opus)")
    ap.add_argument("--max-steps", type=int, default=60)
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
            out = client.run(task=build_batch_task(chunk), schema=BatchVerdict,
                             llm=args.llm, max_steps=args.max_steps)
            data = _to_dict(out)
            verdicts = data.get("verdicts", []) if isinstance(data, dict) else []
            for v in verdicts:
                slug = v.get("slug", "")
                r = fp.get(slug, {})
                results.append({
                    "slug": slug, "app": v.get("app") or r.get("app", ""),
                    "first_pass": {"api_type": r.get("api_type"),
                                   "auth_methods": r.get("auth_methods"),
                                   "access_model": (r.get("access_model") or {}).get("kind"),
                                   "recommended_next_action": r.get("recommended_next_action"),
                                   "confidence": r.get("confidence")},
                    "browser": v,
                })
                print(f"   {slug}: api={v.get('api_type')} access={v.get('access_model')} "
                      f"auth={v.get('auth_methods')}")
        except Exception as e:
            print(f"   TASK ERROR: {str(e)[:200]}")
            for r in chunk:
                results.append({"slug": r["slug"], "app": r["app"],
                                "first_pass": {"api_type": r["api_type"],
                                               "access_model": r["access_model"]["kind"]},
                                "browser": {"error": str(e)[:200]}})
        OUT.parent.mkdir(parents=True, exist_ok=True)
        # merge prior + this run's verdicts (new overrides prior for the same slug)
        merged = {**prior, **{x["slug"]: x for x in results if x.get("slug")}}
        OUT.write_text(json.dumps(list(merged.values()), indent=2, ensure_ascii=False))

    total_now = len({**prior, **{x["slug"]: x for x in results if x.get("slug")}})
    print(f"\nwrote {len(results)} new verdicts; {total_now} total in {OUT}")


if __name__ == "__main__":
    main()
