"""
FlushManager — Pattern cleanup using digestive system metaphor.

Removes stale patterns (>30 days old, confidence <0.4) from the pattern library
to prevent knowledge base bloat. Mirrors waste removal in digestive system.

Part of CORTEX brain metaphor:
- Sensory neurons: ConvergenceNeuron (detect patterns)
- Motor neurons: WorkflowComposer (execute actions)  
- Digestive system: AbsorptionGate (absorb knowledge), FlushManager (remove waste)

Author: CORTEX Phase 84 Stage 2
"""

import logging
import yaml
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Pattern:
    """Pattern stored in knowledge base.
    
    Attributes:
        id: Unique identifier.
        signature: Pattern signature hash.
        confidence: Confidence score (0.0-1.0).
        sighting_count: Number of times pattern was seen.
        first_seen: First observation timestamp.
        last_seen: Most recent observation timestamp.
        context: Additional context data.
    """
    id: str
    signature: str
    confidence: float
    sighting_count: int
    first_seen: datetime
    last_seen: datetime
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlushDecision:
    """Decision on whether to flush a pattern.
    
    Attributes:
        action: "FLUSH" or "KEEP".
        pattern_id: Pattern identifier (optional, for tracking).
        reason: Human-readable explanation.
        age_days: Age of pattern in days (optional).
        confidence: Pattern confidence score (optional).
    """
    action: str  # "FLUSH" or "KEEP"
    reason: str
    pattern_id: Optional[str] = None
    age_days: Optional[int] = None
    confidence: Optional[float] = None


@dataclass
class FlushCriteria:
    """Criteria for flushing patterns.
    
    Attributes:
        max_age_days: Maximum age before pattern is eligible for flush.
        min_confidence: Minimum confidence to retain old patterns.
    """
    max_age_days: int
    min_confidence: float


@dataclass
class FlushReport:
    """Report of flush operation.
    
    Attributes:
        patterns_flushed: Number of patterns removed.
        patterns_retained: Number of patterns kept.
        flush_timestamp: When flush occurred.
        flushed_pattern_ids: IDs of flushed patterns.
    """
    patterns_flushed: int
    patterns_retained: int
    flush_timestamp: datetime
    flushed_pattern_ids: List[str]


# =============================================================================
# FLUSH MANAGER
# =============================================================================

