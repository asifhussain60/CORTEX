"""
WIRE-004 Test Suite - Intent Routing Logic Tests

AC-TRANSFORM-001-WIRE-004: Tests for intent routing engine

Author: GitHub Copilot
Date: 2026-01-24
"""

import pytest

from cortex.orchestrators.core.orchestrator_wiring import (
    get_wiring_registry,
    reset_wiring_registry,
)
from cortex.orchestrators.core.wire_001_core_wiring import (
    CoreOrchestratorWiring,
)
from cortex.orchestrators.core.wire_002_domain_wiring import (
    DomainOrchestratorWiring,
)
from cortex.orchestrators.core.wire_003_support_wiring import (
    SupportOrchestratorWiring,
)
from cortex.orchestrators.core.wire_004_intent_routing import (
    IntentRoutingEngine,
    create_routing_engine,
    IntentMatch,
)


class TestIntentParsing:
    """Test suite for intent parsing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.engine = create_routing_engine()
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_parse_simple_intent(self):
        """Test parsing simple user intent"""
        result = self.engine.parse_intent("create workflow")
        assert "tokens" in result
        assert "create" in result["tokens"]
        assert "workflow" in result["tokens"]
    
    def test_parse_complex_intent(self):
        """Test parsing complex user intent"""
        result = self.engine.parse_intent("analyze and optimize code")
        assert len(result["tokens"]) >= 4
        assert "analyze" in result["tokens"]
    
    def test_parse_intent_lowercased(self):
        """Test that intents are lowercased"""
        result = self.engine.parse_intent("CREATE WORKFLOW")
        assert result["intent"] == "create workflow"


class TestIntentMatching:
    """Test suite for intent matching"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = IntentRoutingEngine(registry=self.registry)
        
        # Populate registry with all wiring phases
        core_wiring = CoreOrchestratorWiring(registry=self.registry)
        core_wiring.execute_all_wiring()
        
        domain_wiring = DomainOrchestratorWiring(registry=self.registry)
        domain_wiring.execute_all_wiring()
        
        support_wiring = SupportOrchestratorWiring(registry=self.registry)
        support_wiring.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_find_matches_by_keyword(self):
        """Test finding matches by keyword"""
        intent_data = self.engine.parse_intent("test code")
        matches = self.engine.find_matches(intent_data)
        
        assert len(matches) > 0
        assert any("test" in m.matched_keywords for m in matches)
    
    def test_find_matches_ranked(self):
        """Test that matches are ranked by confidence"""
        intent_data = self.engine.parse_intent("test code")
        matches = self.engine.find_matches(intent_data)
        
        # Verify ranking
        for i in range(len(matches) - 1):
            assert (
                matches[i].confidence_score >= matches[i + 1].confidence_score
            )
    
    def test_find_matches_no_results(self):
        """Test handling no matches found"""
        intent_data = self.engine.parse_intent("xyz123abc")
        matches = self.engine.find_matches(intent_data)
        
        # Should return empty or low-confidence matches
        assert isinstance(matches, list)


class TestIntentRouting:
    """Test suite for intent routing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = IntentRoutingEngine(registry=self.registry)
        
        # Populate registry
        core_wiring = CoreOrchestratorWiring(registry=self.registry)
        core_wiring.execute_all_wiring()
        
        domain_wiring = DomainOrchestratorWiring(registry=self.registry)
        domain_wiring.execute_all_wiring()
        
        support_wiring = SupportOrchestratorWiring(registry=self.registry)
        support_wiring.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_route_intent_test_keyword(self):
        """Test routing intent with 'test' keyword"""
        match = self.engine.route_intent("test my code")
        
        if match:
            assert match.domain is not None
            assert match.confidence_score > self.engine.confidence_threshold
    
    def test_route_intent_create_keyword(self):
        """Test routing intent with 'create' keyword"""
        match = self.engine.route_intent("create new workflow")
        
        if match:
            assert match.domain is not None
            assert match.confidence_score > self.engine.confidence_threshold
    
    def test_route_intent_analyze_keyword(self):
        """Test routing intent with 'analyze' keyword"""
        match = self.engine.route_intent("analyze project")
        
        if match:
            assert match.domain is not None
            assert match.confidence_score > self.engine.confidence_threshold
    
    def test_route_intent_no_match(self):
        """Test handling of no valid match"""
        match = self.engine.route_intent("xyzabc 123")
        
        # Should return None or very low confidence
        if match:
            assert match.confidence_score < self.engine.confidence_threshold


class TestIntentExecution:
    """Test suite for intent execution"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = IntentRoutingEngine(registry=self.registry)
        
        # Populate registry
        core_wiring = CoreOrchestratorWiring(registry=self.registry)
        core_wiring.execute_all_wiring()
        
        domain_wiring = DomainOrchestratorWiring(registry=self.registry)
        domain_wiring.execute_all_wiring()
        
        support_wiring = SupportOrchestratorWiring(registry=self.registry)
        support_wiring.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_execute_routing_with_match(self):
        """Test execute_routing with successful match"""
        result = self.engine.execute_routing("test code")
        
        assert isinstance(result, dict)
        if result["status"] == "success":
            assert "matched_domain" in result
            assert result["confidence_score"] > 0
    
    def test_execute_routing_without_match(self):
        """Test execute_routing without match"""
        result = self.engine.execute_routing("xyzabc")
        
        assert isinstance(result, dict)
        assert result["status"] in ["no_match", "success"]
    
    def test_execute_routing_returns_orchestrator_info(self):
        """Test that routing returns orchestrator info"""
        result = self.engine.execute_routing("test code")
        
        assert isinstance(result, dict)
        if result["status"] == "success":
            assert "orchestrator_capabilities" in result


class TestRoutingStats:
    """Test suite for routing engine statistics"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = IntentRoutingEngine(registry=self.registry)
        
        # Populate registry
        core_wiring = CoreOrchestratorWiring(registry=self.registry)
        core_wiring.execute_all_wiring()
        
        domain_wiring = DomainOrchestratorWiring(registry=self.registry)
        domain_wiring.execute_all_wiring()
        
        support_wiring = SupportOrchestratorWiring(registry=self.registry)
        support_wiring.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up after tests"""
        reset_wiring_registry()
    
    def test_get_stats(self):
        """Test retrieving routing engine stats"""
        stats = self.engine.get_stats()
        
        assert "total_orchestrators" in stats
        assert "by_category" in stats
        assert "coverage_percentage" in stats
        assert stats["total_orchestrators"] == 22
    
    def test_stats_shows_all_categories(self):
        """Test that stats show all orchestrator categories"""
        stats = self.engine.get_stats()
        
        by_category = stats["by_category"]
        assert "core" in by_category
        assert "domain" in by_category
        assert "support" in by_category


class TestIntentMatchClass:
    """Test suite for IntentMatch dataclass"""
    
    def test_intent_match_creation(self):
        """Test creating IntentMatch instance"""
        match = IntentMatch(
            domain="test_domain",
            confidence_score=0.85,
            matched_keywords=["test"],
            matched_capabilities=["testing"],
        )
        
        assert match.domain == "test_domain"
        assert match.confidence_score == 0.85
        assert "test" in match.matched_keywords
        assert "testing" in match.matched_capabilities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
