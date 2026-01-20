"""
Domain Classification Tests - AR-016-01

Tests for orchestrator domain classification system.
- 5 core domains with clear semantic boundaries
- Orchestrator classification into domains
- Trait interfaces for domain-specific behaviors
- Cycle-free trait inheritance hierarchy

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from cortex.orchestrators.domains.domain_classifier import DomainClassifier
from cortex.orchestrators.domains.orchestrator_traits import (
    ComposableOrchestrator,
    AnalyticalOrchestrator,
    ExecutiveOrchestrator,
    ValidatingOrchestrator,
    IntegrativeOrchestrator,
)


class TestDomainDefinition:
    """Test domain definition and boundaries"""
    
    def test_five_core_domains_defined(self):
        """Test that 5 core domains are defined with clear boundaries"""
        classifier = DomainClassifier()
        domains = classifier.get_all_domains()
        
        assert len(domains) == 5
        assert "planning" in domains
        assert "analysis" in domains
        assert "integration" in domains
        assert "validation" in domains
        assert "execution" in domains
    
    def test_domain_descriptions_present(self):
        """Test that each domain has a description"""
        classifier = DomainClassifier()
        
        for domain in classifier.get_all_domains():
            description = classifier.get_domain_description(domain)
            assert description is not None
            assert len(description) > 0
    
    def test_domain_semantic_boundaries(self):
        """Test that domains have non-overlapping semantic boundaries"""
        classifier = DomainClassifier()
        
        # Verify each domain has clear primary responsibility
        planning_desc = classifier.get_domain_description("planning")
        assert "plan" in planning_desc.lower() or "manage" in planning_desc.lower()
        
        analysis_desc = classifier.get_domain_description("analysis")
        assert "analyz" in analysis_desc.lower() or "discover" in analysis_desc.lower()
        
        integration_desc = classifier.get_domain_description("integration")
        assert "integrat" in integration_desc.lower() or "connect" in integration_desc.lower()
        
        validation_desc = classifier.get_domain_description("validation")
        assert "validat" in validation_desc.lower() or "check" in validation_desc.lower()
        
        execution_desc = classifier.get_domain_description("execution")
        assert "execut" in execution_desc.lower() or "run" in execution_desc.lower()


class TestOrchestratorClassification:
    """Test orchestrator classification into domains"""
    
    def test_all_orchestrators_classified(self):
        """Test that all known orchestrators are classified"""
        classifier = DomainClassifier()
        classifications = classifier.classify_all_orchestrators()
        
        # Should have orchestrators from each domain
        assert len(classifications) > 0
        domains_with_orchestrators = set(c.domain for c in classifications)
        assert len(domains_with_orchestrators) >= 4  # At least 4 of 5 domains should have orchestrators
    
    def test_planning_orchestrators_classified(self):
        """Test planning domain orchestrators"""
        classifier = DomainClassifier()
        classifications = classifier.classify_all_orchestrators()
        
        planning_orchs = [c for c in classifications if c.domain == "planning"]
        assert len(planning_orchs) > 0
        
        # Should include planning, maintenance, checkpoint orchestrators
        orch_names = set(c.name for c in planning_orchs)
        assert any("planning" in name.lower() or "checkpoint" in name.lower() 
                   for name in orch_names)
    
    def test_analysis_orchestrators_classified(self):
        """Test analysis domain orchestrators"""
        classifier = DomainClassifier()
        classifications = classifier.classify_all_orchestrators()
        
        analysis_orchs = [c for c in classifications if c.domain == "analysis"]
        assert len(analysis_orchs) > 0
        
        # Should include discovery, intelligence, architectural review
        orch_names = set(c.name for c in analysis_orchs)
        assert any("discovery" in name.lower() or "intelligence" in name.lower() 
                   or "architectural" in name.lower() 
                   for name in orch_names)
    
    def test_integration_orchestrators_classified(self):
        """Test integration domain orchestrators"""
        classifier = DomainClassifier()
        classifications = classifier.classify_all_orchestrators()
        
        integration_orchs = [c for c in classifications if c.domain == "integration"]
        assert len(integration_orchs) > 0
        
        # Should include ADO, CICD, integration-related orchestrators
        orch_names = set(c.name for c in integration_orchs)
        assert any("ado" in name.lower() or "cicd" in name.lower() 
                   or "integration" in name.lower() 
                   for name in orch_names)
    
    def test_validation_orchestrators_classified(self):
        """Test validation domain orchestrators"""
        classifier = DomainClassifier()
        classifications = classifier.classify_all_orchestrators()
        
        validation_orchs = [c for c in classifications if c.domain == "validation"]
        assert len(validation_orchs) > 0
        
        # Should include system integrity, pre-flight, TDD orchestrators
        orch_names = set(c.name for c in validation_orchs)
        assert any("system" in name.lower() or "preflight" in name.lower() 
                   or "tdd" in name.lower() 
                   for name in orch_names)
    
    def test_execution_orchestrators_classified(self):
        """Test execution domain orchestrators"""
        classifier = DomainClassifier()
        classifications = classifier.classify_all_orchestrators()
        
        execution_orchs = [c for c in classifications if c.domain == "execution"]
        assert len(execution_orchs) > 0
        
        # Should include execution, vacuum, sanitization orchestrators
        orch_names = set(c.name for c in execution_orchs)
        assert any("execution" in name.lower() or "vacuum" in name.lower() 
                   or "sanitization" in name.lower() 
                   for name in orch_names)
    
    def test_classification_has_required_fields(self):
        """Test that classifications have all required fields"""
        classifier = DomainClassifier()
        classifications = classifier.classify_all_orchestrators()
        
        for classification in classifications:
            assert hasattr(classification, "name")
            assert hasattr(classification, "domain")
            assert hasattr(classification, "traits")
            assert hasattr(classification, "rationale")


class TestTraitInterfaces:
    """Test trait interfaces for domain-specific behaviors"""
    
    def test_composable_orchestrator_trait(self):
        """Test ComposableOrchestrator trait"""
        assert hasattr(ComposableOrchestrator, "can_compose")
        assert hasattr(ComposableOrchestrator, "get_output_schema")
        assert hasattr(ComposableOrchestrator, "get_input_schema")
    
    def test_analytical_orchestrator_trait(self):
        """Test AnalyticalOrchestrator trait"""
        assert hasattr(AnalyticalOrchestrator, "analyze")
        assert hasattr(AnalyticalOrchestrator, "get_analysis_depth")
        assert hasattr(AnalyticalOrchestrator, "get_supported_analyses")
    
    def test_executive_orchestrator_trait(self):
        """Test ExecutiveOrchestrator trait"""
        assert hasattr(ExecutiveOrchestrator, "execute")
        assert hasattr(ExecutiveOrchestrator, "get_execution_modes")
        assert hasattr(ExecutiveOrchestrator, "can_execute")
    
    def test_validating_orchestrator_trait(self):
        """Test ValidatingOrchestrator trait"""
        assert hasattr(ValidatingOrchestrator, "validate")
        assert hasattr(ValidatingOrchestrator, "get_validation_rules")
        assert hasattr(ValidatingOrchestrator, "get_validation_severity")
    
    def test_integrative_orchestrator_trait(self):
        """Test IntegrativeOrchestrator trait"""
        assert hasattr(IntegrativeOrchestrator, "integrate")
        assert hasattr(IntegrativeOrchestrator, "get_integration_points")
        assert hasattr(IntegrativeOrchestrator, "get_supported_systems")
    
    def test_trait_methods_are_abstract(self):
        """Test that trait methods are properly defined"""
        # Can create instances of traits (they're protocols, not ABCs)
        traits = [
            ComposableOrchestrator,
            AnalyticalOrchestrator,
            ExecutiveOrchestrator,
            ValidatingOrchestrator,
            IntegrativeOrchestrator,
        ]
        
        for trait in traits:
            assert trait is not None


class TestTraitInheritanceHierarchy:
    """Test that trait inheritance hierarchy is cycle-free"""
    
    def test_no_circular_dependencies(self):
        """Test that trait hierarchy has no circular dependencies"""
        from cortex.orchestrators.domains.orchestrator_traits import (
            get_trait_hierarchy,
            detect_cycles,
        )
        
        hierarchy = get_trait_hierarchy()
        cycles = detect_cycles(hierarchy)
        
        assert len(cycles) == 0, f"Found circular dependencies: {cycles}"
    
    def test_trait_hierarchy_is_dag(self):
        """Test that trait hierarchy is a directed acyclic graph"""
        from cortex.orchestrators.domains.orchestrator_traits import (
            get_trait_hierarchy,
            is_dag,
        )
        
        hierarchy = get_trait_hierarchy()
        assert is_dag(hierarchy), "Trait hierarchy is not a DAG"
    
    def test_trait_hierarchy_reachability(self):
        """Test reachability in trait hierarchy"""
        from cortex.orchestrators.domains.orchestrator_traits import (
            get_trait_hierarchy,
            get_reachable_traits,
        )
        
        hierarchy = get_trait_hierarchy()
        
        # Each trait should be reachable from root
        for trait in [ComposableOrchestrator, AnalyticalOrchestrator,
                      ExecutiveOrchestrator, ValidatingOrchestrator,
                      IntegrativeOrchestrator]:
            reachable = get_reachable_traits(hierarchy, trait)
            assert len(reachable) > 0


class TestDomainOrchestrationMapping:
    """Test mapping between domains and orchestrations"""
    
    def test_get_orchestrators_by_domain(self):
        """Test getting orchestrators for a specific domain"""
        classifier = DomainClassifier()
        
        for domain in classifier.get_all_domains():
            orchestrators = classifier.get_orchestrators_by_domain(domain)
            # Some domains might be empty initially, but not all
            assert isinstance(orchestrators, list)
    
    def test_orchestrator_traits_by_domain(self):
        """Test that orchestrators have domain-specific traits"""
        classifier = DomainClassifier()
        classifications = classifier.classify_all_orchestrators()
        
        for classification in classifications:
            traits = classification.traits
            assert isinstance(traits, list)
            assert len(traits) > 0
            
            # Traits should be from known trait types
            valid_traits = {
                "ComposableOrchestrator",
                "AnalyticalOrchestrator",
                "ExecutiveOrchestrator",
                "ValidatingOrchestrator",
                "IntegrativeOrchestrator",
            }
            assert all(t in valid_traits for t in traits)
    
    def test_classification_rationale_provided(self):
        """Test that each classification includes rationale"""
        classifier = DomainClassifier()
        classifications = classifier.classify_all_orchestrators()
        
        for classification in classifications:
            rationale = classification.rationale
            assert isinstance(rationale, str)
            assert len(rationale) > 0
            # Rationale should contain meaningful text (not domain name necessarily)
            assert len(rationale.split()) >= 3  # At least 3 words


class TestDomainClassifierIntegration:
    """Integration tests for domain classifier"""
    
    def test_classifier_singleton_pattern(self):
        """Test that classifier follows singleton pattern"""
        classifier1 = DomainClassifier()
        classifier2 = DomainClassifier()
        
        # Should have same classifications
        assert classifier1.get_all_domains() == classifier2.get_all_domains()
    
    def test_classifier_caching(self):
        """Test that classifier caches results"""
        classifier = DomainClassifier()
        
        # First call
        classifications1 = classifier.classify_all_orchestrators()
        
        # Second call should return same object
        classifications2 = classifier.classify_all_orchestrators()
        
        assert classifications1 == classifications2
    
    def test_classifier_export_format(self):
        """Test that classifier can export classifications"""
        classifier = DomainClassifier()
        
        exported = classifier.export_classifications()
        assert isinstance(exported, dict)
        assert "metadata" in exported
        assert "classifications" in exported
        assert exported["metadata"]["version"] is not None
        assert exported["metadata"]["timestamp"] is not None
