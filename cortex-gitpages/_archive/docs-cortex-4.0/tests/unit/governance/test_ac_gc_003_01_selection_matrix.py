"""
Tests for AC-GC-003-01: Intent-Profile Selection Matrix

AC-GC-003-01: Intent-Profile Selection Matrix
- Matrix maps (intent_type, confidence_band, phase) → profile name
- O(1) profile lookup via composite key
- Confidence bands: HIGH (≥0.8), MEDIUM (0.5-0.8), LOW (<0.5)
- Phases: COMPREHENSION, ROUTING, KNOWLEDGE, APPROVAL
- Fallback: Intent → generic profile if band/phase combo unavailable
- Cache updated on profile registration
- Deterministic key generation

CORE Governance Rules:
- CORE-008: TDD (tests before code)
- CORE-011: Type hints (100%)
- CORE-012: Docstrings (Google style)
- CORE-027: Audit trail logging
"""

import pytest
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Operation intent types."""
    ANALYZE = "ANALYZE"
    SYNTHESIZE = "SYNTHESIZE"
    VALIDATE = "VALIDATE"
    TRANSFORM = "TRANSFORM"
    AUDIT = "AUDIT"


class ConfidenceBand(Enum):
    """Confidence level bands."""
    HIGH = "HIGH"      # ≥0.8
    MEDIUM = "MEDIUM"  # 0.5-0.8
    LOW = "LOW"        # <0.5


class ExecutionPhase(Enum):
    """Master orchestrator execution phases."""
    COMPREHENSION = "COMPREHENSION"
    ROUTING = "ROUTING"
    KNOWLEDGE = "KNOWLEDGE"
    APPROVAL = "APPROVAL"


@dataclass
class MatrixKey:
    """Composite key for matrix lookup."""
    intent: IntentType
    confidence: ConfidenceBand
    phase: ExecutionPhase
    
    def to_tuple(self) -> Tuple[str, str, str]:
        """Convert to tuple for dictionary key."""
        return (self.intent.value, self.confidence.value, self.phase.value)


class SelectionMatrix:
    """
    Intent-Profile selection matrix for O(1) profile lookup.
    
    Maps (intent_type, confidence_band, phase) → profile_name
    with fallback to intent-specific generic profile.
    """
    
    def __init__(self) -> None:
        """Initialize selection matrix."""
        self._matrix: Dict[Tuple[str, str, str], str] = {}
        self._intent_defaults: Dict[str, str] = {}
        self._phase_defaults: Dict[str, str] = {}
    
    def register_mapping(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase,
        profile_name: str
    ) -> None:
        """
        Register (intent, confidence, phase) → profile mapping.
        
        Args:
            intent: Operation intent type
            confidence: Confidence band
            phase: Execution phase
            profile_name: Name of profile to use
        """
        key = (intent.value, confidence.value, phase.value)
        self._matrix[key] = profile_name
    
    def register_intent_default(
        self,
        intent: IntentType,
        profile_name: str
    ) -> None:
        """
        Register fallback profile for intent.
        
        Args:
            intent: Operation intent type
            profile_name: Default profile for this intent
        """
        self._intent_defaults[intent.value] = profile_name
    
    def register_phase_default(
        self,
        phase: ExecutionPhase,
        profile_name: str
    ) -> None:
        """
        Register fallback profile for phase.
        
        Args:
            phase: Execution phase
            profile_name: Default profile for this phase
        """
        self._phase_defaults[phase.value] = profile_name
    
    def get_profile(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase
    ) -> Optional[str]:
        """
        Look up profile with fallback chain.
        
        Lookup order:
        1. Exact match: (intent, confidence, phase)
        2. Fallback: intent-specific default
        3. Fallback: phase-specific default
        4. None (no mapping found)
        
        Args:
            intent: Operation intent type
            confidence: Confidence band
            phase: Execution phase
        
        Returns:
            Profile name or None if not found
        """
        # Exact match
        key = (intent.value, confidence.value, phase.value)
        if key in self._matrix:
            return self._matrix[key]
        
        # Intent default
        if intent.value in self._intent_defaults:
            return self._intent_defaults[intent.value]
        
        # Phase default
        if phase.value in self._phase_defaults:
            return self._phase_defaults[phase.value]
        
        return None
    
    def has_exact_mapping(
        self,
        intent: IntentType,
        confidence: ConfidenceBand,
        phase: ExecutionPhase
    ) -> bool:
        """
        Check if exact mapping exists (O(1)).
        
        Args:
            intent: Operation intent type
            confidence: Confidence band
            phase: Execution phase
        
        Returns:
            True if exact mapping exists
        """
        key = (intent.value, confidence.value, phase.value)
        return key in self._matrix
    
    def clear_matrix(self) -> None:
        """Clear all mappings."""
        self._matrix.clear()
        self._intent_defaults.clear()
        self._phase_defaults.clear()
    
    def matrix_size(self) -> int:
        """Return number of exact mappings."""
        return len(self._matrix)
    
    def intent_defaults_size(self) -> int:
        """Return number of intent defaults."""
        return len(self._intent_defaults)
    
    def phase_defaults_size(self) -> int:
        """Return number of phase defaults."""
        return len(self._phase_defaults)


class ConfidenceCalculator:
    """Calculates confidence band from confidence score."""
    
    @staticmethod
    def get_band(confidence_score: float) -> ConfidenceBand:
        """
        Calculate confidence band from score (0.0-1.0).
        
        Args:
            confidence_score: Score between 0.0 and 1.0
        
        Returns:
            ConfidenceBand
        
        Raises:
            ValueError: If score out of range
        """
        if confidence_score < 0.0 or confidence_score > 1.0:
            raise ValueError(f"Confidence score must be 0.0-1.0, got {confidence_score}")
        
        if confidence_score >= 0.8:
            return ConfidenceBand.HIGH
        elif confidence_score >= 0.5:
            return ConfidenceBand.MEDIUM
        else:
            return ConfidenceBand.LOW


class TestMatrixKey:
    """Tests for MatrixKey dataclass."""
    
    def test_matrix_key_creation(self) -> None:
        """Test creating matrix key."""
        key = MatrixKey(
            intent=IntentType.ANALYZE,
            confidence=ConfidenceBand.HIGH,
            phase=ExecutionPhase.ROUTING
        )
        assert key.intent == IntentType.ANALYZE
        assert key.confidence == ConfidenceBand.HIGH
        assert key.phase == ExecutionPhase.ROUTING
    
    def test_matrix_key_to_tuple(self) -> None:
        """Test matrix key conversion to tuple."""
        key = MatrixKey(
            intent=IntentType.VALIDATE,
            confidence=ConfidenceBand.MEDIUM,
            phase=ExecutionPhase.KNOWLEDGE
        )
        tup = key.to_tuple()
        assert tup == ("VALIDATE", "MEDIUM", "KNOWLEDGE")


class TestSelectionMatrix:
    """Tests for SelectionMatrix."""
    
    @pytest.fixture
    def matrix(self) -> SelectionMatrix:
        """Create matrix fixture."""
        return SelectionMatrix()
    
    def test_matrix_initialization(self, matrix: SelectionMatrix) -> None:
        """Test matrix initializes empty."""
        assert matrix.matrix_size() == 0
        assert matrix.intent_defaults_size() == 0
        assert matrix.phase_defaults_size() == 0
    
    def test_register_exact_mapping(self, matrix: SelectionMatrix) -> None:
        """Test registering exact mapping."""
        matrix.register_mapping(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            "profile_analyze_high"
        )
        assert matrix.matrix_size() == 1
    
    def test_exact_mapping_lookup(self, matrix: SelectionMatrix) -> None:
        """Test exact mapping lookup (O(1))."""
        matrix.register_mapping(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            "profile_analyze_high"
        )
        profile = matrix.get_profile(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING
        )
        assert profile == "profile_analyze_high"
    
    def test_exact_mapping_not_found(self, matrix: SelectionMatrix) -> None:
        """Test exact mapping returns None when not found."""
        profile = matrix.get_profile(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING
        )
        assert profile is None
    
    def test_has_exact_mapping(self, matrix: SelectionMatrix) -> None:
        """Test checking exact mapping existence."""
        matrix.register_mapping(
            IntentType.VALIDATE,
            ConfidenceBand.MEDIUM,
            ExecutionPhase.KNOWLEDGE,
            "profile_validate"
        )
        assert matrix.has_exact_mapping(
            IntentType.VALIDATE,
            ConfidenceBand.MEDIUM,
            ExecutionPhase.KNOWLEDGE
        ) is True
        assert matrix.has_exact_mapping(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING
        ) is False
    
    def test_intent_default_fallback(self, matrix: SelectionMatrix) -> None:
        """Test fallback to intent default."""
        matrix.register_intent_default(
            IntentType.ANALYZE,
            "profile_analyze_default"
        )
        profile = matrix.get_profile(
            IntentType.ANALYZE,
            ConfidenceBand.LOW,
            ExecutionPhase.COMPREHENSION
        )
        assert profile == "profile_analyze_default"
    
    def test_phase_default_fallback(self, matrix: SelectionMatrix) -> None:
        """Test fallback to phase default."""
        matrix.register_phase_default(
            ExecutionPhase.APPROVAL,
            "profile_approval_default"
        )
        profile = matrix.get_profile(
            IntentType.SYNTHESIZE,
            ConfidenceBand.MEDIUM,
            ExecutionPhase.APPROVAL
        )
        assert profile == "profile_approval_default"
    
    def test_fallback_chain(self, matrix: SelectionMatrix) -> None:
        """Test fallback chain priority."""
        # Register both defaults
        matrix.register_intent_default(IntentType.ANALYZE, "intent_default")
        matrix.register_phase_default(ExecutionPhase.ROUTING, "phase_default")
        
        # Intent default should take priority
        profile = matrix.get_profile(
            IntentType.ANALYZE,
            ConfidenceBand.MEDIUM,
            ExecutionPhase.ROUTING
        )
        assert profile == "intent_default"
    
    def test_multiple_mappings(self, matrix: SelectionMatrix) -> None:
        """Test multiple distinct mappings."""
        matrix.register_mapping(
            IntentType.ANALYZE,
            ConfidenceBand.HIGH,
            ExecutionPhase.ROUTING,
            "profile_1"
        )
        matrix.register_mapping(
            IntentType.VALIDATE,
            ConfidenceBand.MEDIUM,
            ExecutionPhase.KNOWLEDGE,
            "profile_2"
        )
        matrix.register_mapping(
            IntentType.TRANSFORM,
            ConfidenceBand.LOW,
            ExecutionPhase.APPROVAL,
            "profile_3"
        )
        
        assert matrix.matrix_size() == 3
        assert matrix.get_profile(IntentType.ANALYZE, ConfidenceBand.HIGH, ExecutionPhase.ROUTING) == "profile_1"
        assert matrix.get_profile(IntentType.VALIDATE, ConfidenceBand.MEDIUM, ExecutionPhase.KNOWLEDGE) == "profile_2"
        assert matrix.get_profile(IntentType.TRANSFORM, ConfidenceBand.LOW, ExecutionPhase.APPROVAL) == "profile_3"
    
    def test_clear_matrix(self, matrix: SelectionMatrix) -> None:
        """Test clearing matrix."""
        matrix.register_mapping(IntentType.ANALYZE, ConfidenceBand.HIGH, ExecutionPhase.ROUTING, "p1")
        matrix.register_intent_default(IntentType.VALIDATE, "p2")
        matrix.register_phase_default(ExecutionPhase.KNOWLEDGE, "p3")
        
        matrix.clear_matrix()
        assert matrix.matrix_size() == 0
        assert matrix.intent_defaults_size() == 0
        assert matrix.phase_defaults_size() == 0


class TestConfidenceCalculator:
    """Tests for ConfidenceCalculator."""
    
    def test_high_confidence_band(self) -> None:
        """Test HIGH band detection."""
        assert ConfidenceCalculator.get_band(0.8) == ConfidenceBand.HIGH
        assert ConfidenceCalculator.get_band(0.95) == ConfidenceBand.HIGH
        assert ConfidenceCalculator.get_band(1.0) == ConfidenceBand.HIGH
    
    def test_medium_confidence_band(self) -> None:
        """Test MEDIUM band detection."""
        assert ConfidenceCalculator.get_band(0.5) == ConfidenceBand.MEDIUM
        assert ConfidenceCalculator.get_band(0.65) == ConfidenceBand.MEDIUM
        assert ConfidenceCalculator.get_band(0.79) == ConfidenceBand.MEDIUM
    
    def test_low_confidence_band(self) -> None:
        """Test LOW band detection."""
        assert ConfidenceCalculator.get_band(0.0) == ConfidenceBand.LOW
        assert ConfidenceCalculator.get_band(0.25) == ConfidenceBand.LOW
        assert ConfidenceCalculator.get_band(0.49) == ConfidenceBand.LOW
    
    def test_confidence_boundary_values(self) -> None:
        """Test boundary values."""
        assert ConfidenceCalculator.get_band(0.7999) == ConfidenceBand.MEDIUM
        assert ConfidenceCalculator.get_band(0.8000) == ConfidenceBand.HIGH
        assert ConfidenceCalculator.get_band(0.4999) == ConfidenceBand.LOW
        assert ConfidenceCalculator.get_band(0.5000) == ConfidenceBand.MEDIUM
    
    def test_invalid_confidence_too_high(self) -> None:
        """Test invalid confidence score (too high)."""
        with pytest.raises(ValueError):
            ConfidenceCalculator.get_band(1.1)
    
    def test_invalid_confidence_too_low(self) -> None:
        """Test invalid confidence score (too low)."""
        with pytest.raises(ValueError):
            ConfidenceCalculator.get_band(-0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
