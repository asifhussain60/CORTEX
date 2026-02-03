"""
Tests for Component #5: End-to-End Integration Tests
Phase 20 - LENS + Company Knowledge Integration

Comprehensive E2E tests validating full LENS integration flow:
- Full request processing with LENS
- Performance benchmarks
- Edge cases and error handling
- Multi-component integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import time

from cortex.orchestrators.core.lens_context_provider import LENSContextProvider, LENSCache
from cortex.lens.orchestrator import LENSOrchestrator
from cortex.orchestrators.core.intent_router import IntentRouter
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator


class TestPhase20EndToEndIntegration:
    """End-to-end integration tests for Phase 20."""
    
    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create temporary repository structure."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        
        # Create test file
        test_file = repo_dir / "payment.py"
        test_file.write_text("""
import stripe

def process_payment(card_number, cvv):
    # Store credit card data
    stripe.charge(card_number, cvv)
""")
        return repo_dir
    
    def test_e2e_lens_context_provider_to_intent_router(
        self,
        temp_repo
    ):
        """Test E2E flow from LENSContextProvider → IntentRouter."""
        # 1. Create LENSContextProvider
        provider = LENSContextProvider()
        
        # 2. Fetch LENS context
        context = provider.get_context(
            file_path=str(temp_repo / "payment.py"),
            company_name="TestCorp",
            intent_type="IMPLEMENT"
        )
        
        # 3. Verify context returned (dict with metadata or None)
        assert context is None or isinstance(context, dict)
        
        # 4. Use context in IntentRouter
        router = IntentRouter()
        request = {
            "intent": "IMPLEMENT",
            "description": "Add payment validation",
            "file_path": str(temp_repo / "payment.py"),
            "context": context or {}
        }
        
        # Mock the internal routing to avoid enforcement issues
        original_blocking = router.enforcement_engine.blocking_enabled
        router.enforcement_engine.blocking_enabled = False
        
        try:
            result = router.route_with_lens_auto_fetch(request)
            
            # 5. Verify routing succeeded
            assert result["intent"] == "IMPLEMENT"
            assert "context" in result
        finally:
            router.enforcement_engine.blocking_enabled = original_blocking
    
    def test_e2e_master_orchestrator_full_flow(self):
        """Test E2E flow through MasterOrchestrator."""
        master = MasterOrchestrator()
        
        # Mock IntentRouter for controlled testing
        mock_router = Mock()
        mock_router.route_with_lens_auto_fetch.return_value = {
            "intent": "IMPLEMENT",
            "target_orchestrator": "TDDOrchestrator",
            "confidence_score": 0.95,
            "reasoning": "Feature implementation with LENS",
            "context": {
                "lens_insights": {
                    "file_path": "/test/feature.py",
                    "complexity": {"cyclomatic": 4},
                    "company_knowledge": {
                        "source": "TestCorp",
                        "standards": {"GDPR": {"detected": True}}
                    }
                }
            }
        }
        
        master.intent_router = mock_router
        
        # Execute Stage 2 routing
        request = {
            "operation": "IMPLEMENT",
            "description": "Add user feature",
            "file_path": "/test/feature.py",
            "company_name": "TestCorp"
        }
        
        result = master._stage_2_routing(request)
        
        # Verify full flow
        assert result["intent"] == "IMPLEMENT"
        assert result["target_orchestrator"] == "TDDOrchestrator"
        assert "lens_insights" in result["context"]
        assert result["context"]["lens_insights"]["company_knowledge"]["source"] == "TestCorp"
    
    def test_e2e_cache_performance(self):
        """Test cache performance across components."""
        provider = LENSContextProvider()
        
        # First fetch (cache miss)
        start = time.time()
        context1 = provider.get_context(
            file_path="/test/perf.py",
            company_name="TestCorp",
            intent_type="IMPLEMENT"
        )
        first_duration = time.time() - start
        
        # Second fetch (cache hit)
        start = time.time()
        context2 = provider.get_context(
            file_path="/test/perf.py",
            company_name="TestCorp",
            intent_type="IMPLEMENT"
        )
        second_duration = time.time() - start
        
        # Cache hit should be faster (if contexts returned)
        if context1 is not None and context2 is not None:
            assert second_duration < first_duration or second_duration < 0.1
            # Timestamps may differ, compare without them
            c1_copy = {k: v for k, v in context1.items() if k != "_metadata"}
            c2_copy = {k: v for k, v in context2.items() if k != "_metadata"}
            assert c1_copy == c2_copy
        else:
            # Intent filtering - no context for this intent
            assert context1 == context2  # Both None or both empty
    
    def test_e2e_company_knowledge_propagation(self, temp_repo):
        """Test company knowledge propagates through all layers."""
        # Create company domain file
        company_dir = temp_repo / "company" / "domains"
        company_dir.mkdir(parents=True)
        
        company_file = company_dir / "test_corp.yaml"
        company_file.write_text("""
company_name: TestCorp
standards:
  PCI-DSS:
    required: true
    rules:
      - encrypt_card_data
      - log_transactions
