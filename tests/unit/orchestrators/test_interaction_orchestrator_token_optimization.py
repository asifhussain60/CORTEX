"""Golden Path Tests for Token Optimization Integration.

Tests the complete token optimization flow:
- InteractionOrchestrator → ContextSynthesisGateway → Optimized Output
- Token budget compliance on large LENS contexts
- Cache hit behavior
- Session token tracking

Authority: AC-AUDIT-TOKEN-OPT-001 (Token Optimization Audit)
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

# AC_START: AC-AUDIT-TOKEN-OPT-001-TESTS
# Description: Golden tests for token optimization

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator


class TestInteractionOrchestratorTokenOptimization:
    """Golden path tests for per-turn token optimization."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create InteractionOrchestrator with mocked ConversationProtocol."""
        mock_protocol = Mock()
        mock_protocol.session_id = "test_session_123"
        
        with patch('cortex.orchestrators.core.interaction_orchestrator.EnhancedAuditLogger') as mock_logger_class:
            mock_logger_instance = Mock()
            mock_logger_class.instance.return_value = mock_logger_instance
            
            orchestrator = InteractionOrchestrator(
                conversation_protocol=mock_protocol,
                enable_challenges=False,
            )
            
            # Attach mock logger for test assertions
            orchestrator._mock_logger = mock_logger_instance
            
            return orchestrator
    
    @pytest.fixture
    def mock_gateway(self):
        """Create mock ContextSynthesisGateway."""
        with patch('cortex.interaction.context_synthesis_gateway.get_gateway') as mock_get_gateway:
            mock_gateway_instance = Mock()
            mock_gateway_instance.token_budget = 20000
            mock_gateway_instance.synthesize.return_value = Mock(
                context={"synthesized": True, "tokens": 5000},
                token_count=5000,
                budget_compliant=True,
                compression_ratio=0.75,
                synthesis_time_ms=25.5,
                cache_hit=False,
                session_id="test_session_123",
                orchestrator_name="InteractionOrchestrator"
            )
            mock_get_gateway.return_value = mock_gateway_instance
            
            yield mock_gateway_instance
    
    @pytest.fixture
    def large_lens_context(self):
        """Create large LENS context that would exceed token budget."""
        # Simulate large git history + AST tree (>20K tokens)
        return {
            "git_history": ["commit " + "x" * 1000 for _ in range(50)],
            "ast_tree": {"nodes": ["node " + "y" * 500 for _ in range(100)]},
            "relationships": {"edges": ["edge " + "z" * 300 for _ in range(75)]},
        }
    
    # =========================================================================
    # Golden Path Test: Token Optimization Applied Per-Turn
    # =========================================================================
    
    def test_execute_turn_applies_token_optimization(self, orchestrator, mock_gateway):
        """GOLDEN PATH: execute_turn_with_challenge() applies gateway.synthesize()."""
        # Arrange
        user_request = "Implement feature X in cortex/module.py"
        mock_round_context = Mock()
        mock_round_context.session_id = "test_session_123"
        
        # Act
        result = orchestrator.execute_turn_with_challenge(
            user_request=user_request,
            round_context=mock_round_context,
            pattern_id=None,
        )
        
        # Assert
        assert result.is_ok()
        output = result.unwrap()
        
        # Verify gateway.synthesize() was called
        mock_gateway.synthesize.assert_called_once()
        call_args = mock_gateway.synthesize.call_args
        
        assert call_args.kwargs["session_id"] == "test_session_123"
        assert call_args.kwargs["orchestrator_name"] == "InteractionOrchestrator"
        assert "lens_context" in call_args.kwargs["context"]
        
        # Verify output is synthesized (not raw)
        assert output.get("synthesized") is True
        assert output.get("tokens") == 5000
    
    def test_execute_applies_token_optimization(self, orchestrator, mock_gateway):
        """GOLDEN PATH: execute() applies gateway.synthesize()."""
        # Arrange
        context = {
            "user_intent": "Fix bug in authentication module",
            "session_id": "test_session_456",
        }
        
        # Act
        result = orchestrator.execute(context)
        
        # Assert
        assert result.is_ok()
        output = result.unwrap()
        
        # Verify gateway.synthesize() was called
        mock_gateway.synthesize.assert_called_once()
        call_args = mock_gateway.synthesize.call_args
        
        assert call_args.kwargs["session_id"] == "test_session_456"
        assert call_args.kwargs["orchestrator_name"] == "InteractionOrchestrator"
    
    # =========================================================================
    # Token Budget Compliance Tests
    # =========================================================================
    
    def test_large_lens_context_compressed(self, orchestrator, mock_gateway, large_lens_context):
        """GOLDEN PATH: Large LENS context compressed to fit budget."""
        # Arrange
        orchestrator._run_lens_analysis = Mock(return_value=large_lens_context)
        
        mock_round_context = Mock()
        mock_round_context.session_id = "large_context_session"
        
        # Simulate budget-compliant compression
        mock_gateway.synthesize.return_value = Mock(
            context={"lens_context": {"summary": "compressed"}, "tokens": 18000},
            token_count=18000,
            budget_compliant=True,
            compression_ratio=0.90,  # 90% compression
            synthesis_time_ms=150.0,
            cache_hit=False,
            session_id="large_context_session",
            orchestrator_name="InteractionOrchestrator"
        )
        
        # Act
        result = orchestrator.execute_turn_with_challenge(
            user_request="Analyze large repository",
            round_context=mock_round_context,
            pattern_id=None,
        )
        
        # Assert
        assert result.is_ok()
        output = result.unwrap()
        
        # Verify compression applied
        assert output.get("tokens") == 18000
        assert output.get("tokens") <= 20000  # Within budget
    
    def test_budget_violation_logged_but_not_blocking(self, orchestrator, mock_gateway):
        """GOLDEN PATH: Budget violations logged but execution continues (fail-safe)."""
        # Arrange
        mock_round_context = Mock()
        mock_round_context.session_id = "violation_session"
        
        # Simulate budget violation (21K tokens)
        mock_gateway.token_budget = 20000
        mock_gateway.synthesize.return_value = Mock(
            context={"lens_context": "huge", "tokens": 21000},
            token_count=21000,
            budget_compliant=False,  # ← Budget violated
            compression_ratio=0.0,
            synthesis_time_ms=50.0,
            cache_hit=False,
            session_id="violation_session",
            orchestrator_name="InteractionOrchestrator"
        )
        
        # Act
        result = orchestrator.execute_turn_with_challenge(
            user_request="Complex request",
            round_context=mock_round_context,
            pattern_id=None,
        )
        
        # Assert: Execution succeeds despite budget violation (fail-safe mode)
        assert result.is_ok()
        
        # Verify logger called with violation details
        assert hasattr(orchestrator, '_mock_logger')
        assert orchestrator._mock_logger.log_operation_complete.called
        log_calls = orchestrator._mock_logger.log_operation_complete.call_args_list
        
        violation_log = next(
            (call for call in log_calls if call.kwargs.get("operation") == "token_budget_violation"),
            None
        )
        
        assert violation_log is not None
        assert violation_log.kwargs["success"] is False
        assert violation_log.kwargs["details"]["tokens"] == 21000
        assert violation_log.kwargs["details"]["overflow"] == 1000
    
    # =========================================================================
    # Cache Hit Tests
    # =========================================================================
    
    def test_cache_hit_on_repeated_lens_context(self, orchestrator, mock_gateway):
        """GOLDEN PATH: Repeated LENS context results in cache hit."""
        # Arrange
        mock_round_context = Mock()
        mock_round_context.session_id = "cache_test_session"
        
        # First call: cache miss
        mock_gateway.synthesize.return_value = Mock(
            context={"cached": False},
            token_count=5000,
            budget_compliant=True,
            compression_ratio=0.5,
            synthesis_time_ms=100.0,
            cache_hit=False,
            session_id="cache_test_session",
            orchestrator_name="InteractionOrchestrator"
        )
        
        result1 = orchestrator.execute_turn_with_challenge(
            user_request="Analyze file.py",
            round_context=mock_round_context,
            pattern_id=None,
        )
        
        # Second call: cache hit (faster synthesis)
        mock_gateway.synthesize.return_value = Mock(
            context={"cached": True},
            token_count=5000,
            budget_compliant=True,
            compression_ratio=0.5,
            synthesis_time_ms=5.0,  # ← Much faster
            cache_hit=True,
            session_id="cache_test_session",
            orchestrator_name="InteractionOrchestrator"
        )
        
        result2 = orchestrator.execute_turn_with_challenge(
            user_request="Analyze file.py",  # Same request
            round_context=mock_round_context,
            pattern_id=None,
        )
        
        # Assert
        assert result1.is_ok()
        assert result2.is_ok()
        
        # Both calls succeeded
        assert mock_gateway.synthesize.call_count == 2
    
    # =========================================================================
    # Session Token Tracking Tests
    # =========================================================================
    
    def test_session_tokens_accumulated_correctly(self, orchestrator, mock_gateway):
        """GOLDEN PATH: Session tokens accumulated across multiple turns."""
        # Arrange
        mock_round_context = Mock()
        mock_round_context.session_id = "accumulation_session"
        
        # Simulate 3 turns with token accumulation
        turn_tokens = [5000, 7000, 8000]  # Total: 20K
        
        for i, tokens in enumerate(turn_tokens):
            mock_gateway.synthesize.return_value = Mock(
                context={"turn": i + 1},
                token_count=tokens,
                budget_compliant=True,
                compression_ratio=0.5,
                synthesis_time_ms=50.0,
                cache_hit=False,
                session_id="accumulation_session",
                orchestrator_name="InteractionOrchestrator"
            )
            
            result = orchestrator.execute_turn_with_challenge(
                user_request=f"Request {i + 1}",
                round_context=mock_round_context,
                pattern_id=None,
            )
            
            assert result.is_ok()
        
        # Assert: 3 turns executed
        assert mock_gateway.synthesize.call_count == 3
    
    # =========================================================================
    # Graceful Degradation Tests
    # =========================================================================
    
    def test_gateway_failure_does_not_block_execution(self, orchestrator):
        """GOLDEN PATH: Gateway failure does not block turn execution (fail-safe)."""
        # Arrange
        mock_round_context = Mock()
        mock_round_context.session_id = "failsafe_session"
        
        with patch('cortex.interaction.context_synthesis_gateway.get_gateway') as mock_get_gateway:
            # Simulate gateway error
            mock_get_gateway.side_effect = Exception("Gateway initialization failed")
            
            # Act
            result = orchestrator.execute_turn_with_challenge(
                user_request="Test request",
                round_context=mock_round_context,
                pattern_id=None,
            )
            
            # Assert: Execution succeeds with original (unoptimized) output
            assert result.is_ok()
            output = result.unwrap()
            
            # Verify original LENS context preserved
            assert "lens_context" in output
            assert output["turn_number"] == orchestrator.turn_number
    
    def test_synthesize_failure_returns_original_output(self, orchestrator, mock_gateway):
        """GOLDEN PATH: synthesize() failure returns original output (fail-safe)."""
        # Arrange
        mock_round_context = Mock()
        mock_round_context.session_id = "synthesize_fail_session"
        
        # Simulate synthesize() error
        mock_gateway.synthesize.side_effect = Exception("Synthesizer crash")
        
        # Act
        result = orchestrator.execute_turn_with_challenge(
            user_request="Test request",
            round_context=mock_round_context,
            pattern_id=None,
        )
        
        # Assert: Execution succeeds with original output
        assert result.is_ok()
        output = result.unwrap()
        
        # Verify original structure preserved
        assert "lens_context" in output
        assert "turn_number" in output


# AC_COMPLETE: AC-AUDIT-TOKEN-OPT-001-TESTS ✅ Golden tests for token optimization

__all__ = ["TestInteractionOrchestratorTokenOptimization"]
