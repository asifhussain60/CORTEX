"""
Tests for Golden Hammer Anti-Pattern Prevention

Tests governance rules that prevent misuse of workflow templates.

Authority: GOLDEN-HAMMER-001/002/003
Date: 2026-02-17
"""

import pytest
from cortex.governance.golden_hammer_rules import (
    GoldenHammerRules,
    GoldenHammerViolation,
)
from cortex.intent_router.workflow_gate import (
    RoutingDecision,
    RoutingStrategy,
)


class TestGoldenHammerRule001:
    """Test GOLDEN-HAMMER-001: TRIVIAL operations MUST NOT use templates."""
    
    def test_trivial_routed_to_template_violates_rule(self):
        """Routing trivial task (< 0.15) to template should raise violation."""
        rules = GoldenHammerRules()
        decision = RoutingDecision(
            route=RoutingStrategy.WORKFLOW_TEMPLATE,
            complexity=0.10,
            rationale="Override for testing",
            template_id="tdd/feature-implementation"
        )
        
        with pytest.raises(GoldenHammerViolation) as exc_info:
            rules.validate_routing_decision(decision)
        
        assert exc_info.value.rule == "GOLDEN-HAMMER-001"
        assert "overhead violation" in exc_info.value.message.lower()
    
    def test_trivial_routed_to_direct_passes(self):
        """Routing trivial task to direct orchestrator should pass."""
        rules = GoldenHammerRules()
        decision = RoutingDecision(
            route=RoutingStrategy.DIRECT_ORCHESTRATOR,
            complexity=0.10,
            rationale="Correct routing",
            orchestrator="RefactoringOrchestrator"
        )
        
        # Should not raise
        rules.validate_routing_decision(decision)


class TestGoldenHammerRule002:
    """Test GOLDEN-HAMMER-002: HIGH complexity MUST use templates."""
    
    def test_complex_routed_to_direct_violates_rule(self):
        """Routing complex task (>= 0.75) to direct should raise violation."""
        rules = GoldenHammerRules()
        decision = RoutingDecision(
            route=RoutingStrategy.DIRECT_ORCHESTRATOR,
            complexity=0.85,
            rationale="Override for speed",
            orchestrator="MasterOrchestrator"
        )
        
        with pytest.raises(GoldenHammerViolation) as exc_info:
            rules.validate_routing_decision(decision)
        
        assert exc_info.value.rule == "GOLDEN-HAMMER-002"
        assert "safety violation" in exc_info.value.message.lower()
    
    def test_complex_routed_to_template_passes(self):
        """Routing complex task to workflow template should pass."""
        rules = GoldenHammerRules()
        decision = RoutingDecision(
            route=RoutingStrategy.WORKFLOW_TEMPLATE,
            complexity=0.85,
            rationale="Correct routing",
            template_id="migration/legacy-modernization"
        )
        
        # Should not raise
        rules.validate_routing_decision(decision)


class TestGoldenHammerRule003:
    """Test GOLDEN-HAMMER-003: MODERATE operations MAY override with rationale."""
    
    def test_moderate_override_without_rationale_violates(self):
        """Moderate task override without rationale should raise violation."""
        rules = GoldenHammerRules()
        # Moderate complexity (0.40) normally routes to template, override to direct
        decision = RoutingDecision(
            route=RoutingStrategy.DIRECT_ORCHESTRATOR,
            complexity=0.40,
            rationale="Override",
            orchestrator="RefactoringOrchestrator"
        )
        
        with pytest.raises(GoldenHammerViolation) as exc_info:
            rules.validate_routing_decision(decision, override_rationale=None)
        
        assert exc_info.value.rule == "GOLDEN-HAMMER-003"
        assert "requires rationale" in exc_info.value.message.lower()
    
    def test_moderate_override_with_rationale_passes(self):
        """Moderate task override with rationale should pass."""
        rules = GoldenHammerRules()
        decision = RoutingDecision(
            route=RoutingStrategy.DIRECT_ORCHESTRATOR,
            complexity=0.40,
            rationale="Override",
            orchestrator="RefactoringOrchestrator"
        )
        
        # Should not raise with rationale
        rules.validate_routing_decision(
            decision,
            override_rationale="User requested fast path due to time constraint"
        )
    
    def test_moderate_default_routing_passes_without_rationale(self):
        """Moderate task with default routing doesn't need rationale."""
        rules = GoldenHammerRules()
        # Moderate complexity (0.50) normally routes to template
        decision = RoutingDecision(
            route=RoutingStrategy.WORKFLOW_TEMPLATE,
            complexity=0.50,
            rationale="Standard routing",
            template_id="quality/refactoring"
        )
        
        # Should not raise (default route, no override)
        rules.validate_routing_decision(decision, override_rationale=None)


class TestThresholdBoundaries:
    """Test threshold boundary conditions."""
    
    def test_exactly_at_trivial_threshold(self):
        """Task at exactly 0.15 should be allowed to use direct orchestrator."""
        rules = GoldenHammerRules()
        decision = RoutingDecision(
            route=RoutingStrategy.DIRECT_ORCHESTRATOR,
            complexity=0.15,
            rationale="At boundary",
            orchestrator="RefactoringOrchestrator"
        )
        
        # Should not raise (at boundary, not below)
        rules.validate_routing_decision(decision)
    
    def test_exactly_at_complex_threshold(self):
        """Task at exactly 0.75 should require template."""
        rules = GoldenHammerRules()
        decision = RoutingDecision(
            route=RoutingStrategy.DIRECT_ORCHESTRATOR,
            complexity=0.75,
            rationale="At boundary",
            orchestrator="MasterOrchestrator"
        )
        
        # Should raise (at threshold, requires template)
        with pytest.raises(GoldenHammerViolation) as exc_info:
            rules.validate_routing_decision(decision)
        
        assert exc_info.value.rule == "GOLDEN-HAMMER-002"
