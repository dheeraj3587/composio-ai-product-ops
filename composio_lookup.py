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

import re

import requests

import config

CATALOG_URL = "https://composio.dev/toolkits/{slug}"
_UA = {"User-Agent": "Mozilla/5.0 (compatible; readiness-agent/1.0)"}
_CACHE_PATH = config.CACHE_DIR / "composio.json"
_cache: dict | None = None


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
        import composio  # noqa: F401
    except Exception:
        return None
    if not config.COMPOSIO_API_KEY:
        return None
    try:
        from composio import Composio  # type: ignore

        client = Composio(api_key=config.COMPOSIO_API_KEY)
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
