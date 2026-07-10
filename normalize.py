"""Canonical auth labels and comparison helpers.

The dataset records credential *schemes*, not HTTP header syntax. For example,
an OAuth access token is recorded as ``OAuth2`` rather than also being counted
as ``Bearer Token``. ``Bearer Token`` is reserved for a static vendor-issued
token where no OAuth grant is involved.
"""
from __future__ import annotations

import re

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

_CANONICAL_BY_KEY = {
    re.sub(r"[^a-z0-9]", "", label.lower()): label for label in CANONICAL
}


def normalize_auth(label: str, *, strict: bool = False) -> str | None:
    """Map one auth label to the controlled vocabulary.

    ``strict=True`` is used at model boundaries. It accepts common aliases but
    raises for an unknown non-empty value, preventing arbitrary model text from
    being silently relabeled as ``Other Token``.
    """
    if not label or not str(label).strip():
        return None
    raw = str(label).strip()
    low = raw.lower()
    compact = re.sub(r"[^a-z0-9]", "", low)

    if compact in _CANONICAL_BY_KEY:
        return _CANONICAL_BY_KEY[compact]
    if low in {"none", "n/a", "not applicable", "no authentication"}:
        return "None / Not Applicable"

    # Grant flows. A client-credentials grant is OAuth2; the resulting bearer
    # header is transport detail and must not become a second auth method.
    if (
        "oauth" in low
        or low.startswith("lwa")
        or "login with amazon" in low
        or "sign in with" in low
        or "ims access" in low
        or "token exchange" in low
        or ("client" in low and "credential" in low)
    ):
        return "OAuth2"
    if "personal access" in low or low in {"pat", "pats"}:
        return "Personal Access Token"
    if "bot token" in low or low == "bot":
        return "Bot Token"
    if (
        "service account" in low
        or "key-pair" in low
        or "keypair" in low
        or "key pair" in low
        or "workload identity" in low
    ):
        return "Service Account"
    if "basic auth" in low or "http basic" in low or "digest auth" in low:
        return "Basic Auth"
    if "api key" in low or "api-key" in low or "apikey" in low or "x-api-key" in low:
        return "API Key"
    if "api token" in low or low in {"developer token", "application key"}:
        return "API Key"
    if "bearer" in low or low in {
        "access token",
        "static access token",
        "vendor access token",
        "jwt",
        "jwt token",
    }:
        return "Bearer Token"

    if strict:
        raise ValueError(
            f"unknown auth label {raw!r}; expected one of: {', '.join(CANONICAL)}"
        )
    return "Other Token"


def normalize_auth_list(labels, *, strict: bool = False) -> list[str]:
    """Normalize and de-duplicate auth labels while preserving order.

    The not-applicable sentinel is dropped when a real method is present.
    """
    if isinstance(labels, str):
        labels = [labels]
    out: list[str] = []
    for raw in labels or []:
        canonical = normalize_auth(raw, strict=strict)
        if canonical and canonical not in out:
            out.append(canonical)
    real = [item for item in out if item != "None / Not Applicable"]
    return real if real else out


def auth_set(labels, *, strict: bool = False) -> set[str]:
    """Return the canonical set used by all verification comparisons."""
    return set(normalize_auth_list(labels, strict=strict))


def auth_sets_equal(left, right, *, strict: bool = False) -> bool:
    """Exact semantic equality after canonical label normalization."""
    return auth_set(left, strict=strict) == auth_set(right, strict=strict)


def auth_sets_overlap(left, right, *, strict: bool = False) -> bool:
    """Diagnostic overlap only; never use this as the accuracy score."""
    a = auth_set(left, strict=strict)
    b = auth_set(right, strict=strict)
    return (not a and not b) or bool(a & b)


if __name__ == "__main__":
    samples = [
        "OAuth 2.0",
        "API key",
        "API token",
        "Bearer token",
        "Personal Access Tokens (PATs)",
        "Service Account",
        "Key-pair authentication",
        "Bot token",
        "LWA (Login with Amazon)",
        "Basic Auth",
        "None / Not Applicable",
    ]
    for sample in samples:
        print(f"{sample!r:40} -> {normalize_auth(sample, strict=True)}")
