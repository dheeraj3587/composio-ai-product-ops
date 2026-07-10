"""Small persistent cost ledger with hard per-provider run caps."""
from __future__ import annotations

import datetime as dt
import os
import threading

import config

_lock = threading.Lock()

DEFAULT_BUDGETS = {
    "perplexity": 2.0,
    "google": 8.0,
}


def budget_for(provider: str) -> float:
    env_name = f"{provider.upper()}_RUN_BUDGET_USD"
    return float(os.getenv(env_name, str(DEFAULT_BUDGETS[provider])))


def _load() -> dict:
    return config.load_json(config.USAGE_PATH, default={}) or {
        "totals_usd": {},
        "events": [],
    }


def ensure_budget(provider: str, estimated_next_cost_usd: float) -> None:
    """Refuse a call whose conservative estimate would cross the run cap."""
    with _lock:
        ledger = _load()
        spent = float((ledger.get("totals_usd") or {}).get(provider, 0.0))
        budget = budget_for(provider)
        if spent + estimated_next_cost_usd > budget:
            raise RuntimeError(
                f"{provider} run budget would be exceeded: spent=${spent:.4f}, "
                f"next<=${estimated_next_cost_usd:.4f}, cap=${budget:.2f}"
            )


def record(provider: str, operation: str, estimated_cost_usd: float,
           metadata: dict | None = None) -> None:
    """Atomically append one usage event and update provider totals."""
    with _lock:
        ledger = _load()
        totals = ledger.setdefault("totals_usd", {})
        cost = round(float(estimated_cost_usd), 8)
        totals[provider] = round(float(totals.get(provider, 0.0)) + cost, 8)
        ledger.setdefault("events", []).append({
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "provider": provider,
            "operation": operation,
            "estimated_cost_usd": cost,
            "metadata": metadata or {},
        })
        ledger["budgets_usd"] = {
            name: budget_for(name) for name in DEFAULT_BUDGETS
        }
        config.save_json(config.USAGE_PATH, ledger)


def snapshot() -> dict:
    with _lock:
        return _load()
