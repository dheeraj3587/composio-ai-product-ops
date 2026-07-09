"""Documentation research via web SEARCH + direct FETCH (no browser automation).

Gathers raw evidence for one app: search hits + fetched page text. Returns an
Evidence dict whose ``fetched_urls`` is the WHITELIST synthesis may cite
(Flag D: evidence_urls must be real, fetched, resolving URLs — never invented).

Search providers (auto-detected, first that works wins):
  - Tavily             (TAVILY_API_KEY)   clean JSON, preferred
  - Serper             (SERPER_API_KEY)   Google results
  - DuckDuckGo HTML    (keyless)          fallback, no key required

HTML is reduced to text with the stdlib html.parser (no bs4 dependency).
"""
from __future__ import annotations

import html
import os
import re
import time
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse

import requests

import config

UA = {"User-Agent": "Mozilla/5.0 (compatible; readiness-agent/1.0; +https://composio.dev)"}
FETCH_TIMEOUT = 15
MAX_TEXT_CHARS = 12000
MAX_FETCH = 6


# --------------------------------------------------------------------------- #
# HTML -> text
# --------------------------------------------------------------------------- #
class _TextExtractor(HTMLParser):
    _SKIP = {"script", "style", "noscript", "svg", "head"}

    def __init__(self) -> None:
        super().__init__()
        self._skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self._SKIP and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip == 0:
            t = data.strip()
            if t:
                self.parts.append(t)


def html_to_text(raw: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(raw)
        text = " ".join(parser.parts)
    except Exception:
        text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    return text[:MAX_TEXT_CHARS]


# --------------------------------------------------------------------------- #
# fetch
# --------------------------------------------------------------------------- #
def fetch(url: str, timeout: int = FETCH_TIMEOUT) -> dict:
    try:
        r = requests.get(url, headers=UA, timeout=timeout)
        ok = r.status_code == 200 and bool(r.text)
        return {"url": url, "ok": ok, "status": r.status_code,
                "text": html_to_text(r.text) if ok else "", "error": ""}
    except requests.RequestException as e:
        return {"url": url, "ok": False, "status": 0, "text": "", "error": str(e)}


def url_resolves(url: str, timeout: int = 10) -> bool:
    """Flag D helper used before saving evidence_urls: does the URL resolve (<400)?"""
    try:
        r = requests.head(url, headers=UA, timeout=timeout, allow_redirects=True)
        if r.status_code >= 400:  # some servers reject/misreport HEAD; retry GET
            r = requests.get(url, headers=UA, timeout=timeout, stream=True)
        return r.status_code < 400
    except requests.RequestException:
        return False


# --------------------------------------------------------------------------- #
# search providers
# --------------------------------------------------------------------------- #
def _search_tavily(query: str, k: int):
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return None
    r = requests.post("https://api.tavily.com/search",
                      json={"api_key": key, "query": query, "max_results": k}, timeout=20)
    r.raise_for_status()
    return [{"title": x.get("title", ""), "url": x.get("url", ""), "snippet": x.get("content", "")}
            for x in r.json().get("results", [])]


def _search_serper(query: str, k: int):
    key = os.getenv("SERPER_API_KEY")
    if not key:
        return None
    r = requests.post("https://google.serper.dev/search",
                      headers={"X-API-KEY": key, "Content-Type": "application/json"},
                      json={"q": query, "num": k}, timeout=20)
    r.raise_for_status()
    return [{"title": x.get("title", ""), "url": x.get("link", ""), "snippet": x.get("snippet", "")}
            for x in r.json().get("organic", [])][:k]


def _search_ddg(query: str, k: int):
    r = requests.get("https://html.duckduckgo.com/html/", params={"q": query},
                     headers=UA, timeout=20)
    r.raise_for_status()
    results = []
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S):
        href = m.group(1)
        title = re.sub(r"<[^>]+>", "", m.group(2))
        if "duckduckgo.com/l/" in href:
            href = parse_qs(urlparse(href).query).get("uddg", [href])[0]
        results.append({"title": html.unescape(title).strip(), "url": href, "snippet": ""})
        if len(results) >= k:
            break
    return results


def search(query: str, k: int = 6) -> list[dict]:
    for fn in (_search_tavily, _search_serper):
        try:
            res = fn(query, k)
            if res:
                return res
        except Exception:
            pass
    try:
        return _search_ddg(query, k) or []
    except Exception:
        return []


