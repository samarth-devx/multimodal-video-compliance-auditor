from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from backend.src.prompts import build_system_prompt, build_user_prompt
from backend.src.schemas import AuditVerdict, Rule, Severity, Violation

# Policy decision lives in code, not in the prompt.
BLOCKING_SEVERITIES = {Severity.CRITICAL, Severity.MAJOR}


def decide_status(violations: list[Violation]) -> str:
    return "FAIL" if any(v.severity in BLOCKING_SEVERITIES for v in violations) else "PASS"


class ComplianceJudge:
    def __init__(self, llm: BaseChatModel):
        self._llm = llm.with_structured_output(AuditVerdict, method="function_calling")

    def judge(self, transcript: str, ocr_text: list[str], metadata: dict, rules: list[Rule]) -> AuditVerdict:
        return self._llm.invoke([
            SystemMessage(content=build_system_prompt(rules)),
            HumanMessage(content=build_user_prompt(transcript, ocr_text, metadata)),
        ])