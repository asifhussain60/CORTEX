"""Change detection and anomaly identification for knowledge repositories.

This module provides comprehensive change detection capabilities for identifying
schema drifts, semantic shifts, coverage gaps, data staleness, and volume anomalies
in knowledge repositories. Implements a 24-hour detection window with 7-day learning mode.

CORE Governance:
- CORE-004: Tier structure (Tier1 service for MasterOrchestrator)
- CORE-011: Type hints (100% coverage with mypy --strict)
- CORE-012: Documentation (100% docstrings)
- CORE-013: Specific exceptions (ValueError, TypeError, etc.)
- CORE-028: Portable paths (no hardcoding)

Performance Targets:
- Detection latency: <50ms per anomaly type
- Memory overhead: <5MB for 10k entries
- Learning mode: 7 days before strict enforcement

Detection Window: 24 hours (86,400 seconds)
Learning Mode: 7 days (604,800 seconds)
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Classification of anomaly types detected in knowledge repositories."""

    SCHEMA_DRIFT = "schema_drift"
    """Unexpected changes in entry structure or field types."""

    SEMANTIC_SHIFT = "semantic_shift"
    """Significant changes in entry meaning or content interpretation."""

    COVERAGE_GAP = "coverage_gap"
    """Unexpected gaps or missing domains/categories."""

    STALENESS = "staleness"
    """Entries that have not been updated within expected intervals."""

    VOLUME_ANOMALY = "volume_anomaly"
    """Unexpected changes in entry volume or query patterns."""


class SeverityLevel(Enum):
    """Severity classification for detected anomalies."""

    INFO = "info"
    """Informational anomaly, no action required."""

    WARNING = "warning"
    """Warning level anomaly, monitoring recommended."""

    CRITICAL = "critical"
    """Critical anomaly, investigation required."""


