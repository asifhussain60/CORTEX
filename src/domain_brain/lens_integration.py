"""LENS Integration Layer for Domain Brain (AC-DB-004-01).

Integrates Domain Brain with LENS Intent Router for per-turn knowledge synthesis
and intelligent conflict resolution. Enables Domain Brain to query LENS for
synthesis recommendations when conflicts arise.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from src.domain_brain.models import Domain, Entity, Conflict, AuditOperationType
from src.domain_brain.api import DomainBrainAPI


@dataclass
class LENSQuery:
    """Query to send to LENS for synthesis."""

    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conflict_id: str = ""
    domain_id: str = ""
    source_values: Dict[str, Any] = field(default_factory=dict)
    attribute: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_id": self.query_id,
            "conflict_id": self.conflict_id,
            "domain_id": self.domain_id,
            "source_values": self.source_values,
            "attribute": self.attribute,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LENSSynthesis:
    """Synthesis recommendation from LENS."""

    synthesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str = ""
    recommended_value: Any = None
    confidence: float = 0.0
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "synthesis_id": self.synthesis_id,
            "query_id": self.query_id,
            "recommended_value": self.recommended_value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
        }


class LENSIntegrationLayer:
    """Integrates Domain Brain with LENS for intelligent conflict resolution.

    LENS (Logic-driven Entailment & Negotiation Synthesis) provides:
    - Per-turn execution model
    - Multi-phase synthesis (Recognition, Routing, Evaluation, Navigation)
    - Knowledge graph reasoning
    - Intelligent conflict resolution

    This layer enables Domain Brain to query LENS when conflicts arise and
    apply LENS recommendations while maintaining source hierarchy.
    """

    def __init__(self, domain_brain_api: DomainBrainAPI) -> None:
        """Initialize LENS integration layer.

        Args:
            domain_brain_api: API for interacting with Domain Brain
        """
        self.domain_brain_api = domain_brain_api
        self.synthesis_cache: Dict[str, LENSSynthesis] = {}
        self.query_log: List[LENSQuery] = []
        self.lens_requests_made = 0
        self.lens_syntheses_applied = 0

    def query_lens_for_conflict(self, conflict: Conflict) -> Optional[LENSSynthesis]:
        """Query LENS for synthesis recommendation on a conflict.

        LENS 4-Phase Execution:
        1. Recognition: Understand conflict scope
        2. Routing: Route to appropriate reasoning engine
        3. Evaluation: Evaluate candidate resolutions
        4. Navigation: Select best resolution

        Args:
            conflict: Conflict to resolve

        Returns:
            LENSSynthesis recommendation, or None if LENS defers
        """
        # Create LENS query
        query = LENSQuery(
            conflict_id=conflict.conflict_id,
            domain_id=conflict.domain_id,
            source_values=conflict.source_values,
            attribute=conflict.attribute,
        )

        self.query_log.append(query)
        self.lens_requests_made += 1

        # Simulate LENS 4-phase execution
        synthesis = self._execute_lens_phases(query)

        if synthesis:
            self.synthesis_cache[query.query_id] = synthesis
            self.lens_syntheses_applied += 1

        return synthesis

    def _execute_lens_phases(self, query: LENSQuery) -> Optional[LENSSynthesis]:
        """Execute LENS 4-phase synthesis.

        Args:
            query: LENS query

        Returns:
            Synthesis or None if deferred
        """
        # Phase 1: Recognition
        recognized = self._phase_recognition(query)
        if not recognized:
            return None

        # Phase 2: Routing
        routing_decision = self._phase_routing(query, recognized)
        if not routing_decision:
            return None

        # Phase 3: Evaluation
        candidates = self._phase_evaluation(query, routing_decision)
        if not candidates:
            return None

        # Phase 4: Navigation (select best)
        synthesis = self._phase_navigation(query, candidates)
        
        # Cache synthesis for future queries
        if synthesis:
            self.synthesis_cache[query.query_id] = synthesis
        
        return synthesis

    def _phase_recognition(self, query: LENSQuery) -> Dict[str, Any]:
        """Phase 1: Recognize conflict scope and type.

        Args:
            query: LENS query

        Returns:
            Recognition result or None
        """
        if not query.source_values or len(query.source_values) < 2:
            return None

        return {
            "conflict_scope": "multi_source",
            "source_count": len(query.source_values),
            "attribute": query.attribute,
        }

    def _phase_routing(
        self, query: LENSQuery, recognition: Dict[str, Any]
    ) -> Optional[str]:
        """Phase 2: Route to appropriate reasoning engine.

        Args:
            query: LENS query
            recognition: Recognition result

        Returns:
            Routing decision
        """
        if recognition["conflict_scope"] == "multi_source":
            return "hierarchy_reasoning"

        return None

    def _phase_evaluation(
        self, query: LENSQuery, routing: str
    ) -> List[Dict[str, Any]]:
        """Phase 3: Evaluate candidate resolutions.

        Args:
            query: LENS query
            routing: Routing decision

        Returns:
            List of candidate resolutions
        """
        candidates = []

        # Generate candidates from source values
        for source, value in query.source_values.items():
            candidates.append(
                {
                    "source": source,
                    "value": value,
                    "confidence": 0.8 if source == "BKIO" else 0.6,
                    "reasoning": f"Candidate from {source}",
                }
            )

        return candidates

    def _phase_navigation(
        self, query: LENSQuery, candidates: List[Dict[str, Any]]
    ) -> LENSSynthesis:
        """Phase 4: Select best resolution.

        Uses hierarchy: BKIO > RELATIONSHIPS > AST > GIT > LENS

        Args:
            query: LENS query
            candidates: Candidate resolutions

        Returns:
            Selected synthesis
        """
        # Sort by confidence (BKIO highest, then others)
        sorted_candidates = sorted(
            candidates, key=lambda x: (x["source"] != "BKIO", -x["confidence"])
        )

        best = sorted_candidates[0]

        return LENSSynthesis(
            query_id=query.query_id,
            recommended_value=best["value"],
            confidence=best["confidence"],
            reasoning=f"Selected {best['source']}: {best['reasoning']}",
        )

    def apply_synthesis_to_domain(
        self,
        domain: Domain,
        conflict: Conflict,
        synthesis: LENSSynthesis,
    ) -> None:
        """Apply LENS synthesis recommendation to domain.

        Args:
            domain: Domain to update
            conflict: Conflict that was resolved
            synthesis: Synthesis recommendation to apply
        """
        # Find entity(ies) affected by this conflict
        for entity_id, entity in domain.entities.items():
            # Check if this entity is involved in the conflict
            if conflict.attribute in ["description", "name", "source"]:
                # Update the attribute with synthesis value
                if conflict.attribute == "description":
                    entity.description = synthesis.recommended_value
                elif conflict.attribute == "name":
                    entity.name = synthesis.recommended_value
                elif conflict.attribute == "source":
                    entity.source = synthesis.recommended_value

                # Mark synthesis applied
                entity.synthesis_applied = True
                self.lens_syntheses_applied += 1

    def get_synthesis_status(self) -> Dict[str, Any]:
        """Get LENS synthesis status.

        Returns:
            Status dictionary
        """
        return {
            "lens_requests_made": self.lens_requests_made,
            "lens_syntheses_applied": self.lens_syntheses_applied,
            "synthesis_cache_size": len(self.synthesis_cache),
            "query_log_size": len(self.query_log),
            "success_rate": (
                self.lens_syntheses_applied / self.lens_requests_made * 100
                if self.lens_requests_made > 0
                else 0
            ),
        }

    def execute_per_turn(self, domains: List[Domain]) -> Dict[str, Any]:
        """Execute LENS synthesis per turn (per-turn execution model).

        Args:
            domains: Domains to process

        Returns:
            Execution results
        """
        results = {
            "domains_processed": 0,
            "conflicts_resolved": 0,
            "syntheses_applied": 0,
        }

        for domain in domains:
            results["domains_processed"] += 1

            # Process conflicts in this domain
            for conflict in domain.conflicts:
                results["conflicts_resolved"] += 1

                # Query LENS for synthesis
                synthesis = self.query_lens_for_conflict(conflict)
                if synthesis and synthesis.confidence > 0.5:
                    self.apply_synthesis_to_domain(domain, conflict, synthesis)
                    results["syntheses_applied"] += 1

        return results

    def log_lens_audit(self, message: str) -> None:
        """Log LENS activity to audit trail.

        Args:
            message: Message to log
        """
        self.domain_brain_api.audit_logger.log_operation(
            AuditOperationType.AC_EXECUTE,
            description=f"LENS: {message}",
            user="lens-integration",
        )
