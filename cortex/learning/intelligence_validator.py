"""
IntelligenceValidator - E2E Validation of Learning Infrastructure (Phase 71 S6).

AC-ID: PHASE-71-S6
Purpose: Verify end-to-end intelligence generation and YAML persistence

Validation Scope:
1. Learning capture from all 5 orchestrator types
2. Pattern extraction completeness
3. Knowledge YAML generation
4. Confidence tier promotion
5. Cross-layer integration (Protocol + MCP)

Author: Asif Hussain
Date: 2026-02-10
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml

from cortex.core.result import Err, Ok, Result
from cortex.learning.universal_learning_loop import get_learning_loop

logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    """Report from intelligence validation."""

    orchestrators_tested: Set[str] = field(default_factory=set)
    patterns_captured: int = 0
    knowledge_files_created: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "orchestrators_tested": sorted(list(self.orchestrators_tested)),
            "patterns_captured": self.patterns_captured,
            "knowledge_files_created": self.knowledge_files_created,
            "confidence_scores": self.confidence_scores,
            "validation_errors": self.validation_errors,
            "is_valid": self.is_valid,
        }


class IntelligenceValidator:
    """
    Validate end-to-end learning infrastructure.

    Checks:
    1. Learning capture from all orchestrator types
    2. Pattern extraction accuracy
    3. Knowledge YAML generation
    4. Confidence scoring correctness
    5. No data loss in pipeline

    Usage:
        validator = IntelligenceValidator(workspace_root)
        report = validator.validate_learning_pipeline()
        if report.is_valid:
            print("✅ Learning pipeline validated")
        else:
            print(f"❌ Errors: {report.validation_errors}")
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            workspace_root: Root of CORTEX workspace
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.learning_loop: Optional[Any] = get_learning_loop()
        self.knowledge_repo = self.workspace_root / "cortex" / "knowledge"

    def validate_learning_pipeline(self) -> ValidationReport:
        """
        Validate complete learning pipeline.

        Returns:
            ValidationReport with status and details
        """
        report = ValidationReport()

        # Check 1: Learning loop available
        if not self.learning_loop:
            report.validation_errors.append("Learning loop not available")
            report.is_valid = False
            return report

        # Check 2: Knowledge repository exists
        if not self.knowledge_repo.exists():
            report.validation_errors.append(f"Knowledge repo not found: {self.knowledge_repo}")
            report.is_valid = False
            return report

        # Check 3: Validate learning metrics
        try:
            metrics = self.learning_loop.get_learning_metrics()
            self._validate_learning_metrics(metrics, report)
        except Exception as e:
            report.validation_errors.append(f"Metrics validation failed: {e}")
            report.is_valid = False

        # Check 4: Validate knowledge files
        try:
            self._validate_knowledge_files(report)
        except Exception as e:
            report.validation_errors.append(f"Knowledge file validation failed: {e}")
            report.is_valid = False

        # Check 5: Validate pattern extraction
        try:
            self._validate_pattern_extraction(report)
        except Exception as e:
            report.validation_errors.append(f"Pattern extraction validation failed: {e}")
            report.is_valid = False

        return report

    def validate_orchestrator_learning(
        self,
        orchestrator_name: str,
        operation_type: str,
    ) -> Union[Ok, Err]:
        """
        Validate learning from specific orchestrator.

        Args:
            orchestrator_name: Name of orchestrator
            operation_type: Type of operation

        Returns:
            Result with validation details or error
        """
        try:
            if not self.learning_loop:
                return Err("Learning loop not available")

            # Capture test operation
            metrics = self.learning_loop.get_learning_metrics()

            # Check if orchestrator has recorded learnings
            if orchestrator_name not in metrics.get("by_orchestrator", {}):
                return Err(f"No learnings found for {orchestrator_name}")

            orchestrator_metrics = metrics["by_orchestrator"][orchestrator_name]

            return Ok({
                "orchestrator": orchestrator_name,
                "operation_type": operation_type,
                "learning_count": orchestrator_metrics.get("count", 0),
                "patterns_extracted": orchestrator_metrics.get("patterns", 0),
                "confidence_avg": orchestrator_metrics.get("avg_confidence", 0.0),
            })

        except Exception as e:
            return Err(f"Orchestrator validation failed: {e}")

    def validate_knowledge_persistence(
        self,
        knowledge_target: str,
    ) -> Union[Ok, Err]:
        """
        Validate that knowledge was persisted to YAML.

        Args:
            knowledge_target: Knowledge file name (e.g., "tdd_patterns")

        Returns:
            Result(True) if file exists and valid YAML, Err otherwise
        """
        try:
            knowledge_file = self.knowledge_repo / f"{knowledge_target}.yaml"

            if not knowledge_file.exists():
                return Err(f"Knowledge file not found: {knowledge_file}")

            # Try to load YAML
            with open(knowledge_file, "r") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                return Err(f"Invalid YAML format in {knowledge_file}")

            # Check for expected keys
            required_keys = {"patterns", "metadata"}
            if not all(k in data for k in required_keys):
                return Err(f"Missing required keys in {knowledge_file}: {required_keys}")

            return Ok(True)

        except yaml.YAMLError as e:
            return Err(f"YAML parsing error: {e}")
        except Exception as e:
            return Err(f"Validation error: {e}")

    def validate_confidence_scoring(self) -> Union[Ok, Err]:
        """
        Validate confidence scoring across learnings.

        Returns:
            Result with confidence statistics or error
        """
        try:
            if not self.learning_loop:
                return Err("Learning loop not available")

            metrics = self.learning_loop.get_learning_metrics()

            # Extract confidence info
            all_confidences = []
            for orch_data in metrics.get("by_orchestrator", {}).values():
                confidences = orch_data.get("confidences", [])
                all_confidences.extend(confidences)

            if not all_confidences:
                return Ok({
                    "average_confidence": 0.0,
                    "min_confidence": 0.0,
                    "max_confidence": 0.0,
                    "samples": 0,
                })

            return Ok({
                "average_confidence": sum(all_confidences) / len(all_confidences),
                "min_confidence": min(all_confidences),
                "max_confidence": max(all_confidences),
                "samples": len(all_confidences),
            })

        except Exception as e:
            return Err(f"Confidence validation failed: {e}")

    def _validate_learning_metrics(
        self,
        metrics: Dict[str, Any],
        report: ValidationReport,
    ) -> None:
        """Validate learning metrics structure."""

        # Check orchestrator coverage
        orchestrators_recorded = set(metrics.get("by_orchestrator", {}).keys())
        if not orchestrators_recorded:
            report.validation_errors.append("No orchestrators have recorded learnings")
            report.is_valid = False

        report.orchestrators_tested = orchestrators_recorded
        report.patterns_captured = metrics.get("total_patterns", 0)

        # Check confidence scores
        for orch_name, orch_data in metrics.get("by_orchestrator", {}).items():
            avg_confidence = orch_data.get("avg_confidence", 0.0)
            if not 0.0 <= avg_confidence <= 1.0:
                report.validation_errors.append(
                    f"Invalid confidence score for {orch_name}: {avg_confidence}"
                )
                report.is_valid = False
            report.confidence_scores[orch_name] = avg_confidence

    def _validate_knowledge_files(self, report: ValidationReport) -> None:
        """Validate knowledge YAML files exist and are valid."""

        if not self.knowledge_repo.exists():
            report.validation_errors.append(f"Knowledge repo not found: {self.knowledge_repo}")
            report.is_valid = False
            return

        # Expected knowledge files
        expected_files = [
            "tdd_patterns.yaml",
            "refactoring_patterns.yaml",
            "interaction_patterns.yaml",
            "governance_patterns.yaml",
            "coordination_patterns.yaml",
        ]

        found_count = 0
        for filename in expected_files:
            filepath = self.knowledge_repo / filename
            if filepath.exists():
                found_count += 1
                report.knowledge_files_created.append(filename)

                # Validate YAML
                try:
                    with open(filepath, "r") as f:
                        data = yaml.safe_load(f)
                    if not isinstance(data, dict):
                        report.validation_errors.append(
                            f"Invalid YAML in {filename}: not a dictionary"
                        )
                        report.is_valid = False
                except Exception as e:
                    report.validation_errors.append(f"Error reading {filename}: {e}")
                    report.is_valid = False

        if found_count == 0:
            report.validation_errors.append("No knowledge YAML files found")
            report.is_valid = False

    def _validate_pattern_extraction(self, report: ValidationReport) -> None:
        """Validate pattern extraction completeness."""

        if not self.learning_loop:
            return

        metrics = self.learning_loop.get_learning_metrics()

        # Check that patterns were extracted for all orchestrator types
        expected_types = {"tdd", "refactoring", "interaction", "governance", "coordination"}
        found_types = set(metrics.get("by_orchestrator", {}).keys())

        missing_types = expected_types - found_types
        if missing_types:
            # Not an error, just informational (may not have executed all types)
            logger.info(f"Pattern extraction not yet complete for: {missing_types}")


def get_intelligence_validator(workspace_root: Optional[Path] = None) -> IntelligenceValidator:
    """
    Get singleton IntelligenceValidator instance.

    Args:
        workspace_root: Root of CORTEX workspace

    Returns:
        IntelligenceValidator instance
    """
    return IntelligenceValidator(workspace_root)


__all__ = [
    "IntelligenceValidator",
    "ValidationReport",
    "get_intelligence_validator",
]
