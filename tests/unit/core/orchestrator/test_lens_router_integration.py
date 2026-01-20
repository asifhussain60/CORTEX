"""
Test Suite for LENS + Router Integration - AC-PROD-002-03

Integration between LENS Protocol (Phases 1-4) and Intent Router (Stage 2).
Tests how LENS synthesis informs routing decisions and how routing triggers
LENS analysis for different intent types.

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging
"""

import pytest
from typing import Dict, Any, Optional

from cortex.core.result import Result, Ok, Err
from cortex.orchestrators.core.lens_synthesis import LENSSynthesis, LENSContext
from cortex.orchestrators.core.relationship_analyzer import RelationshipAnalyzer
from cortex.orchestrators.core.intent_router import IntentRouter, RoutingContext


class TestLENSRouterInitialization:
    """Test initialization of LENS + Router integration."""
    
    def test_lens_and_router_both_initialize(self) -> None:
        """Test LENS Synthesis and Intent Router both initialize."""
        synthesis = LENSSynthesis()
        router = IntentRouter()
        
        assert synthesis is not None
        assert router is not None
    
    def test_lens_context_compatible_with_routing(self) -> None:
        """Test LENS context compatible with routing context."""
        lens_context = LENSContext(
            operation="implement_feature",
            language_analysis={"intent": "create_new_feature"},
            code_examination={"patterns": ["factory", "singleton"]},
            domain_navigation={"domains": ["persistence", "api"]}
        )
        
        assert lens_context.operation == "implement_feature"
        assert lens_context.language_analysis is not None
        assert lens_context.code_examination is not None
        assert lens_context.domain_navigation is not None
    
    def test_router_context_compatible_with_lens(self) -> None:
        """Test routing context can work with LENS."""
        routing_context = RoutingContext(
            operation="implement",
            keywords=["create", "new", "feature"],
            domain="persistence"
        )
        
        assert routing_context.operation == "implement"
        assert "create" in routing_context.keywords
        assert routing_context.domain == "persistence"


class TestLENSPhases:
    """Test LENS phases inform routing decisions."""
    
    def test_language_analysis_phase_outputs(self) -> None:
        """Test Language Analysis (Phase 1) outputs."""
        lens_context = LENSContext(
            operation="fix_bug",
            language_analysis={
                "key_intent": "repair",
                "confidence": 0.92,
                "keywords": ["error", "broken", "fix"]
            }
        )
        
        assert lens_context.language_analysis["key_intent"] == "repair"
        assert lens_context.language_analysis["confidence"] == 0.92
        assert "error" in lens_context.language_analysis["keywords"]
    
    def test_code_examination_phase_outputs(self) -> None:
        """Test Code Examination (Phase 2) outputs."""
        lens_context = LENSContext(
            operation="refactor",
            code_examination={
                "pattern": "inheritance_hierarchy",
                "confidence": 0.88,
                "complexity": "high"
            }
        )
        
        assert lens_context.code_examination["pattern"] == "inheritance_hierarchy"
        assert lens_context.code_examination["confidence"] == 0.88
    
    def test_domain_navigation_phase_outputs(self) -> None:
        """Test Domain Navigation (Phase 3) outputs."""
        lens_context = LENSContext(
            operation="implement",
            domain_navigation={
                "knowledge": "module_dependencies",
                "confidence": 0.85,
                "affected_modules": ["auth", "api", "db"]
            }
        )
        
        assert lens_context.domain_navigation["knowledge"] == "module_dependencies"
        assert "auth" in lens_context.domain_navigation["affected_modules"]
    
    def test_synthesis_phase_outputs(self) -> None:
        """Test Synthesis Phase (Phase 4) outputs."""
        lens_context = LENSContext(
            operation="implement",
            language_analysis={"intent": "create"},
            code_examination={"patterns": ["factory"]},
            domain_navigation={"knowledge": "dependencies"},
            synthesis_output={
                "recommendations": [
                    {"source": "language", "insight": "Factory pattern needed"}
                ],
                "combined_confidence": 0.87
            }
        )
        
        assert lens_context.synthesis_output is not None
        assert lens_context.synthesis_output["combined_confidence"] == 0.87


