"""
Effectiveness Analyzer - Phase 12 S2

AC-PHASE71-007: Pattern effectiveness scoring and tracking

Analyzes effectiveness of learned patterns by tracking:
- Success rates across multiple applications
- Time savings vs baseline approaches
- Quality improvement metrics (before/after)
- Historical trends and learning velocity

Used by UniversalLearningLoop to determine which patterns to promote
and how to weight recommendations.

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EffectivenessTrend(Enum):
    """Trend in pattern effectiveness over time."""

    IMPROVING = auto()      # Success rate increasing
    STABLE = auto()         # Success rate consistent
    DECLINING = auto()      # Success rate decreasing
    INSUFFICIENT_DATA = auto()  # Not enough data to determine


@dataclass
class PatternApplication:
    """Record of a single pattern application."""

    pattern_id: str                  # ID of pattern applied
    orchestrator: str                # Which orchestrator applied it
    timestamp: datetime              # When applied
    success: bool                    # Whether application succeeded
    time_taken_seconds: float        # Time to apply pattern
    quality_before: float            # Quality score before (0.0-1.0)
    quality_after: float             # Quality score after (0.0-1.0)
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context

    @property
    def quality_improvement(self) -> float:
        """Calculate quality improvement from this application."""
        return self.quality_after - self.quality_before


@dataclass
class EffectivenessMetrics:
    """Effectiveness metrics for a pattern."""

    pattern_id: str
    total_applications: int
    successful_applications: int
    success_rate: float
    average_time_seconds: float
    average_quality_improvement: float
    last_application: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern_id": self.pattern_id,
            "total_applications": self.total_applications,
            "successful_applications": self.successful_applications,
            "success_rate": self.success_rate,
            "average_time_seconds": self.average_time_seconds,
            "average_quality_improvement": self.average_quality_improvement,
            "last_application": self.last_application.isoformat() if self.last_application else None,
        }


class EffectivenessAnalyzer:
    """
    Analyzes effectiveness of learned patterns.

    Tracks pattern applications and calculates:
    - Success rates
    - Time savings
    - Quality improvements
    - Historical trends

    AC-PHASE71-007: Pattern effectiveness scoring and tracking
    """

    def __init__(self) -> None:
        """Initialize effectiveness analyzer."""
        # Store all pattern applications
        self._applications: Dict[str, List[PatternApplication]] = {}

        # Cache calculated metrics
        self._metrics_cache: Dict[str, EffectivenessMetrics] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 300  # 5 minutes

    def record_application(self, application: PatternApplication) -> None:
        """
        Record a pattern application.

        Args:
            application: PatternApplication to record
        """
        pattern_id = application.pattern_id

        if pattern_id not in self._applications:
            self._applications[pattern_id] = []

        self._applications[pattern_id].append(application)

        # Invalidate cache for this pattern
        if pattern_id in self._metrics_cache:
            del self._metrics_cache[pattern_id]

        logger.debug(
            f"Recorded application of pattern {pattern_id}: "
            f"success={application.success}, time={application.time_taken_seconds}s"
        )

    def get_metrics_for_pattern(
        self,
        pattern_id: str,
        since: Optional[datetime] = None
    ) -> EffectivenessMetrics:
        """
        Get effectiveness metrics for a pattern.

        Args:
            pattern_id: ID of pattern to analyze
            since: Optional start date for analysis (default: all time)

        Returns:
            EffectivenessMetrics for the pattern
        """
        # Check cache (only if analyzing all time)
        if since is None and self._is_cache_valid():
            if pattern_id in self._metrics_cache:
                return self._metrics_cache[pattern_id]

        # Get applications for this pattern
        applications = self._applications.get(pattern_id, [])

        # Filter by date if specified
        if since is not None:
            applications = [
                app for app in applications
                if app.timestamp >= since
            ]

        # Calculate metrics
        if not applications:
            return EffectivenessMetrics(
                pattern_id=pattern_id,
                total_applications=0,
                successful_applications=0,
                success_rate=0.0,
                average_time_seconds=0.0,
                average_quality_improvement=0.0,
                last_application=None
            )

        total = len(applications)
        successful = sum(1 for app in applications if app.success)
        success_rate = successful / total if total > 0 else 0.0

        avg_time = sum(app.time_taken_seconds for app in applications) / total
        avg_quality = sum(app.quality_improvement for app in applications) / total

        last_app = max(applications, key=lambda app: app.timestamp).timestamp

        metrics = EffectivenessMetrics(
            pattern_id=pattern_id,
            total_applications=total,
            successful_applications=successful,
            success_rate=success_rate,
            average_time_seconds=avg_time,
            average_quality_improvement=avg_quality,
            last_application=last_app
        )

        # Cache if all-time query
        if since is None:
            self._metrics_cache[pattern_id] = metrics
            self._cache_timestamp = datetime.now()

        return metrics

    def calculate_time_savings(
        self,
        pattern_id: str,
        baseline_time: float
    ) -> float:
        """
        Calculate time savings vs baseline approach.

        Args:
            pattern_id: ID of pattern to analyze
            baseline_time: Baseline time without pattern (seconds)

        Returns:
            Average time saved per application (seconds)
        """
        metrics = self.get_metrics_for_pattern(pattern_id)

        if metrics.total_applications == 0:
            return 0.0

        savings = baseline_time - metrics.average_time_seconds
        return savings

    def analyze_trend(
        self,
        pattern_id: str,
        window_days: int = 30
    ) -> str:
        """
        Analyze effectiveness trend over time.

        Args:
            pattern_id: ID of pattern to analyze
            window_days: Window for trend analysis (days)

        Returns:
            Trend classification: "improving", "stable", "declining", "insufficient_data"
        """
        applications = self._applications.get(pattern_id, [])

        if len(applications) < 5:
            return "insufficient_data"

        # Get applications in window
        cutoff = datetime.now() - timedelta(days=window_days)
        recent_apps = [app for app in applications if app.timestamp >= cutoff]

        if len(recent_apps) < 5:
            return "insufficient_data"

        # Sort by timestamp
        recent_apps.sort(key=lambda app: app.timestamp)

        # Split into first half and second half
        midpoint = len(recent_apps) // 2
        first_half = recent_apps[:midpoint]
        second_half = recent_apps[midpoint:]

        # Calculate success rates
        first_success_rate = sum(1 for app in first_half if app.success) / len(first_half)
        second_success_rate = sum(1 for app in second_half if app.success) / len(second_half)

        # Determine trend
        diff = second_success_rate - first_success_rate

        if diff > 0.1:  # 10% improvement
            return "improving"
        elif diff < -0.1:  # 10% decline
            return "declining"
        else:
            return "stable"

    def get_all_metrics(self) -> Dict[str, EffectivenessMetrics]:
        """
        Get effectiveness metrics for all patterns.

        Returns:
            Dictionary mapping pattern_id to EffectivenessMetrics
        """
        return {
            pattern_id: self.get_metrics_for_pattern(pattern_id)
            for pattern_id in self._applications.keys()
        }

    def _is_cache_valid(self) -> bool:
        """Check if metrics cache is still valid."""
        if self._cache_timestamp is None:
            return False

        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age < self._cache_ttl_seconds

    def clear_cache(self) -> None:
        """Clear metrics cache."""
        self._metrics_cache.clear()
        self._cache_timestamp = None
        logger.debug("Effectiveness metrics cache cleared")

    def decay_stale_patterns(
        self,
        max_age_days: int = 30,
        decay_amount: float = 0.1,
    ) -> List[str]:
        """
        Decay confidence of patterns that have not been used recently.

        Scans all recorded patterns and identifies those whose most recent
        application is older than ``max_age_days``. Returns the list of
        pattern IDs that were flagged for decay.

        AC-PHASE83-002: Stale pattern decay

        Args:
            max_age_days: Number of days of inactivity before decay.
            decay_amount: Amount to subtract from confidence (informational).

        Returns:
            List of pattern IDs flagged as stale.
        """
        cutoff = datetime.now() - timedelta(days=max_age_days)
        stale_ids: List[str] = []

        for pattern_id, applications in self._applications.items():
            if not applications:
                continue
            most_recent = max(applications, key=lambda a: a.timestamp)
            if most_recent.timestamp < cutoff:
                stale_ids.append(pattern_id)

        logger.debug(f"Decayed {len(stale_ids)} stale patterns (>{max_age_days} days)")
        return stale_ids

    def promote_high_confidence(
        self,
        threshold: float = 0.9,
        min_apps: int = 3,
    ) -> List[str]:
        """
        Identify patterns with high success rate and sufficient applications.

        A pattern is promotable when:
        - It has at least ``min_apps`` recorded applications.
        - Its success rate is ≥ ``threshold``.

        AC-PHASE83-002: High-confidence pattern promotion

        Args:
            threshold: Minimum success rate to qualify (0.0–1.0).
            min_apps: Minimum number of applications required.

        Returns:
            List of pattern IDs eligible for promotion.
        """
        promoted: List[str] = []

        for pattern_id in self._applications:
            metrics = self.get_metrics_for_pattern(pattern_id)
            if (
                metrics.total_applications >= min_apps
                and metrics.success_rate >= threshold
            ):
                promoted.append(pattern_id)

        logger.debug(
            f"Promoted {len(promoted)} patterns "
            f"(≥{threshold} success, ≥{min_apps} apps)"
        )
        return promoted

    def quarantine_low_confidence(
        self,
        threshold: float = 0.3,
        min_punishments: int = 2,
    ) -> List[str]:
        """
        Identify patterns with consistently poor performance.

        A pattern is quarantined when:
        - It has at least ``min_punishments`` failed applications.
        - Its success rate is ≤ ``threshold``.

        AC-PHASE83-002: Low-confidence pattern quarantine

        Args:
            threshold: Maximum success rate to trigger quarantine (0.0–1.0).
            min_punishments: Minimum number of failed applications.

        Returns:
            List of pattern IDs flagged for quarantine.
        """
        quarantined: List[str] = []

        for pattern_id in self._applications:
            metrics = self.get_metrics_for_pattern(pattern_id)
            failures = metrics.total_applications - metrics.successful_applications
            if failures >= min_punishments and metrics.success_rate <= threshold:
                quarantined.append(pattern_id)

        logger.debug(
            f"Quarantined {len(quarantined)} patterns "
            f"(≤{threshold} success, ≥{min_punishments} failures)"
        )
        return quarantined

    def get_cross_cutting_boost(
        self,
        pattern_id: str,
        min_orchestrators: int = 3,
        boost: float = 0.15,
    ) -> bool:
        """
        Check if a pattern qualifies for cross-cutting confidence boost.

        A pattern qualifies when it has been successfully applied by at
        least ``min_orchestrators`` distinct orchestrators.

        AC-PHASE83-002: Cross-cutting validation boost

        Args:
            pattern_id: ID of pattern to check.
            min_orchestrators: Minimum number of distinct orchestrators.
            boost: Boost amount (informational — caller applies).

        Returns:
            True if pattern qualifies for cross-cutting boost.
        """
        applications = self._applications.get(pattern_id, [])
        if not applications:
            return False

        distinct_orchestrators = {
            app.orchestrator
            for app in applications
            if app.success
        }
        qualifies = len(distinct_orchestrators) >= min_orchestrators

        if qualifies:
            logger.debug(
                f"Pattern {pattern_id} qualifies for cross-cutting boost "
                f"({len(distinct_orchestrators)} orchestrators, boost={boost})"
            )
        return qualifies


# Singleton accessor
_analyzer_instance: Optional[EffectivenessAnalyzer] = None


def get_effectiveness_analyzer() -> EffectivenessAnalyzer:
    """
    Get singleton EffectivenessAnalyzer instance.

    Returns:
        Singleton EffectivenessAnalyzer instance
    """
    global _analyzer_instance

    if _analyzer_instance is None:
        _analyzer_instance = EffectivenessAnalyzer()

    return _analyzer_instance
