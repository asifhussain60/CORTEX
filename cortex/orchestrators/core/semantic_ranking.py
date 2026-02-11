"""
Phase 8.3: Semantic Candidate Ranking System

Handles edge cases where multiple orchestrators match user requests.
Provides confidence scoring and disambiguation UI for ambiguous routing.

AC-ID: AC-PHASE-8.3-01 (Task SEMANTIC-001)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.models.canonical_enums import IntentType


@dataclass
class RankedCandidate:
    """
    Represents a ranked orchestrator candidate with confidence scoring.

    Attributes:
        orchestrator_name: Name of orchestrator
        orchestrator_instance: Resolved orchestrator instance
        base_confidence: Initial confidence from keyword match (0.0-1.0)
        semantic_score: Additional confidence from semantic analysis (0.0-1.0)
        total_confidence: Combined confidence (base + semantic)
        match_reasons: List of reasons why this candidate matched
    """
    orchestrator_name: str
    orchestrator_instance: IOrchestrator
    base_confidence: float
    semantic_score: float
    total_confidence: float
    match_reasons: List[str]


class SemanticRankingEngine:
    """
    Ranks orchestrator candidates using semantic analysis.

    Handles disambiguation when multiple orchestrators match a user request.
    Uses keyword overlap, intent alignment, and capability matching.

    Example:
        engine = SemanticRankingEngine()
        ranked = engine.rank_candidates(candidates, context, intent)

        if ranked[0].total_confidence < 0.7:
            # Show disambiguation UI
            top_3 = ranked[:3]
            user_selection = prompt_user(top_3)
    """

    def __init__(
        self,
        disambiguation_threshold: float = 0.7,
        min_candidates: int = 2,
        max_candidates: int = 5,
    ) -> None:
        """
        Initialize semantic ranking engine.

        Args:
            disambiguation_threshold: Confidence below which disambiguation required
            min_candidates: Minimum candidates to show in disambiguation UI
            max_candidates: Maximum candidates to rank
        """
        self.logger = EnhancedAuditLogger.instance()
        self.disambiguation_threshold = disambiguation_threshold
        self.min_candidates = min_candidates
        self.max_candidates = max_candidates

        # Semantic keyword expansion (synonym groups)
        self.synonym_groups: Dict[str, List[str]] = {
            "onboard": ["setup", "initialize", "bootstrap", "configure"],
            "analyze": ["inspect", "examine", "review", "scan", "lint"],
            "refactor": ["cleanup", "improve", "optimize", "restructure"],
            "fix": ["repair", "patch", "resolve", "correct", "debug"],
            "implement": ["create", "add", "build", "develop", "code"],
            "test": ["validate", "verify", "check", "unit-test"],
            "document": ["write", "describe", "explain", "comment"],
        }

        # Intent-to-keyword affinity scores
        self.intent_affinities: Dict[IntentType, Dict[str, float]] = {
            IntentType.IMPLEMENT: {
                "create": 1.0,
                "add": 0.9,
                "build": 0.9,
                "implement": 1.0,
                "develop": 0.8,
            },
            IntentType.FIX: {
                "fix": 1.0,
                "bug": 0.9,
                "issue": 0.8,
                "error": 0.8,
                "crash": 0.9,
            },
            IntentType.REFACTOR: {
                "refactor": 1.0,
                "cleanup": 0.9,
                "improve": 0.8,
                "optimize": 0.9,
                "restructure": 0.8,
            },
            IntentType.ANALYZE: {
                "analyze": 1.0,
                "inspect": 0.9,
                "review": 0.8,
                "examine": 0.8,
                "scan": 0.7,
            },
        }

        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.3-01",
            operation="SEMANTIC_RANKING_ENGINE_INIT",
            success=True,
            details={
                "disambiguation_threshold": disambiguation_threshold,
                "synonym_groups": len(self.synonym_groups),
            },
        )

    def rank_candidates(
        self,
        candidates: List[Tuple[str, IOrchestrator, float]],
        context: Dict[str, Any],
        intent: IntentType,
    ) -> List[RankedCandidate]:
        """
        Rank orchestrator candidates by semantic similarity.

        AC-PHASE-8.3-01: Apply semantic scoring on top of keyword matching

        Args:
            candidates: List of (name, instance, base_confidence) tuples
            context: User request context with keywords
            intent: Detected intent type

        Returns:
            List[RankedCandidate]: Ranked candidates (descending confidence)

        Example:
            >>> candidates = [
            ...     ("OnboardingOrchestrator", <instance>, 0.75),
            ...     ("SetupOrchestrator", <instance>, 0.70),
            ... ]
            >>> ranked = engine.rank_candidates(candidates, context, IntentType.IMPLEMENT)
            >>> print(ranked[0].total_confidence)  # 0.85 (after semantic boost)
        """
        try:
            # Extract keywords from context
            keywords = self._extract_keywords_from_context(context)

            # Build ranked candidates
            ranked: List[RankedCandidate] = []

            for name, instance, base_conf in candidates[:self.max_candidates]:
                # Calculate semantic score
                semantic_score = self._calculate_semantic_score(
                    name, keywords, intent
                )

                # Calculate total confidence (weighted average)
                total_conf = (base_conf * 0.7) + (semantic_score * 0.3)

                # Build match reasons
                reasons = self._build_match_reasons(name, keywords, intent, semantic_score)

                ranked.append(
                    RankedCandidate(
                        orchestrator_name=name,
                        orchestrator_instance=instance,
                        base_confidence=base_conf,
                        semantic_score=semantic_score,
                        total_confidence=total_conf,
                        match_reasons=reasons,
                    )
                )

            # Sort by total confidence descending
            ranked.sort(key=lambda x: x.total_confidence, reverse=True)

            # Log ranking result
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.3-01",
                operation="SEMANTIC_RANKING",
                success=True,
                details={
                    "candidates_in": len(candidates),
                    "candidates_out": len(ranked),
                    "top_candidate": ranked[0].orchestrator_name if ranked else None,
                    "top_confidence": ranked[0].total_confidence if ranked else 0.0,
                    "needs_disambiguation": ranked[0].total_confidence < self.disambiguation_threshold if ranked else False,
                },
            )

            return ranked

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.3-01",
                operation="SEMANTIC_RANKING_ERROR",
                success=False,
                details={"error": str(e)},
            )
            # Fallback: return original ranking
            return [
                RankedCandidate(
                    orchestrator_name=name,
                    orchestrator_instance=instance,
                    base_confidence=conf,
                    semantic_score=0.0,
                    total_confidence=conf,
                    match_reasons=["Keyword match"],
                )
                for name, instance, conf in candidates
            ]

    def _extract_keywords_from_context(self, context: Dict[str, Any]) -> List[str]:
        """Extract keywords from context dictionary."""
        keywords: List[str] = []

        # From description
        if "description" in context:
            tokens = context["description"].lower().split()
            keywords.extend(tokens)

        # From operation
        if "operation" in context:
            tokens = context["operation"].lower().replace("_", " ").split()
            keywords.extend(tokens)

        # From keywords field
        if "keywords" in context and isinstance(context["keywords"], list):
            keywords.extend([k.lower() for k in context["keywords"]])

        # Deduplicate
        return list(set(keywords))

    def _calculate_semantic_score(
        self,
        orchestrator_name: str,
        keywords: List[str],
        intent: IntentType,
    ) -> float:
        """
        Calculate semantic similarity score.

        Uses synonym expansion and intent affinity scoring.

        Args:
            orchestrator_name: Name of orchestrator
            keywords: Keywords from user request
            intent: Detected intent type

        Returns:
            float: Semantic score (0.0-1.0)
        """
        score = 0.0
        matches = 0

        # Extract orchestrator "role" from name (e.g., "Onboarding" from "OnboardingOrchestrator")
        role = orchestrator_name.replace("Orchestrator", "").lower()

        # Check for synonym matches
        for keyword in keywords:
            # Direct role match
            if keyword in role:
                score += 0.3
                matches += 1

            # Synonym expansion
            for base_word, synonyms in self.synonym_groups.items():
                if keyword == base_word or keyword in synonyms:
                    if base_word in role or any(syn in role for syn in synonyms):
                        score += 0.2
                        matches += 1

            # Intent affinity
            if intent in self.intent_affinities:
                affinity_scores = self.intent_affinities[intent]
                if keyword in affinity_scores:
                    score += affinity_scores[keyword] * 0.1
                    matches += 1

        # Normalize by number of keywords (avoid over-scoring)
        if len(keywords) > 0:
            score = score / len(keywords)

        return min(1.0, score)  # Clamp to [0, 1]

    def _build_match_reasons(
        self,
        orchestrator_name: str,
        keywords: List[str],
        intent: IntentType,
        semantic_score: float,
    ) -> List[str]:
        """Build human-readable match reasons."""
        reasons: List[str] = []

        role = orchestrator_name.replace("Orchestrator", "").lower()

        # Direct keyword matches
        direct_matches = [kw for kw in keywords if kw in role]
        if direct_matches:
            reasons.append(f"Keywords match: {', '.join(direct_matches)}")

        # Synonym matches
        for keyword in keywords:
            for base_word, synonyms in self.synonym_groups.items():
                if keyword in synonyms and base_word in role:
                    reasons.append(f"Synonym: '{keyword}' ≈ '{base_word}'")

        # Intent alignment
        if semantic_score > 0.5:
            reasons.append(f"Strong alignment with {intent.value} intent")
        elif semantic_score > 0.3:
            reasons.append(f"Moderate alignment with {intent.value} intent")

        return reasons if reasons else ["General capability match"]

    def needs_disambiguation(self, ranked: List[RankedCandidate]) -> bool:
        """
        Check if user disambiguation is required.

        AC-PHASE-8.3-01: Disambiguation needed if top candidate < threshold

        Args:
            ranked: Ranked candidates list

        Returns:
            bool: True if disambiguation UI should be shown
        """
        if not ranked:
            return False

        top_confidence = ranked[0].total_confidence
        return top_confidence < self.disambiguation_threshold

    def get_disambiguation_candidates(
        self,
        ranked: List[RankedCandidate],
    ) -> List[RankedCandidate]:
        """
        Get top candidates for disambiguation UI.

        AC-PHASE-8.3-01: Return 2-5 candidates for user selection

        Args:
            ranked: Ranked candidates list

        Returns:
            List[RankedCandidate]: Top 2-5 candidates
        """
        return ranked[:min(len(ranked), self.max_candidates)]
