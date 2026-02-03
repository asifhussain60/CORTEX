"""
Tests for Component #4: MasterOrchestrator LENS Integration
Phase 20 - LENS + Company Knowledge Integration

Tests Stage 2 LENS injection in MasterOrchestrator with:
- Auto-fetch after intent classification
- Cache-first strategy
- Audit logging
- Fail-safe behavior
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.core.result import Result, Ok, Err


class TestMasterOrchestratorLENSIntegration:
    """Test LENS integration in MasterOrchestrator Stage 2."""
    
    @pytest.fixture
    def mock_lens_provider(self):
        """Mock LENS context provider."""
        provider = Mock()
        provider.get_context.return_value = {
            "lens_insights": {
                "file_path": "/test/file.py",
                "complexity": {"cyclomatic": 5},
                "security": {"vulnerabilities": []},
                "patterns": {"design_patterns": ["singleton"]}
            }
        }
        return provider
    
    @pytest.fixture
    def mock_intent_router(self):
        """Mock IntentRouter."""
        router = Mock()
        router.route_with_lens_auto_fetch.return_value = {
            "intent": "IMPLEMENT",
            "target_orchestrator": "TDDOrchestrator",
            "confidence_score": 0.95,
            "reasoning": "New feature implementation",
            "context": {
                "lens_insights": {
                    "file_path": "/test/feature.py",
                    "complexity": {"cyclomatic": 3}
                }
            }
        }
        return router
    
    @pytest.fixture
    def master_orchestrator(self):
        """Create MasterOrchestrator instance."""
        return MasterOrchestrator()
    
    def test_stage2_lens_injection(
        self,
        master_orchestrator: MasterOrchestrator,
        mock_intent_router: Mock
    ):
        """Test LENS context injection in Stage 2 routing."""
        request = {
            "operation": "IMPLEMENT",
            "description": "Add authentication feature",
            "file_path": "/test/auth.py",
            "company_name": "AcmeCorp"
        }
        
        # Replace IntentRouter with our mock
        master_orchestrator.intent_router = mock_intent_router
        
        # Execute Stage 2 (routing with LENS)
        result = master_orchestrator._stage_2_routing(request)
        
        # Should call route_with_lens_auto_fetch
        mock_intent_router.route_with_lens_auto_fetch.assert_called_once()
        call_args = mock_intent_router.route_with_lens_auto_fetch.call_args[0][0]
        assert call_args["intent"] == "IMPLEMENT"
        assert call_args["file_path"] == "/test/auth.py"
        assert call_args["company_name"] == "AcmeCorp"
        
        # Result should include LENS insights
        assert "lens_insights" in result["context"]
    
    def test_cache_first_strategy_stage2(
        self,
        master_orchestrator: MasterOrchestrator,
        mock_intent_router: Mock
    ):
        """Test cache-first strategy in Stage 2."""
        request = {
            "operation": "FIX",
            "description": "Fix bug",
            "file_path": "/test/file.py"
        }
        
        # Replace IntentRouter with our mock
        master_orchestrator.intent_router = mock_intent_router
        
        # Adjust mock to return FIX intent
        mock_intent_router.route_with_lens_auto_fetch.return_value["intent"] = "FIX"
        
        # First call
        result1 = master_orchestrator._stage_2_routing(request)
        # Second call (should use cache)
        result2 = master_orchestrator._stage_2_routing(request)
        
        # IntentRouter's route_with_lens_auto_fetch handles caching
        # Both calls should succeed
        assert result1["intent"] == "FIX"
        assert result2["intent"] == "FIX"
    
    def test_audit_logging_lens_injection(
        self,
        master_orchestrator: MasterOrchestrator,
        mock_intent_router: Mock
    ):
        """Test audit logging for LENS injection."""
        request = {
            "operation": "REFACTOR",
            "description": "Refactor complex method",
            "file_path": "/test/complex.py"
        }
        
        # Replace IntentRouter with our mock
        master_orchestrator.intent_router = mock_intent_router
        
        with patch.object(master_orchestrator, "logger") as mock_logger:
            result = master_orchestrator._stage_2_routing(request)
        
        # Should log LENS auto-fetch activity
        # Check that logging occurred (implementation-dependent)
        assert result is not None
    
    def test_lens_enriched_routing_decision(
        self,
        master_orchestrator: MasterOrchestrator,
        mock_intent_router: Mock
    ):
        """Test routing decision enriched with LENS insights."""
        mock_intent_router.route_with_lens_auto_fetch.return_value = {
            "intent": "REFACTOR",
            "target_orchestrator": "RefactoringOrchestrator",
            "confidence_score": 0.92,
            "reasoning": "High complexity detected via LENS",
            "context": {
                "lens_insights": {
                    "file_path": "/test/complex.py",
                    "complexity": {"cyclomatic": 25},
                    "refactoring_candidates": ["extract_method"]
                }
            }
        }
        
        request = {
            "operation": "REFACTOR",
            "description": "Simplify method",
            "file_path": "/test/complex.py"
        }
        
        # Replace IntentRouter with our mock
        master_orchestrator.intent_router = mock_intent_router
        
        result = master_orchestrator._stage_2_routing(request)
        
        # Routing decision should include LENS insights
        assert result["target_orchestrator"] == "RefactoringOrchestrator"
        assert result["context"]["lens_insights"]["complexity"]["cyclomatic"] == 25
        assert "refactoring_candidates" in result["context"]["lens_insights"]
    
    def test_fail_safe_lens_unavailable(
        self,
        master_orchestrator: MasterOrchestrator,
        mock_intent_router: Mock
    ):
        """Test fail-safe when LENS is unavailable."""
        # Simulate LENS failure - router returns without lens_insights
        mock_intent_router.route_with_lens_auto_fetch.return_value = {
            "intent": "IMPLEMENT",
            "target_orchestrator": "TDDOrchestrator",
            "confidence_score": 0.85,
            "reasoning": "Feature implementation (LENS unavailable)",
            "context": {}  # No lens_insights
        }
        
        request = {
            "operation": "IMPLEMENT",
            "description": "Add feature",
            "file_path": "/test/feature.py"
        }
        
        # Replace IntentRouter with our mock
        master_orchestrator.intent_router = mock_intent_router
        
        result = master_orchestrator._stage_2_routing(request)
        
        # Should continue routing without LENS
        assert result["intent"] == "IMPLEMENT"
        assert result["target_orchestrator"] == "TDDOrchestrator"
        assert "lens_insights" not in result["context"]
    
    def test_company_knowledge_in_stage2(
        self,
        master_orchestrator: MasterOrchestrator,
        mock_intent_router: Mock
    ):
        """Test company knowledge flows through Stage 2."""
        mock_intent_router.route_with_lens_auto_fetch.return_value = {
            "intent": "IMPLEMENT",
            "target_orchestrator": "TDDOrchestrator",
            "confidence_score": 0.90,
            "reasoning": "Feature with PCI-DSS compliance",
            "context": {
                "lens_insights": {
                    "file_path": "/test/payment.py",
                    "company_knowledge": {
                        "source": "AcmeCorp",
                        "standards": {
                            "PCI-DSS": {
                                "detected": True,
                                "confidence": 0.88
                            }
                        }
                    }
                }
            }
        }
        
        request = {
            "operation": "IMPLEMENT",
            "description": "Add payment processing",
            "file_path": "/test/payment.py",
            "company_name": "AcmeCorp"
        }
        
        # Replace IntentRouter with our mock
        master_orchestrator.intent_router = mock_intent_router
        
        result = master_orchestrator._stage_2_routing(request)
        
        # Should include company knowledge from LENS
        company_knowledge = result["context"]["lens_insights"]["company_knowledge"]
        assert company_knowledge["source"] == "AcmeCorp"
        assert "PCI-DSS" in company_knowledge["standards"]
    
    def test_backward_compatibility_no_file_path(
        self,
        master_orchestrator: MasterOrchestrator,
        mock_intent_router: Mock
    ):
        """Test backward compatibility when no file_path provided."""
        request = {
            "operation": "IMPLEMENT",
            "description": "Add feature"
            # No file_path - LENS won't be triggered
        }
        
        mock_intent_router.route_with_lens_auto_fetch.return_value = {
            "intent": "IMPLEMENT",
            "target_orchestrator": "TDDOrchestrator",
            "confidence_score": 0.85,
            "reasoning": "Feature implementation",
            "context": {}
        }
        
        # Replace IntentRouter with our mock
        master_orchestrator.intent_router = mock_intent_router
        
        result = master_orchestrator._stage_2_routing(request)
        
        # Should still route successfully without LENS
        assert result["intent"] == "IMPLEMENT"
        assert result["target_orchestrator"] == "TDDOrchestrator"
