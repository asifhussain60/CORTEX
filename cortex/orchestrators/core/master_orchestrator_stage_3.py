"""Stage 3: Knowledge — LENS graph building and recommendation synthesis.

Implements Stage 3 of the Master Orchestrator pipeline.
Builds a knowledge graph from Stage 1/2 outputs and synthesises
LENS-phase recommendations for Stage 4 approval.

CORE Governance:
    CORE-008: TDD mandatory
    CORE-011: Type hints on all functions
    CORE-012: Docstrings on all public APIs
    CORE-027: Audit trail logging

AC-PROD-003-03
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result


@dataclass
class Stage3KnowledgeContext:
    """Input context for Stage 3 knowledge processing.

    Attributes:
        operation: Operation type from Stage 1
        stage1_output: Output produced by Stage 1
        scan_output: Repository scan output from Stage 2 (optional)
        domain: Target domain
        metadata: Additional processing metadata
    """

    operation: str
    stage1_output: Optional[Any] = None
    scan_output: Optional[Any] = None
    domain: str = "core"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Stage3Output:
    """Output produced by Stage 3 knowledge synthesis.

    Attributes:
        operation: Operation type
        stage1_output: Forwarded Stage 1 output
        knowledge_graph: Entity/relationship graph built from context
        lens_recommendations: Ordered LENS-phase recommendations
        confidence_score: Synthesis confidence (0.0–1.0)
        domain: Target domain
        metadata: Additional metadata
    """

    operation: str
    stage1_output: Optional[Any] = None
    knowledge_graph: Dict[str, Any] = field(default_factory=dict)
    lens_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.85
    domain: str = "core"
    metadata: Dict[str, Any] = field(default_factory=dict)


class MasterOrchestrationStage3:
    """Stage 3 of the Master Orchestrator pipeline — Knowledge Synthesis.

    Builds a knowledge graph from stage outputs and produces LENS-phase
    recommendations used by Stage 4 for approval gating.

    Example:
        >>> stage3 = MasterOrchestrationStage3()
        >>> ctx = Stage3KnowledgeContext(operation="implement_oauth2", domain="auth")
        >>> result = stage3.synthesise_knowledge(ctx)
        >>> assert result.is_ok()
    """

    def __init__(self) -> None:
        """Initialise Stage 3 with logger and empty history."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.knowledge_history: List[Dict[str, Any]] = []

    def synthesise_knowledge(
        self, context: Stage3KnowledgeContext
    ) -> Result[Stage3Output]:
        """Build knowledge graph and synthesise recommendations.

        Args:
            context: Stage3KnowledgeContext with operation and prior outputs

        Returns:
            Result[Stage3Output] — Ok on success, Err on failure
        """
        if context is None:
            return Err("Stage3KnowledgeContext must not be None")

        try:
            graph = self._build_knowledge_graph(context)
            recommendations = self._build_recommendations(context, graph)
            confidence = self._compute_confidence(context, graph)

            output = Stage3Output(
                operation=context.operation,
                stage1_output=context.stage1_output,
                knowledge_graph=graph,
                lens_recommendations=recommendations,
                confidence_score=confidence,
                domain=context.domain,
            )

            self.knowledge_history.append(
                {
                    "operation": context.operation,
                    "domain": context.domain,
                    "confidence": confidence,
                    "entities": len(graph.get("entities", [])),
                }
            )
            self.logger.debug(
                "Stage3: synthesised op=%s domain=%s confidence=%.2f",
                context.operation,
                context.domain,
                confidence,
            )
            return Ok(output)

        except Exception as exc:  # noqa: BLE001
            self.logger.error("Stage3 error: %s", exc)
            return Err(str(exc))

    def get_knowledge_history(self) -> List[Dict[str, Any]]:
        """Return chronological knowledge synthesis history.

        Returns:
            List of knowledge synthesis result dicts
        """
        return list(self.knowledge_history)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_knowledge_graph(
        self, context: Stage3KnowledgeContext
    ) -> Dict[str, Any]:
        """Build a knowledge entity/relationship graph from context.

        Args:
            context: Stage3KnowledgeContext

        Returns:
            Dict with 'entities' and 'relationships' keys
        """
        entities: List[str] = []
        keywords = []
        if context.stage1_output and hasattr(context.stage1_output, "keywords"):
            keywords = context.stage1_output.keywords or []
        for kw in keywords:
            entities.append(kw.capitalize())

        return {
            "entities": entities,
            "relationships": [],
            "domain": context.domain,
        }

    def _build_recommendations(
        self,
        context: Stage3KnowledgeContext,
        graph: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Synthesise LENS-phase recommendations from the graph.

        Args:
            context: Stage3KnowledgeContext
            graph: Knowledge graph produced by _build_knowledge_graph

        Returns:
            List of recommendation dicts with 'phase' and 'recommendation'
        """
        recommendations: List[Dict[str, Any]] = []
        if graph.get("entities"):
            recommendations.append(
                {
                    "phase": "language",
                    "recommendation": f"Analyse {context.domain} domain entities",
                }
            )
        recommendations.append(
            {
                "phase": "synthesis",
                "recommendation": f"Apply {context.operation} pattern in {context.domain}",
            }
        )
        return recommendations

    def _compute_confidence(
        self,
        context: Stage3KnowledgeContext,
        graph: Dict[str, Any],
    ) -> float:
        """Compute confidence based on graph density and stage 1 output.

        Args:
            context: Stage3KnowledgeContext
            graph: Built knowledge graph

        Returns:
            Confidence score in range [0.0, 1.0]
        """
        base = 0.75
        entity_count = len(graph.get("entities", []))
        entity_bonus = min(entity_count * 0.02, 0.15)

        stage1_confidence = 0.0
        if context.stage1_output and hasattr(context.stage1_output, "confidence_score"):
            stage1_confidence = context.stage1_output.confidence_score or 0.0

        return min(base + entity_bonus + stage1_confidence * 0.10, 1.0)