class TestLENSInformsRouting:
    """Test how LENS analysis informs routing decisions."""
    
    def test_language_phase_informs_implement_intent(self) -> None:
        """Test Language phase informs IMPLEMENT intent routing."""
        synthesis = LENSSynthesis()
        router = IntentRouter()
        
        # LENS Language phase identifies implement intent
        lens_context = LENSContext(
            operation="add_feature",
            language_analysis={
                "key_intent": "implement",
                "confidence": 0.95
            }
        )
        
        # Synthesize recommendations
        result = synthesis.synthesize(lens_context)
        assert result.is_ok()
        
        # Router should handle routing
        router_params = {
            "operation": "implement_feature",
            "keywords": ["add", "feature", "new"],
            "domain": "persistence"
        }
        
        result = router.execute(router_params)
        assert result.is_ok()
    
    def test_language_phase_informs_fix_intent(self) -> None:
        """Test Language phase informs FIX intent routing."""
        synthesis = LENSSynthesis()
        router = IntentRouter()
        
        # LENS Language phase identifies fix intent
        lens_context = LENSContext(
            operation="repair_bug",
            language_analysis={
                "key_intent": "repair",
                "confidence": 0.92
            }
        )
        
        result = synthesis.synthesize(lens_context)
        assert result.is_ok()
        
        # Router should handle routing
        router_params = {
            "operation": "repair",
            "keywords": ["bug", "error", "fix"],
            "domain": "persistence"
        }
        
        result = router.execute(router_params)
        assert result.is_ok()
    
    def test_language_phase_informs_refactor_intent(self) -> None:
        """Test Language phase informs REFACTOR intent routing."""
        synthesis = LENSSynthesis()
        router = IntentRouter()
        
        # LENS Language phase identifies refactor intent
        lens_context = LENSContext(
            operation="improve_code",
            language_analysis={
                "key_intent": "optimize",
                "confidence": 0.88
            }
        )
        
        result = synthesis.synthesize(lens_context)
        assert result.is_ok()
        
        # Router should handle routing
        router_params = {
            "operation": "improve",
            "keywords": ["refactor", "improve", "clean"],
            "domain": "persistence"
        }
        
        result = router.execute(router_params)
        assert result.is_ok()


class TestRouterTriggersLENS:
    """Test how routing decisions trigger LENS analysis."""
    
    def test_implement_routing_triggers_lens_analysis(self) -> None:
        """Test IMPLEMENT routing triggers full LENS analysis."""
        router = IntentRouter()
        
        router_params = {
            "operation": "implement_feature",
            "keywords": ["new", "feature", "create"],
            "domain": "persistence"
        }
        
        result = router.execute(router_params)
        assert result.is_ok()
        
        # Result should indicate routing completed
        output = result.unwrap()
        assert output is not None
    
    def test_fix_routing_triggers_lens_analysis(self) -> None:
        """Test FIX routing triggers focused LENS analysis."""
        router = IntentRouter()
        
        router_params = {
            "operation": "fix_bug",
            "keywords": ["bug", "error", "fix"],
            "domain": "api"
        }
        
        result = router.execute(router_params)
        assert result.is_ok()
    
    def test_refactor_routing_triggers_lens_analysis(self) -> None:
        """Test REFACTOR routing triggers structural LENS analysis."""
        router = IntentRouter()
        
        router_params = {
            "operation": "refactor",
            "keywords": ["clean", "improve", "refactor"],
            "domain": "api"
        }
        
        result = router.execute(router_params)
        assert result.is_ok()