@dataclass
class AnomalyScore:
    """Quantitative measurement of anomaly severity.

    Attributes:
        value: Score from 0.0 (normal) to 1.0 (severe).
        confidence: Confidence in the score (0.0-1.0).
        reasoning: Human-readable explanation of the score.
    """

    value: float
    confidence: float
    reasoning: str

    def __post_init__(self) -> None:
        """Validate score ranges."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Anomaly score must be 0.0-1.0, got {self.value}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


@dataclass
class AnomalyDetection:
    """Result of anomaly detection analysis.

    Attributes:
        anomaly_type: Classification of anomaly.
        severity: Severity level (INFO, WARNING, CRITICAL).
        score: Quantitative measurement (0.0-1.0).
        affected_entries: List of entry IDs affected.
        detected_at: Timestamp of detection.
        reasoning: Detailed explanation of findings.
        recommendations: Suggested actions.
    """

    anomaly_type: AnomalyType
    severity: SeverityLevel
    score: AnomalyScore
    affected_entries: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.utcnow)
    reasoning: str = ""
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ChangeHistory:
    """Historical record of changes to knowledge entries.

    Attributes:
        entry_id: Unique identifier for the entry.
        timestamps: List of modification timestamps.
        versions: List of entry versions (snapshots).
        changes: Dictionary mapping timestamp to change summary.
    """

    entry_id: str
    timestamps: List[datetime] = field(default_factory=list)
    versions: List[Dict[str, Any]] = field(default_factory=list)
    changes: Dict[datetime, str] = field(default_factory=dict)

    def add_change(self, version: Dict[str, Any], timestamp: datetime, change_summary: str) -> None:
        """Record a change to the entry.

        Args:
            version: Current version of the entry.
            timestamp: When the change occurred.
            change_summary: Description of what changed.
        """
        self.timestamps.append(timestamp)
        self.versions.append(version.copy())
        self.changes[timestamp] = change_summary

    def get_last_change(self) -> Optional[Tuple[datetime, str]]:
        """Get the most recent change.

        Returns:
            Tuple of (timestamp, change_summary) or None if no changes.
        """
        if not self.timestamps:
            return None
        last_ts = self.timestamps[-1]
        return (last_ts, self.changes[last_ts])

    def get_changes_since(self, since: datetime) -> List[Tuple[datetime, str]]:
        """Get all changes since a specific timestamp.

        Args:
            since: Timestamp to start searching from.

        Returns:
            List of (timestamp, change_summary) tuples.
        """
        return [(ts, self.changes[ts]) for ts in self.timestamps if ts >= since]


class AnomalyDetector(ABC):
    """Base class for anomaly detection algorithms.

    Subclasses implement specific detection strategies for different anomaly types.
    """

    def __init__(self, learning_mode_duration: int = 604800) -> None:
        """Initialize detector.

        Args:
            learning_mode_duration: Duration of learning mode in seconds (default: 7 days).
        """
        self.learning_mode_duration = learning_mode_duration
        self.learning_start: Optional[datetime] = None

    def start_learning_mode(self) -> None:
        """Start the learning mode for this detector."""
        self.learning_start = datetime.utcnow()
        logger.info(f"{self.__class__.__name__} entered learning mode until {self._get_learning_end()}")

    def is_learning_mode(self) -> bool:
        """Check if detector is still in learning mode.

        Returns:
            True if learning mode is active, False otherwise.
        """
        if self.learning_start is None:
            return False
        elapsed = (datetime.utcnow() - self.learning_start).total_seconds()
        return elapsed < self.learning_mode_duration

    def _get_learning_end(self) -> datetime:
        """Get when learning mode ends.

        Returns:
            Datetime when learning mode expires.
        """
        if self.learning_start is None:
            return datetime.utcnow()
        return self.learning_start + timedelta(seconds=self.learning_mode_duration)

    @abstractmethod
    def detect(self, entries: List[Dict[str, Any]], history: Dict[str, ChangeHistory]) -> List[AnomalyDetection]:
        """Detect anomalies in the provided entries and history.

        Args:
            entries: Current list of knowledge entries.
            history: Historical change records.

        Returns:
            List of detected anomalies.
        """


class SchemaDriftDetector(AnomalyDetector):
    """Detector for schema drift anomalies.

    Identifies unexpected changes in entry structure, field types, or required fields.
    """

    def __init__(self, learning_mode_duration: int = 604800) -> None:
        """Initialize schema drift detector.

        Args:
            learning_mode_duration: Duration of learning mode in seconds.
        """
        super().__init__(learning_mode_duration)
        self.baseline_schema: Optional[Dict[str, Set[str]]] = None

    def detect(self, entries: List[Dict[str, Any]], history: Dict[str, ChangeHistory]) -> List[AnomalyDetection]:
        """Detect schema drift in entries.

        Args:
            entries: Current list of knowledge entries.
            history: Historical change records.

        Returns:
            List of schema drift anomalies.
        """
        anomalies: List[AnomalyDetection] = []

        if not entries:
            return anomalies

        # Initialize baseline on first run
        if self.baseline_schema is None:
            self.baseline_schema = self._extract_schema(entries)
            self.start_learning_mode()
            return anomalies

        current_schema = self._extract_schema(entries)
        drift_entries: List[str] = []
        score_sum = 0.0

        # Check for schema differences
        for entry_id, current_fields in current_schema.items():
            baseline_fields = self.baseline_schema.get(entry_id, set())
            if current_fields != baseline_fields:
                drift_entries.append(entry_id)
                score_sum += 0.5

        # Check for new fields in existing entries
        for entry_id, current_fields in current_schema.items():
            baseline_fields = self.baseline_schema.get(entry_id, set())
            added_fields = current_fields - baseline_fields
            if added_fields:
                drift_entries.append(entry_id)
                score_sum += len(added_fields) * 0.1

        if drift_entries and not self.is_learning_mode():
            score_value = min(score_sum / max(len(drift_entries), 1) / 5.0, 1.0)
            anomaly = AnomalyDetection(
                anomaly_type=AnomalyType.SCHEMA_DRIFT,
                severity=SeverityLevel.WARNING if score_value < 0.7 else SeverityLevel.CRITICAL,
                score=AnomalyScore(
                    value=score_value,
                    confidence=min(len(drift_entries) / max(len(current_schema), 1), 1.0),
                    reasoning=f"Schema drift detected in {len(drift_entries)} entries",
                ),
                affected_entries=drift_entries,
                reasoning=f"Unexpected schema changes: {len(drift_entries)} entries affected",
                recommendations=["Verify schema changes", "Update baseline if intentional"],
            )
            anomalies.append(anomaly)

        return anomalies

    def _extract_schema(self, entries: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """Extract schema (field names) from entries.

        Args:
            entries: List of entries to analyze.

        Returns:
            Dictionary mapping entry ID to set of field names.
        """
        schema: Dict[str, Set[str]] = {}
        for entry in entries:
            if isinstance(entry, dict) and "id" in entry:
                entry_id = entry["id"]
                schema[entry_id] = set(entry.keys())
        return schema


class SemanticShiftDetector(AnomalyDetector):
    """Detector for semantic shift anomalies.

    Identifies significant changes in entry meaning, content interpretation, or domain categorization.
    """

    def __init__(self, learning_mode_duration: int = 604800) -> None:
        """Initialize semantic shift detector.

        Args:
            learning_mode_duration: Duration of learning mode in seconds.
        """
        super().__init__(learning_mode_duration)
        self.baseline_content: Optional[Dict[str, str]] = None

    def detect(self, entries: List[Dict[str, Any]], history: Dict[str, ChangeHistory]) -> List[AnomalyDetection]:
        """Detect semantic shifts in entries.

        Args:
            entries: Current list of knowledge entries.
            history: Historical change records.

        Returns:
            List of semantic shift anomalies.
        """
        anomalies: List[AnomalyDetection] = []

        if not entries:
            return anomalies

        # Initialize baseline on first run
        if self.baseline_content is None:
            self.baseline_content = self._extract_content(entries)
            self.start_learning_mode()
            return anomalies

        current_content = self._extract_content(entries)
        shifted_entries: List[str] = []
        score_sum = 0.0

        # Check for significant content changes
        for entry_id, current_text in current_content.items():
            baseline_text = self.baseline_content.get(entry_id, "")
            similarity = self._calculate_text_similarity(baseline_text, current_text)
            if similarity < 0.7:  # 30% change threshold
                shifted_entries.append(entry_id)
                score_sum += (1.0 - similarity)

        if shifted_entries and not self.is_learning_mode():
            score_value = min(score_sum / max(len(shifted_entries), 1), 1.0)
            anomaly = AnomalyDetection(
                anomaly_type=AnomalyType.SEMANTIC_SHIFT,
                severity=SeverityLevel.WARNING if score_value < 0.6 else SeverityLevel.CRITICAL,
                score=AnomalyScore(
                    value=score_value,
                    confidence=0.8,
                    reasoning=f"Semantic changes detected in {len(shifted_entries)} entries",
                ),
                affected_entries=shifted_entries,
                reasoning=f"Significant content changes: {len(shifted_entries)} entries affected",
                recommendations=["Review content changes", "Verify domain categorization", "Update documentation"],
            )
            anomalies.append(anomaly)

        return anomalies

    def _extract_content(self, entries: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract content text from entries.

        Args:
            entries: List of entries to analyze.

        Returns:
            Dictionary mapping entry ID to concatenated content text.
        """
        content: Dict[str, str] = {}
        for entry in entries:
            if isinstance(entry, dict) and "id" in entry:
                entry_id = entry["id"]
                # Extract text content fields
                text_parts = []
                for key, value in entry.items():
                    if isinstance(value, str) and key not in {"id", "timestamp"}:
                        text_parts.append(value)
                content[entry_id] = " ".join(text_parts)
        return content

    @staticmethod
    def _calculate_text_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts using word overlap.

        Args:
            text1: First text to compare.
            text2: Second text to compare.

        Returns:
            Similarity score from 0.0 to 1.0.
        """
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0


class CoverageGapDetector(AnomalyDetector):
    """Detector for coverage gap anomalies.

    Identifies unexpected gaps in domains, categories, or knowledge coverage areas.
    """

    def __init__(self, learning_mode_duration: int = 604800) -> None:
        """Initialize coverage gap detector.

        Args:
            learning_mode_duration: Duration of learning mode in seconds.
        """
        super().__init__(learning_mode_duration)
        self.baseline_coverage: Optional[Dict[str, int]] = None

    def detect(self, entries: List[Dict[str, Any]], history: Dict[str, ChangeHistory]) -> List[AnomalyDetection]:
        """Detect coverage gaps in entries.

        Args:
            entries: Current list of knowledge entries.
            history: Historical change records.

        Returns:
            List of coverage gap anomalies.
        """
        anomalies: List[AnomalyDetection] = []

        if not entries:
            return anomalies

        # Initialize baseline on first run
        if self.baseline_coverage is None:
            self.baseline_coverage = self._extract_coverage(entries)
            self.start_learning_mode()
            return anomalies

        current_coverage = self._extract_coverage(entries)
        gap_entries: List[str] = []
        score_sum = 0.0

        # Check for missing domains/categories
        baseline_domains = set(self.baseline_coverage.keys())
        current_domains = set(current_coverage.keys())

        missing_domains = baseline_domains - current_domains
        if missing_domains:
            gap_entries.extend(list(missing_domains))
            score_sum += len(missing_domains) * 0.3

        # Check for significant coverage reduction
        for domain, current_count in current_coverage.items():
            baseline_count = self.baseline_coverage.get(domain, current_count)
            if current_count < baseline_count * 0.8:  # 20% reduction threshold
                gap_entries.append(domain)
                score_sum += (baseline_count - current_count) / max(baseline_count, 1) * 0.5

        if gap_entries and not self.is_learning_mode():
            score_value = min(score_sum / max(len(gap_entries), 1) / 2.0, 1.0)
            anomaly = AnomalyDetection(
                anomaly_type=AnomalyType.COVERAGE_GAP,
                severity=SeverityLevel.WARNING if score_value < 0.6 else SeverityLevel.CRITICAL,
                score=AnomalyScore(
                    value=score_value,
                    confidence=0.75,
                    reasoning=f"Coverage gaps detected in {len(gap_entries)} domains",
                ),
                affected_entries=gap_entries,
                reasoning=f"Knowledge coverage gaps: {len(gap_entries)} areas affected",
                recommendations=["Investigate missing domains", "Replenish coverage", "Verify data integrity"],
            )
            anomalies.append(anomaly)

        return anomalies

    def _extract_coverage(self, entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract coverage metrics from entries.

        Args:
            entries: List of entries to analyze.

        Returns:
            Dictionary mapping domain/category to entry count.
        """
        coverage: Dict[str, int] = {}
        for entry in entries:
            if isinstance(entry, dict):
                # Extract domain or category
                domain = entry.get("domain") or entry.get("category") or "unknown"
                coverage[domain] = coverage.get(domain, 0) + 1
        return coverage


