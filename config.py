"""Central configuration: env loading, filesystem paths, and the LLM layer.

LLM = multi-provider, OpenAI-compatible, ORDERED FALLBACK CHAIN. Default:
  1) Claude Opus 4.7 on AgentRouter                 [primary]
  2) Claude Fable 5 (anthropic/claude-fable-5-free) on ZenMux   [fallback]
  3) Tencent Hy3     (tencent/hy3:free)             on OpenRouter [last resort]
llm_json() tries each tier in order until one succeeds. Kept small and explicit
so every line is interview-explainable.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "out"
REASONING_DIR = OUT_DIR / "reasoning"
CACHE_DIR = OUT_DIR / "cache"
REPORT_DIR = ROOT / "report"
HANDCHECK_DIR = ROOT / "handcheck"

APPS_PATH = DATA_DIR / "apps.json"
PRESEED_PATH = DATA_DIR / "preseed.json"
RESULTS_PATH = OUT_DIR / "results.json"
METRICS_PATH = OUT_DIR / "metrics.json"
FAILURES_PATH = OUT_DIR / "failures.log"
HANDCHECK_PATH = HANDCHECK_DIR / "handcheck.json"


def ensure_dirs() -> None:
    for d in (OUT_DIR, REASONING_DIR, CACHE_DIR, HANDCHECK_DIR):
        d.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Small JSON helpers (used across modules)
# --------------------------------------------------------------------------- #
def load_json(path: Path, default: Any = None) -> Any:
    if not Path(path).exists():
        return default
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path: Path, data: Any) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- #
# LLM — multi-provider, OpenAI-compatible, ordered fallback chain
# --------------------------------------------------------------------------- #
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY", "")

_APP_URL = os.getenv("APP_PUBLIC_URL", "http://localhost")
_APP_TITLE = os.getenv("APP_TITLE", "API Integration Readiness Agent")
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "75"))

# Provider registry (OpenAI-compatible gateways).
PROVIDERS = {
    "agentrouter": {
        "base_url": os.getenv("AGENTROUTER_BASE_URL", "https://agentrouter.org/v1"),
        # Reuse Claude Code's AgentRouter key if the explicit OpenAI-compatible
        # key env is not set. Same secret, different endpoint shape.
        "api_key": os.getenv("AGENTROUTER_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN", ""),
    },
    "zenmux": {
        "base_url": os.getenv("ZENMUX_BASE_URL", "https://zenmux.ai/api/v1"),
        "api_key": os.getenv("ZENMUX_API_KEY", ""),
    },
    "openrouter": {
        "base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        "api_key": os.getenv("OPENROUTER_API_KEY", ""),
    },
    "google": {
        "base_url": os.getenv("GOOGLE_BASE_URL",
                              "https://generativelanguage.googleapis.com/v1beta/openai/"),
        "api_key": os.getenv("GOOGLE_API_KEY", ""),
    },
}

# Ordered chain. Default: OpenRouter Claude Opus 4.8 -> OpenRouter GPT-5-mini -> Google Gemini 2.5 Flash.
PRIMARY_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
PRIMARY_MODEL = os.getenv("LLM_MODEL", "anthropic/claude-opus-4.8")
FALLBACK_PROVIDER = os.getenv("LLM_FALLBACK_PROVIDER", "openrouter")
FALLBACK_MODEL = os.getenv("LLM_FALLBACK_MODEL", "openai/gpt-5-mini")
FALLBACK2_PROVIDER = os.getenv("LLM_FALLBACK2_PROVIDER", "google")
FALLBACK2_MODEL = os.getenv("LLM_FALLBACK2_MODEL", "gemini-2.5-flash")
OPENROUTER_MODEL = PRIMARY_MODEL  # back-compat alias used in some logs

# Per-provider model for SHARDING: round-robin the lead provider across apps to
# spread load across free-tier rate limits (each provider still falls back to the others).
PROVIDER_MODELS = {
    "agentrouter": os.getenv("AGENTROUTER_MODEL", "claude-opus-4-7"),
    "zenmux": os.getenv("ZENMUX_MODEL", "x-ai/grok-4.5-free"),
    "openrouter": os.getenv("OPENROUTER_MODEL_ID", "anthropic/claude-opus-4.8"),
    "google": os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
}
SHARD_PROVIDERS = [p.strip() for p in
                   os.getenv("LLM_SHARD_PROVIDERS", "openrouter").split(",") if p.strip()]


def keyed_shard_providers() -> list[str]:
    """Shard providers that actually have an API key configured."""
    return [p for p in SHARD_PROVIDERS if PROVIDERS.get(p, {}).get("api_key")]


@lru_cache(maxsize=8)
def get_client(provider: str):
    """Return a cached OpenAI-compatible client for a provider."""
    from openai import OpenAI

    cfg = PROVIDERS.get(provider)
    if not cfg:
        raise RuntimeError(f"unknown LLM provider: {provider!r}")
    if not cfg["api_key"]:
        raise RuntimeError(
            f"{provider.upper()}_API_KEY not set. Copy .env.example to .env and fill it in.")
    return OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"],
                  timeout=LLM_TIMEOUT_SECONDS,
                  default_headers={"HTTP-Referer": _APP_URL, "X-Title": _APP_TITLE})


def get_llm_client():  # back-compat: the primary provider's client
    return get_client(PRIMARY_PROVIDER)


def _default_chain() -> list[tuple[str, str]]:
    """The configured tiers. An optional LLM_CHAIN='prov:model, prov:model' overrides."""
    raw = os.getenv("LLM_CHAIN", "").strip()
    if raw:
        tiers = []
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                prov, mdl = part.split(":", 1)  # maxsplit=1 keeps ':free' in the model id
            else:
                prov, mdl = PRIMARY_PROVIDER, part
            tiers.append((prov.strip(), mdl.strip()))
        return tiers
    return [
        (PRIMARY_PROVIDER, PRIMARY_MODEL),
        (FALLBACK_PROVIDER, FALLBACK_MODEL),
        (FALLBACK2_PROVIDER, FALLBACK2_MODEL),
    ]


def _model_chain(model: str | None, lead: str | None = None) -> list[tuple[str, str]]:
    """Ordered (provider, model) attempts. If `lead` is given (sharding), that
    provider goes first with its PROVIDER_MODELS model, then the other shard
    providers as fallbacks. Otherwise the configured LLM_MODEL chain is used
    (with an optional --model override on the primary). Dups/empties removed."""
    if lead:
        order = [lead] + [p for p in SHARD_PROVIDERS if p != lead]
        tiers = [(p, PROVIDER_MODELS.get(p, "")) for p in order]
    else:
        tiers = _default_chain()
        if model:
            tiers = [(PRIMARY_PROVIDER, model)] + tiers
    seen, chain = set(), []
    for prov, mdl in tiers:
        if prov and mdl and (prov, mdl) not in seen:
            seen.add((prov, mdl))
            chain.append((prov, mdl))
    return chain


def _extract_json_object(text: str) -> dict:
    """Best-effort parse of a JSON object from an LLM response.

    Handles raw JSON, ```json fenced blocks, and stray prose around the object.
    """
    text = (text or "").strip()
    if text.startswith("```"):
        body = text.split("\n", 1)[1] if "\n" in text else text
        if body.rstrip().endswith("```"):
            body = body.rstrip()[:-3]
        text = body.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


