"""Curated LIVE opportunity snapshots.

These are not scraped at runtime and are never presented as self-updating facts.
Each record carries its source URL, verification timestamp and factual assertions.
The app can later refresh these through a connector without changing the domain model.
"""
from __future__ import annotations
from .models import Opportunity, SourceEvidence


def curated_live_opportunities() -> list[Opportunity]:
    return [
        Opportunity(
            id="live-future-vision-xprize-2026",
            source="Future Vision XPRIZE official rules",
            title="Future Vision XPRIZE — optimistic technology-forward film",
            url="https://futurevisionxprize.com/rules",
            reward=100000,
            currency="USD",
            deadline="2026-08-15T23:59:00-07:00",
            media_type="video",
            deliverables=[
                "Video up to 3 minutes plus required 15-second sponsor trailer",
                "MP4/MOV at 1080p minimum",
                "English dialogue or subtitles",
                "Cover sheet and treatment up to 12 pages",
            ],
            ai_policy="AI-generated and hybrid production approaches are explicitly allowed; participants may use preferred production tools.",
            policy_evidence="Official rules state that live action, animation, AI-generated content and hybrid formats are acceptable, with any production tools allowed.",
            ai_permission_explicit=True,
            commercial_rights_required=True,
            sample=False,
            human_review_flags=[
                "Submission grants temporary exclusivity through the winner announcement.",
                "Cash-prize eligibility requires in-person attendance at the September 25 finals.",
                "No explicit entry-fee statement was located in the rules snapshot; verify before pursuing.",
            ],
            source_evidence=SourceEvidence(
                url="https://futurevisionxprize.com/rules",
                verified_at="2026-07-26T19:00:00+02:00",
                live=True,
                facts=[
                    "Deadline August 15, 2026.",
                    "AI-generated content and hybrid formats are explicitly accepted.",
                    "Any production tools may be used.",
                    "Grand-prize cash component is $100,000; runner-up awards are also cash prizes.",
                    "Finalists have rights/exclusivity and attendance obligations that require human review.",
                ],
            ),
        ),
        Opportunity(
            id="live-runway-big-ad-2026",
            source="Runway official contest page",
            title="Runway — Another Big Ad Contest, Volume II",
            url="https://runway.com/AnotherBigAdContest",
            reward=50000,
            currency="USD",
            deadline="2026-07-31T23:59:00-07:00",
            media_type="video",
            deliverables=[
                "15–30 second original advertisement",
                "Respond to one official fictional-product brief",
                "Include official contest watermark",
            ],
            ai_policy="Generative video is required to be created inside Runway.",
            policy_evidence="Official rules require all generative video to be made inside Runway and require an active paid Runway subscription.",
            ai_permission_explicit=True,
            sample=False,
            requires_paid_plan=True,
            mandatory_platform="Runway",
            source_evidence=SourceEvidence(
                url="https://runway.com/AnotherBigAdContest",
                verified_at="2026-07-26T19:00:00+02:00",
                live=True,
                facts=[
                    "Submission deadline July 31, 2026.",
                    "Grand prize is $50,000 cash; places 2–15 also receive cash.",
                    "All generative video must be created in Runway.",
                    "An active paid Runway plan is required at submission.",
                ],
            ),
        ),
    ]
