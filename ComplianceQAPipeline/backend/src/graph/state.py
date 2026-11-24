import operator
from typing import Annotated, TypedDict

from backend.src.schemas import Rule, Violation


class AuditState(TypedDict, total=False):
    # input
    video_url: str
    video_id: str
    # stage 1: evidence
    transcript: str
    ocr_text: list[str]
    video_metadata: dict
    # stage 2: rules
    rules: list[Rule]
    # stage 3: verdict
    violations: list[Violation]
    status: str    # PASS | FAIL | ERROR
    report: str
    errors: Annotated[list[str], operator.add]