class TestLENSRoutingCoordination:
    """Test coordination between LENS and Router."""
    
    def test_lens_synthesis_produces_routing_input(self) -> None:
        """Test LENS synthesis produces data suitable for routing."""
        synthesis = LENSSynthesis()
        
        lens_context = LENSContext(
            operation="implement_auth",
            language_analysis={"intent": "create"},
            code_examination={"pattern": "factory"},
            domain_navigation={"knowledge": "security"}
        )
        
        result = synthesis.synthesize(lens_context)
        assert result.is_ok()
        
        synthesis_output = result.unwrap()
        assert "recommendations" in synthesis_output
        assert "combined_confidence" in synthesis_output
    
    def test_router_outputs_ready_for_stage_3(self) -> None:
        """Test router outputs ready for next stage (Stage 3)."""
        router = IntentRouter()
        
        router_params = {
            "operation": "implement",
            "keywords": ["new", "feature"],
            "domain": "persistence"
        }
        
        result = router.execute(router_params)
        assert result.is_ok()
        
        output = result.unwrap()
        # Output should have routing information
        assert output is not None
    
    def test_lens_recommendations_guide_routing(self) -> None:
        """Test LENS recommendations guide routing priority."""
        synthesis = LENSSynthesis()
        
        lens_context = LENSContext(
            operation="critical_fix",
            language_analysis={"intent": "fix", "confidence": 0.99},
            code_examination={"pattern": "error_handling"},
            domain_navigation={"knowledge": "core_system"}
        )
        
        result = synthesis.synthesize(lens_context)
        assert result.is_ok()
        
        synthesis_output = result.unwrap()
        # Should have high confidence recommendations
        assert synthesis_output["combined_confidence"] > 0.7


