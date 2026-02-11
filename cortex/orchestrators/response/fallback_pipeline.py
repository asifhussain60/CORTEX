"""
FallbackPipeline for CORTEX Response Optimization.

Multi-tier graceful degradation for summarization.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 specification
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from cortex.orchestrators.response.extractive_summarizer import ExtractiveSummarizer


class FallbackTier(Enum):
    """Fallback tiers for summarization (priority order)."""
    ML_EXTRACTIVE = "ml_extractive"  # ML-based extractive (highest quality)
    DEDUPLICATION = "deduplication"  # Semantic deduplication
    POLICY_BASED = "policy_based"  # Rule-based compression
    RAW = "raw"  # No summarization (fallback)


@dataclass
class FallbackResult:
    """
    Result from fallback pipeline execution.

    Attributes:
        summary: Summarized text
        tier_used: Which fallback tier succeeded
        success: Whether summarization succeeded
        reduction_ratio: Actual compression achieved (0.0-1.0)
    """
    summary: str
    tier_used: FallbackTier
    success: bool
    reduction_ratio: float


class FallbackPipeline:
    """
    Multi-tier fallback pipeline for response summarization.

    Tiers (priority order):
    1. ML_EXTRACTIVE — Sentence-transformer based extraction
    2. DEDUPLICATION — Semantic deduplication (Phase 34)
    3. POLICY_BASED — Rule-based compression
    4. RAW — Return original text

    Example:
        >>> pipeline = FallbackPipeline()
        >>> result = pipeline.summarize(long_text, target_ratio=0.5)
        >>> print(f"Used tier: {result.tier_used}")
    """

    def __init__(self):
        """Initialize fallback pipeline with tier ordering."""
        self.tiers = [
            FallbackTier.ML_EXTRACTIVE,
            FallbackTier.DEDUPLICATION,
            FallbackTier.POLICY_BASED,
            FallbackTier.RAW,
        ]

        # Lazy load extractive summarizer
        self._extractive_summarizer: Optional[ExtractiveSummarizer] = None

    @property
    def extractive_summarizer(self) -> ExtractiveSummarizer:
        """Lazy load extractive summarizer."""
        if self._extractive_summarizer is None:
            self._extractive_summarizer = ExtractiveSummarizer()
        return self._extractive_summarizer

    def summarize(self, text: str, target_ratio: float = 0.5) -> FallbackResult:
        """
        Summarize text using best available tier.

        Tries tiers in priority order until one succeeds.

        Args:
            text: Input text to summarize
            target_ratio: Target compression ratio (0.1-1.0)

        Returns:
            FallbackResult with summary and tier used
        """
        for tier in self.tiers:
            try:
                if tier == FallbackTier.ML_EXTRACTIVE:
                    result = self._apply_ml_tier(text, target_ratio)
                elif tier == FallbackTier.DEDUPLICATION:
                    result = self._apply_dedup_tier(text, target_ratio)
                elif tier == FallbackTier.POLICY_BASED:
                    result = self._apply_policy_tier(text, target_ratio)
                else:  # RAW
                    result = self._apply_raw_tier(text, target_ratio)

                if result.success:
                    return result

            except Exception:
                # Continue to next tier on failure
                continue

        # Should never reach here (RAW always succeeds)
        return self._apply_raw_tier(text, target_ratio)

    def _apply_ml_tier(self, text: str, target_ratio: float) -> FallbackResult:
        """
        Apply ML extractive summarization.

        Args:
            text: Input text
            target_ratio: Target compression ratio

        Returns:
            FallbackResult with ML summary
        """
        try:
            summary = self.extractive_summarizer.summarize(
                text,
                compression_ratio=target_ratio
            )

            reduction = self._compute_reduction(text, summary)

            return FallbackResult(
                summary=summary,
                tier_used=FallbackTier.ML_EXTRACTIVE,
                success=True,
                reduction_ratio=reduction,
            )

        except Exception:
            return FallbackResult(
                summary="",
                tier_used=FallbackTier.ML_EXTRACTIVE,
                success=False,
                reduction_ratio=0.0,
            )

    def _apply_dedup_tier(self, text: str, target_ratio: float) -> FallbackResult:
        """
        Apply semantic deduplication.

        NOTE: Deduplication from Phase 34 not yet integrated.
        Falls through to policy tier.
        """
        # TODO: Integrate SemanticDeduplicator from Phase 34
        return FallbackResult(
            summary="",
            tier_used=FallbackTier.DEDUPLICATION,
            success=False,
            reduction_ratio=0.0,
        )

    def _apply_policy_tier(self, text: str, target_ratio: float) -> FallbackResult:
        """
        Apply rule-based compression.

        Simple heuristic: truncate to target length.
        """
        target_length = int(len(text) * target_ratio)
        summary = text[:target_length]

        # Try to break at sentence boundary
        if summary and len(summary) < len(text):
            last_period = summary.rfind('.')
            if last_period > len(summary) * 0.7:  # Keep if >70% of target
                summary = summary[:last_period + 1]

        reduction = self._compute_reduction(text, summary)

        return FallbackResult(
            summary=summary,
            tier_used=FallbackTier.POLICY_BASED,
            success=True,
            reduction_ratio=reduction,
        )

    def _apply_raw_tier(self, text: str, target_ratio: float) -> FallbackResult:
        """
        Raw tier (no summarization).

        Always succeeds by returning original text.
        """
        return FallbackResult(
            summary=text,
            tier_used=FallbackTier.RAW,
            success=True,
            reduction_ratio=0.0,  # No reduction
        )

    def _compute_reduction(self, original: str, summary: str) -> float:
        """
        Compute actual reduction ratio achieved.

        Args:
            original: Original text
            summary: Summarized text

        Returns:
            Reduction ratio (0.0 = no reduction, 1.0 = 100% reduction)
        """
        if not original:
            return 0.0

        reduction = 1.0 - (len(summary) / len(original))
        return max(0.0, min(1.0, reduction))