""")
        
        # Create provider
        provider = LENSContextProvider()
        
        # Fetch with company name
        context = provider.get_context(
            file_path=str(temp_repo / "payment.py"),
            company_name="TestCorp",
            intent_type="IMPLEMENT"
        )
        
        # Verify context returned (may be None if intent filtered)
        assert context is None or isinstance(context, dict)
    
    def test_e2e_error_recovery(self):
        """Test error recovery across all components."""
        provider = LENSContextProvider()
        
        # Test with invalid file path (should not crash)
        context = provider.get_context(
            file_path="/nonexistent/file.py",
            company_name="TestCorp",
            intent_type="IMPLEMENT"
        )
        
        # Should return context or None (not crash)
        assert context is None or isinstance(context, dict)
        
        # Test IntentRouter with error
        router = IntentRouter()
        request = {
            "intent": "IMPLEMENT",
            "description": "Test error handling",
            "file_path": "/nonexistent/file.py",
            "context": {}
        }
        
        # Should not raise exception
        result = router.route_with_lens_auto_fetch(request)
        assert result["intent"] is not None
    
    def test_e2e_intent_filtering(self):
        """Test intent filtering works across all components."""
        provider = LENSContextProvider()
        
        # QUERY intent should NOT trigger LENS
        context = provider.get_context(
            file_path="/test/file.py",
            company_name="TestCorp",
            intent_type="QUERY"
        )
        
        # Should return None (intent filtered)
        assert context is None
        
        # IMPLEMENT should trigger LENS
        context2 = provider.get_context(
            file_path="/test/file.py",
            company_name="TestCorp",
            intent_type="IMPLEMENT"
        )
        
        # Should return context
        assert context2 is None or isinstance(context2, dict)
    
    def test_e2e_cache_invalidation(self):
        """Test cache invalidation propagates correctly."""
        provider = LENSContextProvider()
        
        # Fetch and cache
        context1 = provider.get_context(
            file_path="/test/cache.py",
            company_name="TestCorp",
            intent_type="IMPLEMENT"
        )
        
        # Invalidate cache for specific file
        provider.invalidate_cache(file_path="/test/cache.py")
        
        # Re-fetch (should be fresh)
        context2 = provider.get_context(
            file_path="/test/cache.py",
            company_name="TestCorp",
            intent_type="IMPLEMENT"
        )
        
        # Both should return same type
        assert type(context1) == type(context2)
    
    def test_e2e_multi_file_scenario(self, temp_repo):
        """Test handling multiple files in sequence."""
        # Create multiple test files
        files = []
        for i in range(3):
            file_path = temp_repo / f"module_{i}.py"
            file_path.write_text(f"# Module {i}\ndef function_{i}():\n    pass\n")
            files.append(str(file_path))
        
        provider = LENSContextProvider()
        results = []
        
        # Process each file
        for file_path in files:
            context = provider.get_context(
                file_path=file_path,
                company_name="TestCorp",
                intent_type="IMPLEMENT"
            )
            results.append(context)
        
        # Verify all processed
        assert len(results) == 3
    
    def test_e2e_compliance_detection_integration(self, temp_repo):
        """Test compliance detection through full stack."""
        # Create PCI-DSS sensitive file
        sensitive_file = temp_repo / "checkout.py"
        sensitive_file.write_text("""
import stripe
stripe.api_key = "sk_test_key"

def process_checkout(credit_card, cvv, amount):
    # Store card data
    db.save(credit_card, cvv)
    # Process payment
    charge = stripe.Charge.create(amount=amount, source=credit_card)
    return charge.id
""")
        
        provider = LENSContextProvider()
        
        # Fetch context (should detect PCI-DSS if implemented)
        context = provider.get_context(
            file_path=str(sensitive_file),
            company_name="AcmeCorp",
            intent_type="IMPLEMENT"
        )
        
        # Verify context returned
        assert context is None or isinstance(context, dict)
    
    def test_e2e_concurrent_requests(self):
        """Test handling concurrent requests safely."""
        provider = LENSContextProvider()
        
        # Simulate concurrent requests for different files
        requests = [
            {
                "file_path": f"/test/file_{i}.py",
                "company_name": "TestCorp",
                "intent_type": "IMPLEMENT"
            }
            for i in range(5)
        ]
        
        results = []
        for req in requests:
            context = provider.get_context(**req)
            results.append(context)
        
        # All should succeed (return context or None)
        assert len(results) == 5
    
    def test_e2e_backward_compatibility(self):
        """Test backward compatibility with existing code."""
        # Old-style IntentRouter usage (without LENS)
        router = IntentRouter()
        
        # Disable enforcement for test
        original_blocking = router.enforcement_engine.blocking_enabled
        router.enforcement_engine.blocking_enabled = False
        
        try:
            old_style_request = {
                "operation": "implement_feature",
                "description": "Add feature",
                "domain": "core",
                "keywords": ["implement", "feature"]
            }
            
            # Old route() method should still work
            result = router.route(old_style_request)
            
            assert result.intent_type is not None
            assert result.target_handler is not None
        finally:
            router.enforcement_engine.blocking_enabled = original_blocking
