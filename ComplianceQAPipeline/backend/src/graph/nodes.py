import logging
from functools import wraps

from backend.src.graph.state import AuditState
from backend.src.prompts import CATEGORY_GUIDE
from backend.src.services.judge import ComplianceJudge, decide_status
from backend.src.services.retriever import RuleRetriever
from backend.src.services.video_downloader import downloaded_video
from backend.src.services.video_indexer import VideoIndexerClient

logger = logging.getLogger("mvca.nodes")

RULES_PER_CATEGORY = 2
TRANSCRIPT_EXCERPT_CHARS = 500


def safe_node(fn):
    """Turn any exception into an ERROR state so the graph can stop cleanly."""
    @wraps(fn)
    def wrapper(self, state: AuditState):
        try:
            return fn(self, state)
        except Exception as exc:
            logger.exception("Node '%s' failed", fn.__name__)
            return {"errors": [f"{fn.__name__}: {exc}"], "status": "ERROR"}
    return wrapper


class AuditNodes:
    """The three pipeline stages. Dependencies are injected, so each stage is testable."""

    def __init__(self, indexer: VideoIndexerClient, retriever: RuleRetriever, judge: ComplianceJudge):
        self._indexer = indexer
        self._retriever = retriever
        self._judge = judge

    @safe_node
    def extract_evidence(self, state: AuditState):
        """Stage 1: video -> timestamped transcript + on-screen text."""
        with downloaded_video(state["video_url"]) as path:
            evidence = self._indexer.analyze(path, name=state["video_id"])
        if not (evidence.transcript or evidence.ocr_text):
            raise RuntimeError("No speech or on-screen text could be extracted from this video.")
        return {
            "transcript": evidence.transcript,
            "ocr_text": evidence.ocr_text,
            "video_metadata": evidence.metadata,
        }

    @safe_node
    def retrieve_rules(self, state: AuditState):
        """Stage 2: one targeted query per compliance category, deduplicated."""
        excerpt = state.get("transcript", "")[:TRANSCRIPT_EXCERPT_CHARS]
        unique = {}
        for question in CATEGORY_GUIDE.values():
            for rule in self._retriever.search(f"{question} Ad content: {excerpt}", k=RULES_PER_CATEGORY):
                unique.setdefault(rule.text, rule)
        logger.info("Retrieved %d unique rules", len(unique))
        return {"rules": list(unique.values())}

    @safe_node
    def judge_content(self, state: AuditState):
        """Stage 3: LLM finds violations (with evidence); code decides PASS/FAIL."""
        verdict = self._judge.judge(
            transcript=state.get("transcript", ""),
            ocr_text=state.get("ocr_text", []),
            metadata=state.get("video_metadata", {}),
            rules=state.get("rules", []),
        )
        return {
            "violations": verdict.violations,
            "status": decide_status(verdict.violations),
            "report": verdict.summary,
        }