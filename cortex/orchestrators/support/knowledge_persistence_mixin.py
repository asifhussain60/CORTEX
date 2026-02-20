"""
Knowledge Persistence Mixin for Repository Onboarding - Phase 12 S4

AC-PHASE71-012: Knowledge persistence in onboarding

Mixin that adds knowledge persistence capabilities to onboarding orchestrator:
- Captures learnings during repository analysis
- Extracts patterns from onboarding outcomes
- Integrates with brain layers for intelligence
- Generates knowledge artifacts

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cortex.intelligence.learning.universal_learning_loop import UniversalLearningLoop
from cortex.intelligence.learning.knowledge_synthesizer import KnowledgeSynthesizer
from cortex.intelligence.perception.pattern_registry import PatternRegistry
from cortex.intelligence.reasoning.strategy_selector import StrategySelector
from cortex.intelligence.action.execution_planner import ExecutionPlanner

logger = logging.getLogger(__name__)


class KnowledgePersistenceMixin:
    """
    Mixin for adding knowledge persistence to onboarding.

    Extends onboarding orchestrator with:
    - Pattern capture from repository analysis
    - Brain layer integration
    - Knowledge artifact generation
    - Learning loop integration

    AC-PHASE71-012: Knowledge persistence in onboarding
    """

    def __init__(self) -> None:
        """Initialize knowledge persistence components."""
        super().__init__()  # type: ignore
        self.learning_loop = UniversalLearningLoop()
        self.knowledge_synthesizer = KnowledgeSynthesizer()
        self.pattern_registry = PatternRegistry()
        self.strategy_selector = StrategySelector()
        self.execution_planner = ExecutionPlanner()

    def capture_onboarding_learning(
        self,
        repository_path: str,
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Capture learnings from repository onboarding.

        Args:
            repository_path: Path to repository
            analysis_result: Result from repository analysis

        Returns:
            Learning capture metadata
        """
        try:
            # Extract key patterns
            patterns = self._extract_patterns_from_analysis(analysis_result)

            # Capture each pattern — use correct UniversalLearningLoop.capture_from_operation
            # signature: (orchestrator, operation, context, result) → List[LearningCapture]
            all_captures = []
            for pattern in patterns:
                captures = self.learning_loop.capture_from_operation(
                    orchestrator="OnboardingOrchestrator",
                    operation=f"onboarding:{repository_path}",
                    context={
                        "pattern_type": pattern["type"],
                        **pattern["data"]
                    },
                    result={"status": "success", "confidence": pattern.get("confidence", 0.8)},
                )
                all_captures.extend(captures if isinstance(captures, list) else [captures])

            logger.info(
                f"Captured {len(all_captures)} patterns from "
                f"onboarding {repository_path}"
            )

            return {
                "patterns_captured": len(all_captures),
                "pattern_ids": [
                    getattr(c, "pattern_id", None) or (c.get("pattern_id") if isinstance(c, dict) else None)
                    for c in all_captures
                ],
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Failed to capture onboarding learning: {e}")
            return {
                "patterns_captured": 0,
                "status": "failed",
                "error": str(e)
            }

    def enhance_with_brain_intelligence(
        self,
        repository_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance onboarding with brain layer intelligence.

        Args:
            repository_context: Repository analysis context

        Returns:
            Enhancement results with detected patterns and strategies
        """
        try:
            # Detect similar patterns — use correct PatternRegistry.detect_patterns
            # signature: (repository_analysis, fuzzy=False)
            detected_patterns = self.pattern_registry.detect_patterns(
                repository_context,
                fuzzy=False
            )

            # Select strategies based on context — correct sig: (context,)
            strategies = self.strategy_selector.select_strategies(
                repository_context
            )

            # Generate execution plan
            execution_plan = self.execution_planner.generate_plan(
                repository_context
            )

            logger.info(
                f"Brain enhancement: {len(detected_patterns)} patterns, "
                f"{len(strategies)} strategies"
            )

            return {
                "patterns_detected": len(detected_patterns),
                "strategies_recommended": len(strategies),
                "execution_plan_steps": len(execution_plan.steps),
                "detected_patterns": detected_patterns,
                "strategies": strategies,
                "execution_plan": execution_plan.to_dict()
            }

        except Exception as e:
            logger.error(f"Brain enhancement failed: {e}")
            return {
                "patterns_detected": 0,
                "strategies_recommended": 0,
                "error": str(e)
            }

    def generate_knowledge_artifacts(
        self,
        onboarding_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate knowledge artifacts from onboarding.

        Args:
            onboarding_data: Data from onboarding process

        Returns:
            Generated artifact metadata
        """
        try:
            artifacts = []

            # Generate pattern template if patterns detected
            if "patterns" in onboarding_data:
                for pattern in onboarding_data["patterns"]:
                    template = self.knowledge_synthesizer.generate_pattern_template(
                        extracted_pattern=pattern
                    )
                    artifacts.append({
                        "type": "template",
                        "pattern_id": template.get("pattern_id")
                    })

            # Generate best practices YAML
            if "best_practices" in onboarding_data:
                yaml_artifact = self.knowledge_synthesizer.generate_best_practices_yaml(
                    category=onboarding_data.get("category", "repository"),
                    practices=onboarding_data["best_practices"]
                )
                artifacts.append({
                    "type": "best_practices",
                    "artifact": yaml_artifact
                })

            logger.info(f"Generated {len(artifacts)} knowledge artifacts")

            return {
                "artifacts_generated": len(artifacts),
                "artifacts": artifacts,
                "templates_generated": sum(1 for a in artifacts if a.get("type") == "template"),
                "yaml_files_created": sum(1 for a in artifacts if a.get("type") == "best_practices"),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Artifact generation failed: {e}")
            return {
                "artifacts_generated": 0,
                "status": "failed",
                "error": str(e)
            }

    def promote_high_confidence_learnings(
        self,
        confidence_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Promote high-confidence learnings to knowledge base.

        Args:
            confidence_threshold: Minimum confidence for promotion

        Returns:
            Promotion results
        """
        try:
            merge_result = self.learning_loop.merge_to_knowledge(
                confidence_threshold=confidence_threshold
            )

            logger.info(
                f"Promoted {merge_result['promoted']} learnings to knowledge base"
            )

            return merge_result

        except Exception as e:
            logger.error(f"Learning promotion failed: {e}")
            return {
                "promoted": 0,
                "skipped": 0,
                "error": str(e)
            }

    def get_learning_metrics(self) -> Dict[str, Any]:
        """
        Get learning metrics from onboarding.

        Returns:
            Learning metrics including patterns, promotions, etc.
        """
        try:
            metrics = self.learning_loop.get_learning_metrics()
            return metrics

        except Exception as e:
            logger.error(f"Failed to get learning metrics: {e}")
            return {}

    def _extract_patterns_from_analysis(
        self,
        analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract patterns from repository analysis.

        Args:
            analysis_result: Analysis result dictionary

        Returns:
            List of extracted patterns
        """
        patterns = []

        # Extract architecture pattern
        if "architecture_type" in analysis_result:
            patterns.append({
                "type": "architecture",
                "data": {
                    "architecture_type": analysis_result["architecture_type"],
                    "layer_count": analysis_result.get("layer_count"),
                    "separation_score": analysis_result.get("separation_score")
                },
                "confidence": 0.85
            })

        # Extract code quality patterns
        if "code_quality" in analysis_result:
            patterns.append({
                "type": "code_quality",
                "data": analysis_result["code_quality"],
                "confidence": 0.8
            })

        # Extract testing patterns
        if "test_coverage" in analysis_result or "testing" in analysis_result:
            patterns.append({
                "type": "testing",
                "data": {
                    "coverage": analysis_result.get("test_coverage"),
                    "frameworks": analysis_result.get("testing", {}).get("frameworks")
                },
                "confidence": 0.75
            })

        # Extract detected patterns
        if "patterns_detected" in analysis_result:
            for pattern_name in analysis_result["patterns_detected"]:
                patterns.append({
                    "type": "design_pattern",
                    "data": {"pattern_name": pattern_name},
                    "confidence": 0.7
                })

        return patterns


__all__ = ["KnowledgePersistenceMixin"]