# providers/models that returned repeated permanent (4xx) errors this run -> skip
_DEAD: set[tuple[str, str]] = set()
_perm_fails: dict[tuple[str, str], int] = {}
_DEAD_AFTER = 3  # only mark a tier dead after this many permanent failures, so a
                 # transient 402/quota blip won't kill a mostly-working free model


def _classify_error(exc) -> str:
    """'retry' (transient) | 'permanent' (stable 4xx -> may mark tier dead) |
    'skip' (402 credit/quota -> fall through this call but keep the tier alive) | 'other'."""
    try:
        from openai import APIConnectionError, APIStatusError, APITimeoutError
    except Exception:  # pragma: no cover
        return "other"
    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return "retry"
    if isinstance(exc, APIStatusError):
        sc = getattr(exc, "status_code", None)
        if sc == 429 or (isinstance(sc, int) and sc >= 500):
            return "retry"
        if sc == 402:
            return "skip"       # free-tier credit/quota: transient under load, do NOT kill the tier
        if sc in (401, 403, 404):
            return "permanent"  # bad key / forbidden / missing model -> won't recover this run
    return "other"


def llm_json(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 2000,
    lead: str | None = None,
) -> tuple[dict, str]:
    """Call the model chain and return (parsed_json, raw_text).

    Tries each tier in order, skipping providers with no key and any (provider,
    model) that already returned a permanent 4xx this run (e.g. a 402 'needs
    balance' on a free model -> fall straight through to the next tier). Transient
    errors (429/5xx/network) retry up to 3x; JSON-mode is dropped if rejected.
    """
    from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

    def _attempt(provider: str, mdl: str) -> str:
        client = get_client(provider)

        @retry(retry=retry_if_exception(lambda e: _classify_error(e) == "retry"),
               stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=3, max=30))
        def _call(use_json_mode: bool) -> str:
            kwargs: dict[str, Any] = dict(
                model=mdl, messages=messages, temperature=temperature, max_tokens=max_tokens)
            if use_json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            resp = client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content or ""

        out = ""
        try:
            out = _call(True)
        except Exception:
            pass
        if not out.strip():
            out = _call(False)  # may raise a permanent error -> handled by the caller
        if not out.strip():
            raise RuntimeError(f"empty completion from {provider}:{mdl}")
        return out

    last_err = None
    for provider, mdl in _model_chain(model, lead=lead):
        if (provider, mdl) in _DEAD:
            continue
        cfg = PROVIDERS.get(provider)
        if not cfg or not cfg["api_key"]:
            continue
        try:
            raw = _attempt(provider, mdl)
            obj = _extract_json_object(raw)
            if isinstance(obj, list):  # some models return a JSON array
                obj = next((x for x in obj if isinstance(x, dict)), None)
            if not isinstance(obj, dict):
                raise ValueError("model did not return a JSON object")
            return obj, raw
        except Exception as e:
            last_err = e
            if _classify_error(e) == "permanent":
                key = (provider, mdl)
                _perm_fails[key] = _perm_fails.get(key, 0) + 1
                if _perm_fails[key] >= _DEAD_AFTER:
                    _DEAD.add(key)  # stop re-trying a consistently-blocked tier
            continue
    raise RuntimeError(f"all LLM providers failed (last error: {last_err})")
