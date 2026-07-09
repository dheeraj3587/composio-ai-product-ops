#!/usr/bin/env python3
"""Optional: a real, READ-ONLY Composio tool call — proof of live tool-calling.

Executes a low-risk read action (default: list a few of your GitHub repos) through
the Composio SDK using your connected account. Read-only: it makes no writes.

Setup
  1. pip install composio
  2. Put COMPOSIO_API_KEY in .env
  3. Connect an account in Composio (dashboard, or `composio add github`)
  4. python demo/composio_demo.py            # GitHub repos
     python demo/composio_demo.py notion      # or a Notion read

This is a NICE-TO-HAVE, separate from the research pipeline. The pipeline itself is
the primary "real agent" proof:  python research.py --app <slug>
"""
from __future__ import annotations

import json
import os
import sys

# allow running from repo root or from demo/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402

# Read-only action-slug candidates (names vary by SDK version; we try in order).
READONLY = {
    "github": [
        "GITHUB_LIST_REPOSITORIES_FOR_THE_AUTHENTICATED_USER",
        "GITHUB_GET_THE_AUTHENTICATED_USER",
    ],
    "notion": ["NOTION_SEARCH", "NOTION_LIST_USERS"],
}


def _attempts(client, slug, user_id):
    """Yield callables trying a few known SDK signatures across composio versions."""
    yield lambda: client.tools.execute(slug, user_id=user_id, arguments={})
    yield lambda: client.tools.execute(slug=slug, user_id=user_id, arguments={})
    yield lambda: client.actions.execute(action=slug, params={}, entity_id=user_id)


def _truncate(obj, n=5):
    if isinstance(obj, list):
        return obj[:n]
    if isinstance(obj, dict):
        data = obj.get("data") or obj.get("response_data")
        if isinstance(data, list):
            return {f"data (first {n})": data[:n]}
    return obj


def main() -> None:
    toolkit = (sys.argv[1] if len(sys.argv) > 1
               else os.getenv("COMPOSIO_DEMO_TOOLKIT", "github")).lower()
    user_id = os.getenv("COMPOSIO_DEMO_USER_ID", "default")

    if not config.COMPOSIO_API_KEY:
        sys.exit("COMPOSIO_API_KEY not set — add it to .env")
    try:
        from composio import Composio
    except Exception as e:  # pragma: no cover
        sys.exit(f"composio SDK not installed (pip install composio): {e}")

    candidates = READONLY.get(toolkit)
    if not candidates:
        sys.exit(f"no read-only demo actions configured for toolkit {toolkit!r}")

    client = Composio(api_key=config.COMPOSIO_API_KEY)
    print(f"Composio read-only demo · toolkit={toolkit} · user_id={user_id}")

    last_err = None
    for slug in candidates:
        for attempt in _attempts(client, slug, user_id):
            try:
                result = attempt()
                print(f"\n[ok] executed {slug}:")
                print(json.dumps(_truncate(result), indent=2, default=str)[:2000])
                return
            except Exception as e:  # try next signature/action
                last_err = e

    print(f"\nCould not execute a demo action. Last error: {last_err}")
    print("Tips: connect the toolkit account in Composio, and confirm the action slug "
          "matches your installed SDK version.")


if __name__ == "__main__":
    main()