class StalenessDetector(AnomalyDetector):
    """Detector for staleness anomalies.

    Identifies entries that have not been updated within expected intervals.
    """

    def __init__(self, max_age_hours: int = 720, learning_mode_duration: int = 604800) -> None:
        """Initialize staleness detector.

        Args:
            max_age_hours: Maximum age for entries in hours (default: 30 days).
            learning_mode_duration: Duration of learning mode in seconds.
        """
        super().__init__(learning_mode_duration)
        self.max_age_seconds = max_age_hours * 3600

    def detect(self, entries: List[Dict[str, Any]], history: Dict[str, ChangeHistory]) -> List[AnomalyDetection]:
        """Detect stale entries.

        Args:
            entries: Current list of knowledge entries.
            history: Historical change records.

        Returns:
            List of staleness anomalies.
        """
        anomalies: List[AnomalyDetection] = []

        if not entries:
            return anomalies

        now = datetime.utcnow()
        stale_entries: List[str] = []
        score_sum = 0.0

        for entry in entries:
            if isinstance(entry, dict) and "id" in entry:
                entry_id = entry["id"]

                # Get last update time from history or entry timestamp
                last_update = None
                if entry_id in history:
                    change = history[entry_id].get_last_change()
                    if change:
                        last_update = change[0]

                if last_update is None:
                    last_update = entry.get("updated_at") or entry.get("created_at")

                if last_update:
                    if isinstance(last_update, str):
                        try:
                            last_update = datetime.fromisoformat(last_update)
                        except (ValueError, TypeError):
                            last_update = None

                    if last_update:
                        age_seconds = (now - last_update).total_seconds()
                        if age_seconds > self.max_age_seconds:
                            stale_entries.append(entry_id)
                            score_sum += min(age_seconds / self.max_age_seconds, 1.0)

        if stale_entries and not self.is_learning_mode():
            score_value = min(score_sum / max(len(stale_entries), 1), 1.0)
            anomaly = AnomalyDetection(
                anomaly_type=AnomalyType.STALENESS,
                severity=SeverityLevel.WARNING if score_value < 0.5 else SeverityLevel.CRITICAL,
                score=AnomalyScore(
                    value=score_value,
                    confidence=0.9,
                    reasoning=f"Stale entries detected: {len(stale_entries)} entries older than {self.max_age_seconds // 3600} hours",
                ),
                affected_entries=stale_entries,
                reasoning=f"Data staleness: {len(stale_entries)} entries require update",
                recommendations=["Update stale entries", "Review update procedures", "Verify data pipeline"],
            )
            anomalies.append(anomaly)

        return anomalies


