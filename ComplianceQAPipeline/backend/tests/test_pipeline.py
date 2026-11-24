from backend.src.graph.nodes import AuditNodes
from backend.src.schemas import Rule, Severity, Violation, Category
from backend.src.services.judge import decide_status


class FakeRetriever:
    def search(self, query, k=3):
        return [Rule("Sponsorships must be clearly disclosed.", "ftc.pdf")]


def test_rules_are_deduplicated_across_categories():
    nodes = AuditNodes(indexer=None, retriever=FakeRetriever(), judge=None)
    out = nodes.retrieve_rules({"transcript": "buy now!", "ocr_text": []})
    assert len(out["rules"]) == 1


def test_only_major_or_critical_fails():
    warn = Violation(category=Category.AD_SPECS, severity=Severity.WARNING, description="x", evidence="y")
    crit = Violation(category=Category.FTC_DISCLOSURE, severity=Severity.CRITICAL, description="x", evidence="y")
    assert decide_status([warn]) == "PASS"
    assert decide_status([warn, crit]) == "FAIL"