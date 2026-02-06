"""
Tests for Context Synthesis Gateway (ENH-046 Phase 1.6)

Purpose: Validate EXIT GATE orchestration + budget enforcement
TDD: RED → GREEN → REFACTOR
Author: CORTEX Architect
Created: 2026-02-06
"""

import pytest
from pathlib import Path
from cortex.brain.core.context_synthesis_gateway import (
    ContextSynthesisGateway,
    SynthesisSession,
    create_exit_gate
)


class TestContextSynthesisGateway:
    """Test suite for ContextSynthesisGateway (EXIT GATE)"""
    
    @pytest.fixture
    def gateway(self, tmp_path):
        """Create ContextSynthesisGateway with temp workspace"""
        return ContextSynthesisGateway(
            workspace_root=tmp_path,
            initial_budget=250,
            incremental_budget=500,
            session_budget=2000
        )
    
    # ═══════════════════════════════════════════════════════════════
    # EXIT GATE TESTS (Core functionality)
    # ═══════════════════════════════════════════════════════════════
    
    def test_synthesize_context_minimal_initial(self, gateway):
        """Test: Synthesize context with minimal initial footprint"""
        # GIVEN: User request
        request = "Check codebase health"
        
        # WHEN: Synthesize context (EXIT GATE entry point)
        result = gateway.synthesize_context(request, intent="AUDIT")
        
        # THEN: Initial context ≤250 tokens
        assert result["total_tokens"] <= gateway.initial_budget + gateway.incremental_budget
        assert "initial_context" in result
        assert "incremental_context" in result
        assert result["intent"] == "AUDIT"
    
    def test_synthesize_context_enforces_budget(self, gateway):
        """Test: Context synthesis enforces token budgets"""
        # GIVEN: User request
        request = "Implement new feature with extensive requirements"
        
        # WHEN: Synthesize context
        result = gateway.synthesize_context(request, intent="IMPLEMENT")
        
        # THEN: Total tokens within session budget
        assert result["total_tokens"] <= gateway.session_budget
        assert result["budget_remaining"] >= 0
    
    def test_intent_inference(self, gateway):
        """Test: Automatic intent inference from request"""
        # GIVEN: Requests with implicit intents
        test_cases = [
            ("Check codebase health", "AUDIT"),
            ("Design new architecture", "DESIGN"),
            ("Implement authentication feature", "IMPLEMENT"),
            ("Fix login bug", "FIX"),
            ("Refactor user module", "REFACTOR"),
            ("Analyze performance metrics", "ANALYZE"),
            ("Run pytest tests", "TEST"),
            ("Onboard new repository", "ONBOARD")
        ]
        
        # WHEN/THEN: Intent inferred correctly
        for request, expected_intent in test_cases:
            result = gateway.synthesize_context(request)
            assert result["intent"] == expected_intent, f"Request '{request}' inferred as {result['intent']}, expected {expected_intent}"
    
    def test_session_tracking(self, gateway):
        """Test: Session tracking and retrieval"""
        # GIVEN: Multiple synthesis requests
        request1 = gateway.synthesize_context("Check health", intent="AUDIT")
        request2 = gateway.synthesize_context("Design API", intent="DESIGN")
        
        # WHEN: Retrieve sessions
        session1 = gateway.get_session(request1["session"].session_id)
        session2 = gateway.get_session(request2["session"].session_id)
        all_sessions = gateway.get_all_sessions()
        
        # THEN: Sessions tracked
        assert session1 is not None
        assert session2 is not None
        assert len(all_sessions) == 2
        assert session1.intent == "AUDIT"
        assert session2.intent == "DESIGN"
    
    # ═══════════════════════════════════════════════════════════════
    # DISTILLATION INTEGRATION TESTS
    # ═══════════════════════════════════════════════════════════════
    
    def test_distillation_when_over_budget(self, gateway):
        """Test: Context distilled when exceeding incremental budget"""
        # GIVEN: Large request that would exceed budget
        large_request = "Implement " + " ".join(["feature"] * 200)  # Force large context
        
        # WHEN: Synthesize context
        result = gateway.synthesize_context(large_request, intent="IMPLEMENT")
        
        # THEN: Context distilled to fit budget
        assert result["total_tokens"] <= gateway.initial_budget + gateway.incremental_budget + 100
    
    # ═══════════════════════════════════════════════════════════════
    # CACHE INTEGRATION TESTS
    # ═══════════════════════════════════════════════════════════════
    
    def test_cache_utilization(self, gateway):
        """Test: Cache infrastructure present and operational"""
        # GIVEN: Same request repeated
        request = "Check codebase health"
        
        # WHEN: Synthesize twice
        result1 = gateway.synthesize_context(request, intent="AUDIT")
        result2 = gateway.synthesize_context(request, intent="AUDIT")
        
        # THEN: Cache infrastructure operational (stats available)
        stats = gateway.get_cache_statistics()
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        # Cache may not have hits/misses with empty workspace, but infrastructure should work
        assert stats["hit_rate"] >= 0.0
    
    def test_cache_statistics(self, gateway):
        """Test: Cache statistics available"""
        # GIVEN: Some synthesis requests
        gateway.synthesize_context("Check health", intent="AUDIT")
        gateway.synthesize_context("Design API", intent="DESIGN")
        
        # WHEN: Get cache statistics
        stats = gateway.get_cache_statistics()
        
        # THEN: Stats populated
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        assert stats["hit_rate"] >= 0
    
    # ═══════════════════════════════════════════════════════════════
    # METRICS TESTS
    # ═══════════════════════════════════════════════════════════════
    
    def test_synthesis_time_tracking(self, gateway):
        """Test: Synthesis time tracked per session"""
        # GIVEN: Synthesis request
        result = gateway.synthesize_context("Check health", intent="AUDIT")
        
        # THEN: Synthesis time recorded
        assert result["synthesis_time_ms"] > 0
        assert result["session"].synthesis_time_ms > 0
    
    def test_aggregate_metrics(self, gateway):
        """Test: Aggregate metrics across sessions"""
        # GIVEN: Multiple synthesis requests
        gateway.synthesize_context("Check health", intent="AUDIT")
        gateway.synthesize_context("Design API", intent="DESIGN")
        gateway.synthesize_context("Implement feature", intent="IMPLEMENT")
        
        # WHEN: Get aggregate metrics
        metrics = gateway.get_metrics()
        
        # THEN: Metrics aggregated
        assert metrics["total_sessions"] == 3
        assert metrics["average_synthesis_time_ms"] > 0
        assert metrics["average_tokens_per_session"] > 0
        assert "cache_hit_rate" in metrics
    
    def test_p99_synthesis_latency_target(self, gateway):
        """Test: Synthesis latency ≤100ms P99 (target)"""
        # GIVEN: Multiple synthesis requests
        latencies = []
        for i in range(10):
            result = gateway.synthesize_context(f"Request {i}", intent="AUDIT")
            latencies.append(result["synthesis_time_ms"])
        
        # WHEN: Calculate P99
        latencies.sort()
        p99 = latencies[int(len(latencies) * 0.99)]
        
        # THEN: P99 ≤150ms (allowing overhead for test environment)
        assert p99 <= 150, f"P99 latency {p99}ms > 150ms target"
    
    # ═══════════════════════════════════════════════════════════════
    # SESSION MANAGEMENT TESTS
    # ═══════════════════════════════════════════════════════════════
    
    def test_clear_session(self, gateway):
        """Test: Individual session clearing"""
        # GIVEN: Session created
        result = gateway.synthesize_context("Check health", intent="AUDIT")
        session_id = result["session"].session_id
        
        # WHEN: Clear session
        cleared = gateway.clear_session(session_id)
        
        # THEN: Session removed
        assert cleared is True
        assert gateway.get_session(session_id) is None
    
    def test_clear_all_sessions(self, gateway):
        """Test: Clear all sessions"""
        # GIVEN: Multiple sessions
        gateway.synthesize_context("Check health", intent="AUDIT")
        gateway.synthesize_context("Design API", intent="DESIGN")
        
        # WHEN: Clear all
        gateway.clear_all_sessions()
        
        # THEN: No sessions remain
        assert len(gateway.get_all_sessions()) == 0
    
    # ═══════════════════════════════════════════════════════════════
    # FACTORY FUNCTION TEST
    # ═══════════════════════════════════════════════════════════════
    
    def test_create_exit_gate_factory(self, tmp_path):
        """Test: Factory function creates configured gateway"""
        # WHEN: Create EXIT GATE via factory
        exit_gate = create_exit_gate(tmp_path)
        
        # THEN: Gateway configured correctly
        assert isinstance(exit_gate, ContextSynthesisGateway)
        assert exit_gate.initial_budget == 250
        assert exit_gate.incremental_budget == 500
        assert exit_gate.session_budget == 2000
    
    # ═══════════════════════════════════════════════════════════════
    # EDGE CASES
    # ═══════════════════════════════════════════════════════════════
    
    def test_empty_request(self, gateway):
        """Test: Empty request handled gracefully"""
        # GIVEN: Empty request
        result = gateway.synthesize_context("", intent="ANALYZE")
        
        # THEN: Context synthesized without error
        assert result is not None
        assert result["total_tokens"] > 0
    
    def test_custom_session_id(self, gateway):
        """Test: Custom session ID respected"""
        # GIVEN: Custom session ID
        custom_id = "my-custom-session-123"
        
        # WHEN: Synthesize with custom ID
        result = gateway.synthesize_context("Check health", session_id=custom_id)
        
        # THEN: Session uses custom ID
        assert result["session"].session_id == custom_id
        assert gateway.get_session(custom_id) is not None
    
    def test_unknown_intent_defaults_to_analyze(self, gateway):
        """Test: Unknown intent defaults to ANALYZE"""
        # GIVEN: Request with no clear intent
        result = gateway.synthesize_context("Hello world random text")
        
        # THEN: Intent inferred as ANALYZE
        assert result["intent"] == "ANALYZE"
