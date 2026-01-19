"""
Implementation of AC-GC-003-01: Intent-Profile Selection Matrix

Provides O(1) profile lookup via composite key: (intent_type, confidence_band, phase)
Confidence bands: HIGH (≥0.8), MEDIUM (0.5-0.8), LOW (<0.5)
Phases: COMPREHENSION, ROUTING, KNOWLEDGE, APPROVAL

Fallback chain enables gradual specificity reduction:
1. Exact match: (intent, confidence, phase)
2. Intent default: Intent-specific generic profile
3. Phase default: Phase-specific generic profile
4. None: No mapping found

Integrates with Stage 2 Intent Router for automatic profile selection.

CORE Governance Rules:
- CORE-005: Path portability (pathlib used for paths)
- CORE-008: TDD (tests created first)
- CORE-011: Type hints (100% coverage)
- CORE-012: Google docstrings
- CORE-027: Audit trail logging
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class IntentType(Enum):
    """
    Master Orchestrator operation intent types.
    
    ANALYZE: Information extraction and comprehension
    SYNTHESIZE: Generate or combine outputs
    VALIDATE: Check correctness and compliance
    TRANSFORM: Convert between representations
    AUDIT: Create records for compliance trail
    """
    ANALYZE = "ANALYZE"
    SYNTHESIZE = "SYNTHESIZE"
    VALIDATE = "VALIDATE"
    TRANSFORM = "TRANSFORM"
    AUDIT = "AUDIT"


class ConfidenceBand(Enum):
    """
    Confidence level bands for operation outcomes.
    
    HIGH: ≥0.8 (high confidence in result)
    MEDIUM: 0.5-0.8 (moderate confidence)
    LOW: <0.5 (low confidence)
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ExecutionPhase(Enum):
    """
    Master Orchestrator execution phases.
    
    COMPREHENSION: Understand input and context
    ROUTING: Route to appropriate handler
    KNOWLEDGE: Gather supporting information
    APPROVAL: Final validation and approval
    """
    COMPREHENSION = "COMPREHENSION"
    ROUTING = "ROUTING"
    KNOWLEDGE = "KNOWLEDGE"
    APPROVAL = "APPROVAL"


@dataclass
class MatrixKey:
    """
    Composite key for matrix lookup.
    
    Attributes:
        intent: Operation intent type
        confidence: Confidence band
        phase: Execution phase
    """
    intent: IntentType
    confidence: ConfidenceBand
    phase: ExecutionPhase
    
    def to_tuple(self) -> Tuple[str, str, str]:
        """
        Convert to tuple for dictionary key.
        
        Returns:
            Tuple of (intent_value, confidence_value, phase_value)
        """
        return (self.intent.value, self.confidence.value, self.phase.value)


class ConfidenceCalculator:
    """
    Calculates confidence band from numeric confidence score.
    
    Bands:
    - HIGH: ≥0.8
    - MEDIUM: 0.5-0.8
    - LOW: <0.5
    """
    
    @staticmethod
    def get_band(confidence_score: float) -> ConfidenceBand:
        """
        Calculate confidence band from score (0.0-1.0).
        
        Args:
            confidence_score: Score between 0.0 and 1.0
        
        Returns:
            ConfidenceBand (HIGH/MEDIUM/LOW)
        
        Raises:
            ValueError: If score outside 0.0-1.0 range
        """
        if confidence_score < 0.0 or confidence_score > 1.0:
            raise ValueError(
                f"Confidence score must be 0.0-1.0, got {confidence_score}"
            )
        
        if confidence_score >= 0.8:
            return ConfidenceBand.HIGH
        elif confidence_score >= 0.5:
            return ConfidenceBand.MEDIUM
        else:
            return ConfidenceBand.LOW


