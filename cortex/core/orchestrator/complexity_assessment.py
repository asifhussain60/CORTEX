"""Complexity Assessment - Evaluates operation and orchestration complexity.

Provides metrics and analysis for operation complexity, resource requirements,
and execution path complexity.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class ComplexityLevel(Enum):
    """Operation complexity levels."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


@dataclass
class ComplexityMetrics:
    """Complexity metrics for an operation.

    Attributes:
        cyclomatic: Cyclomatic complexity (1-inf).
        cognitive: Cognitive complexity (0-100).
        resource_intensity: Resource intensity (0-100).
        temporal_complexity: Temporal complexity score (0-100).
        spatial_complexity: Spatial complexity score (0-100).
    """

    cyclomatic: float
    cognitive: float
    resource_intensity: float
    temporal_complexity: float
    spatial_complexity: float

    def overall_score(self) -> float:
        """Calculate overall complexity score.

        Returns:
            Weighted complexity score (0-100).
        """
        return (
            (self.cyclomatic * 0.2)
            + (self.cognitive * 0.2)
            + (self.resource_intensity * 0.2)
            + (self.temporal_complexity * 0.2)
            + (self.spatial_complexity * 0.2)
        )

    def level(self) -> ComplexityLevel:
        """Determine complexity level.

        Returns:
            ComplexityLevel based on overall score.
        """
        score = self.overall_score()
        if score < 25:
            return ComplexityLevel.SIMPLE
        elif score < 50:
            return ComplexityLevel.MODERATE
        elif score < 75:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.CRITICAL


class ComplexityAssessment:
    """Analyzes and assesses operation complexity."""

    def __init__(self) -> None:
        """Initialize complexity assessment engine."""
        self.cache: Dict[str, ComplexityMetrics] = {}

    def assess(self, operation_id: str, details: Dict[str, Any]) -> ComplexityMetrics:
        """Assess complexity of an operation.

        Args:
            operation_id: Operation identifier.
            details: Operation details dictionary.

        Returns:
            ComplexityMetrics for the operation.
        """
        # Check cache
        if operation_id in self.cache:
            return self.cache[operation_id]

        # Calculate metrics
        cyclomatic = self._calculate_cyclomatic(details)
        cognitive = self._calculate_cognitive(details)
        resource_intensity = self._calculate_resource_intensity(details)
        temporal = self._calculate_temporal_complexity(details)
        spatial = self._calculate_spatial_complexity(details)

        metrics = ComplexityMetrics(
            cyclomatic=cyclomatic,
            cognitive=cognitive,
            resource_intensity=resource_intensity,
            temporal_complexity=temporal,
            spatial_complexity=spatial,
        )

        # Cache result
        self.cache[operation_id] = metrics
        return metrics

    def _calculate_cyclomatic(self, details: Dict[str, Any]) -> float:
        """Calculate cyclomatic complexity.

        Args:
            details: Operation details.

        Returns:
            Cyclomatic complexity score.
        """
        branches = details.get("branches", 0)
        loops = details.get("loops", 0)
        conditions = details.get("conditions", 0)
        return 1 + branches + loops + conditions

    def _calculate_cognitive(self, details: Dict[str, Any]) -> float:
        """Calculate cognitive complexity.

        Args:
            details: Operation details.

        Returns:
            Cognitive complexity (0-100).
        """
        nesting = details.get("nesting_level", 0)
        decisions = details.get("decision_points", 0)
        abstractions = details.get("abstraction_levels", 0)
        return min(100, (nesting * 10) + (decisions * 5) + (abstractions * 2))

    def _calculate_resource_intensity(self, details: Dict[str, Any]) -> float:
        """Calculate resource intensity.

        Args:
            details: Operation details.

        Returns:
            Resource intensity (0-100).
        """
        memory_estimate = details.get("memory_estimate_mb", 0) / 10
        cpu_estimate = details.get("cpu_percentage", 0)
        io_operations = details.get("io_operations", 0) * 2
        return min(100, memory_estimate + cpu_estimate + io_operations)

    def _calculate_temporal_complexity(self, details: Dict[str, Any]) -> float:
        """Calculate temporal complexity.

        Args:
            details: Operation details.

        Returns:
            Temporal complexity (0-100).
        """
        time_estimate = details.get("estimated_time_seconds", 0) / 10
        serialization = details.get("serialization_overhead", 0) * 10
        return min(100, time_estimate + serialization)

    def _calculate_spatial_complexity(self, details: Dict[str, Any]) -> float:
        """Calculate spatial complexity.

        Args:
            details: Operation details.

        Returns:
            Spatial complexity (0-100).
        """
        state_size = details.get("state_size_kb", 0) / 10
        data_structures = details.get("data_structures", 0) * 5
        return min(100, state_size + data_structures)

    def clear_cache(self) -> None:
        """Clear the assessment cache."""
        self.cache.clear()


__all__ = [
    "ComplexityAssessment",
    "ComplexityMetrics",
    "ComplexityLevel",
]
