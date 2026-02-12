"""
Integration tests for ResponseEngine in core orchestrators (Wave H Stage 4).

Tests for AC-ENH082-W2-S4-001: Core Orchestrator ResponseEngine Integration
- Verify mixin integration does not break existing functionality
- Verify response engine is disabled by default (safety)
- Verify backward compatibility (orchestrators work without engine)

Total: 10 regression tests (2 per orchestrator)

Author: Asif Hussain
Created: 2026-02-12
AC-ID: AC-ENH082-W2-S4-001
"""

import pytest
from pathlib import Path

from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
from cortex.orchestrators.core.lens_synthesis import LENSSynthesis


# ============================================================================
# TEST: TDDOrchestrator Integration
# ============================================================================


class TestTDDOrchestratorIntegration:
    """Test ResponseEngine integration with TDDOrchestrator."""

    def test_tdd_orchestrator_has_response_engine_methods(self):
        """Test TDDOrchestrator has ResponseEngine mixin methods."""
        orchestrator = TDDOrchestrator()
        
        # Verify mixin methods present
        assert hasattr(orchestrator, '_init_response_engine')
        assert hasattr(orchestrator, '_compose_response')
        assert hasattr(orchestrator, '_response_config')
        assert hasattr(orchestrator, '_response_engine')

    def test_tdd_orchestrator_response_engine_disabled_by_default(self):
        """Test response engine is disabled by default for safety."""
        orchestrator = TDDOrchestrator()
        
        # Verify disabled by default
        assert orchestrator._response_config.enable_response_engine is False
        
    def test_tdd_orchestrator_backward_compatibility(self):
        """Test TDDOrchestrator works without response engine (backward compat)."""
        orchestrator = TDDOrchestrator()
        
        # Verify orchestrator can initialize successfully
        assert orchestrator is not None
        assert hasattr(orchestrator, 'knowledge_loader')
        assert hasattr(orchestrator, 'guidance_engine')
        
        # Response engine present but disabled = backward compatible
        assert orchestrator._response_config.enable_response_engine is False


# ============================================================================
# TEST: LENSSynthesis Integration
# ============================================================================


class TestLENSSynthesisIntegration:
    """Test ResponseEngine integration with LENSSynthesis."""

    def test_lens_synthesis_has_response_engine_methods(self):
        """Test LENSSynthesis has ResponseEngine mixin methods."""
        orchestrator = LENSSynthesis()
        
        # Verify mixin methods present
        assert hasattr(orchestrator, '_init_response_engine')
        assert hasattr(orchestrator, '_compose_response')
        assert hasattr(orchestrator, '_response_config')
        assert hasattr(orchestrator, '_response_engine')

    def test_lens_synthesis_response_engine_disabled_by_default(self):
        """Test response engine is disabled by default for safety."""
        orchestrator = LENSSynthesis()
        
        # Verify disabled by default
        assert orchestrator._response_config.enable_response_engine is False
        
    def test_lens_synthesis_backward_compatibility(self):
        """Test LENSSynthesis works without response engine (backward compat)."""
        orchestrator = LENSSynthesis()
        
        # Verify orchestrator can initialize successfully
        assert orchestrator is not None
        assert hasattr(orchestrator, 'logger')
        assert hasattr(orchestrator, 'synthesis_history')
        assert hasattr(orchestrator, 'phase_weights')
        
        # Response engine present but disabled = backward compatible
        assert orchestrator._response_config.enable_response_engine is False
