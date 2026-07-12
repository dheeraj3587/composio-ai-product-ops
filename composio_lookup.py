"""Composio catalog lookup.

Answers ONE question well: does this app already have a Composio toolkit?
(`composio_toolkit` = Yes/No), plus a light `existing_mcp` hint.

Attempt order:
  1. Composio Python SDK  -> authoritative, if installed and COMPOSIO_API_KEY set.
  2. HTTP catalog check    -> heuristic GET of composio.dev/toolkits/<slug>.

Honest caveat: the HTTP path is a heuristic (it scrapes a public page and looks
for the app name + toolkit/MCP markers). The SDK is authoritative; prefer it in
production. Results are cached to out/cache/composio.json keyed by slug so the
batch run is resumable and cheap.
"""

from __future__ import annotations

import concurrent.futures as cf
import datetime as dt
import importlib.metadata
import re
import statistics

import requests

import config

CATALOG_URL = "https://composio.dev/toolkits/{slug}"
_UA = {"User-Agent": "Mozilla/5.0 (compatible; readiness-agent/1.0)"}
_CACHE_PATH = config.CACHE_DIR / "composio.json"
_cache: dict | None = None
DEFAULT_AUDIT_WORKERS = 6


# --------------------------------------------------------------------------- #
# cache
# --------------------------------------------------------------------------- #
def _load_cache() -> dict:
    global _cache
    if _cache is None:
        _cache = config.load_json(_CACHE_PATH, default={}) or {}
    return _cache


def _save_cache() -> None:
    if _cache is not None:
        config.save_json(_CACHE_PATH, _cache)


# --------------------------------------------------------------------------- #
# candidate toolkit slugs
# --------------------------------------------------------------------------- #
def _slug_variants(app: str, slug: str) -> list[str]:
    base = slug.replace("-", "")
    name = re.sub(r"[^a-z0-9]", "", app.lower())
    variants = [slug, base, slug.replace("-", "_"), name]
    seen, out = set(), []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _normalized_identity(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower().split(" (")[0])


def _enum_value(value) -> str:
    raw = getattr(value, "value", value)
    return str(raw) if raw is not None else ""


def _status_code(exc: Exception) -> int | None:
    for field in ("status_code", "code", "status"):
        value = getattr(exc, field, None)
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    match = re.search(r"\b(4\d\d|5\d\d)\b", str(exc))
    return int(match.group(1)) if match else None


def _sdk_client():
    if not config.COMPOSIO_API_KEY:
        raise RuntimeError("COMPOSIO_API_KEY is not set")
    try:
        from composio import Composio
    except ImportError as exc:
        raise RuntimeError("composio SDK is not installed") from exc
    return Composio(api_key=config.COMPOSIO_API_KEY)