class VolumeAnomalyDetector(AnomalyDetector):
    """Detector for volume anomalies.

    Identifies unexpected changes in entry volume or query pattern distributions.
    """

    def __init__(self, variance_threshold: float = 0.3, learning_mode_duration: int = 604800) -> None:
        """Initialize volume anomaly detector.

        Args:
            variance_threshold: Threshold for volume variance (default: 30%).
            learning_mode_duration: Duration of learning mode in seconds.
        """
        super().__init__(learning_mode_duration)
        self.variance_threshold = variance_threshold
        self.baseline_volume: Optional[int] = None
        self.volume_history: List[int] = []

    def detect(self, entries: List[Dict[str, Any]], history: Dict[str, ChangeHistory]) -> List[AnomalyDetection]:
        """Detect volume anomalies in entries.

        Args:
            entries: Current list of knowledge entries.
            history: Historical change records.

        Returns:
            List of volume anomalies.
        """
        anomalies: List[AnomalyDetection] = []

        current_volume = len(entries)
        self.volume_history.append(current_volume)

        # Initialize baseline on first run
        if self.baseline_volume is None:
            self.baseline_volume = current_volume
            self.start_learning_mode()
            return anomalies

        # Keep history to 24 measurements (daily if checked hourly)
        if len(self.volume_history) > 24:
            self.volume_history = self.volume_history[-24:]

        # Calculate variance
        if len(self.volume_history) < 3:
            return anomalies

        avg_volume = sum(self.volume_history) / len(self.volume_history)
        variance = sum((v - avg_volume) ** 2 for v in self.volume_history) / len(self.volume_history)
        std_dev = variance ** 0.5
        cv = (std_dev / avg_volume) if avg_volume > 0 else 0  # Coefficient of variation

        if cv > self.variance_threshold and not self.is_learning_mode():
            anomaly = AnomalyDetection(
                anomaly_type=AnomalyType.VOLUME_ANOMALY,
                severity=SeverityLevel.WARNING if cv < 0.5 else SeverityLevel.CRITICAL,
                score=AnomalyScore(
                    value=min(cv / 2.0, 1.0),
                    confidence=min(len(self.volume_history) / 24.0, 1.0),
                    reasoning=f"Volume variance {cv:.1%} exceeds threshold {self.variance_threshold:.1%}",
                ),
                affected_entries=[],
                reasoning=f"Entry volume anomaly detected (CV: {cv:.1%})",
                recommendations=["Investigate volume fluctuations", "Review ingestion pipeline", "Check for data loss"],
            )
            anomalies.append(anomaly)

        return anomalies


