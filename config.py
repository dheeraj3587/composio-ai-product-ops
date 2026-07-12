"""Environment, paths, atomic JSON helpers, and native Google Gen AI access."""
from __future__ import annotations

import json
import os
import threading
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_ENV_ROOT = Path(__file__).resolve().parent
load_dotenv(_ENV_ROOT / ".env")
load_dotenv(_ENV_ROOT / ".env.providers", override=True)

# Actual model used by the latest llm_json() call on this thread. The batch
# runner is concurrent, so this cannot be process-global.
_last_llm = threading.local()


def last_llm_used() -> str:
    return getattr(_last_llm, "value", "")

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ROOT = _ENV_ROOT
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
FAILURE_STATE_PATH = OUT_DIR / "failures.json"
USAGE_PATH = OUT_DIR / "usage.json"
BATCH_STATE_PATH = OUT_DIR / "batch_state.json"
BROWSER_EVIDENCE_PATH = OUT_DIR / "browser_evidence.json"
COMPOSIO_COVERAGE_PATH = OUT_DIR / "composio_coverage.json"
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
    """Atomically replace a JSON artifact so interrupted batches cannot truncate it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
    )
    try:
        with open(temporary, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


# --------------------------------------------------------------------------- #
# LLM - one native provider, intentionally no gateway fallback
# --------------------------------------------------------------------------- #
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "180"))
GOOGLE_MAX_WORKERS = int(os.getenv("GOOGLE_MAX_WORKERS", "2"))
GOOGLE_API_KEY = (
    os.getenv("GOOGLE_GENAI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY", "")
)
PRIMARY_MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-3.1-pro-preview")
GOOGLE_THINKING_LEVEL = os.getenv("GOOGLE_THINKING_LEVEL", "medium")
GOOGLE_TOKEN_PRICES = {
    "gemini-3.1-pro-preview": (2.0, 12.0),
    "gemini-3-flash-preview": (0.5, 3.0),
    "gemini-3.5-flash": (1.5, 9.0),
    "gemini-3.1-flash-lite": (0.25, 1.5),
}


def _google_token_prices(model: str) -> tuple[float, float]:
    """USD per 1M input/output tokens; unknown models use the conservative Pro rate."""
    return GOOGLE_TOKEN_PRICES.get(model, (2.0, 12.0))


@lru_cache(maxsize=1)
def get_client():
    """Return the native Google Gen AI SDK client."""
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_GENAI_API_KEY/GOOGLE_API_KEY is not set")
    from google import genai
    from google.genai import types

    return genai.Client(
        api_key=GOOGLE_API_KEY,
        http_options=types.HttpOptions(
            timeout=int(LLM_TIMEOUT_SECONDS * 1000),
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

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


class StructuredOutputError(ValueError):
    """The provider answered, but not with a complete JSON object."""


class ProviderQuotaExhausted(RuntimeError):
    """A provider's long-lived project quota is exhausted; pause the batch."""


class ProviderCapacityUnavailable(RuntimeError):
    """Repeated provider capacity failures make continuing the batch wasteful."""


def _classify_error(exc) -> str:
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    try:
        code = int(code)
    except (TypeError, ValueError):
        return "other"
    message = str(exc).lower()
    if code == 429 and any(
        marker in message
        for marker in (
            "generate_requests_per_model_per_day",
            "generaterequestsperdayperprojectpermodel",
            "requests per day",
        )
    ):
        return "quota"
    return "retry" if code in {408, 429, 499} or code >= 500 else "other"


def is_capacity_error(exc) -> bool:
    """Return true for provider-wide high-demand failures after local retries."""
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    try:
        code = int(code)
    except (TypeError, ValueError):
        return False
    message = str(exc).lower()
    return code == 503 and any(
        marker in message for marker in ("high demand", "capacity", "unavailable")
    )


def _google_contents(messages: list[dict]):
    from google.genai import types

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
        contents.append(types.Content(
            role=role,
            parts=[types.Part.from_text(text=str(message.get("content", "")))],
        ))
    return system, contents


def llm_json(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 2000,
    thinking_level: str | None = None,
    response_schema: Any | None = None,
) -> tuple[dict, str]:
    """Call Gemini through the native Google SDK and return parsed strict JSON."""
    from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
    from google.genai import types
    import usage_tracker

    selected_model = model or PRIMARY_MODEL
    system, contents = _google_contents(messages)
    input_price, output_price = _google_token_prices(selected_model)
    input_estimate = sum(len(str(message.get("content", ""))) for message in messages) / 4
    conservative_cost = (
        input_estimate * input_price / 1_000_000
        + max_tokens * output_price / 1_000_000
    )
    usage_tracker.ensure_budget("google", conservative_cost)

    @retry(
        retry=retry_if_exception(lambda exc: _classify_error(exc) == "retry"),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=3, max=30),
        reraise=True,
    )
    def _call():
        generation_config: dict[str, Any] = {
            "system_instruction": system or None,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "response_mime_type": "application/json",
            "thinking_config": types.ThinkingConfig(
                thinking_level=thinking_level or GOOGLE_THINKING_LEVEL
            ),
        }
        if response_schema is not None:
            generation_config["response_schema"] = response_schema
        return get_client().models.generate_content(
            model=selected_model,
            contents=contents,
            config=types.GenerateContentConfig(**generation_config),
        )

    try:
        response = _call()
    except Exception as exc:
        if _classify_error(exc) == "quota":
            raise ProviderQuotaExhausted(str(exc)) from exc
        raise
    raw = response.text or ""
    usage = response.usage_metadata
    prompt_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
    answer_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
    thought_tokens = int(getattr(usage, "thoughts_token_count", 0) or 0)
    estimated_cost = (
        prompt_tokens * input_price / 1_000_000
        + (answer_tokens + thought_tokens) * output_price / 1_000_000
    )
    candidate = response.candidates[0] if response.candidates else None
    usage_tracker.record("google", "generate_content", estimated_cost, {
        "model": selected_model,
        "prompt_tokens": prompt_tokens,
        "answer_tokens": answer_tokens,
        "thought_tokens": thought_tokens,
        "input_usd_per_million": input_price,
        "output_usd_per_million": output_price,
        "finish_reason": str(getattr(candidate, "finish_reason", "") or ""),
    })
    try:
        if not raw.strip():
            raise ValueError("empty completion")
        parsed = getattr(response, "parsed", None)
        if hasattr(parsed, "model_dump"):
            obj = parsed.model_dump(mode="json")
        elif isinstance(parsed, dict):
            obj = parsed
        else:
            obj = _extract_json_object(raw)
        if isinstance(obj, list):
            obj = next((item for item in obj if isinstance(item, dict)), None)
        if not isinstance(obj, dict):
            raise ValueError("model did not return a JSON object")
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise StructuredOutputError(
            f"incomplete JSON from google:{selected_model}"
        ) from exc
    _last_llm.value = f"google:{selected_model}"
    return obj, raw
