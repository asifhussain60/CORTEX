"""
AbsorptionGate — Pattern learning gate using digestive system metaphor.

Absorbs valuable patterns (seen 3+ times with confidence >0.7) into long-term
knowledge (tier3). Mirrors nutrient absorption in digestive system.

Part of CORTEX brain metaphor:
- Sensory neurons: ConvergenceNeuron (detect patterns)
- Motor neurons: WorkflowComposer (execute actions)
- Digestive system: AbsorptionGate (absorb knowledge), FlushManager (remove waste)

Author: CORTEX Phase 84 Stage 2
"""

import logging
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class PatternObservation:
    """Single observation of a pattern in the wild.
    
    Attributes:
        pattern_id: Unique identifier for the pattern.
        confidence: Confidence score (0.0-1.0) for this observation.
        timestamp: When the pattern was observed.
        context: Additional context (file, lines, etc.).
    """
    pattern_id: str
    confidence: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AbsorptionDecision:
    """Decision on whether to absorb a pattern into tier3 knowledge.
    
    Attributes:
        should_absorb: Whether pattern meets absorption criteria.
        reason: Human-readable explanation of decision.
        confidence: Average confidence across all sightings.
        sighting_count: Number of times pattern was observed.
    """
    should_absorb: bool
    reason: str
    confidence: float
    sighting_count: int


# =============================================================================
# ABSORPTION GATE
# =============================================================================

class AbsorptionGate:
    """Pattern learning gate - absorbs valuable patterns into tier3 knowledge.
    
    Digestive metaphor: Absorbs nutrients (valuable patterns) while rejecting
    low-quality or infrequent patterns.
    
    Criteria for absorption:
    - Pattern seen >= min_sightings times
    - Average confidence >= min_confidence
    
    Example:
        >>> gate = AbsorptionGate(min_sightings=3, min_confidence=0.7)
        >>> gate.observe(PatternObservation("error-handling-v1", 0.85, datetime.now(), {}))
        >>> gate.observe(PatternObservation("error-handling-v1", 0.80, datetime.now(), {}))
        >>> gate.observe(PatternObservation("error-handling-v1", 0.82, datetime.now(), {}))
        >>> decision = gate.evaluate("error-handling-v1")
        >>> if decision.should_absorb:
        ...     gate.absorb("error-handling-v1")
    """
    
    def __init__(
        self,
        min_sightings: int = 3,
        min_confidence: float = 0.7,
        tier3_path: Optional[Path] = None,
    ) -> None:
        """Initialize AbsorptionGate.
        
        Args:
            min_sightings: Minimum number of observations required for absorption.
            min_confidence: Minimum average confidence required for absorption.
            tier3_path: Path to tier3 learned-patterns.yaml file.
        """
        self.min_sightings = min_sightings
        self.min_confidence = min_confidence
        self.tier3_path = tier3_path or Path("cortex/knowledge/tier3/learned-patterns.yaml")
        
        # Observation history: pattern_id -> List[PatternObservation]
        self._observations: Dict[str, List[PatternObservation]] = {}
        
        logger.info(
            f"AbsorptionGate initialized: min_sightings={min_sightings}, "
            f"min_confidence={min_confidence}"
        )
    
    def observe(self, observation: PatternObservation) -> None:
        """Record a pattern observation.
        
        Args:
            observation: PatternObservation with pattern_id, confidence, timestamp, context.
        """
        pattern_id = observation.pattern_id
        
        if pattern_id not in self._observations:
            self._observations[pattern_id] = []
        
        self._observations[pattern_id].append(observation)
        
        logger.debug(
            f"Pattern observed: {pattern_id} (confidence={observation.confidence:.2f}, "
            f"total_sightings={len(self._observations[pattern_id])})"
        )
    
    def get_observation_history(self, pattern_id: str) -> List[PatternObservation]:
        """Get all observations for a pattern.
        
        Args:
            pattern_id: Pattern identifier.
            
        Returns:
            List of PatternObservation objects for this pattern.
        """
        return self._observations.get(pattern_id, [])
    
    def evaluate(self, pattern_id: str) -> AbsorptionDecision:
        """Evaluate whether pattern should be absorbed into tier3.
        
        Args:
            pattern_id: Pattern identifier to evaluate.
            
        Returns:
            AbsorptionDecision with should_absorb flag and reasoning.
        """
        observations = self._observations.get(pattern_id, [])
        
        if not observations:
            return AbsorptionDecision(
                should_absorb=False,
                reason="No observations recorded",
                confidence=0.0,
                sighting_count=0,
            )
        
        sighting_count = len(observations)
        avg_confidence = sum(obs.confidence for obs in observations) / sighting_count
        
        # Check criteria
        if sighting_count < self.min_sightings:
            return AbsorptionDecision(
                should_absorb=False,
                reason=f"Insufficient sightings: {sighting_count} < {self.min_sightings}",
                confidence=avg_confidence,
                sighting_count=sighting_count,
            )
        
        if avg_confidence < self.min_confidence:
            return AbsorptionDecision(
                should_absorb=False,
                reason=f"Low confidence: {avg_confidence:.2f} < {self.min_confidence}",
                confidence=avg_confidence,
                sighting_count=sighting_count,
            )
        
        # Criteria met - approve absorption
        return AbsorptionDecision(
            should_absorb=True,
            reason=f"Pattern seen {sighting_count} times with avg confidence {avg_confidence:.2f}",
            confidence=avg_confidence,
            sighting_count=sighting_count,
        )
    
    def absorb(self, pattern_id: str) -> bool:
        """Absorb pattern into tier3 knowledge.
        
        Args:
            pattern_id: Pattern identifier to absorb.
            
        Returns:
            True if pattern was absorbed, False otherwise.
        """
        decision = self.evaluate(pattern_id)
        
        if not decision.should_absorb:
            logger.warning(f"Pattern {pattern_id} does not meet absorption criteria: {decision.reason}")
            return False
        
        observations = self._observations[pattern_id]
        
        # Build pattern entry
        pattern_entry = {
            "pattern_id": pattern_id,
            "absorbed_at": datetime.now().isoformat(),
            "sighting_count": decision.sighting_count,
            "confidence": decision.confidence,
            "first_seen": observations[0].timestamp.isoformat(),
            "last_seen": observations[-1].timestamp.isoformat(),
            "contexts": [obs.context for obs in observations],
        }
        
        # Write to tier3 YAML
        try:
            self._write_to_tier3(pattern_entry)
            self._emit_event("PATTERN_ABSORBED", {
                "pattern_id": pattern_id,
                "confidence": decision.confidence,
                "sighting_count": decision.sighting_count,
            })
            logger.info(f"Pattern {pattern_id} absorbed into tier3 knowledge")
            return True
        except Exception as e:
            logger.error(f"Failed to absorb pattern {pattern_id}: {e}")
            return False
    
    def _write_to_tier3(self, pattern_entry: Dict[str, Any]) -> None:
        """Write pattern to tier3 YAML file.
        
        Args:
            pattern_entry: Pattern data to write.
        """
        # Load existing patterns
        if self.tier3_path.exists():
            with open(self.tier3_path, "r") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
        
        if "patterns" not in data:
            data["patterns"] = []
        
        # Append new pattern
        data["patterns"].append(pattern_entry)
        
        # Write back
        self.tier3_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tier3_path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
    
    def _emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Emit event (placeholder for EventBus integration).
        
        Args:
            event_name: Name of event.
            data: Event payload.
        """
        logger.debug(f"Event: {event_name} | Data: {data}")
