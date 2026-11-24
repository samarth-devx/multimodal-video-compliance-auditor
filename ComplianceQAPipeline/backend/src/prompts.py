from backend.src.schemas import Category, Rule

# Single source of truth: used for the prompt AND for retrieval queries.
CATEGORY_GUIDE: dict[Category, str] = {
    Category.FTC_DISCLOSURE: "Is there a clear paid partnership or sponsorship disclosure?",
    Category.CLAIM_VALIDATION: "Are product claims substantiated? Any absolute guarantees?",
    Category.ENDORSEMENT: "Is the endorser's relationship to the brand disclosed?",
    Category.AD_SPECS: "Does the ad meet YouTube advertising standards?",
    Category.MISLEADING: "Any deceptive pricing, fake urgency, or exaggerated results?",
    Category.PROFESSIONAL: "Are doctors or experts shown without verified credentials?",
    Category.TRADEMARK: "Any unauthorized use of trademarks or copyrighted material?",
}


def build_system_prompt(rules: list[Rule]) -> str:
    rules_block = "\n\n".join(f"[{r.source}]\n{r.text}" for r in rules) or "(no rules retrieved)"
    checks = "\n".join(f"- {c.value}: {q}" for c, q in CATEGORY_GUIDE.items())
    return f"""You are a Senior Brand Compliance Auditor specializing in FTC regulations, \
YouTube ad policies and influencer marketing guidelines.

OFFICIAL RULES FROM THE KNOWLEDGE BASE:
{rules_block}

Check the ad for each of the following:
{checks}

Instructions:
- Only flag real violations backed by the rules above, not assumptions.
- For every violation, quote the exact phrase from the transcript or on-screen text as evidence.
- Copy the [timestamp] from the evidence line when one is available.
- Severity: CRITICAL (legal risk), MAJOR (serious), MODERATE (should fix), WARNING (minor).
- If there are no violations, return an empty list and say so in the summary."""


def build_user_prompt(transcript: str, ocr_text: list[str], metadata: dict) -> str:
    return (
        f"VIDEO METADATA: {metadata}\n\n"
        f"TRANSCRIPT:\n{transcript or '(none)'}\n\n"
        f"ON-SCREEN TEXT (OCR):\n" + ("\n".join(ocr_text) or "(none)")
    )