def _toolkit_profile(client, app_meta: dict, checked_at: str) -> dict:
    app = app_meta["app"]
    slug = app_meta["slug"]
    variants = _slug_variants(app, slug)
    toolkit = None
    for candidate in variants:
        try:
            toolkit = client.toolkits.get(candidate)
        except Exception as exc:
            if _status_code(exc) == 404:
                continue
            raise RuntimeError(f"{slug}: Composio lookup failed for {candidate}: {exc}") from exc
        if toolkit:
            returned_slug = str(getattr(toolkit, "slug", "") or "")
            returned_name = str(getattr(toolkit, "name", "") or "")
            valid_identity = (
                returned_slug in variants
                or _normalized_identity(returned_name) == _normalized_identity(app)
            )
            if not valid_identity:
                raise RuntimeError(
                    f"{slug}: SDK returned unrelated toolkit {returned_slug or returned_name!r}"
                )
            break

    if toolkit is None:
        return {
            "app": app,
            "status": "Missing",
            "toolkit_slug": None,
            "toolkit_name": None,
            "tools_count": 0,
            "triggers_count": 0,
            "auth_schemes": [],
            "managed_auth_schemes": [],
            "latest_version": None,
            "versions_count": 0,
            "categories": [],
            "catalog_url": CATALOG_URL.format(slug=slug),
            "source": "sdk",
            "checked_at": checked_at,
        }

    meta = getattr(toolkit, "meta", None)
    missing_counts = [
        field
        for field in ("tools_count", "triggers_count")
        if meta is None or getattr(meta, field, None) is None
    ]
    if missing_counts:
        raise RuntimeError(
            f"{slug}: SDK toolkit metadata is missing {', '.join(missing_counts)}"
        )
    tools_count = int(getattr(meta, "tools_count", 0) or 0)
    triggers_count = int(getattr(meta, "triggers_count", 0) or 0)
    versions = list(getattr(meta, "available_versions", None) or [])
    categories = sorted({
        str(getattr(category, "name", "") or "").strip()
        for category in (getattr(meta, "categories", None) or [])
        if str(getattr(category, "name", "") or "").strip()
    })
    auth_schemes = sorted({
        _enum_value(getattr(detail, "mode", None))
        for detail in (getattr(toolkit, "auth_config_details", None) or [])
        if _enum_value(getattr(detail, "mode", None))
    })
    managed_auth_schemes = sorted({
        _enum_value(value)
        for value in (getattr(toolkit, "composio_managed_auth_schemes", None) or [])
        if _enum_value(value)
    })
    toolkit_slug = str(getattr(toolkit, "slug", "") or slug)
    return {
        "app": app,
        "status": "Active" if tools_count > 0 else "Catalog-only",
        "toolkit_slug": toolkit_slug,
        "toolkit_name": str(getattr(toolkit, "name", "") or app),
        "tools_count": tools_count,
        "triggers_count": triggers_count,
        "auth_schemes": auth_schemes,
        "managed_auth_schemes": managed_auth_schemes,
        "latest_version": str(getattr(meta, "version", "") or "") or None,
        "versions_count": len(versions),
        "categories": categories,
        "catalog_url": CATALOG_URL.format(slug=toolkit_slug),
        "source": "sdk",
        "checked_at": checked_at,
    }


def audit_catalog(apps: list[dict], workers: int = DEFAULT_AUDIT_WORKERS,
                  client=None) -> dict:
    """Build an authoritative, all-or-nothing Composio coverage snapshot."""
    if workers < 1:
        raise ValueError("workers must be at least 1")
    sdk_client = client or _sdk_client()
    checked_at = dt.datetime.now(dt.timezone.utc).isoformat()
    profiles: dict[str, dict] = {}
    errors = []
    with cf.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(_toolkit_profile, sdk_client, app, checked_at): app
            for app in apps
        }
        for future in cf.as_completed(futures):
            app = futures[future]
            try:
                profiles[app["slug"]] = future.result()
            except Exception as exc:
                errors.append(f"{app['slug']}: {exc}")
    if errors:
        raise RuntimeError(
            "Composio SDK audit incomplete; prior snapshot was preserved:\n- "
            + "\n- ".join(sorted(errors))
        )

    ordered = {app["slug"]: profiles[app["slug"]] for app in apps}
    matched = [profile for profile in ordered.values() if profile["status"] != "Missing"]
    tool_counts = [profile["tools_count"] for profile in matched]
    summary = {
        "n_apps": len(ordered),
        "active": sum(profile["status"] == "Active" for profile in ordered.values()),
        "catalog_only": sum(
            profile["status"] == "Catalog-only" for profile in ordered.values()
        ),
        "missing": sum(profile["status"] == "Missing" for profile in ordered.values()),
        "tools_total": sum(tool_counts),
        "tools_median": round(float(statistics.median(tool_counts)), 1) if tool_counts else 0,
        "trigger_enabled": sum(profile["triggers_count"] > 0 for profile in matched),
        "without_triggers": sum(profile["triggers_count"] == 0 for profile in matched),
    }
    if summary["active"] + summary["catalog_only"] + summary["missing"] != len(apps):
        raise RuntimeError("Composio SDK audit summary does not cover every app")
    try:
        sdk_version = importlib.metadata.version("composio")
    except importlib.metadata.PackageNotFoundError:
        sdk_version = "unknown"
    return {
        "schema_version": 1,
        "generated": checked_at,
        "source": "Composio Python SDK",
        "sdk_version": sdk_version,
        "summary": summary,
        "apps": ordered,
    }


