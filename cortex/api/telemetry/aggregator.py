"""Aggregation engine for telemetry insights and GitHub issue auto-generation (AC-UNIFIED-DEPLOY-001-03)."""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json
import hashlib
import logging


logger = logging.getLogger(__name__)


@dataclass
class ErrorPattern:
    """Aggregated error pattern for analysis."""

    error_id: str
    error_category: str
    impact_score: float  # frequency × severity × reproducibility
    frequency: int  # Number of occurrences
    severity: float  # 0.0-1.0 based on reproducibility
    reproducibility: float  # 0.0-1.0 from original events
    affected_environments: List[str] = field(default_factory=list)
    first_seen: str = ""
    last_seen: str = ""
    trend_direction: str = ""  # "increasing", "decreasing", "stable"


@dataclass
class TelemetryInsight:
    """Aggregated telemetry insight for dashboard."""

    insight_type: str  # "error_pattern", "performance_trend", "capability_gap"
    title: str
    pattern: ErrorPattern
    affected_count: int
    environments: List[str]
    recommendations: List[str]


@dataclass
class GitHubIssuePayload:
    """Payload for auto-generated GitHub issue."""

    title: str
    body: str
    labels: List[str]
    assignees: List[str] = field(default_factory=list)
    impact_level: str = ""  # "critical", "high", "medium", "low"


