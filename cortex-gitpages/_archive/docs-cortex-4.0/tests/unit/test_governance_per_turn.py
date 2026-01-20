"""
Unit tests for per-turn governance validation (AC-REM-002-01/02/03).

Tests:
- GovernanceRegistry.should_proceed() method validation
- ConversationProtocol per-turn governance validation
- Multi-turn governance consistency

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.core.governance_registry import GovernanceRegistry, GovernanceRule, GovernanceViolationError
from src.core.result import Ok, Err


class TestGovernanceRegistryShouldProceed:
    """Tests for GovernanceRegistry.should_proceed() method (AC-REM-002-01)."""
    
    @pytest.fixture
    def registry(self):
        """Create and initialize registry for testing."""
        reg = GovernanceRegistry()
        reg.reset_instance()
        reg = GovernanceRegistry.instance()
        
        # Initialize with sample Tier 0 rules
        result = reg.initialize()
        assert result.is_ok()
        
        return reg
    
    def test_should_proceed_method_exists(self, registry):
        """Verify GovernanceRegistry.should_proceed() method exists and is callable."""
        # Method should exist
        assert hasattr(registry, 'should_proceed')
        assert callable(getattr(registry, 'should_proceed'))
        
        # Method should not be a stub (must be callable with parameters)
        result = registry.should_proceed(turn_number=1, orchestrator_id="test-orch")
        assert result is not None
    
    def test_should_proceed_valid_state_turn_1(self, registry):
        """Test should_proceed returns Ok(True) for fresh orchestrator (Turn 1)."""
        result = registry.should_proceed(turn_number=1, orchestrator_id="planning-orch")
        
        assert result.is_ok()
        assert result.unwrap() is True
    
    def test_should_proceed_valid_state_turn_2(self, registry):
        """Test should_proceed returns Ok(True) for multi-turn execution (Turn 2+)."""
        result = registry.should_proceed(turn_number=2, orchestrator_id="planning-orch")
        
        assert result.is_ok()
        assert result.unwrap() is True
    
    def test_should_proceed_checks_tier0_immutability(self, registry):
        """Test should_proceed validates TIER-0 immutability."""
        # Get Tier 0 rules
        tier0_rules = registry.get_all_tier0_rules()
        assert len(tier0_rules) > 0  # Verify rules loaded
        
        # Verify all Tier 0 rules are immutable
        for rule in tier0_rules:
            assert rule.is_immutable is True
        
        # should_proceed should check these
        result = registry.should_proceed(turn_number=1, orchestrator_id="test-orch")
        assert result.is_ok()
    
    def test_should_proceed_returns_type_result(self, registry):
        """Test should_proceed returns Result type."""
        result = registry.should_proceed(turn_number=1, orchestrator_id="test-orch")
        
        # Must return Result
        assert hasattr(result, 'is_ok')
        assert hasattr(result, 'is_err')
        assert hasattr(result, 'unwrap')
    
    def test_should_proceed_different_orchestrators(self, registry):
        """Test should_proceed works with different orchestrator IDs."""
        orchestrators = ["planning-orch", "ado-orch", "tdd-orch", "master-orch"]
        
        for orch_id in orchestrators:
            result = registry.should_proceed(turn_number=1, orchestrator_id=orch_id)
            assert result.is_ok()
            assert result.unwrap() is True
    
    def test_should_proceed_multiple_turns(self, registry):
        """Test should_proceed across multiple turns (1-5)."""
        for turn in range(1, 6):
            result = registry.should_proceed(turn_number=turn, orchestrator_id="test-orch")
            assert result.is_ok()
            assert result.unwrap() is True


class TestConversationProtocolGovernanceValidation:
    """Tests for ConversationProtocol per-turn governance validation (AC-REM-002-02)."""
    
    def test_conversation_protocol_governance_method_exists(self):
        """Verify ConversationProtocol has _validate_governance_before_turn() method."""
        from src.core.orchestrator.conversation_protocol import ConversationProtocol
        
        # Protocol should have governance validation method
        assert hasattr(ConversationProtocol, '_validate_governance_before_turn')
    
    def test_conversation_protocol_governance_validation_turn_1(self):
        """Test _validate_governance_before_turn() passes on Turn 1."""
        from src.core.orchestrator.conversation_protocol import ConversationProtocol
        
        protocol = ConversationProtocol("test-orch")
        protocol.current_turn = 1
        
        # Should validate successfully on Turn 1
        result = protocol._validate_governance_before_turn()
        assert result.is_ok()
    
    def test_conversation_protocol_governance_validation_turn_2plus(self):
        """Test _validate_governance_before_turn() passes on Turn 2+."""
        from src.core.orchestrator.conversation_protocol import ConversationProtocol
        
        protocol = ConversationProtocol("test-orch")
        
        # Test multiple turns
        for turn in range(2, 6):
            protocol.current_turn = turn
            result = protocol._validate_governance_before_turn()
            assert result.is_ok(), f"Governance validation should pass on turn {turn}"
    
    def test_conversation_protocol_governance_validation_integration(self):
        """Test multi-turn conversation with governance validation (integration test)."""
        from src.core.orchestrator.conversation_protocol import ConversationProtocol
        
        protocol = ConversationProtocol("planning-orch")
        
        # Simulate 5-turn conversation
        for turn in range(1, 6):
            protocol.current_turn = turn
            result = protocol._validate_governance_before_turn()
            
            # Each turn should validate successfully
            assert result.is_ok(), f"Turn {turn} should pass governance validation"
            assert result.unwrap() is True


class TestPerTurnGovernanceIntegration:
    """Tests for overall per-turn governance integration (AC-REM-002-03)."""
    
    def test_governance_validated_on_each_turn(self):
        """Test governance is validated on every turn (not just first/last)."""
        from src.core.orchestrator.conversation_protocol import ConversationProtocol
        
        protocol = ConversationProtocol("test-orch")
        validation_count = 0
        
        # Simulate calling _validate_governance_before_turn() for each turn
        for turn in range(1, 6):
            protocol.current_turn = turn
            result = protocol._validate_governance_before_turn()
            
            if result.is_ok():
                validation_count += 1
        
        # All 5 turns should have passed validation
        assert validation_count == 5
    
    def test_governance_registry_singleton_consistency(self):
        """Test GovernanceRegistry maintains consistent state across turns."""
        registry = GovernanceRegistry.instance()
        
        # Get rule count
        counts_1 = registry.rule_count_by_tier()
        
        # Call should_proceed multiple times
        for _ in range(5):
            registry.should_proceed(turn_number=1, orchestrator_id="test")
        
        # Rule count should remain consistent
        counts_2 = registry.rule_count_by_tier()
        assert counts_1 == counts_2
    
    def test_tier0_rules_immutable_per_turn(self):
        """Test TIER-0 rules remain immutable across per-turn calls."""
        registry = GovernanceRegistry.instance()
        
        tier0_before = registry.get_all_tier0_rules()
        
        # Call should_proceed multiple times
        for turn in range(1, 6):
            registry.should_proceed(turn_number=turn, orchestrator_id="test-orch")
        
        tier0_after = registry.get_all_tier0_rules()
        
        # Tier 0 rules should not change
        assert len(tier0_before) == len(tier0_after)
        for rule_before, rule_after in zip(tier0_before, tier0_after):
            assert rule_before.rule_id == rule_after.rule_id