def write_catalog_audit(apps: list[dict], workers: int = DEFAULT_AUDIT_WORKERS,
                        client=None) -> dict:
    payload = audit_catalog(apps, workers=workers, client=client)
    config.save_json(config.COMPOSIO_COVERAGE_PATH, payload)
    return payload


# --------------------------------------------------------------------------- #
# HTTP heuristic
# --------------------------------------------------------------------------- #
def _looks_like_toolkit_page(html: str, app: str) -> bool:
    low = html.lower()
    name = app.lower().split(" (")[0].strip()
    name_hit = bool(name) and name in low
    toolkit_hit = ("mcp integration" in low) or ("toolkit" in low) or (" tools" in low)
    # Guard against soft-404 SPA shells that render nothing app-specific.
    not_found = ("page not found" in low) or ("404" in low and "not found" in low)
    return bool(name_hit and toolkit_hit and not not_found)


def _http_catalog_check(app: str, slug: str, timeout: int = 12) -> dict:
    tried = []
    for cand in _slug_variants(app, slug):
        url = CATALOG_URL.format(slug=cand)
        tried.append(url)
        try:
            r = requests.get(url, headers=_UA, timeout=timeout)
        except requests.RequestException:
            continue
        if r.status_code == 200 and _looks_like_toolkit_page(r.text, app):
            return {"exists": True, "url": url, "toolkit_slug": cand, "source": "http"}
    return {
        "exists": False,
        "url": CATALOG_URL.format(slug=slug),
        "toolkit_slug": None,
        "source": "http",
        "tried": tried,
    }


# --------------------------------------------------------------------------- #
# SDK (authoritative, best-effort — surface varies by version)
# --------------------------------------------------------------------------- #
def _sdk_check(app: str, slug: str) -> dict | None:
    try:
        client = _sdk_client()
        for cand in _slug_variants(app, slug):
            try:
                tk = client.toolkits.get(cand)  # type: ignore[attr-defined]
            except Exception:
                tk = None
            if tk:
                return {
                    "exists": True,
                    "url": CATALOG_URL.format(slug=cand),
                    "toolkit_slug": cand,
                    "source": "sdk",
                }
        return {
            "exists": False,
            "url": CATALOG_URL.format(slug=slug),
            "toolkit_slug": None,
            "source": "sdk",
        }
    except Exception:
        return None  # fall back to HTTP


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def lookup(app: str, slug: str, use_cache: bool = True) -> dict:
    """Return {composio_toolkit, existing_mcp_hint, composio_url, source, confidence}."""
    cache = _load_cache()
    if use_cache and slug in cache:
        return cache[slug]

    res = _sdk_check(app, slug) or _http_catalog_check(app, slug)

    out = {
        "composio_toolkit": "Yes" if res.get("exists") else "No",
        # Having a Composio toolkit implies reachability via Composio's MCP router,
        # but that is NOT the app's own official MCP. Leave the app-MCP call to synthesis.
        "existing_mcp_hint": "unknown",
        "composio_url": res.get("url", ""),
        "source": res.get("source", "http"),
        # SDK is authoritative (high); HTTP heuristic is lower-confidence.
        "confidence": 0.9
        if res.get("source") == "sdk"
        else (0.6 if res.get("exists") else 0.4),
    }
    cache[slug] = out
    _save_cache()
    return out


if __name__ == "__main__":  # live smoke (needs network; safe to fail offline)
    import sys

    app = sys.argv[1] if len(sys.argv) > 1 else "GitHub"
    slug = sys.argv[2] if len(sys.argv) > 2 else "github"
    print(lookup(app, slug, use_cache=False))
