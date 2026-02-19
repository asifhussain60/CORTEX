"""
LearningDashboard - Visualization of learning infrastructure (Phase 71 S7).

AC-ID: PHASE-71-S7
Purpose: Dashboard and metrics for learning operations

Components:
1. Learning metrics aggregation
2. Test quality visualization
3. Orchestrator statistics
4. Pattern extraction tracking
5. Confidence tier distribution

Author: Asif Hussain
Date: 2026-02-10
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from cortex.learning.universal_learning_loop import get_learning_loop
from cortex.testing.test_value_scorer import ScoreTier, get_test_value_scorer

logger = logging.getLogger(__name__)


@dataclass
class MetricsSnapshot:
    """Snapshot of learning metrics at a point in time."""

    timestamp: datetime = field(default_factory=datetime.now)
    total_learnings: int = 0
    total_patterns: int = 0
    orchestrators: Set[str] = field(default_factory=set)
    avg_confidence: float = 0.0
    high_value_tests: int = 0
    deduplication_rate: float = 0.0
    success_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_learnings": self.total_learnings,
            "total_patterns": self.total_patterns,
            "orchestrators": sorted(list(self.orchestrators)),
            "avg_confidence": self.avg_confidence,
            "high_value_tests": self.high_value_tests,
            "deduplication_rate": self.deduplication_rate,
            "success_rate": self.success_rate,
        }


class LearningDashboard:
    """
    Dashboard for learning infrastructure metrics and visualization.

    Provides:
    - Real-time metrics snapshots
    - Orchestrator statistics
    - Test quality summaries
    - Pattern extraction tracking
    - Confidence tier distribution

    Usage:
        dashboard = LearningDashboard()
        snapshot = dashboard.capture_metrics()
        report = dashboard.generate_report()
    """

    def __init__(self):
        """Initialize learning dashboard."""
        self.learning_loop: Optional[Any] = get_learning_loop()
        self.test_scorer: Optional[Any] = get_test_value_scorer()
        self._snapshots: List[MetricsSnapshot] = []

    def capture_metrics(self) -> MetricsSnapshot:
        """
        Capture current learning metrics.

        Returns:
            MetricsSnapshot with current state
        """
        snapshot = MetricsSnapshot()

        try:
            if not self.learning_loop:
                logger.debug("Learning loop unavailable, returning empty snapshot")
                return snapshot

            # Get learning loop metrics
            metrics = self.learning_loop.get_learning_metrics()

            snapshot.total_learnings = metrics.get("total_learnings", 0)
            snapshot.total_patterns = metrics.get("total_patterns", 0)
            snapshot.success_rate = metrics.get("success_rate", 0.0)

            # Collect orchestrators
            orchestrators = set()
            confidences = []
            for orch_name, orch_data in metrics.get("by_orchestrator", {}).items():
                orchestrators.add(orch_name)
                confidences.append(orch_data.get("avg_confidence", 0.0))

            snapshot.orchestrators = orchestrators
            if confidences:
                snapshot.avg_confidence = sum(confidences) / len(confidences)

            # Get deduplication metrics
            snapshot.deduplication_rate = metrics.get("deduplication_rate", 0.0)

            # Get test scoring metrics
            if self.test_scorer:
                summary = self.test_scorer.get_score_summary()
                snapshot.high_value_tests = summary.get("high_value_count", 0)

            self._snapshots.append(snapshot)

        except Exception as e:
            logger.warning(f"Failed to capture metrics: {e}", exc_info=False)

        return snapshot

    def get_orchestrator_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each orchestrator.

        Returns:
            Dict mapping orchestrator names to their statistics
        """
        try:
            if not self.learning_loop:
                return {}

            metrics = self.learning_loop.get_learning_metrics()
            stats = {}

            for orch_name, orch_data in metrics.get("by_orchestrator", {}).items():
                stats[orch_name] = {
                    "learnings": orch_data.get("count", 0),
                    "patterns": orch_data.get("patterns", 0),
                    "avg_confidence": orch_data.get("avg_confidence", 0.0),
                    "confidences": orch_data.get("confidences", []),
                }

            return stats

        except Exception as e:
            logger.warning(f"Failed to get orchestrator statistics: {e}")
            return {}

    def get_test_quality_distribution(self) -> Dict[str, int]:
        """
        Get distribution of tests by quality tier.

        Returns:
            Dict mapping tier names to test counts
        """
        try:
            if not self.test_scorer:
                return {}

            summary = self.test_scorer.get_score_summary()
            return summary.get("by_tier", {})

        except Exception as e:
            logger.warning(f"Failed to get test quality distribution: {e}")
            return {}

    def get_confidence_distribution(self) -> Dict[str, int]:
        """
        Get distribution of confidence scores.

        Returns:
            Dict with confidence tier buckets (0.0-0.25, 0.25-0.5, etc.)
        """
        try:
            if not self.learning_loop:
                return {}

            metrics = self.learning_loop.get_learning_metrics()

            # Collect all confidence scores
            all_confidences = []
            for orch_data in metrics.get("by_orchestrator", {}).values():
                confidences = orch_data.get("confidences", [])
                all_confidences.extend(confidences)

            if not all_confidences:
                return {}

            # Bucket into confidence ranges
            distribution = {
                "0.0-0.25": 0,
                "0.25-0.5": 0,
                "0.5-0.75": 0,
                "0.75-0.9": 0,
                "0.9-1.0": 0,
            }

            for conf in all_confidences:
                if conf < 0.25:
                    distribution["0.0-0.25"] += 1
                elif conf < 0.5:
                    distribution["0.25-0.5"] += 1
                elif conf < 0.75:
                    distribution["0.5-0.75"] += 1
                elif conf < 0.9:
                    distribution["0.75-0.9"] += 1
                else:
                    distribution["0.9-1.0"] += 1

            return distribution

        except Exception as e:
            logger.warning(f"Failed to get confidence distribution: {e}")
            return {}

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive learning infrastructure report.

        Returns:
            Dict with full dashboard report
        """
        snapshot = self.capture_metrics()

        return {
            "timestamp": snapshot.timestamp.isoformat(),
            "summary": {
                "total_learnings": snapshot.total_learnings,
                "total_patterns": snapshot.total_patterns,
                "orchestrators_active": len(snapshot.orchestrators),
                "avg_confidence": snapshot.avg_confidence,
                "high_value_tests": snapshot.high_value_tests,
                "deduplication_rate": snapshot.deduplication_rate,
                "success_rate": snapshot.success_rate,
            },
            "orchestrators": self.get_orchestrator_statistics(),
            "test_quality": self.get_test_quality_distribution(),
            "confidence": self.get_confidence_distribution(),
        }

    def generate_ascii_report(self) -> str:
        """
        Generate ASCII text report for terminal display.

        Returns:
            Formatted ASCII report string
        """
        report = self.generate_report()
        summary = report["summary"]

        lines = [
            "",
            "=" * 70,
            "📊 PHASE 71: UNIVERSAL LEARNING LOOP - DASHBOARD",
            "=" * 70,
            "",
            f"⏱️  Timestamp: {report['timestamp']}",
            "",
            "📈 SUMMARY",
            "-" * 70,
            f"  Total Learnings:      {summary['total_learnings']:,}",
            f"  Total Patterns:       {summary['total_patterns']:,}",
            f"  Active Orchestrators: {summary['orchestrators_active']}",
            f"  Avg Confidence:       {summary['avg_confidence']:.2%}",
            f"  High-Value Tests:     {summary['high_value_tests']:,}",
            f"  Deduplication Rate:   {summary['deduplication_rate']:.2%}",
            f"  Success Rate:         {summary['success_rate']:.2%}",
            "",
        ]

        # Orchestrator statistics
        orches = report["orchestrators"]
        if orches:
            lines.append("🎯 ORCHESTRATOR STATISTICS")
            lines.append("-" * 70)
            for orch_name, stats in orches.items():
                lines.append(f"  {orch_name}:")
                lines.append(f"    Learnings:      {stats['learnings']}")
                lines.append(f"    Patterns:       {stats['patterns']}")
                lines.append(f"    Avg Confidence: {stats['avg_confidence']:.2%}")
            lines.append("")

        # Test quality distribution
        quality = report["test_quality"]
        if quality:
            lines.append("✅ TEST QUALITY DISTRIBUTION")
            lines.append("-" * 70)
            for tier, count in quality.items():
                bar_width = count // 5 + 1  # Scale bars
                bar = "█" * min(bar_width, 20)
                lines.append(f"  {tier:8s}: {bar} ({count})")
            lines.append("")

        # Confidence distribution
        conf = report["confidence"]
        if conf:
            lines.append("🎲 CONFIDENCE DISTRIBUTION")
            lines.append("-" * 70)
            for bucket, count in conf.items():
                bar_width = count // 5 + 1
                bar = "░" * min(bar_width, 20)
                lines.append(f"  {bucket}: {bar} ({count})")
            lines.append("")

        lines.append("=" * 70)
        lines.append("")

        return "\n".join(lines)

    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """
        Get historical snapshots of metrics.

        Returns:
            List of metric snapshots
        """
        return [snapshot.to_dict() for snapshot in self._snapshots]


def get_learning_dashboard() -> LearningDashboard:
    """
    Get singleton LearningDashboard instance.

    Returns:
        LearningDashboard instance
    """
    return LearningDashboard()


__all__ = [
    "LearningDashboard",
    "MetricsSnapshot",
    "get_learning_dashboard",
]
