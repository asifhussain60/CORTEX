"""advanced_optimization.py — Semantic deduplication and quality scoring.

Provides SemanticDeduplicator for removing duplicate content blocks,
ResponseQualityScorer for scoring response quality, and RoleVerbosityProfiles
for role-based verbosity control.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
Phase: 34 (Advanced Response Optimization) — activated Phase 116-b GAP-116-04
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

_log = logging.getLogger(__name__)


class VerbosityRole(str, Enum):
    """User role for verbosity profiling.

    Attributes:
        DEVELOPER: Standard developer — full detail.
        LEAD: Team lead — executive summaries preferred.
        EXECUTIVE: Executive — bullet points only.
    """

    DEVELOPER = "developer"
    LEAD = "lead"
    EXECUTIVE = "executive"


@dataclass
class ResponseQualityScore:
    """Response quality assessment.

    Attributes:
        overall: Overall quality score (0.0 — 1.0).
        clarity: Clarity score.
        completeness: Completeness score.
        conciseness: Conciseness score.
        actionability: Actionability score.
        deductions: List of deduction reasons.
    """

    overall: float = 1.0
    clarity: float = 1.0
    completeness: float = 1.0
    conciseness: float = 1.0
    actionability: float = 1.0
    deductions: List[str] = field(default_factory=list)


class SemanticDeduplicator:
    """Removes semantically duplicate content blocks from responses.

    Uses simple heuristics (header matching, paragraph fingerprinting)
    to detect and collapse repeated content.

    Attributes:
        similarity_threshold: Minimum similarity ratio to consider duplicate.
    """

    def __init__(self, similarity_threshold: float = 0.85) -> None:
        """Initialise deduplicator.

        Args:
            similarity_threshold: Similarity ratio threshold (0.0 — 1.0).
        """
        self.similarity_threshold = similarity_threshold

    def deduplicate(self, response: str) -> str:
        """Remove duplicate content blocks from response.

        Args:
            response: Full response text.

        Returns:
            Response with duplicate blocks removed.
        """
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
        """Generate a normalised fingerprint for a text block.

        Args:
            text: Text block to fingerprint.

        Returns:
            Normalised fingerprint string.
        """
        # Normalise whitespace and case for comparison
        normalised = " ".join(text.lower().split())
        # Use first 100 chars as fingerprint (sufficient for section-level dedup)
        return normalised[:100] if normalised else ""


class ResponseQualityScorer:
    """Scores response quality against CORTEX standards.

    Evaluates clarity, completeness, conciseness, and actionability.

    Attributes:
        role: Target audience role for scoring adjustments.
    """

    def __init__(self, role: VerbosityRole = VerbosityRole.DEVELOPER) -> None:
        """Initialise quality scorer.

        Args:
            role: Target audience role.
        """
        self.role = role

    def score(self, response: str, context: Optional[Dict[str, Any]] = None) -> ResponseQualityScore:
        """Score a response for quality.

        Args:
            response: Full response text.
            context: Optional context (intent type, etc.).

        Returns:
            ResponseQualityScore with component scores and deductions.
        """
        result = ResponseQualityScore()
        word_count = len(response.split())

        # Conciseness check
        if word_count > 800:
            penalty = min(0.3, (word_count - 800) / 1000)
            result.conciseness -= penalty
            result.deductions.append(f"Verbose: {word_count} words (target ≤800)")

        # Clarity check — look for structure
        if "##" not in response and word_count > 100:
            result.clarity -= 0.2
            result.deductions.append("Missing section headers for long response")

        # Actionability — check for next steps or proceed gate
        if "proceed" not in response.lower() and "next step" not in response.lower():
            if context and context.get("requires_action", False):
                result.actionability -= 0.2
                result.deductions.append("Missing proceed gate or next steps")

        # Compute overall
        result.overall = (
            result.clarity * 0.25
            + result.completeness * 0.25
            + result.conciseness * 0.25
            + result.actionability * 0.25
        )

        return result


@dataclass
class VerbosityProfile:
    """Verbosity settings for a specific role.

    Attributes:
        max_words: Maximum word count.
        include_tables: Whether to include comparison tables.
        include_code_blocks: Whether to include code blocks.
        include_timelines: Whether to include engagement timelines.
    """

    max_words: int = 800
    include_tables: bool = True
    include_code_blocks: bool = True
    include_timelines: bool = True


class RoleVerbosityProfiles:
    """Role-based verbosity profile registry.

    Maps user roles to verbosity settings for response tailoring.
    """

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
        """Get verbosity profile for a role.

        Args:
            role: User role.

        Returns:
            VerbosityProfile for the specified role.
        """
        return cls._profiles.get(role, cls._profiles[VerbosityRole.DEVELOPER])


# Backward-compatible aliases for import contract
# (master_orchestrator_response_mixin.py imports these names)
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
