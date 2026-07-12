#!/usr/bin/env python3
"""Compatibility entry point for the read-only Composio Session agent.

The canonical interface is ``python research.py --composio-agent SLUG``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import composio_agent  # noqa: E402


def main() -> None:
    slug = sys.argv[1] if len(sys.argv) > 1 else "otter-ai"
    result = composio_agent.run(slug)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