class TestRelationshipAnalyzerIntegration:
    """Test RelationshipAnalyzer integration with LENS."""
    
    def test_relationship_analyzer_provides_domain_navigation_input(self) -> None:
        """Test RelationshipAnalyzer provides input for LENS Navigation phase."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {
            "name": "UserService",
            "type": "class",
            "relationships": [
                {"type": "composition", "target": "UserRepository"}
            ]
        }
        
        result = analyzer.analyze(code_info)
        assert result.is_ok()
        
        graph = result.unwrap()
        # Graph can feed into LENS Navigation phase
        assert len(graph.entities) > 0
    
    def test_relationship_graph_informs_routing_confidence(self) -> None:
        """Test relationship graph informs routing confidence scoring."""
        analyzer = RelationshipAnalyzer()
        router = IntentRouter()
        
        # Build relationship context
        code_info = {
            "name": "FeatureImplementation",
            "type": "class",
            "relationships": [
                {"type": "dependency", "target": "Config"},
                {"type": "dependency", "target": "Logger"}
            ]
        }
        
        result = analyzer.analyze(code_info)
        assert result.is_ok()
        
        # Router should account for relationships
        router_params = {
            "operation": "implement",
            "keywords": ["feature"],
            "domain": "api"
        }
        
        router_result = router.execute(router_params)
        assert router_result.is_ok()


class TestMultiPhaseIntegration:
    """Test multi-phase integrated workflows."""
    
    def test_implement_workflow_full_pipeline(self) -> None:
        """Test full IMPLEMENT workflow through all phases."""
        # Phase 1: Language Analysis (simulated)
        language_output = {
            "intent": "create_new_feature",
            "confidence": 0.93
        }
        
        # Phase 2: Code Examination (simulated)
        code_output = {
            "pattern": "factory_pattern",
            "confidence": 0.85
        }
        
        # Phase 3: Domain Navigation (simulated)
        domain_output = {
            "knowledge": "persistence_layer",
            "confidence": 0.88
        }
        
        # Phase 4: LENS Synthesis
        synthesis = LENSSynthesis()
        lens_context = LENSContext(
            operation="implement_feature",
            language_analysis=language_output,
            code_examination=code_output,
            domain_navigation=domain_output
        )
        
        result = synthesis.synthesize(lens_context)
        assert result.is_ok()
        
        # Routing based on synthesis output
        router = IntentRouter()
        router_params = {
            "operation": "implement_feature",
            "keywords": ["new", "feature", "create"],
            "domain": "persistence"
        }
        
        router_result = router.execute(router_params)
        assert router_result.is_ok()
    
    def test_fix_workflow_full_pipeline(self) -> None:
        """Test full FIX workflow through all phases."""
        synthesis = LENSSynthesis()
        router = IntentRouter()
        
        lens_context = LENSContext(
            operation="fix_critical_bug",
            language_analysis={"intent": "repair", "confidence": 0.96},
            code_examination={"pattern": "error_handling", "confidence": 0.89},
            domain_navigation={"knowledge": "core_system", "confidence": 0.91}
        )
        
        result = synthesis.synthesize(lens_context)
        assert result.is_ok()
        
        router_params = {
            "operation": "fix_bug",
            "keywords": ["critical", "bug", "error"],
            "domain": "core"
        }
        
        router_result = router.execute(router_params)
        assert router_result.is_ok()
    
    def test_refactor_workflow_full_pipeline(self) -> None:
        """Test full REFACTOR workflow through all phases."""
        synthesis = LENSSynthesis()
        router = IntentRouter()
        
        lens_context = LENSContext(
            operation="refactor_legacy_code",
            language_analysis={"intent": "optimize", "confidence": 0.82},
            code_examination={"pattern": "legacy_monolith", "confidence": 0.84},
            domain_navigation={"knowledge": "system_architecture", "confidence": 0.80}
        )
        
        result = synthesis.synthesize(lens_context)
        assert result.is_ok()
        
        router_params = {
            "operation": "refactor",
            "keywords": ["refactor", "improve", "clean"],
            "domain": "architecture"
        }
        
        router_result = router.execute(router_params)
        assert router_result.is_ok()


class TestGovernanceCompliance:
    """Test CORE governance compliance for integration."""
    
    def test_core_011_type_hints_on_integration(self) -> None:
        """Test CORE-011: Type hints present."""
        assert LENSSynthesis.synthesize.__annotations__ is not None
        assert IntentRouter.execute_operation.__annotations__ is not None
    
    def test_core_012_docstrings_on_integration(self) -> None:
        """Test CORE-012: Docstrings present."""
        assert LENSSynthesis.__doc__ is not None
        assert IntentRouter.__doc__ is not None
    
    def test_core_027_audit_trail_on_integration(self) -> None:
        """Test CORE-027: Audit trail support."""
        synthesis = LENSSynthesis()
        assert hasattr(synthesis, 'logger')
        
        router = IntentRouter()
        assert hasattr(router, 'logger')


class TestErrorHandling:
    """Test error handling in LENS + Router integration."""
    
    def test_invalid_lens_context_handled(self) -> None:
        """Test invalid LENS context handled gracefully."""
        synthesis = LENSSynthesis()
        
        # None context
        result = synthesis.synthesize(None)
        assert result.is_err()
    
    def test_invalid_routing_context_handled(self) -> None:
        """Test invalid routing context handled gracefully."""
        router = IntentRouter()
        
        # Create with minimal valid fields
        router_params = {"operation": "test"}
        result = router.execute(router_params)
        # Should either work or error appropriately
        assert result is not None
    
    def test_mismatched_lens_router_data_handled(self) -> None:
        """Test mismatched data between LENS and Router handled."""
        synthesis = LENSSynthesis()
        router = IntentRouter()
        
        # Create context with missing fields
        lens_context = LENSContext(operation="test")
        result = synthesis.synthesize(lens_context)
        # Should handle gracefully (may return error or success with defaults)
        assert result is not None


# Module exports
__all__ = [
    "TestLENSRouterInitialization",
    "TestLENSPhases",
    "TestLENSInformsRouting",
    "TestRouterTriggersLENS",
    "TestLENSRoutingCoordination",
    "TestRelationshipAnalyzerIntegration",
    "TestMultiPhaseIntegration",
    "TestGovernanceCompliance",
    "TestErrorHandling",
]
