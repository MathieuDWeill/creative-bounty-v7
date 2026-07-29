import re
from .models import Decision, Opportunity, RightsAssessment

ALLOW_PATTERNS = [
    r"\bgenerative ai (?:is )?(?:explicitly )?(?:allowed|welcome|permitted)\b",
    r"\bai[- ]generated (?:content|media) (?:is )?(?:allowed|welcome|permitted)\b",
    r"\bai (?:is )?(?:explicitly )?(?:allowed|permitted)\b",
    r"\buse of generative ai (?:is )?(?:allowed|permitted)\b",
    r"\bai-generated content\b",
]
DENY_PATTERNS = [
    r"\bgenerative ai (?:is )?(?:strictly )?(?:prohibited|forbidden|not allowed)\b",
    r"\bai[- ]generated (?:content|media) (?:is )?(?:prohibited|forbidden|not allowed)\b",
    r"\bai (?:is )?(?:prohibited|forbidden|not allowed)\b",
    r"\bno ai[- ]generated (?:content|media|assets?)\b",
    r"\bhuman[- ]only\b",
]

def _matches(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)

def assess_rights(op: Opportunity) -> RightsAssessment:
    text = f"{op.ai_policy} {op.policy_evidence}"

    # Structured evidence takes precedence over fuzzy text matching.
    if op.ai_prohibition_explicit:
        return RightsAssessment(
            decision=Decision.REJECT,
            confidence=0.995,
            reasons=["Structured source evidence explicitly prohibits generative AI."],
            evidence=op.policy_evidence,
        )
    if op.ai_permission_explicit is True:
        reasons = ["Structured source evidence explicitly permits generative AI."]
        if op.disclosure_required:
            reasons.append("AI-use disclosure must accompany submission.")
        return RightsAssessment(
            decision=Decision.PASS,
            confidence=0.99,
            reasons=reasons,
            evidence=op.policy_evidence,
        )

    if _matches(DENY_PATTERNS, text):
        return RightsAssessment(
            decision=Decision.REJECT,
            confidence=0.98,
            reasons=["Source evidence explicitly prohibits generative AI."],
            evidence=op.policy_evidence,
        )
    if _matches(ALLOW_PATTERNS, text):
        reasons = ["Source evidence explicitly permits generative AI."]
        if op.disclosure_required:
            reasons.append("AI-use disclosure must accompany submission.")
        return RightsAssessment(
            decision=Decision.PASS,
            confidence=0.95,
            reasons=reasons,
            evidence=op.policy_evidence,
        )
    return RightsAssessment(
        decision=Decision.REVIEW,
        confidence=0.55,
        reasons=[
            "No explicit permission to use generative AI was found.",
            "Human review is required before generation.",
        ],
        evidence=op.policy_evidence,
    )