class TelemetryAggregator:
    """
    Server-side processing pipeline for telemetry insights and automated issue creation.

    Features:
    • Event deduplication
    • Impact score computation
    • Pattern identification
    • GitHub issue auto-creation
    """

    IMPACT_SCORE_THRESHOLD_CRITICAL = 8.5
    IMPACT_SCORE_THRESHOLD_HIGH = 6.0
    IMPACT_SCORE_THRESHOLD_MEDIUM = 3.0

    def __init__(self, time_window_hours: int = 24):
        """
        Initialize aggregator.

        Args:
            time_window_hours: Time window for aggregation (default 24h).
        """
        self.time_window = timedelta(hours=time_window_hours)
        self.deduplication_cache: Dict[str, ErrorPattern] = {}
        self.patterns: List[ErrorPattern] = []

    def compute_impact_score(
        self, frequency: int, severity: float, reproducibility: float
    ) -> float:
        """
        Compute impact score for error pattern.

        Formula: (frequency × severity × reproducibility)

        Args:
            frequency: Number of occurrences (normalized to 0-1).
            severity: Severity component (0-1).
            reproducibility: Reproducibility score (0-1).

        Returns:
            Impact score (0-10).
        """
        # Normalize frequency (cap at 100 for scoring)
        freq_normalized = min(frequency / 100.0, 1.0)

        # Impact = (frequency × severity × reproducibility) × 10
        impact = freq_normalized * severity * reproducibility * 10.0
        return impact

    def deduplicate_errors(
        self, events: List[Dict[str, Any]]
    ) -> Dict[str, ErrorPattern]:
        """
        Deduplicate error events within time window.

        Groups by error_id + environment_signature + 1h window.

        Args:
            events: List of error events.

        Returns:
            Dict of deduplicated patterns by error_id.
        """
        patterns: Dict[str, ErrorPattern] = {}

        for event in events:
            if event.get("event_type") != "error":
                continue

            error_id = event.get("error_id", "unknown")
            env_sig = event.get("environment_signature", "unknown")
            category = event.get("error_category", "unknown")
            reproducibility = event.get("reproducibility_score", 0.5)
            first_seen = event.get("first_seen_at", datetime.now().isoformat())
            last_seen = event.get("last_seen_at", datetime.now().isoformat())
            occurrence_count = event.get("occurrence_count", 1)

            # Create composite key (error_id + environment + 1h window)
            event_time = datetime.fromisoformat(first_seen)
            window_key = event_time.replace(minute=0, second=0, microsecond=0)
            composite_key = f"{error_id}:{env_sig}:{window_key.isoformat()}"

            if composite_key not in patterns:
                patterns[composite_key] = ErrorPattern(
                    error_id=error_id,
                    error_category=category,
                    impact_score=0.0,
                    frequency=0,
                    severity=0.8,  # Default severity
                    reproducibility=reproducibility,
                    affected_environments=[env_sig],
                    first_seen=first_seen,
                    last_seen=last_seen,
                )

            # Update pattern
            pattern = patterns[composite_key]
            pattern.frequency += occurrence_count

            if env_sig not in pattern.affected_environments:
                pattern.affected_environments.append(env_sig)

            # Compute impact score
            pattern.impact_score = self.compute_impact_score(
                pattern.frequency, pattern.severity, pattern.reproducibility
            )

        return patterns

    def identify_trends(
        self, current_patterns: Dict[str, ErrorPattern],
        historical_patterns: Optional[Dict[str, ErrorPattern]] = None
    ) -> Dict[str, ErrorPattern]:
        """
        Identify trends in patterns (increasing, decreasing, stable).

        Args:
            current_patterns: Patterns from current time window.
            historical_patterns: Patterns from previous time window (optional).

        Returns:
            Current patterns with trend_direction populated.
        """
        for key, pattern in current_patterns.items():
            if historical_patterns is None:
                pattern.trend_direction = "stable"
                continue

            # Find matching pattern in historical data
            hist_pattern = None
            for h_key, h_pattern in historical_patterns.items():
                if h_pattern.error_id == pattern.error_id:
                    hist_pattern = h_pattern
                    break

            if hist_pattern is None:
                pattern.trend_direction = "new"
            else:
                # Compare frequencies
                if pattern.frequency > hist_pattern.frequency * 1.5:
                    pattern.trend_direction = "increasing"
                elif pattern.frequency < hist_pattern.frequency * 0.67:
                    pattern.trend_direction = "decreasing"
                else:
                    pattern.trend_direction = "stable"

        return current_patterns

    def generate_insights(
        self, patterns: Dict[str, ErrorPattern]
    ) -> List[TelemetryInsight]:
        """
        Generate actionable insights from patterns.

        Args:
            patterns: Deduplicated error patterns.

        Returns:
            List of insights.
        """
        insights: List[TelemetryInsight] = []

        # Sort by impact score
        sorted_patterns = sorted(
            patterns.values(), key=lambda p: p.impact_score, reverse=True
        )

        for pattern in sorted_patterns[:10]:  # Top 10 patterns
            recommendations = self._generate_recommendations(pattern)
            insight = TelemetryInsight(
                insight_type="error_pattern",
                title=f"{pattern.error_category} ({pattern.error_id[:8]}...)",
                pattern=pattern,
                affected_count=pattern.frequency,
                environments=pattern.affected_environments,
                recommendations=recommendations,
            )
            insights.append(insight)

        return insights

    def _generate_recommendations(self, pattern: ErrorPattern) -> List[str]:
        """Generate recommendations for a pattern."""
        recommendations = []

        if pattern.reproducibility > 0.8:
            recommendations.append("Error is highly reproducible - good for fixing")
        if pattern.impact_score > self.IMPACT_SCORE_THRESHOLD_CRITICAL:
            recommendations.append("CRITICAL: High impact, prioritize fixing")
        if pattern.trend_direction == "increasing":
            recommendations.append("Trend is increasing - requires urgent attention")
        if len(pattern.affected_environments) > 3:
            recommendations.append(f"Affects {len(pattern.affected_environments)} environments")

        return recommendations if recommendations else ["Monitor and investigate"]

    def create_github_issue_payload(
        self, insight: TelemetryInsight
    ) -> GitHubIssuePayload:
        """
        Create GitHub issue payload for high-impact pattern.

        Args:
            insight: Telemetry insight.

        Returns:
            GitHub issue payload.
        """
        pattern = insight.pattern

        # Determine impact level
        if pattern.impact_score > self.IMPACT_SCORE_THRESHOLD_CRITICAL:
            impact_level = "critical"
        elif pattern.impact_score > self.IMPACT_SCORE_THRESHOLD_HIGH:
            impact_level = "high"
        elif pattern.impact_score > self.IMPACT_SCORE_THRESHOLD_MEDIUM:
            impact_level = "medium"
        else:
            impact_level = "low"

        # Build issue title
        title = f"[TELEMETRY] {pattern.error_category} ({impact_level.upper()})"

        # Build issue body
        body = f"""## Error Pattern Detected

**Pattern ID**: {pattern.error_id}
**Category**: {pattern.error_category}
**Impact Score**: {pattern.impact_score:.2f}

### Statistics
- **Occurrences**: {pattern.frequency}
- **Reproducibility**: {pattern.reproducibility:.1%}
- **First Seen**: {pattern.first_seen}
- **Last Seen**: {pattern.last_seen}
- **Trend**: {pattern.trend_direction}

### Affected Environments
{self._format_env_list(pattern.affected_environments)}

### Recommendations
{self._format_recommendations(insight.recommendations)}

### Analysis
This pattern was identified by CORTEX telemetry aggregation.
[View Telemetry Data](https://cortex-ai.io/telemetry)

---
*Auto-generated by CORTEX Unified Deployment System*
"""

        labels = ["telemetry-generated"]
        if impact_level == "critical":
            labels.append("p0-critical")
        elif impact_level == "high":
            labels.append("p1-high")
        elif impact_level == "medium":
            labels.append("p2-medium")

        return GitHubIssuePayload(
            title=title,
            body=body,
            labels=labels,
            impact_level=impact_level,
        )

    def _format_env_list(self, envs: List[str]) -> str:
        """Format environment list for GitHub issue."""
        return "\n".join(f"- `{env[:16]}`..." for env in envs[:5])

    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations for GitHub issue."""
        return "\n".join(f"- {rec}" for rec in recommendations)

    def aggregate_events(
        self,
        events: List[Dict[str, Any]],
        historical_patterns: Optional[Dict[str, ErrorPattern]] = None,
    ) -> Tuple[List[ErrorPattern], List[TelemetryInsight], List[GitHubIssuePayload]]:
        """
        Complete aggregation pipeline.

        Args:
            events: List of telemetry events.
            historical_patterns: Previous time window patterns (optional).

        Returns:
            Tuple of (patterns, insights, github_issues).
        """
        # Deduplicate
        patterns = self.deduplicate_errors(events)

        # Identify trends
        patterns = self.identify_trends(patterns, historical_patterns)

        # Generate insights
        insights = self.generate_insights(patterns)

        # Create GitHub issues for high-impact patterns
        github_issues = []
        for insight in insights:
            if insight.pattern.impact_score >= self.IMPACT_SCORE_THRESHOLD_HIGH:
                issue = self.create_github_issue_payload(insight)
                github_issues.append(issue)

        self.patterns = list(patterns.values())
        return list(patterns.values()), insights, github_issues
