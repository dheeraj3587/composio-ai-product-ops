"""Documentation research via Perplexity Search SDK + direct HTTP fetch.

Gathers raw evidence for one app: search hits + fetched page text. Returns an
Evidence dict whose ``fetched_urls`` is the WHITELIST synthesis may cite
(Flag D: evidence_urls must be real, fetched, resolving URLs — never invented).

HTML is reduced to text with the stdlib html.parser (no bs4 dependency).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import os
import re
import threading
import time
from functools import lru_cache
from html.parser import HTMLParser
from urllib.parse import urlparse, urlunparse

import requests

import config

UA = {"User-Agent": "Mozilla/5.0 (compatible; readiness-agent/1.0; +https://composio.dev)"}
FETCH_TIMEOUT = 15
MAX_TEXT_CHARS = 12000
MAX_FETCH = 6

MCP_OFFICIAL_SEEDS = {
    # Vendor-owned MCP pages/servers that search can miss or rank below generic
    # MCP directories. These are used as evidence seeds, not as final labels.
    "github": ["https://github.com/github/github-mcp-server"],
    "cloudflare": ["https://github.com/cloudflare/mcp-server-cloudflare"],
    "stripe": ["https://docs.stripe.com/mcp"],
    "linear": ["https://linear.app/docs/mcp"],
    "sentry": ["https://mcp.sentry.dev"],
    "netlify": ["https://docs.netlify.com/build/build-with-ai/netlify-mcp-server/"],
    "vercel": ["https://vercel.com/docs/agent-resources/vercel-mcp"],
    "mongodb-atlas": ["https://www.mongodb.com/docs/mcp-server/"],
    "jira": ["https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/"],
    "hubspot": ["https://developers.hubspot.com/mcp"],
    "klaviyo": ["https://developers.klaviyo.com/en/docs/klaviyo_mcp_server"],
    "shopify": ["https://shopify.dev/docs/apps/build/storefront-mcp"],
    "slack": ["https://docs.slack.dev/ai/slack-mcp-server/"],
    "airtable": ["https://support.airtable.com/docs/using-the-airtable-mcp-server"],
    "ramp": ["https://docs.ramp.com/developer-api/v1/developer-mcp"],
    "twilio": ["https://www.twilio.com/docs/ai/mcp"],
    "vonage": ["https://developer.vonage.com/en/mcp-server/overview"],
    "dataforseo": ["https://dataforseo.com/help-center/setting-up-the-official-dataforseo-mcp-server-simple-guide"],
    "freshdesk": ["https://support.freshdesk.com/support/solutions/articles/50000012670-model-context-protocol-mcp-integration-in-freshdesk-eap-"],
    "gohighlevel": ["https://help.gohighlevel.com/support/solutions/articles/155000007981-highlevel-mcp-server-connect-ai-agents-to-highlevel-tools"],
    "gorgias": ["https://docs.gorgias.com/en-US/connect-your-ai-assistant-to-the-gorgias-mcp-6310546"],
    "podio": ["https://docs.sharefile.com/en-us/podio/using-podio/general-features/podio-mcp-server.html"],
    "quickbooks": ["https://github.com/intuit/quickbooks-online-mcp-server"],
    "salesforce": [
        "https://developer.salesforce.com/docs/platform/hosted-mcp-servers/overview",
        "https://github.com/salesforcecli/mcp",
    ],
    "snowflake": ["https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp"],
    "woocommerce": ["https://developer.woocommerce.com/docs/features/mcp/"],
    "zoho-crm": ["https://www.zoho.com/crm/developer/docs/mcp/overview.html"],
    "zoho-cliq": ["https://www.zoho.com/cliq/help/platform/zoho-cliq-mcp.html"],
    "systeme-io": ["https://help.systeme.io/article/9489-how-to-use-systeme-ios-mcp"],
    "consensus": ["https://docs.consensus.app/docs/mcp"],
    "lark": [
        "https://github.com/larksuite/lark-openapi-mcp",
        "https://open.larksuite.com/document/mcp_open_tools/call-feishu-mcp-server-in-remote-mode",
    ],
    "neo4j": [
        "https://neo4j.com/developer/genai-ecosystem/model-context-protocol-mcp/",
        "https://github.com/neo4j/mcp",
    ],
    "xero": ["https://github.com/xeroapi/xero-mcp-server"],
    "attio": ["https://docs.attio.com/mcp/overview"],
    "close": ["https://help.close.com/docs/mcp-server"],
    "front": ["https://dev.frontapp.com/docs/mcp-server"],
    "intercom": ["https://developers.intercom.com/docs/guides/mcp"],
    "pylon": ["https://docs.usepylon.com/pylon-docs/integrations/pylon-mcp"],
    "plain": ["https://help.plain.com/article/mcp-server"],
    "google-ads": ["https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server"],
    "se-ranking": ["https://seranking.com/api/integrations/mcp/"],
    "ahrefs": ["https://docs.ahrefs.com/en/mcp/docs/introduction"],
    "apify": ["https://docs.apify.com/platform/integrations/mcp"],
    "firecrawl": ["https://docs.firecrawl.dev/use-cases/developers-mcp"],
    "bright-data": ["https://brightdata.com/ai/mcp-server"],
    "clay": ["https://www.clay.com/mcp"],
    "supabase": ["https://supabase.com/docs/guides/ai-tools/mcp"],
    "datadog": ["https://docs.datadoghq.com/mcp_server/"],
    "notion": ["https://developers.notion.com/guides/mcp/overview"],
    "asana": ["https://developers.asana.com/docs/using-asanas-mcp-server"],
    "monday": ["https://monday.com/w/mcp"],
    "clickup": ["https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server"],
    "coda": ["https://coda.io/resources/guides/getting_started_with_coda_mcp"],
    "smartsheet": ["https://developers.smartsheet.com/ai-mcp/smartsheet/mcp-server"],
    "brex": ["https://developer.brex.com/docs/mcp"],
    "reducto": ["https://docs.reducto.ai/mcp-server"],
    "devin": ["https://docs.devin.ai/work-with-devin/devin-mcp"],
    "higgsfield": ["https://higgsfield.ai/mcp", "https://higgsfield.ai/cli"],
    "youtube-transcript": ["https://transcriptapi.com/blog/youtube-mcp-server-setup-connect-claude"],
    "pitchbook": [
        "https://pitchbook.com/media/press-releases/"
        "pitchbook-announces-new-essential-mcp-integration-with-perplexity-expanding-access-to-ai-powered-verifiable-market-intelligence"
    ],
}

ACCESS_OFFICIAL_SEEDS = {
    # Claim-bearing pages that explain how credentials are enabled or obtained.
    "salesforce": [
        "https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_using_oauth.html",
        "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest_compatible_editions.htm",
    ],
    "plain": ["https://help.plain.com/article/api-quickstart"],
    "telegram": ["https://core.telegram.org/api/auth"],
    "pinterest": [
        "https://github.com/pinterest/api-quickstart/blob/main/nodejs/README.md"
    ],
    "gumroad": [
        "https://gumroad.com/api",
        "https://gumroad.com/help/article/280-create-application-api",
    ],
    "fanbasis": ["https://apidocs.fan/"],
    "clay": [
        "https://community.clay.com/x/support/5cwjpgptccda/authenticating-an-api-key-in-clay-steps-beyond-cur"
    ],
    "snowflake": [
        "https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/authentication",
        "https://www.snowflake.com/en/pricing-options/",
    ],
    "harvest": [
        "https://support.getharvest.com/hc/en-us/articles/360048180732-The-Harvest-API",
        "https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/",
    ],
    "notebooklm": [
        "https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/set-up-notebooklm"
    ],
    "dealcloud": ["https://api.docs.dealcloud.com/docs/apikeys"],
    "mrscraper": ["https://docs.mrscraper.com/docs/features/activating-api"],
    "waterfall": ["https://waterfall.io"],
    "salesforce-commerce-cloud": [
        "https://developer.salesforce.com/docs/commerce/commerce-api/guide/authorization.html",
        "https://developer.salesforce.com/docs/commerce/account-manager/guide/account-manager-get-started.html",
    ],
    "paygent-connect": ["https://www.gopaygent.com/"],
    "pitchbook": ["https://pitchbook.com/help/PitchBook-api"],
}

OFFICIAL_HOST_ALIASES = {
    "gohighlevel": {"gohighlevel.com"},
    "sendgrid": {"sendgrid.com", "twilio.com"},
    "binance": {"binance.com", "binance.us"},
    "ipayx": {"ipayx.ai", "i-pay.io"},
    "fathom": {"fathom.video", "fathom.ai"},
    "paygent-connect": {"gopaygent.com"},
    "fanbasis": {"fanbasis.com", "apidocs.fan"},
    "notebooklm": {"google.com"},
}


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
        text = html_to_text(r.text) if ok else ""
        content_url = url

        # Mintlify-style docs can serve a navigation-heavy HTML shell while
        # advertising a complete first-party Markdown representation. Fetching
        # that variant recovers the actual auth instructions without a browser.
        if ok and ".md for the markdown version" in text.lower():
            parsed = urlparse(url)
            if not parsed.path.lower().endswith(".md"):
                markdown_url = urlunparse(parsed._replace(
                    path=parsed.path.rstrip("/") + ".md",
                    fragment="",
                ))
                try:
                    markdown = requests.get(markdown_url, headers=UA, timeout=timeout)
                    markdown_text = (
                        html_to_text(markdown.text) if markdown.status_code == 200 else ""
                    )
                    if len(markdown_text) >= 200:
                        text = markdown_text
                        content_url = markdown_url
                except requests.RequestException:
                    pass

        return {
            "url": url,
            "ok": ok,
            "status": r.status_code,
            "text": text,
            "error": "",
            "content_url": content_url,
        }
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
# Perplexity Search API (official SDK, one paid provider only)
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _perplexity_client():
    key = config.PERPLEXITY_API_KEY
    if not key:
        raise RuntimeError("PERPLEXITY_API_KEY is not set")
    from perplexity import Perplexity

    return Perplexity(api_key=key, max_retries=3, timeout=30.0)


def _search_cache_path(queries: list[str], k: int):
    payload = json.dumps({"v": 1, "queries": queries, "k": k}, sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return config.CACHE_DIR / "perplexity_search" / f"{digest}.json"


def _cached_search(queries: list[str], k: int) -> list[dict] | None:
    path = _search_cache_path(queries, k)
    cached = config.load_json(path)
    if not cached:
        return None
    try:
        generated = dt.datetime.fromisoformat(cached["generated"])
    except (KeyError, TypeError, ValueError):
        return None
    max_age = dt.timedelta(days=float(os.getenv("PERPLEXITY_SEARCH_CACHE_DAYS", "7")))
    if dt.datetime.now(dt.timezone.utc) - generated > max_age:
        return None
    return cached.get("results") or []


def search_many(queries: list[str], k: int = 6) -> list[dict]:
    """Run related queries in one paid Search API request and cache the result."""
    clean_queries = list(dict.fromkeys(query.strip() for query in queries if query.strip()))
    if not clean_queries:
        return []
    cached = _cached_search(clean_queries, k)
    if cached is not None:
        return cached

    import usage_tracker

    request_cost = 0.005  # official Search API price: $5 / 1,000 requests
    usage_tracker.ensure_budget("perplexity", request_cost)
    response = _perplexity_client().search.create(
        query=clean_queries if len(clean_queries) > 1 else clean_queries[0],
        max_results=k,
        max_tokens=min(8_000, max(2_000, k * 1_000)),
        max_tokens_per_page=1_000,
    )
    results = []
    for item in response.results:
        results.append({
            "title": str(getattr(item, "title", "") or ""),
            "url": str(getattr(item, "url", "") or ""),
            "snippet": str(getattr(item, "snippet", "") or "")[:4_000],
            "date": str(getattr(item, "date", "") or ""),
            "last_updated": str(getattr(item, "last_updated", "") or ""),
            "search_provider": "perplexity",
        })
    config.save_json(_search_cache_path(clean_queries, k), {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "queries": clean_queries,
        "results": results,
    })
    usage_tracker.record("perplexity", "search", request_cost, {
        "query_count": len(clean_queries),
        "result_count": len(results),
    })
    return results


def search(query: str, k: int = 6) -> list[dict]:
    return search_many([query], k=k)


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


def _apex_host(url: str) -> str:
    host = urlparse(url).netloc.lower().split(":", 1)[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def is_first_party(url: str, hint_url: str = "", slug: str = "") -> bool:
    """Recognize vendor-owned pages, including known cross-domain doc properties."""
    if not url:
        return False
    seeded = {
        *MCP_OFFICIAL_SEEDS.get(slug, []),
        *ACCESS_OFFICIAL_SEEDS.get(slug, []),
    }
    if url in seeded:
        return True
    host = urlparse(url).netloc.lower().split(":", 1)[0]
    aliases = OFFICIAL_HOST_ALIASES.get(slug, set())
    if any(host == alias or host.endswith("." + alias) for alias in aliases):
        return True
    hint_apex = _apex_host(hint_url)
    return bool(hint_apex and _apex_host(url) == hint_apex)


def identity_matches(url: str, text: str, app: str, slug: str, hint_url: str = "") -> bool:
    """Require evidence to identify the actual app, not only a generic API topic."""
    if is_first_party(url, hint_url, slug):
        return True
    compact = re.sub(r"[^a-z0-9]", "", f"{url} {text}".lower())
    app_key = re.sub(r"[^a-z0-9]", "", app.lower())
    slug_key = re.sub(r"[^a-z0-9]", "", slug.lower())
    return bool((app_key and app_key in compact) or (slug_key and slug_key in compact))


def _candidate_score(result: dict, hint_url: str = "", app: str = "", slug: str = "") -> int:
    """Rank likely first-party, claim-bearing documentation pages."""
    url = result.get("url", "")
    title = result.get("title", "")
    snippet = result.get("snippet", "")
    text = f"{url} {title} {snippet}".lower()
    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    score = 0

    for token, weight in (
        ("auth", 9), ("oauth", 9), ("getting-started", 7), ("quickstart", 7),
        ("pricing", 9), ("plans", 8), ("subscription", 8),
        ("api", 6), ("developer", 5), ("reference", 4), ("access", 6),
        ("credential", 4), ("production", 7), ("sandbox", 4), ("trial", 5),
    ):
        if token in path or token in title.lower():
            score += weight

    hint_apex = _apex_host(hint_url)
    if hint_apex and (host == hint_apex or host.endswith("." + hint_apex)):
        score += 22
    app_key = re.sub(r"[^a-z0-9]", "", app.lower())
    if app_key and app_key in re.sub(r"[^a-z0-9]", "", text):
        score += 8
    for part in [p for p in slug.lower().split("-") if len(p) >= 4][:2]:
        if part in text:
            score += 4

    if any(prefix in host for prefix in ("docs.", "developer.", "developers.", "api.")):
        score += 8
    if any(bad in host for bad in (
        "medium.com", "dev.to", "stackshare.io", "zapier.com", "merge.dev",
        "rollout.com", "getknit.dev", "apideck.com", "stackoverflow.com",
    )):
        score -= 25
    if any(bad in text for bad in ("top 10", "alternatives", "integration guide by")):
        score -= 8
    return score


def _candidate_topic_score(result: dict, topic: str) -> int:
    """Score a search result for one evidence slot, independent of popularity."""
    text = " ".join(
        str(result.get(key, "")) for key in ("url", "title", "snippet")
    ).lower()
    patterns = {
        "auth": (
            r"authenticat", r"authoriz", r"oauth", r"api.?key", r"access token",
            r"credential", r"basic auth", r"personal access token",
        ),
        "access": (
            r"production", r"go.?live", r"pricing", r"plans?", r"paid",
            r"subscription", r"trial", r"sandbox", r"approval", r"app review",
            r"business verification", r"request access", r"contact sales",
        ),
        "api": (
            r"api reference", r"developer", r"endpoint", r"\brest\b", r"graphql",
            r"\bsdk\b", r"quickstart", r"getting started",
        ),
    }
    return sum(1 for expression in patterns[topic] if re.search(expression, text))


def _dedupe_search_results(groups: list[list[dict]]) -> list[dict]:
    by_url: dict[str, dict] = {}
    for group in groups:
        for result in group:
            url = result.get("url", "")
            if url.startswith("http") and url not in by_url:
                by_url[url] = result
    return list(by_url.values())


def _candidate_urls(hint_url: str, search_results: list[dict], app: str = "",
                    slug: str = "") -> list[str]:
    """Choose a balanced fetch set.

    At least half of the available slots are reserved for exact search results.
    Previously the hint plus six guessed doc roots consumed every slot, which
    meant the authentication page found by search was never fetched.
    """
    ranked = sorted(
        search_results,
        key=lambda result: _candidate_score(result, hint_url, app, slug),
        reverse=True,
    )
    searched = []
    for result in ranked:
        url = result.get("url", "")
        if url.startswith("http") and url not in searched:
            searched.append(url)

    # Reserve distinct search-result slots for authentication, production
    # entitlement, and API shape. A single high-ranking auth page cannot crowd
    # the pricing/plan evidence out of the six-page fetch budget.
    balanced_search: list[str] = []
    for topic in ("auth", "access", "api"):
        topic_results = sorted(
            ranked,
            key=lambda result: (
                _candidate_topic_score(result, topic),
                _candidate_score(result, hint_url, app, slug),
            ),
            reverse=True,
        )
        for result in topic_results:
            url = result.get("url", "")
            if (
                url.startswith("http")
                and url not in balanced_search
                and _candidate_topic_score(result, topic) > 0
            ):
                balanced_search.append(url)
                break
    for url in searched:
        if len(balanced_search) >= min(3, len(searched)):
            break
        if url not in balanced_search:
            balanced_search.append(url)

    urls: list[str] = []

    def add(url: str) -> None:
        if url and url.startswith("http") and url not in urls and len(urls) < MAX_FETCH:
            urls.append(url)

    add(hint_url)
    seeds = ACCESS_OFFICIAL_SEEDS.get(slug, [])
    if seeds:
        add(seeds[0])
    for url in balanced_search:
        add(url)
    for url in seeds[1:]:
        add(url)
    for url in _derived_doc_urls(hint_url):
        add(url)
    for url in searched:
        add(url)
    return urls


def auth_evidence_signals(text: str, url: str = "") -> list[str]:
    """Extract conservative credential labels explicitly named by a page.

    These signals validate model output; they do not choose the final auth set.
    In particular, an OAuth client ID is not an API key, and a key-pair is
    surfaced as a Service Account rather than a generic token.
    """
    haystack = f"{url} {text}".lower()
    signals: list[str] = []
    patterns = {
        "OAuth2": (
            r"oauth\s*(?:2(?:\.0)?|v2)\b", r"authorization.?code (?:flow|grant)",
            r"client.?credentials (?:flow|grant)", r"\bpkce\b",
            r"facebook login for business", r"login with (?:facebook|google|microsoft)",
        ),
        "API Key": (
            r"\bapi[ _-]?keys?\b", r"\bx-api-keys?\b", r"\bapi tokens?\b",
            r"\bdeveloper tokens?\b", r"\bapplication keys?\b",
            r"\bapi (?:and|or) application keys?\b",
            r"\bapis? (?:use|uses|require|requires).{0,60}client id.{0,30}(?:and|with).{0,30}(?:client )?secret credentials?",
        ),
        "Bearer Token": (
            r"\bbearer[ -](?:api )?tokens?\b", r"authorization\s*:\s*bearer",
            r"private integration tokens?", r"static (?:access )?tokens?",
            r"\bbearer credentials?\b", r"\bjwt bearer credentials?\b",
            r"\bsystem[ -]?user access tokens?\b",
            r"\b(?:customer|admin|integration) tokens?\b",
            r"independently issued.{0,50}access tokens?",
            r"(?:through|via|as) bearer\b",
        ),
        "Basic Auth": (
            r"\bbasic auth(?:entication)?\b", r"\bhttp basic\b",
        ),
        "Personal Access Token": (
            r"\bpersonal access tokens?\b", r"\bprogrammatic access tokens?\b",
            r"\bpersonal api tokens?\b", r"\bpersonal tokens?\b",
            r"\baccount access tokens?\b", r"\buser pats?\b",
        ),
        "Service Account": (
            r"\bservice[ -]?accounts?\b", r"\bkey[ -]?pairs?(?: authentication)?\b",
            r"\bprivate key authentication\b", r"\bworkload identity\b",
            r"\bjwt authentication\b",
        ),
        "Bot Token": (r"\bbot tokens?\b",),
        "Other Token": (
            r"oauth\s*1(?:\.0a?)?\b", r"internal[ -]?integration (?:authentication )?tokens?",
            r"\bworkspace access tokens?\b",
        ),
    }
    for label, expressions in patterns.items():
        if any(re.search(expression, haystack) for expression in expressions):
            signals.append(label)

    # Vendor pages often write simply "OAuth" when only OAuth 2 is supported.
    if "OAuth2" not in signals and re.search(r"\boauth\b", haystack):
        if "Other Token" not in signals:
            signals.append("OAuth2")
    negative_api_key = re.search(
        r"(?:not (?:an? )?(?:independent )?|does not (?:use|accept|support) |"
        r"not (?:accepted|supported|used) as (?:an? )?)api[ _-]?keys?|"
        r"api[ _-]?keys?.{0,50}(?:is |are )?not (?:accepted|supported|used)",
        haystack,
    )
    positive_api_key = re.search(
        r"(?:uses?|supports?|accepts?|requires?|generate|create).{0,50}api[ _-]?keys?",
        haystack,
    )
    if "API Key" in signals and negative_api_key and not positive_api_key:
        signals.remove("API Key")
    return signals


def access_evidence_signals(text: str, url: str = "") -> list[str]:
    """Classify whether a page can resolve the production-access decision."""
    haystack = re.sub(r"\s+", " ", f"{url} {text}".lower())
    patterns = {
        "manual_gate": (
            r"request (?:production )?access", r"apply for (?:api )?access",
            r"(?:production|api|app|access|credentials?|developer account).{0,100}(?:requires?|needs?|must|subject to|undergo).{0,60}(?:approval|review|business verification)",
            r"(?:approval|review|business verification).{0,60}(?:is )?(?:required|needed).{0,60}(?:production|api access|app|credentials?)",
            r"production apps?.{0,80}app review",
            r"app (?:must|needs? to) be reviewed",
            r"business (?:must|needs? to) be verified",
            r"(?:app review|business verification|partner approval) (?:is )?(?:required|needed)",
            r"contact sales", r"book a call", r"talk to (?:our )?(?:sales|team)",
            r"contact (?:your )?(?:account manager|customer success manager|admin)",
        ),
        "commercial_gate": (
            r"existing (?:paid )?customer", r"paid (?:plan|account|subscription|edition|tier)",
            r"paid.{0,80}(?:plan|account|subscription|edition|tier)",
            r"paid production (?:plans?|accounts?|editions?|tiers?)",
            r"existing.{0,30}(?:licensed|customer).{0,30}(?:account|environment|workspace|subscription)",
            r"customer[ -]?gated", r"licensed environment",
            r"consumption[ -]?based pricing", r"pre[ -]?paid capacity",
            r"subscription (?:is )?(?:required|needed)",
            r"requires?.{0,60}(?:paid plan|paid account|customer subscription|paid subscription)",
            r"available only (?:to|for) .{0,50}customers",
            r"included only (?:in|with|on) .{0,50}(?:plan|tier)",
            r"(?:api access|api calls?).{0,80}(?:paid|starter|pro|professional|business|enterprise) (?:plan|tier)",
            r"(?:paid|starter|pro|professional|business|enterprise) (?:plan|tier).{0,80}(?:api access|api calls?)",
            r"(?:plans?|tiers?|editions?) (?:are )?paid",
            r"after (?:the )?(?:free |temporary )?trial", r"trial (?:ends|expires)",
            r"upgrade (?:your )?(?:plan|account|subscription)",
        ),
        "nonproduction_only": (
            r"\bsandbox\b", r"\btest mode\b", r"\btest credentials?\b",
            r"\bfree trial\b", r"\btrial account\b", r"developer (?:edition|environment)",
        ),
        "credential_enablement": (
            r"(?:create|generate|obtain|get|issue).{0,50}(?:api key|api token|access token|credentials?)",
            r"(?:api key|api token|access token|credentials?).{0,50}(?:dashboard|settings|console)",
            r"sign[ -]?up.{0,80}(?:api|developer|credentials?|token)",
        ),
        "free_account": (
            r"\bfree (?:account|plan|tier|edition)\b",
            r"(?:account|plan|tier|edition) (?:is |can be )?free\b",
            r"\bfree\b.{0,30}(?:\$\s?0|0\s*/\s*month|forever)",
        ),
        "free_api_account": (
            r"(?:free account|free plan|free tier|free edition).{0,60}(?:has|includes?|offers?|provides?|allows?|supports?|with).{0,60}api (?:access|credits?|requests?|calls?)",
            r"api (?:access|credits?|requests?|calls?).{0,60}(?:included|available|enabled).{0,60}(?:free account|free plan|free tier|free edition)",
            r"api.{0,60}(?:free edition|free plan|free tier).{0,50}[1-9][\d,]* credits?",
            r"(?:free edition|free plan|free tier).{0,50}[1-9][\d,]* credits?",
        ),
        "self_serve_production": (
            r"(?:create|generate|obtain|get).{0,80}(?:production|live).{0,50}(?:api key|token|credentials?)",
            r"(?:production|live).{0,80}(?:api key|token|credentials?).{0,60}(?:dashboard|settings|immediately|without approval)",
            r"(?:free plan|free tier|free edition)[^.;]{0,60}(?:has|includes?|offers?|provides?|allows?|supports?)[^.;]{0,60}(?:production|live) api (?:access|credits?|requests?)",
            r"(?:production|live) api (?:access|credits?|requests?)[^.;]{0,60}(?:included|available|enabled)[^.;]{0,60}(?:free plan|free tier|free edition)",
            r"(?:free account|free plan|free tier).{0,100}(?:run|use|host).{0,60}production",
            r"(?:free account|free plan|free tier).{0,100}production (?:environment|projects?|workloads?)",
            r"(?:account|plan|tier) (?:is |can be )?free.{0,100}production (?:environment|projects?|workloads?)",
            r"free production (?:environment|projects?|workloads?)",
            r"(?:create|generate|retrieve|obtain).{0,80}(?:app|token|key|credentials?).{0,80}without (?:manual |vendor )?(?:approval|review)",
            r"(?:api|token|key|credentials?).{0,120}available without (?:manual |vendor )?(?:approval|review)",
            r"custom distribution.{0,80}without (?:app store |vendor )?(?:approval|review)",
            r"(?:app|token|key|credentials?).{0,60}(?:is |are |can be )?self[ -]?serve",
            r"self[ -]?created (?:app|token|key|credentials?)|(?:app|token|key|credentials?).{0,20}self[ -]?created",
            r"production.{0,80}without (?:manual )?(?:approval|review)",
        ),
        "hosted_connection": (
            r"connect (?:your )?(?:account|workspace|organization)",
            r"click (?:connect|authorize)", r"sign in.{0,60}(?:authorize|connect)",
            r"oauth.{0,80}(?:mcp|connect)", r"mcp.{0,80}oauth",
        ),
        "non_hosted_surface": (
            r"open[ -]?source (?:command[ -]?line|cli|library)",
            r"(?:local|command[ -]?line) tool.{0,80}(?:not|no) (?:a )?hosted api",
            r"no (?:public|hosted) api", r"does not (?:provide|offer|have) (?:a )?(?:public|hosted) api",
        ),
    }
    signals = []
    for label, expressions in patterns.items():
        if any(re.search(expression, haystack) for expression in expressions):
            signals.append(label)
    if "free_api_account" in signals and re.search(
        r"(?:free account|free plan|free tier|free edition).{0,80}(?:zero|no|without|not included).{0,40}api (?:access|credits?|requests?|calls?)",
        haystack,
    ):
        signals.remove("free_api_account")
    paid_pricing = re.search(
        r"\$\s?[1-9][\d,.]*.{0,60}(?:/\s?month|per month|per seat,? per month|usd/\s?month)",
        haystack,
    )
    if (
        paid_pricing
        and "nonproduction_only" in signals
        and "free_api_account" not in signals
        and "commercial_gate" not in signals
    ):
        signals.append("commercial_gate")
    if (
        paid_pricing
        and re.search(r"/pricing(?:\b|/)", haystack)
        and "free_account" not in signals
        and "free_api_account" not in signals
        and "commercial_gate" not in signals
    ):
        signals.append("commercial_gate")
    return signals


def access_decision_ready(items: list[dict]) -> bool:
    """Return whether fetched evidence can decide production access honestly."""
    for item in items:
        if not item.get("ok"):
            continue
        signals = set(
            item.get("access_signals")
            or access_evidence_signals(item.get("text", ""), item.get("url", ""))
        )
        if signals & {
            "manual_gate", "commercial_gate", "self_serve_production",
            "free_api_account", "non_hosted_surface",
        }:
            return True
        if "hosted_connection" in signals and "mcp" in item.get("support_tags", []):
            return True
    return False


def support_tags(text: str, url: str = "") -> list[str]:
    """Identify which claim families a fetched page can plausibly support."""
    haystack = f"{url} {text}".lower()
    tags = []
    patterns = {
        "api": (r"\bapi\b", r"\brest\b", r"graphql", r"endpoint", r"\bsdk\b"),
        "auth": (r"oauth", r"authenticat", r"authoriz", r"api.?key", r"token", r"credential"),
        "access": (
            r"production", r"sandbox", r"request access", r"approval", r"app review",
            r"business verification", r"paid plan", r"existing customer", r"partner",
            r"self.?serve", r"sign.?up", r"free trial", r"free (?:account|plan|tier|edition)",
            r"developer account",
            r"account settings", r"create (an )?api key", r"generate (an )?api key",
            r"generate (an )?(access )?token",
            r"activate.{0,30}api", r"api (mode|access)", r"open your dashboard",
            r"book a call", r"contact sales", r"talk to our team", r"account manager",
            r"customer success manager", r"contact your.{0,40}admin",
            r"enable api access", r"user group permissions", r"api capabilities",
            r"standalone contract", r"contract agreement",
        ),
        "mcp": (r"\bmcp\b", r"model context protocol"),
        "non_hosted": (
            r"open[ -]?source (?:command[ -]?line|cli|library)",
            r"no (?:public|hosted) api", r"not a hosted api",
        ),
    }
    for tag, expressions in patterns.items():
        if any(re.search(expression, haystack) for expression in expressions):
            tags.append(tag)
    return tags


def _source_kind(url: str, hint_url: str, search_urls: set[str]) -> str:
    if url in search_urls:
        return "search_result"
    if url == hint_url:
        return "hint"
    return "derived_guess"


def _annotate_fetch(item: dict, hint_url: str, search_lookup: dict[str, dict],
                    app: str, slug: str) -> dict:
    result = search_lookup.get(item["url"], {"url": item["url"]})
    text = item.get("text", "")
    return {
        **item,
        "source_kind": _source_kind(item["url"], hint_url, set(search_lookup)),
        "relevance_score": _candidate_score(result, hint_url, app, slug),
        "support_tags": support_tags(text, item["url"]) if item.get("ok") else [],
        "auth_signals": auth_evidence_signals(text, item["url"]) if item.get("ok") else [],
        "access_signals": access_evidence_signals(text, item["url"]) if item.get("ok") else [],
    }


def _browser_verified_evidence(slug: str) -> list[dict]:
    """Load browser-captured official evidence for pages direct HTTP could not read."""
    payload = config.load_json(config.BROWSER_EVIDENCE_PATH, default={}) or {}
    items = []
    for item in payload.get("entries", []):
        if item.get("slug") != slug or not item.get("url") or not item.get("text"):
            continue
        items.append({
            "url": item["url"],
            "ok": True,
            "status": 200,
            "text": item["text"],
            "error": "",
            "source_kind": "browser_verified_summary",
            "relevance_score": 100,
            "support_tags": support_tags(item["text"], item["url"]),
            "auth_signals": auth_evidence_signals(item["text"], item["url"]),
            "access_signals": access_evidence_signals(item["text"], item["url"]),
            "browser_capture": {
                "captured_at": item.get("captured_at", ""),
                "method": item.get("method", ""),
                "analyst_summary": bool(item.get("analyst_summary")),
            },
        })
    return items


def _mcp_score(url: str, title: str, app: str, slug: str) -> int:
    text = f"{title} {url}".lower()
    host = urlparse(url).netloc.lower()
    compact_app = re.sub(r"[^a-z0-9]", "", app.lower())
    slug_parts = [p for p in slug.lower().replace("_", "-").split("-") if p]
    score = 0
    if "mcp" in text or "model-context-protocol" in text:
        score += 8
    if "official" in text:
        score += 4
    if compact_app and compact_app in re.sub(r"[^a-z0-9]", "", text):
        score += 8
    for part in slug_parts[:2]:
        if len(part) >= 4 and part in text:
            score += 5
    vendorish = ("docs." in host or "developer" in host or "support." in host)
    if vendorish and any(part in host for part in slug_parts[:2]):
        score += 18
    if host == "github.com" and slug_parts and f"github.com/{slug_parts[0]}/" in url.lower():
        score += 18
    generic_hosts = (
        "modelcontextprotocol.io",
        "modelcontextprotocol.info",
        "mcpservers.org",
        "mcpserver.dev",
        "remote-mcp.com",
        "findmcpservers.com",
        "deepwiki.com",
        "a2a-mcp.org",
        "registry.modelcontextprotocol.io",
    )
    if any(g in host for g in generic_hosts):
        score -= 20
    return score


def gather_mcp_evidence(app: str, slug: str = "", k: int = 8, max_fetch: int = 4) -> dict:
    """Dedicated probe for the `existing_mcp` field.

    API-reference pages almost never mention MCP, so deriving existing_mcp from
    the main evidence pass systematically produced false "None"s — the first
    batch marked many vendor-owned MCP servers as "None" because API reference
    docs rarely mention MCP. One extra search + a few high-confidence official
    seeds per app is cheap and fixes the field at the source.
    """
    q = f"{app} official MCP server Model Context Protocol"
    results = search(q, k=k)
    ranked = sorted(
        results,
        key=lambda r: _mcp_score(r.get("url", ""), r.get("title", ""), app, slug),
        reverse=True,
    )
    candidates = list(MCP_OFFICIAL_SEEDS.get(slug, []))
    for r in ranked:
        u = r.get("url", "")
        if u.startswith("http") and u not in candidates:
            candidates.append(u)

    fetched = []
    for u in candidates:
        if len(fetched) >= max_fetch:
            continue
        f = fetch(u)
        if f["ok"]:
            text = f.get("text", "")
            fetched.append({
                **f,
                "support_tags": support_tags(text, u),
                "auth_signals": auth_evidence_signals(text, u),
                "access_signals": access_evidence_signals(text, u),
            })
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
    queries = [
        query or f"{app} official API authentication developer documentation",
        f"{app} API production access approval credentials official documentation",
        f"{app} official pricing API access free plan trial production plan",
    ]
    results = _dedupe_search_results([search_many(queries, k=8)])
    candidates = _candidate_urls(hint_url, results, app=app, slug=slug)
    search_lookup = {result["url"]: result for result in results if result.get("url")}

    fetched = []
    for u in candidates:
        fetched.append(_annotate_fetch(fetch(u), hint_url, search_lookup, app, slug))
        time.sleep(0.2)

    for browser_item in _browser_verified_evidence(slug):
        fetched = [item for item in fetched if item.get("url") != browser_item["url"]]
        fetched.append(browser_item)

    ok_urls = [f["url"] for f in fetched if f["ok"]]
    mcp = gather_mcp_evidence(app, slug)
    evidence_items = [*fetched, *mcp.get("fetched", [])]
    supported_topics = sorted({
        tag
        for item in evidence_items
        if item.get("ok")
        for tag in item.get("support_tags", [])
    })
    supported_auth_signals = sorted({
        signal
        for item in evidence_items
        if item.get("ok")
        for signal in (
            item.get("auth_signals")
            or auth_evidence_signals(item.get("text", ""), item.get("url", ""))
        )
    })
    supported_access_signals = sorted({
        signal
        for item in evidence_items
        if item.get("ok")
        for signal in (
            item.get("access_signals")
            or access_evidence_signals(item.get("text", ""), item.get("url", ""))
        )
    })
    decision_ready = access_decision_ready(evidence_items)
    topics = set(supported_topics)
    usable_hosted_surface = bool(
        "auth" in topics and ({"api", "mcp"} & topics)
    )
    explicit_non_hosted = "non_hosted" in topics
    adequate = bool(explicit_non_hosted or (usable_hosted_surface and decision_ready))
    degraded = not adequate
    if degraded and log:
        _log_failure(
            slug,
            "insufficient claim-bearing evidence; "
            f"queries={queries!r}; topics={supported_topics}; "
            f"access_signals={supported_access_signals}; candidates={candidates}",
            phase="evidence",
        )

    return {
        "app": app, "slug": slug, "category": category, "query": queries[0],
        "queries": queries,
        "search_results": results,
        "fetched": fetched,
        # Flag D whitelist for evidence_urls (MCP-probe pages are citable too)
        "fetched_urls": ok_urls + [u for u in mcp["fetched_urls"] if u not in ok_urls],
        "supported_topics": supported_topics,
        "supported_auth_signals": supported_auth_signals,
        "supported_access_signals": supported_access_signals,
        "access_decision_ready": decision_ready,
        "evidence_quality": "adequate" if adequate else "degraded",
        "degraded": degraded,
        "mcp": mcp,
    }


_failure_lock = threading.Lock()


def _log_failure(slug: str, msg: str, phase: str = "research") -> None:
    """Append audit history and update the current unresolved failure state."""
    config.ensure_dirs()
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    key = f"{slug}:{phase}"
    with _failure_lock:
        with open(config.FAILURES_PATH, "a", encoding="utf-8") as fh:
            fh.write(f"{timestamp}\tFAILED\t{phase}\t{slug}\t{msg}\n")
        state = config.load_json(config.FAILURE_STATE_PATH, default={}) or {}
        state[key] = {
            "slug": slug,
            "phase": phase,
            "message": msg,
            "updated": timestamp,
        }
        config.save_json(config.FAILURE_STATE_PATH, state)


def resolve_failure(slug: str, phase: str) -> None:
    """Clear one recovered failure without erasing its event-history entry."""
    key = f"{slug}:{phase}"
    with _failure_lock:
        state = config.load_json(config.FAILURE_STATE_PATH, default={}) or {}
        if key not in state:
            return
        state.pop(key)
        config.save_json(config.FAILURE_STATE_PATH, state)
        timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
        with open(config.FAILURES_PATH, "a", encoding="utf-8") as fh:
            fh.write(f"{timestamp}\tRESOLVED\t{phase}\t{slug}\n")
