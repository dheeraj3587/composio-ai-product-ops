"""Canonical auth-method labels + a normalizer.

Raw LLM/browser output uses many spellings (OAuth / OAuth 2.0 / OAuth2.0,
API key / API Key / API token, Bearer token, etc.). We map everything to a small
canonical set so pattern stats are meaningful and the report reads cleanly.
"""
from __future__ import annotations

CANONICAL = [
    "OAuth2",
    "API Key",
    "Bearer Token",
    "Basic Auth",
    "Personal Access Token",
    "Service Account",
    "Bot Token",
    "Other Token",
    "None / Not Applicable",
]


def normalize_auth(label: str) -> str | None:
    """Map one raw auth label to a canonical label (or None to drop empties)."""
    if not label or not str(label).strip():
        return None
    low = str(label).strip().lower()

    if low in ("none / not applicable", "none", "n/a", "not applicable"):
        return "None / Not Applicable"
    # OAuth family (incl. LWA, Adobe IMS, Slack sign-in, client-credentials grant)
    if ("oauth" in low or low.startswith("lwa") or "login with amazon" in low
            or "sign in with" in low or "ims access" in low or "token exchange" in low
            or ("client" in low and "credential" in low)):
        return "OAuth2"
    if "personal access" in low or low in ("pat", "pats"):
        return "Personal Access Token"
    if "bot" in low:
        return "Bot Token"
    if ("service account" in low or "key-pair" in low or "keypair" in low
            or "key pair" in low or "workload identity" in low):
        return "Service Account"
    if "basic" in low or "digest" in low or "username" in low or "user/pass" in low:
        return "Basic Auth"
    if "bearer" in low or "jwt" in low:
        return "Bearer Token"
    if ("api key" in low or "api-key" in low or "apikey" in low or "x-api-key" in low
            or "api credential" in low or "application key" in low
            or ("api" in low and "key" in low)):
        return "API Key"
    if "api token" in low or ("api" in low and "token" in low):
        return "API Key"
    if "access token" in low or low in ("token", "token-based") or "accesstoken" in low:
        return "Bearer Token"
    # everything else that is clearly a token/credential -> Other Token
    return "Other Token"


def normalize_auth_list(labels) -> list[str]:
    """Normalize + de-duplicate a list of auth labels, preserving order.

    Drops the sentinel 'None / Not Applicable' if any real method is present."""
    out: list[str] = []
    for raw in labels or []:
        c = normalize_auth(raw)
        if c and c not in out:
            out.append(c)
    real = [c for c in out if c != "None / Not Applicable"]
    return real if real else out


if __name__ == "__main__":
    samples = ["OAuth", "OAuth 2.0", "OAuth2.0", "API key", "API Keys", "API token",
               "Bearer token", "Personal Access Tokens (PATs)", "Service Account",
               "Key-pair authentication", "Bot tokens", "LWA (Login with Amazon)",
               "Basic Auth (Email + API Token)", "accessToken", "session tokens",
               "None / Not Applicable"]
    for s in samples:
        print(f"{s!r:40} -> {normalize_auth(s)}")
    print("list:", normalize_auth_list(["OAuth", "OAuth 2.0", "API key", "API Key"]))
