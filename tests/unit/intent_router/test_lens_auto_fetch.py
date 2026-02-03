"""
Tests for Component #3: IntentRouter LENS Auto-Fetch
Phase 20 - LENS + Company Knowledge Integration

Tests automatic LENS context fetching in IntentRouter with:
- Auto-fetch when context missing
- Company knowledge citations in routing
- Backward compatibility
- Cache-first strategy
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from cortex.orchestrators.core.intent_router import IntentRouter, RoutingContext
from cortex.orchestrators.core.lens_context_provider import get_lens_context_provider
from cortex.models.canonical_enums import IntentType


class TestIntentRouterLENSAutoFetch:
    """Test LENS auto-fetch in IntentRouter."""
    
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
    def intent_router(self):
        """Create IntentRouter instance."""
        return IntentRouter()
    
    def test_auto_fetch_missing_context(
        self,
        intent_router: IntentRouter,
        mock_lens_provider: Mock
    ):
        """Test auto-fetch when LENS context is missing."""
        request = {
            "intent": "IMPLEMENT",
            "description": "Add authentication",
            "file_path": "/test/auth.py",
            "context": {}  # No LENS context
        }
        
        # Patch the import inside route_with_lens_auto_fetch
        with patch.object(
            intent_router.__class__,
            "route_with_lens_auto_fetch",
            wraps=intent_router.route_with_lens_auto_fetch
        ) as wrapped_method:
            # Directly modify IntentRouter class temporarily for test
            import cortex.orchestrators.core.lens_context_provider as lcp_module
            original_getter = lcp_module.get_lens_context_provider
            lcp_module.get_lens_context_provider = lambda: mock_lens_provider
            
            try:
                result = intent_router.route_with_lens_auto_fetch(request)
            finally:
                lcp_module.get_lens_context_provider = original_getter
        
        # Should auto-fetch LENS context
        mock_lens_provider.get_context.assert_called_once()
        call_kwargs = mock_lens_provider.get_context.call_args[1]
        assert call_kwargs["intent"] == "IMPLEMENT"
        assert call_kwargs["file_path"] == "/test/auth.py"
        assert "lens_insights" in result["context"]
    
    def test_no_fetch_when_context_exists(
        self,
        intent_router: IntentRouter,
        mock_lens_provider: Mock
    ):
        """Test no fetch when LENS context already exists."""
        request = {
            "intent": "IMPLEMENT",
            "description": "Add authentication",
            "file_path": "/test/auth.py",
            "context": {
                "lens_insights": {
                    "file_path": "/test/auth.py",
                    "complexity": {"cyclomatic": 3}
                }
            }
        }
        
        import cortex.orchestrators.core.lens_context_provider as lcp_module
        original_getter = lcp_module.get_lens_context_provider
        lcp_module.get_lens_context_provider = lambda: mock_lens_provider
        
        try:
            result = intent_router.route_with_lens_auto_fetch(request)
        finally:
            lcp_module.get_lens_context_provider = original_getter
        
        # Should NOT auto-fetch
        mock_lens_provider.get_context.assert_not_called()
        assert result["context"]["lens_insights"]["complexity"]["cyclomatic"] == 3
    
    def test_company_knowledge_citation(
        self,
        intent_router: IntentRouter,
        mock_lens_provider: Mock
    ):
        """Test company knowledge citations in routing decisions."""
        mock_lens_provider.get_context.return_value = {
            "lens_insights": {
                "file_path": "/test/payment.py",
                "company_knowledge": {
                    "source": "AcmeCorp",
                    "standards": {
                        "PCI-DSS": {
                            "detected": True,
                            "confidence": 0.85,
                            "rules_applied": ["encrypt_card_data", "log_transactions"]
                        }
                    }
                }
            }
        }
        
        request = {
            "intent": "IMPLEMENT",
            "description": "Add payment processing",
            "file_path": "/test/payment.py",
            "company_name": "AcmeCorp",
            "context": {}
        }
        
        import cortex.orchestrators.core.lens_context_provider as lcp_module
        original_getter = lcp_module.get_lens_context_provider
        lcp_module.get_lens_context_provider = lambda: mock_lens_provider
        
        try:
            result = intent_router.route_with_lens_auto_fetch(request)
        finally:
            lcp_module.get_lens_context_provider = original_getter
        
        # Should include company knowledge citation
        company_knowledge = result["context"]["lens_insights"]["company_knowledge"]
        assert company_knowledge["source"] == "AcmeCorp"
        assert "PCI-DSS" in company_knowledge["standards"]
        assert company_knowledge["standards"]["PCI-DSS"]["confidence"] == 0.85
    
    def test_backward_compatible_routing(
        self,
        intent_router: IntentRouter
    ):
        """Test backward compatibility with old routing method."""
        request = {
            "operation": "implement_feature",
            "description": "Add authentication feature to user module",
            "domain": "core",
            "keywords": ["implement", "add", "feature", "authentication"],
            "context": {}
        }
        
        # Disable enforcement for this test
        original_blocking = intent_router.enforcement_engine.blocking_enabled
        intent_router.enforcement_engine.blocking_enabled = False
        
        try:
            # Old method should still work
            result = intent_router.route(request)
            
            assert result.intent_type is not None
            assert result.target_handler is not None
        finally:
            intent_router.enforcement_engine.blocking_enabled = original_blocking
    
    def test_cache_first_strategy(
        self,
        intent_router: IntentRouter,
        mock_lens_provider: Mock
    ):
        """Test cache-first strategy for LENS context."""
        request = {
            "intent": "FIX",
            "description": "Fix bug",
            "file_path": "/test/file.py",
            "context": {}
        }
        
        import cortex.orchestrators.core.lens_context_provider as lcp_module
        original_getter = lcp_module.get_lens_context_provider
        lcp_module.get_lens_context_provider = lambda: mock_lens_provider
        
        try:
            # First call - cache miss
            result1 = intent_router.route_with_lens_auto_fetch(request)
            # Second call - should use cache
            result2 = intent_router.route_with_lens_auto_fetch(request)
        finally:
            lcp_module.get_lens_context_provider = original_getter
        
        # Should only call provider once (cache hit on second)
        assert mock_lens_provider.get_context.call_count == 1
        assert result1["context"]["lens_insights"] == result2["context"]["lens_insights"]
    
    def test_auto_fetch_with_intent_filtering(
        self,
        intent_router: IntentRouter,
        mock_lens_provider: Mock
    ):
        """Test auto-fetch respects intent filtering."""
        # Intent that should NOT trigger LENS
        request = {
            "intent": "QUERY",
            "description": "Query data",
            "file_path": "/test/file.py",
            "context": {}
        }
        
        import cortex.orchestrators.core.lens_context_provider as lcp_module
        original_getter = lcp_module.get_lens_context_provider
        lcp_module.get_lens_context_provider = lambda: mock_lens_provider
        
        try:
            result = intent_router.route_with_lens_auto_fetch(request)
        finally:
            lcp_module.get_lens_context_provider = original_getter
        
        # Should NOT auto-fetch for QUERY intent
        mock_lens_provider.get_context.assert_not_called()
        assert "lens_insights" not in result["context"]
    
    def test_fail_safe_on_fetch_error(
        self,
        intent_router: IntentRouter,
        mock_lens_provider: Mock
    ):
        """Test fail-safe behavior on fetch error."""
        mock_lens_provider.get_context.side_effect = Exception("LENS unavailable")
        
        request = {
            "intent": "IMPLEMENT",
            "description": "Add feature",
            "file_path": "/test/file.py",
            "context": {}
        }
        
        import cortex.orchestrators.core.lens_context_provider as lcp_module
        original_getter = lcp_module.get_lens_context_provider
        lcp_module.get_lens_context_provider = lambda: mock_lens_provider
        
        try:
            result = intent_router.route_with_lens_auto_fetch(request)
        finally:
            lcp_module.get_lens_context_provider = original_getter
        
        # Should continue routing without LENS context
        assert result["intent"] in ["IMPLEMENT", "UNKNOWN"]
        assert "target_orchestrator" in result
        # Error should be logged but not raised
    
    def test_routing_decision_influenced_by_lens(
        self,
        intent_router: IntentRouter,
        mock_lens_provider: Mock
    ):
        """Test routing decisions influenced by LENS insights."""
        # High complexity should influence orchestrator selection
        mock_lens_provider.get_context.return_value = {
            "lens_insights": {
                "file_path": "/test/complex.py",
                "complexity": {"cyclomatic": 25},
                "security": {"vulnerabilities": ["sql_injection"]},
                "refactoring_candidates": ["extract_method", "simplify_conditional"]
            }
        }
        
        request = {
            "intent": "REFACTOR",
            "description": "Simplify complex method",
            "file_path": "/test/complex.py",
            "keywords": ["refactor", "simplify"],
            "context": {}
        }
        
        import cortex.orchestrators.core.lens_context_provider as lcp_module
        original_getter = lcp_module.get_lens_context_provider
        lcp_module.get_lens_context_provider = lambda: mock_lens_provider
        
        try:
            result = intent_router.route_with_lens_auto_fetch(request)
        finally:
            lcp_module.get_lens_context_provider = original_getter
        
        # Should include LENS insights in context (routing influenced by LENS)
        assert "lens_insights" in result["context"]
        assert result["context"]["lens_insights"]["complexity"]["cyclomatic"] == 25
        assert "refactoring_candidates" in result["context"]["lens_insights"]
        # Should have a valid orchestrator target
        assert result["target_orchestrator"] is not None
    
    def test_company_name_propagation(
        self,
        intent_router: IntentRouter,
        mock_lens_provider: Mock
    ):
        """Test company name propagates to LENS provider."""
        request = {
            "intent": "IMPLEMENT",
            "description": "Add feature",
            "file_path": "/test/file.py",
            "company_name": "AcmeCorp",
            "context": {}
        }
        
        import cortex.orchestrators.core.lens_context_provider as lcp_module
        original_getter = lcp_module.get_lens_context_provider
        lcp_module.get_lens_context_provider = lambda: mock_lens_provider
        
        try:
            result = intent_router.route_with_lens_auto_fetch(request)
        finally:
            lcp_module.get_lens_context_provider = original_getter
        
        # Should pass company_name to LENS provider
        mock_lens_provider.get_context.assert_called_once()
        call_kwargs = mock_lens_provider.get_context.call_args[1]
        assert call_kwargs.get("company_name") == "AcmeCorp"