class SelectionMatrix:
    """
    Intent-Profile selection matrix for O(1) profile lookup.
    
    Maps (intent_type, confidence_band, phase) → profile_name with multi-level
    fallback enabling graceful degradation of specificity.
    
    Fallback chain:
    1. Exact match: (intent, confidence, phase)
    2. Intent default: Intent-specific generic profile
    3. Phase default: Phase-specific generic profile
    4. None: No mapping found
    
    Integrates with Stage 2 Intent Router for automatic profile selection based
    on operation context and confidence level.
    """
    
    def __init__(self) -> None:
        """Initialize selection matrix with empty mappings."""
        self._matrix: Dict[Tuple[str, str, str], str] = {}
        self._intent_defaults: Dict[str, str] = {}
        self._phase_defaults: Dict[str, str] = {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_mapping(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase,
        profile_name: str,
        audit: bool = True
    ) -> None:
        """
        Register (intent, confidence, phase) → profile mapping.
        
        Args:
            intent: Operation intent type
            confidence: Confidence band
            phase: Execution phase
            profile_name: Name of profile to use
            audit: Whether to log to audit trail
        """
        key = (intent.value, confidence.value, phase.value)
        self._matrix[key] = profile_name
        
        if audit:
            self._logger.info(
                f"Matrix mapping registered: {intent.value}/{confidence.value}/{phase.value} → {profile_name}",
                extra={"key": key, "profile": profile_name}
            )
    
    def register_intent_default(
        self,
        intent: IntentType,
        profile_name: str,
        audit: bool = True
    ) -> None:
        """
        Register fallback profile for intent.
        
        Used when exact (intent, confidence, phase) mapping unavailable.
        
        Args:
            intent: Operation intent type
            profile_name: Default profile for this intent
            audit: Whether to log to audit trail
        """
        self._intent_defaults[intent.value] = profile_name
        
        if audit:
            self._logger.info(
                f"Intent default registered: {intent.value} → {profile_name}",
                extra={"intent": intent.value, "profile": profile_name}
            )
    
    def register_phase_default(
        self,
        phase: ExecutionPhase,
        profile_name: str,
        audit: bool = True
    ) -> None:
        """
        Register fallback profile for phase.
        
        Used when intent default and exact mapping unavailable.
        
        Args:
            phase: Execution phase
            profile_name: Default profile for this phase
            audit: Whether to log to audit trail
        """
        self._phase_defaults[phase.value] = profile_name
        
        if audit:
            self._logger.info(
                f"Phase default registered: {phase.value} → {profile_name}",
                extra={"phase": phase.value, "profile": profile_name}
            )
    
    def get_profile(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase,
        audit: bool = True
    ) -> Optional[str]:
        """
        Look up profile with multi-level fallback (O(1) typical case).
        
        Lookup order:
        1. Exact match: (intent, confidence, phase)
        2. Fallback: intent-specific default
        3. Fallback: phase-specific default
        4. None: No mapping found
        
        Args:
            intent: Operation intent type
            confidence: Confidence band
            phase: Execution phase
            audit: Whether to log to audit trail
        
        Returns:
            Profile name or None if not found
        """
        # Exact match lookup (O(1))
        key = (intent.value, confidence.value, phase.value)
        if key in self._matrix:
            profile = self._matrix[key]
            if audit:
                self._logger.debug(
                    f"Matrix lookup: exact match found",
                    extra={"key": key, "profile": profile}
                )
            return profile
        
        # Intent default fallback
        if intent.value in self._intent_defaults:
            profile = self._intent_defaults[intent.value]
            if audit:
                self._logger.debug(
                    f"Matrix lookup: using intent default",
                    extra={"intent": intent.value, "profile": profile}
                )
            return profile
        
        # Phase default fallback
        if phase.value in self._phase_defaults:
            profile = self._phase_defaults[phase.value]
            if audit:
                self._logger.debug(
                    f"Matrix lookup: using phase default",
                    extra={"phase": phase.value, "profile": profile}
                )
            return profile
        
        if audit:
            self._logger.warning(
                f"Matrix lookup: no mapping found",
                extra={"intent": intent.value, "confidence": confidence.value, "phase": phase.value}
            )
        return None
    
    def has_exact_mapping(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase
    ) -> bool:
        """
        Check if exact (intent, confidence, phase) mapping exists (O(1)).
        
        Args:
            intent: Operation intent type
            confidence: Confidence band
            phase: Execution phase
        
        Returns:
            True if exact mapping exists
        """
        key = (intent.value, confidence.value, phase.value)
        return key in self._matrix
    
    def get_all_for_intent(self, intent: IntentType) -> Dict[str, str]:
        """
        Get all mappings for specific intent.
        
        Args:
            intent: Operation intent type
        
        Returns:
            Dictionary of (confidence, phase) → profile mappings
        """
        result = {}
        for (int_val, conf_val, phase_val), profile in self._matrix.items():
            if int_val == intent.value:
                result[f"{conf_val}/{phase_val}"] = profile
        return result
    
    def get_all_for_phase(self, phase: ExecutionPhase) -> Dict[str, str]:
        """
        Get all mappings for specific phase.
        
        Args:
            phase: Execution phase
        
        Returns:
            Dictionary of (intent, confidence) → profile mappings
        """
        result = {}
        for (int_val, conf_val, phase_val), profile in self._matrix.items():
            if phase_val == phase.value:
                result[f"{int_val}/{conf_val}"] = profile
        return result
    
    def clear_matrix(self) -> None:
        """Clear all mappings (exact and defaults)."""
        self._matrix.clear()
        self._intent_defaults.clear()
        self._phase_defaults.clear()
        self._logger.info("Matrix cleared")
    
    def matrix_size(self) -> int:
        """
        Get count of exact mappings.
        
        Returns:
            Number of (intent, confidence, phase) → profile mappings
        """
        return len(self._matrix)
    
    def intent_defaults_size(self) -> int:
        """
        Get count of intent default mappings.
        
        Returns:
            Number of intent-level default mappings
        """
        return len(self._intent_defaults)
    
    def phase_defaults_size(self) -> int:
        """
        Get count of phase default mappings.
        
        Returns:
            Number of phase-level default mappings
        """
        return len(self._phase_defaults)
    
    def total_mappings(self) -> int:
        """
        Get total mapping count (exact + defaults).
        
        Returns:
            Total number of mappings
        """
        return self.matrix_size() + self.intent_defaults_size() + self.phase_defaults_size()
    
    def get_coverage_stats(self) -> Dict[str, int]:
        """
        Get coverage statistics.
        
        Returns:
            Dictionary with exact, intent_default, phase_default, total counts
        """
        return {
            "exact_mappings": self.matrix_size(),
            "intent_defaults": self.intent_defaults_size(),
            "phase_defaults": self.phase_defaults_size(),
            "total_mappings": self.total_mappings()
        }
