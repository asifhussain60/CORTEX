"""advanced_optimization.py — Semantic deduplication and quality scoring.

Provides SemanticDeduplicator for removing duplicate content blocks,
ResponseQualityScorer for scoring response quality, and RoleVerbosityProfiles
for role-based verbosity control.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

_log = logging.getLogger(__name__)


class VerbosityRole(str, Enum):
    DEVELOPER = "developer"
    LEAD = "lead"
    EXECUTIVE = "executive"


@dataclass
class ResponseQualityScore:
    overall: float = 1.0
    clarity: float = 1.0
    completeness: float = 1.0
    conciseness: float = 1.0
    actionability: float = 1.0
    deductions: List[str] = field(default_factory=list)


class SemanticDeduplicator:
    def __init__(self, similarity_threshold: float = 0.85) -> None:
        self.similarity_threshold = similarity_threshold

    def deduplicate(self, response: str) -> str:
        sections = response.split("\n\n")
        seen_fingerprints: Dict[str, int] = {}
        unique_sections: List[str] = []

        for section in sections:
            fingerprint = self._fingerprint(section)
            if fingerprint not in seen_fingerprints:
                seen_fingerprints[fingerprint] = len(unique_sections)
                unique_sections.append(section)

        return "\n\n".join(unique_sections)

    @staticmethod
    def _fingerprint(text: str) -> str:
        normalised = " ".join(text.lower().split())
        return normalised[:100] if normalised else ""


class ResponseQualityScorer:
    def __init__(self, role: VerbosityRole = VerbosityRole.DEVELOPER) -> None:
        self.role = role

    def score(self, response: str, context: Optional[Dict[str, Any]] = None) -> ResponseQualityScore:
        result = ResponseQualityScore()
        word_count = len(response.split())

        if word_count > 800:
            penalty = min(0.3, (word_count - 800) / 1000)
            result.conciseness -= penalty
            result.deductions.append(f"Verbose: {word_count} words (target ≤800)")

        if "##" not in response and word_count > 100:
            result.clarity -= 0.2
            result.deductions.append("Missing section headers for long response")

        if "proceed" not in response.lower() and "next step" not in response.lower():
            if context and context.get("requires_action", False):
                result.actionability -= 0.2
                result.deductions.append("Missing proceed gate or next steps")

        result.overall = (
            result.clarity * 0.25
            + result.completeness * 0.25
            + result.conciseness * 0.25
            + result.actionability * 0.25
        )

        return result


@dataclass
class VerbosityProfile:
    max_words: int = 800
    include_tables: bool = True
    include_code_blocks: bool = True
    include_timelines: bool = True


class RoleVerbosityProfiles:
    _profiles: Dict[VerbosityRole, VerbosityProfile] = {
        VerbosityRole.DEVELOPER: VerbosityProfile(
            max_words=800,
            include_tables=True,
            include_code_blocks=True,
            include_timelines=True,
        ),
        VerbosityRole.LEAD: VerbosityProfile(
            max_words=500,
            include_tables=True,
            include_code_blocks=False,
            include_timelines=False,
        ),
        VerbosityRole.EXECUTIVE: VerbosityProfile(
            max_words=200,
            include_tables=False,
            include_code_blocks=False,
            include_timelines=False,
        ),
    }

    @classmethod
    def get_profile(cls, role: VerbosityRole) -> VerbosityProfile:
        return cls._profiles.get(role, cls._profiles[VerbosityRole.DEVELOPER])


Role = VerbosityRole
QualityScore = ResponseQualityScore

__all__ = [
    "VerbosityRole",
    "ResponseQualityScore",
    "Role",
    "QualityScore",
    "SemanticDeduplicator",
    "ResponseQualityScorer",
    "RoleVerbosityProfiles",
    "VerbosityProfile",
]
