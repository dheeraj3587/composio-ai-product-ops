"""Locked 19-field schema for an app's API-integration-readiness record.

Do NOT add/remove/rename fields without explicit sign-off. `extra="forbid"`
keeps the contract locked: any stray field raises a validation error.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --------------------------------------------------------------------------- #
# Enums (the controlled vocabularies)
# --------------------------------------------------------------------------- #
class Category(str, Enum):
    CRM = "CRM"
    SUPPORT = "Support"
    COMMS = "Comms"
    ADS = "Ads/Marketing"
    COMMERCE = "Commerce"
    RESEARCH = "Research/Scraping"
    DEVINFRA = "DevInfra"
    PRODUCTIVITY = "Productivity/PM"
    FINTECH = "Fintech"
    AI = "AI/Meeting-tools"


class AccessKind(str, Enum):
    SELF_SERVE = "Self-Serve"
    GATED = "Gated"


class ApiType(str, Enum):
    REST = "REST"
    GRAPHQL = "GraphQL"
    SDK = "SDK"
    SOAP = "SOAP"
    MCP_ONLY = "MCP-only"
    NONE = "None"


class ApiBreadth(str, Enum):
    NARROW = "Narrow"
    MODERATE = "Moderate"
    BROAD = "Broad"


class ExistingMcp(str, Enum):
    OFFICIAL = "Official"
    COMMUNITY = "Community"
    NONE = "None"


class YesNo(str, Enum):
    YES = "Yes"
    NO = "No"


class Buildability(str, Enum):
    EASY = "Easy"
    MODERATE = "Moderate"
    HARD = "Hard"
    BLOCKED = "Blocked"


class NextAction(str, Enum):
    BUILD_NOW = "Build Now"
    NEEDS_OUTREACH = "Needs Outreach"
    PARTNER_GATED = "Partner-Gated"
    BLOCKED = "Blocked"


class VerificationStatus(str, Enum):
    AUTO = "Auto"
    HAND_CHECKED = "Hand-Checked"


# --------------------------------------------------------------------------- #
# access_model = "Self-Serve/Gated + note"  (one field, structured)
# --------------------------------------------------------------------------- #
class AccessModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: AccessKind
    note: str = ""


# --------------------------------------------------------------------------- #
# The locked record
# --------------------------------------------------------------------------- #
class AppRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    app: str
    category: Category
    one_liner: str = Field(..., max_length=120)
    auth_methods: list[str] = Field(default_factory=list)
    access_model: AccessModel
    api_type: ApiType
    api_breadth: ApiBreadth
    existing_mcp: ExistingMcp
    composio_toolkit: YesNo
    buildability: Buildability
    main_blocker: str = ""
    recommended_next_action: NextAction
    evidence_urls: list[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    verification_status: VerificationStatus = VerificationStatus.AUTO
    slug: str
    primary_docs_url: str = ""
    rate_limit_note: str = ""
    last_verified: date

    @field_validator("evidence_urls")
    @classmethod
    def _urls_must_be_http(cls, v: list[str]) -> list[str]:
        for u in v:
            if not (isinstance(u, str) and u.startswith(("http://", "https://"))):
                raise ValueError(
                    f"evidence_urls must be absolute http(s) URLs, got: {u!r}"
                )
        return v

    @field_validator("one_liner")
    @classmethod
    def _one_liner_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("one_liner must not be empty")
        return v


def validate_record(data: dict) -> AppRecord:
    """Validate a dict against the locked schema (raises pydantic.ValidationError)."""
    return AppRecord.model_validate(data)