# --------------------------------------------------------------------------- #
# evidence gathering
# --------------------------------------------------------------------------- #
def _derived_doc_urls(hint_url: str) -> list[str]:
    """Common developer-doc locations derived from the app's domain, so we still
    reach real docs when search misses them and the hint is a marketing homepage."""
    if not hint_url:
        return []
    host = urlparse(hint_url).netloc
    if not host:
        return []
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    apex = ".".join(parts[-2:]) if len(parts) >= 2 else host
    return [f"https://developer.{apex}", f"https://developers.{apex}", f"https://docs.{apex}",
            f"https://api.{apex}", f"https://{apex}/developers", f"https://{apex}/docs"]


def _candidate_urls(hint_url: str, search_results: list[dict]) -> list[str]:
    urls: list[str] = []
    if hint_url:
        urls.append(hint_url)
    for u in _derived_doc_urls(hint_url):  # likely developer-doc subdomains/paths
        if u not in urls:
            urls.append(u)

    def score(u: str) -> int:
        u = u.lower()
        return sum(tok in u for tok in ("docs", "developer", "developers", "api", "reference"))

    for r in sorted(search_results, key=lambda r: -score(r.get("url", ""))):
        u = r.get("url", "")
        if u.startswith("http") and u not in urls:
            urls.append(u)
    return urls[:MAX_FETCH]


def gather_mcp_evidence(app: str, k: int = 5, max_fetch: int = 2) -> dict:
    """Dedicated probe for the `existing_mcp` field.

    API-reference pages almost never mention MCP, so deriving existing_mcp from
    the main evidence pass systematically produced false "None"s — the first
    batch marked GitHub, Stripe, Cloudflare, Linear, Sentry, Vercel, Netlify,
    MongoDB, Jira, HubSpot, Klaviyo and Shopify as having no official MCP server
    when all twelve have one. One extra search + up to two fetches per app is
    cheap and fixes the field at the source.
    """
    q = f"{app} official MCP server Model Context Protocol"
    results = search(q, k=k)
    fetched = []
    for r in results:
        u = r.get("url", "")
        if not u.startswith("http") or len(fetched) >= max_fetch:
            continue
        f = fetch(u)
        if f["ok"]:
            fetched.append(f)
        time.sleep(0.2)
    return {
        "query": q,
        "search_results": results,
        "fetched": fetched,
        "fetched_urls": [f["url"] for f in fetched],
    }


def gather_evidence(app: str, slug: str, hint_url: str = "", category: str = "",
                    query: str | None = None, log: bool = True) -> dict:
    """Search + fetch → raw Evidence dict (no LLM here; cheap & deterministic)."""
    q = query or f"{app} API documentation authentication developer"
    results = search(q, k=6)
    candidates = _candidate_urls(hint_url, results)

    fetched = []
    for u in candidates:
        fetched.append(fetch(u))
        time.sleep(0.2)

    ok_urls = [f["url"] for f in fetched if f["ok"]]
    degraded = len(ok_urls) == 0
    if degraded and log:
        _log_failure(slug, f"no fetchable docs; query={q!r}; candidates={candidates}")

    mcp = gather_mcp_evidence(app)

    return {
        "app": app, "slug": slug, "category": category, "query": q,
        "search_results": results,
        "fetched": fetched,
        # Flag D whitelist for evidence_urls (MCP-probe pages are citable too)
        "fetched_urls": ok_urls + [u for u in mcp["fetched_urls"] if u not in ok_urls],
        "degraded": degraded,
        "mcp": mcp,
    }


def _log_failure(slug: str, msg: str) -> None:
    config.ensure_dirs()
    with open(config.FAILURES_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{slug}\t{msg}\n")


if __name__ == "__main__":  # live smoke (needs network)
    import json
    import sys

    app = sys.argv[1] if len(sys.argv) > 1 else "Stripe"
    slug = sys.argv[2] if len(sys.argv) > 2 else "stripe"
    ev = gather_evidence(app, slug, hint_url="https://stripe.com/docs/api")
    print(json.dumps({"query": ev["query"], "fetched_urls": ev["fetched_urls"],
                      "degraded": ev["degraded"],
                      "n_search": len(ev["search_results"])}, indent=2))