class ChangeDetectionService:
    """Comprehensive change detection service for knowledge repositories.

    Orchestrates multiple anomaly detectors and maintains change history.
    """

    def __init__(self, detection_window_hours: int = 24) -> None:
        """Initialize change detection service.

        Args:
            detection_window_hours: Window for tracking changes in hours (default: 24).
        """
        self.detection_window_seconds = detection_window_hours * 3600
        self.detectors: Dict[AnomalyType, AnomalyDetector] = {
            AnomalyType.SCHEMA_DRIFT: SchemaDriftDetector(),
            AnomalyType.SEMANTIC_SHIFT: SemanticShiftDetector(),
            AnomalyType.COVERAGE_GAP: CoverageGapDetector(),
            AnomalyType.STALENESS: StalenessDetector(),
            AnomalyType.VOLUME_ANOMALY: VolumeAnomalyDetector(),
        }
        self.history: Dict[str, ChangeHistory] = {}

    def record_entry_change(self, entry_id: str, version: Dict[str, Any], change_summary: str) -> None:
        """Record a change to an entry.

        Args:
            entry_id: Unique identifier for the entry.
            version: Current version of the entry.
            change_summary: Description of what changed.
        """
        if entry_id not in self.history:
            self.history[entry_id] = ChangeHistory(entry_id)

        self.history[entry_id].add_change(version, datetime.utcnow(), change_summary)

    def detect_anomalies(self, entries: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect all anomalies in the provided entries.

        Args:
            entries: Current list of knowledge entries.

        Returns:
            List of detected anomalies across all detector types.
        """
        all_anomalies: List[AnomalyDetection] = []

        for anomaly_type, detector in self.detectors.items():
            try:
                anomalies = detector.detect(entries, self.history)
                all_anomalies.extend(anomalies)
            except Exception as e:
                logger.error(f"Error in {anomaly_type.value} detection: {e}")

        return all_anomalies

    def get_critical_anomalies(self, entries: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Get only critical-severity anomalies.

        Args:
            entries: Current list of knowledge entries.

        Returns:
            List of critical anomalies.
        """
        all_anomalies = self.detect_anomalies(entries)
        return [a for a in all_anomalies if a.severity == SeverityLevel.CRITICAL]

    def get_change_summary(self, since: datetime) -> Dict[str, int]:
        """Get summary of changes since a specific timestamp.

        Args:
            since: Timestamp to start from.

        Returns:
            Dictionary with change counts by entry ID.
        """
        summary: Dict[str, int] = {}
        for entry_id, history in self.history.items():
            changes = history.get_changes_since(since)
            if changes:
                summary[entry_id] = len(changes)
        return summary
