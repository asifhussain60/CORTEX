"""
Unit Tests for ChallengeEngine Tier-3 Gate Logic.

Tests for Tier-3 (Hard/Soft/Context) gate implementation in ChallengeEngine.
Replaces single 0.7 threshold with violation-type-specific challenge rules.

Authority: CORE-008 (TDD - tests first)
Coverage Target: 90%+
Phase: 8.1 - Tier-3 Gate Logic & Challenge Routing
"""

import pytest
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import time

from cortex.orchestrators.core.challenge_engine import (
    ChallengeEngine,
    ChallengeType,
    GateType,
    DisagreementType,
    LENSContext,
    ChallengeResponse,
    ChallengeRule,
)


class TestTier3GateLogic:
    """Test Tier-3 gate logic in ChallengeEngine."""
    
    @pytest.fixture
    def engine(self) -> ChallengeEngine:
        """Create ChallengeEngine with Tier-3 rules."""
        return ChallengeEngine()
    
    @pytest.fixture
    def challenge_rules(self) -> Dict[ChallengeType, ChallengeRule]:
        """Define challenge rules for Tier-3 gates."""
        return {
            ChallengeType.SECURITY: ChallengeRule(
                challenge_type=ChallengeType.SECURITY,
                gate_type=GateType.HARD,
                threshold=0.4,  # Low threshold, high priority
                auto_proceed_ms=0,  # No auto-proceed
                description="Security vulnerability detected"
            ),
            ChallengeType.HARMFUL: ChallengeRule(
                challenge_type=ChallengeType.HARMFUL,
                gate_type=GateType.HARD,
                threshold=0.5,
                auto_proceed_ms=0,
                description="Harmful action detected"
            ),
            ChallengeType.SRP_VIOLATION: ChallengeRule(
                challenge_type=ChallengeType.SRP_VIOLATION,
                gate_type=GateType.SOFT,
                threshold=0.6,
                auto_proceed_ms=10000,  # 10 second timeout
                description="Single Responsibility Principle violation"
            ),
            ChallengeType.ARCHITECTURE_VIOLATION: ChallengeRule(
                challenge_type=ChallengeType.ARCHITECTURE_VIOLATION,
                gate_type=GateType.SOFT,
                threshold=0.65,
                auto_proceed_ms=10000,
                description="Architectural constraint violation"
            ),
            ChallengeType.MISSING_CONTEXT: ChallengeRule(
                challenge_type=ChallengeType.MISSING_CONTEXT,
                gate_type=GateType.CONTEXT,
                threshold=0.5,
                auto_proceed_ms=0,
                description="Request missing critical context"
            ),
            ChallengeType.AMBIGUITY: ChallengeRule(
                challenge_type=ChallengeType.AMBIGUITY,
                gate_type=GateType.CONTEXT,
                threshold=0.7,
                auto_proceed_ms=0,
                description="Request contains ambiguity"
            ),
            ChallengeType.REDUNDANT_WORK: ChallengeRule(
                challenge_type=ChallengeType.REDUNDANT_WORK,
                gate_type=GateType.SOFT,
                threshold=0.75,
                auto_proceed_ms=10000,
                description="Work already exists"
            ),
        }
    
    @pytest.fixture
    def lens_context_high_confidence(self) -> LENSContext:
        """Create high-confidence LENS context."""
        return LENSContext(
            language="Refactor large class",
            examination={"classes": ["BigClass"], "size": 600},
            navigation=["file1.py", "file2.py"],
            synthesis="Class BigClass is 600 lines with 25 methods",
            confidence=0.85
        )
    
    @pytest.fixture
    def lens_context_low_confidence(self) -> LENSContext:
        """Create low-confidence LENS context."""
        return LENSContext(
            language="Improve something",
            examination={},
            navigation=[],
            synthesis="Request lacks specificity",
            confidence=0.3
        )
    
    def test_hard_gate_blocks_security_violation(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that hard gate blocks security violations."""
        challenge = engine.generate_challenge(
            "Add weak encryption",
            lens_context_high_confidence,
            challenge_type=ChallengeType.SECURITY
        )
        
        assert challenge.has_disagreement
        assert challenge.disagreement_type == DisagreementType.HARMFUL_ACTION
        # Hard gate should require explicit user response
        assert challenge.gate_type == GateType.HARD
        assert len(challenge.options) >= 2  # At least accept/reject
    
    def test_hard_gate_blocks_harmful_action(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that hard gate blocks harmful actions."""
        challenge = engine.generate_challenge(
            "Delete production database",
            lens_context_high_confidence,
            challenge_type=ChallengeType.HARMFUL
        )
        
        assert challenge.has_disagreement
        assert challenge.gate_type == GateType.HARD
    
    def test_soft_gate_suggests_srp_violation(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that soft gate suggests SRP improvements with timeout."""
        challenge = engine.generate_challenge(
            "Refactor large class",
            lens_context_high_confidence,
            challenge_type=ChallengeType.SRP_VIOLATION
        )
        
        assert challenge.has_disagreement
        assert challenge.gate_type == GateType.SOFT
        assert challenge.auto_proceed_ms == 10000
        # Options should include auto-proceed option
        assert any("proceed" in opt.lower() for opt in challenge.options)
    
    def test_context_gate_asks_clarifying_questions(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that context gate asks clarifying questions."""
        challenge = engine.generate_challenge(
            "Improve the system",
            lens_context_high_confidence,
            challenge_type=ChallengeType.AMBIGUITY
        )
        
        assert challenge.has_disagreement
        assert challenge.gate_type == GateType.CONTEXT
        # Should have clarifying questions in options
        assert len(challenge.options) >= 3
        assert any("clarify" in opt.lower() or "context" in opt.lower() for opt in challenge.options)
    
    def test_threshold_below_min_no_challenge(self, engine: ChallengeEngine):
        """Test that confidence below threshold doesn't trigger challenge."""
        low_context = LENSContext(
            language="Request",
            confidence=0.3  # Below SRP threshold of 0.6
        )
        
        challenge = engine.generate_challenge(
            "Some request",
            low_context,
            challenge_type=ChallengeType.SRP_VIOLATION
        )
        
        assert not challenge.has_disagreement
    
    def test_security_gate_has_lowest_threshold(self, engine: ChallengeEngine):
        """Test that security gates trigger at 0.4 confidence."""
        medium_context = LENSContext(
            language="Security issue",
            confidence=0.45  # Above security threshold of 0.4
        )
        
        challenge = engine.generate_challenge(
            "Weak crypto",
            medium_context,
            challenge_type=ChallengeType.SECURITY
        )
        
        assert challenge.has_disagreement
    
    def test_soft_gate_timeout_value(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that soft gate timeout is configurable."""
        challenge = engine.generate_challenge(
            "Refactor class",
            lens_context_high_confidence,
            challenge_type=ChallengeType.SRP_VIOLATION
        )
        
        assert challenge.auto_proceed_ms == 10000
        assert challenge.gate_type == GateType.SOFT
    
    def test_hard_gate_no_timeout(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that hard gates don't auto-proceed."""
        challenge = engine.generate_challenge(
            "Delete data",
            lens_context_high_confidence,
            challenge_type=ChallengeType.HARMFUL
        )
        
        assert challenge.gate_type == GateType.HARD
        assert challenge.auto_proceed_ms == 0 or challenge.auto_proceed_ms is None
    
    def test_challenge_rule_lookup(self, engine: ChallengeEngine, challenge_rules: Dict):
        """Test challenge rule lookup by type."""
        rule = challenge_rules[ChallengeType.SRP_VIOLATION]
        
        assert rule.gate_type == GateType.SOFT
        assert rule.threshold == 0.6
        assert rule.auto_proceed_ms == 10000
    
    def test_all_challenge_types_covered(self, challenge_rules: Dict):
        """Test that all challenge types have rules defined."""
        for challenge_type in ChallengeType:
            assert challenge_type in challenge_rules
    
    def test_gate_type_consistency(self, challenge_rules: Dict):
        """Test that gate types are consistent."""
        for challenge_type, rule in challenge_rules.items():
            if challenge_type in [ChallengeType.SECURITY, ChallengeType.HARMFUL]:
                assert rule.gate_type == GateType.HARD
            elif challenge_type in [ChallengeType.SRP_VIOLATION, ChallengeType.ARCHITECTURE_VIOLATION, ChallengeType.REDUNDANT_WORK]:
                assert rule.gate_type == GateType.SOFT
            elif challenge_type in [ChallengeType.MISSING_CONTEXT, ChallengeType.AMBIGUITY]:
                assert rule.gate_type == GateType.CONTEXT
    
    def test_threshold_ordering(self, challenge_rules: Dict):
        """Test that thresholds follow logical ordering."""
        # Security should have lowest threshold (most important)
        assert challenge_rules[ChallengeType.SECURITY].threshold < challenge_rules[ChallengeType.SRP_VIOLATION].threshold
        # Redundant work should have highest or equal threshold
        redundant_threshold = challenge_rules[ChallengeType.REDUNDANT_WORK].threshold
        for ctype, rule in challenge_rules.items():
            if ctype != ChallengeType.REDUNDANT_WORK:
                assert redundant_threshold >= rule.threshold or rule.challenge_type == ChallengeType.REDUNDANT_WORK
    
    def test_challenge_has_options(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that all challenges provide options."""
        challenge = engine.generate_challenge(
            "Some request",
            lens_context_high_confidence,
            challenge_type=ChallengeType.SRP_VIOLATION
        )
        
        assert len(challenge.options) > 0
        assert all(isinstance(opt, str) for opt in challenge.options)
    
    def test_challenge_includes_reasoning(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that challenges include reasoning."""
        challenge = engine.generate_challenge(
            "Refactor class",
            lens_context_high_confidence,
            challenge_type=ChallengeType.SRP_VIOLATION
        )
        
        assert challenge.has_disagreement
        assert len(challenge.reasoning) > 0
    
    def test_challenge_includes_evidence(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that challenges include supporting evidence."""
        challenge = engine.generate_challenge(
            "Refactor class",
            lens_context_high_confidence,
            challenge_type=ChallengeType.SRP_VIOLATION
        )
        
        assert challenge.has_disagreement
        assert len(challenge.evidence) > 0
    
    def test_challenge_alternative_present(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that challenges include recommended alternatives."""
        challenge = engine.generate_challenge(
            "Refactor class",
            lens_context_high_confidence,
            challenge_type=ChallengeType.SRP_VIOLATION
        )
        
        assert challenge.has_disagreement
        assert len(challenge.recommended_alternative) > 0
    
    def test_multiple_challenge_types_in_sequence(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test handling multiple challenges in sequence."""
        challenges = []
        for challenge_type in [ChallengeType.SECURITY, ChallengeType.SRP_VIOLATION, ChallengeType.AMBIGUITY]:
            challenge = engine.generate_challenge(
                "Some request",
                lens_context_high_confidence,
                challenge_type=challenge_type
            )
            challenges.append(challenge)
        
        assert len(challenges) == 3
        assert challenges[0].gate_type == GateType.HARD  # SECURITY
        assert challenges[1].gate_type == GateType.SOFT  # SRP
        assert challenges[2].gate_type == GateType.CONTEXT  # AMBIGUITY
    
    def test_backward_compatibility_with_existing_threshold(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test backward compatibility with existing 0.7 threshold."""
        # Default challenge without explicit type should still work
        challenge = engine.generate_challenge(
            "Refactor large class",
            lens_context_high_confidence
        )
        
        # Should work with either new or old logic
        assert challenge is not None
    
    def test_soft_gate_includes_proceed_option(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that soft gates include proceed option."""
        challenge = engine.generate_challenge(
            "Refactor class",
            lens_context_high_confidence,
            challenge_type=ChallengeType.SRP_VIOLATION
        )
        
        assert challenge.gate_type == GateType.SOFT
        # Should have proceed option
        assert any("proceed" in opt.lower() for opt in challenge.options)
    
    def test_challenge_metadata_complete(self, engine: ChallengeEngine, lens_context_high_confidence: LENSContext):
        """Test that challenge response includes all metadata."""
        challenge = engine.generate_challenge(
            "Refactor large class",
            lens_context_high_confidence,
            challenge_type=ChallengeType.SRP_VIOLATION
        )
        
        assert challenge.has_disagreement
        assert challenge.disagreement_type is not None
        assert challenge.gate_type is not None
        assert len(challenge.user_request_interpretation) > 0
        assert len(challenge.cortex_analysis) > 0
        assert len(challenge.recommended_alternative) > 0
        assert len(challenge.reasoning) > 0
        assert len(challenge.options) > 0
