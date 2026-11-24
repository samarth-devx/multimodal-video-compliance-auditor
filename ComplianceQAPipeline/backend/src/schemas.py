from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    CRITICAL = "CRITICAL"   # legal risk
    MAJOR = "MAJOR"         # serious issue
    MODERATE = "MODERATE"   # should fix
    WARNING = "WARNING"     # minor


class Category(str, Enum):
    FTC_DISCLOSURE = "FTC Disclosure"
    CLAIM_VALIDATION = "Claim Validation"
    ENDORSEMENT = "Endorsement Disclosure"
    AD_SPECS = "Ad Specs"
    MISLEADING = "Misleading Content"
    PROFESSIONAL = "Professional Misrepresentation"
    TRADEMARK = "Trademark"


class Violation(BaseModel):
    category: Category
    severity: Severity
    description: str = Field(description="What is wrong and which rule it breaks.")
    evidence: str = Field(description="Exact quote from the transcript or on-screen text.")
    timestamp: Optional[str] = Field(
        default=None, description="Timestamp such as 0:00:12, copied from the evidence line."
    )


class AuditVerdict(BaseModel):
    """What the LLM returns. PASS/FAIL is decided in code, not by the model."""
    violations: list[Violation] = Field(default_factory=list)
    summary: str = Field(description="Concise professional summary with recommended actions.")


# ---- internal data passed between stages ----

@dataclass(frozen=True)
class Rule:
    text: str
    source: str   # which guideline PDF the chunk came from


@dataclass(frozen=True)
class Evidence:
    transcript: str                      # lines like "[0:00:03] text"
    ocr_text: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


# ---- API contract (field names unchanged, so the frontend keeps working) ----

class AuditRequest(BaseModel):
    video_url: str

    @field_validator("video_url")
    @classmethod
    def must_be_youtube(cls, v: str) -> str:
        host = (urlparse(v).hostname or "").removeprefix("www.")
        if host not in {"youtube.com", "m.youtube.com", "youtu.be"}:
            raise ValueError("Please provide a valid YouTube URL.")
        return v


class AuditResponse(BaseModel):
    session_id: str
    video_id: str
    status: str   # PASS | FAIL | ERROR
    final_report: str
    compliance_results: list[Violation]