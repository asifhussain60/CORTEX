"""
Tests for GovernedOrchestrator.

Author: Test Suite
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.orchestrators.governed_orchestrator import GovernedOrchestrator


class TestGovernedOrchestrator:
    """Test GovernedOrchestrator orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return GovernedOrchestrator()
    
    def test_initialization(self, orchestrator):
        """Orchestrator should initialize."""
        assert orchestrator is not None
        assert orchestrator.domain == "governed"
    
    def test_execute_basic(self, orchestrator):
        """Orchestrator should execute basic request."""
        request = {'intent': 'test'}
        result = orchestrator.execute(request)
        
        assert result is not None
        assert result.get('success') is not None
        assert result.get('orchestrator') == "GovernedOrchestrator"