class FlushManager:
    """Pattern cleanup manager - removes stale patterns from knowledge base.
    
    Digestive metaphor: Removes waste (low-value patterns) to maintain system health.
    
    Flush criteria:
    - Pattern age > max_age_days AND
    - Pattern confidence < min_confidence
    
    Example:
        >>> criteria = FlushCriteria(max_age_days=30, min_confidence=0.4)
        >>> manager = FlushManager(criteria=criteria)
        >>> stale_patterns = manager.scan()
        >>> report = manager.flush()
        >>> print(f"Flushed {report.patterns_flushed} patterns")
    """
    
    def __init__(
        self,
        criteria: Optional[FlushCriteria] = None,
        max_age_days: int = 30,
        min_confidence: float = 0.4,
        pattern_library_path: Optional[Path] = None,
    ) -> None:
        """Initialize FlushManager.
        
        Args:
            criteria: FlushCriteria object (overrides individual params if provided).
            max_age_days: Maximum age in days before pattern eligible for flush.
            min_confidence: Minimum confidence to retain old patterns.
            pattern_library_path: Path to pattern library YAML file.
        """
        if criteria:
            self.criteria = criteria
            self.max_age_days = criteria.max_age_days
            self.min_confidence = criteria.min_confidence
        else:
            self.criteria = FlushCriteria(max_age_days=max_age_days, min_confidence=min_confidence)
            self.max_age_days = max_age_days
            self.min_confidence = min_confidence
        
        self.pattern_library_path = pattern_library_path or Path(
            "cortex/knowledge/tier3/learned-patterns.yaml"
        )
        
        logger.info(
            f"FlushManager initialized: max_age_days={self.max_age_days}, "
            f"min_confidence={self.min_confidence}"
        )
    
    def scan(self) -> List[Dict[str, Any]]:
        """Scan pattern library for stale patterns.
        
        Returns:
            List of pattern dicts that meet flush criteria.
        """
        if not self.pattern_library_path.exists():
            logger.warning(f"Pattern library not found: {self.pattern_library_path}")
            return []
        
        # Load patterns
        with open(self.pattern_library_path, "r") as f:
            data = yaml.safe_load(f) or {}
        
        patterns = data.get("patterns", [])
        stale_patterns = []
        
        now = datetime.now()
        
        for pattern in patterns:
            try:
                absorbed_at_str = pattern.get("absorbed_at", "")
                absorbed_at = datetime.fromisoformat(absorbed_at_str)
                age_days = (now - absorbed_at).days
                confidence = pattern.get("confidence", 0.0)
                
                # Check flush criteria
                if age_days > self.max_age_days and confidence < self.min_confidence:
                    stale_patterns.append(pattern)
                    logger.debug(
                        f"Stale pattern found: {pattern.get('pattern_id')} "
                        f"(age={age_days}d, confidence={confidence:.2f})"
                    )
            except Exception as e:
                logger.warning(f"Error evaluating pattern: {e}")
                continue
        
        logger.info(f"Scan complete: {len(stale_patterns)} stale patterns found")
        return stale_patterns
    
    def evaluate(self, pattern: Pattern) -> FlushDecision:
        """Evaluate whether a pattern should be flushed.
        
        Args:
            pattern: Pattern object to evaluate.
            
        Returns:
            FlushDecision with action ("FLUSH" or "KEEP") and reasoning.
        """
        now = datetime.now()
        # Use first_seen for age calculation (when pattern was originally observed)
        age_days = (now - pattern.first_seen).days
        
        # Check criteria
        if age_days <= self.max_age_days:
            return FlushDecision(
                action="KEEP",
                reason=f"Pattern is recent ({age_days} days old)",
                age_days=age_days,
                confidence=pattern.confidence,
            )
        
        if pattern.confidence >= self.min_confidence:
            return FlushDecision(
                action="KEEP",
                reason=f"High confidence ({pattern.confidence:.2f}) despite age",
                age_days=age_days,
                confidence=pattern.confidence,
            )
        
        # Criteria met - approve flush
        return FlushDecision(
            action="FLUSH",
            reason=f"Stale pattern: {age_days} days old with confidence {pattern.confidence:.2f}",
            age_days=age_days,
            confidence=pattern.confidence,
        )
    
    def flush(self, pattern: Optional[Pattern] = None) -> FlushReport:
        """Remove stale patterns from library.
        
        Args:
            pattern: Optional specific pattern to flush (if None, scans all).
            
        Returns:
            FlushReport with flush statistics.
        """
        if pattern:
            # Single pattern flush
            return self._flush_single_pattern(pattern)
        else:
            # Batch flush all stale patterns
            return self._flush_all_stale()
    
    def _flush_single_pattern(self, pattern: Pattern) -> FlushReport:
        """Flush a specific pattern.
        
        Args:
            pattern: Pattern to remove.
            
        Returns:
            FlushReport.
        """
        # Load full library
        with open(self.pattern_library_path, "r") as f:
            data = yaml.safe_load(f) or {}
        
        all_patterns = data.get("patterns", [])
        
        # Filter out the specific pattern
        retained_patterns = [p for p in all_patterns if p.get("id") != pattern.id]
        
        flushed_count = len(all_patterns) - len(retained_patterns)
        
        # Write back
        data["patterns"] = retained_patterns
        with open(self.pattern_library_path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        
        # Emit event
        self._emit_event("PATTERN_FLUSHED", {
            "pattern_id": pattern.id,
            "reason": "Manual flush",
        })
        
        logger.info(f"Pattern {pattern.id} flushed")
        
        return FlushReport(
            patterns_flushed=flushed_count,
            patterns_retained=len(retained_patterns),
            flush_timestamp=datetime.now(),
            flushed_pattern_ids=[pattern.id] if flushed_count > 0 else [],
        )
    
    def _flush_all_stale(self) -> FlushReport:
        """Flush all stale patterns based on criteria.
        
        Returns:
            FlushReport with statistics.
        """
        stale_patterns = self.scan()
        
        if not stale_patterns:
            logger.info("No patterns to flush")
            return FlushReport(
                patterns_flushed=0,
                patterns_retained=0,
                flush_timestamp=datetime.now(),
                flushed_pattern_ids=[],
            )
        
        # Load full library
        with open(self.pattern_library_path, "r") as f:
            data = yaml.safe_load(f) or {}
        
        all_patterns = data.get("patterns", [])
        stale_ids = {p.get("pattern_id") for p in stale_patterns}
        
        # Filter out stale patterns
        retained_patterns = [p for p in all_patterns if p.get("pattern_id") not in stale_ids]
        
        # Write back
        data["patterns"] = retained_patterns
        with open(self.pattern_library_path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        
        # Emit event
        self._emit_event("PATTERNS_FLUSHED", {
            "patterns_flushed": len(stale_patterns),
            "patterns_retained": len(retained_patterns),
            "flushed_ids": list(stale_ids),
        })
        
        logger.info(
            f"Flush complete: {len(stale_patterns)} patterns removed, "
            f"{len(retained_patterns)} retained"
        )
        
        return FlushReport(
            patterns_flushed=len(stale_patterns),
            patterns_retained=len(retained_patterns),
            flush_timestamp=datetime.now(),
            flushed_pattern_ids=list(stale_ids),
        )
    
    def _emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Emit event (placeholder for EventBus integration).
        
        Args:
            event_name: Name of event.
            data: Event payload.
        """
        logger.debug(f"Event: {event_name} | Data: {data}")
