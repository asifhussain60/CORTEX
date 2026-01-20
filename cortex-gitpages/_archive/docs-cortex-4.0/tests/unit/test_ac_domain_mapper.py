"""
Tests for AC-to-Domain Mapping functionality.

Comprehensive test suite for:
- ACDomainRegistry singleton pattern
- AC-to-domain bidirectional lookups
- Orchestrator AC assignment
- Category filtering
- Statistics and analytics
"""

import pytest
from pathlib import Path
from src.core.path_resolver import resolve_path
from src.core.ac_domain_mapper import (
    ACDomainRegistry,
    ACMetadata,
    DomainMetadata,
    ACDomainLoader,
    ACDomainPopulator,
)


# =============================================================================
# ACMetadata Tests
# =============================================================================

@pytest.mark.ac("AR-001-01")
class TestACMetadata:
    """Test AC metadata dataclass."""
    
    def test_ac_metadata_creation(self):
        """Test creating AC metadata."""
        ac = ACMetadata(
            ac_id="AC-AR-001-01",
            title="Tier 0 immutable rules",
            description="SKULL rules defined and locked",
            domain="planning",
            categories=["phase_management"],
            severity="CRITICAL",
        )
        
        assert ac.ac_id == "AC-AR-001-01"
        assert ac.domain == "planning"
        assert len(ac.categories) == 1
        assert ac.severity == "CRITICAL"
    
    def test_ac_metadata_to_dict(self):
        """Test serialization to dictionary."""
        ac = ACMetadata(
            ac_id="AC-AR-006-01",
            title="pytest plugin architecture",
            description="Test execution framework",
            domain="tdd",
            categories=["test_execution", "code_coverage"],
            severity="HIGH",
        )
        
        d = ac.to_dict()
        assert d['ac_id'] == "AC-AR-006-01"
        assert d['domain'] == "tdd"
        assert len(d['categories']) == 2


# =============================================================================
# DomainMetadata Tests
# =============================================================================

class TestDomainMetadata:
    """Test domain metadata dataclass."""
    
    def test_domain_metadata_creation(self):
        """Test creating domain metadata."""
        domain = DomainMetadata(
            domain_id="tdd",
            domain_name="Test-Driven Development",
            orchestrator="TDDOrchestrator",
            tier_access=[0, 1, 2],
            ac_count=28,
            primary_rules=["TDD-RULE-001", "TDD-RULE-002"],
        )
        
        assert domain.domain_id == "tdd"
        assert domain.orchestrator == "TDDOrchestrator"
        assert domain.ac_count == 28
        assert len(domain.primary_rules) == 2
    
    def test_domain_metadata_to_dict(self):
        """Test serialization to dictionary."""
        domain = DomainMetadata(
            domain_id="planning",
            domain_name="Strategic Planning",
            orchestrator="PlanningOrchestrator",
            tier_access=[0, 1, 2, 3],
            ac_count=25,
        )
        
        d = domain.to_dict()
        assert d['domain_id'] == "planning"
        assert d['orchestrator'] == "PlanningOrchestrator"
        assert d['ac_count'] == 25


# =============================================================================
# ACDomainRegistry Tests
# =============================================================================

class TestACDomainRegistry:
    """Test the central AC-to-domain registry."""
    
    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """Reset registry singleton before each test."""
        ACDomainRegistry._instance = None
        yield
        ACDomainRegistry._instance = None
    
    def test_registry_singleton(self):
        """Test that registry is a singleton."""
        registry1 = ACDomainRegistry()
        registry2 = ACDomainRegistry()
        assert registry1 is registry2
    
    def test_register_ac(self):
        """Test registering an AC."""
        registry = ACDomainRegistry()
        
        ac = ACMetadata(
            ac_id="AC-AR-001-01",
            title="Test AC",
            description="Test description",
            domain="planning",
            categories=["phase_management"],
        )
        
        registry.register_ac(ac)
        assert registry.get_domain_for_ac("AC-AR-001-01") == "planning"
    
    def test_register_domain(self):
        """Test registering domain metadata."""
        registry = ACDomainRegistry()
        
        domain = DomainMetadata(
            domain_id="tdd",
            domain_name="Test-Driven Development",
            orchestrator="TDDOrchestrator",
            tier_access=[0, 1, 2],
            ac_count=28,
        )
        
        registry.register_domain(domain)
        assert registry.get_domain_metadata("tdd") is not None
        assert registry.get_domain_metadata("tdd").orchestrator == "TDDOrchestrator"
    
    def test_get_domain_for_ac(self):
        """Test getting domain for a specific AC."""
        registry = ACDomainRegistry()
        
        ac = ACMetadata(
            ac_id="AC-AR-006-01",
            title="Test AC",
            description="Description",
            domain="tdd",
        )
        registry.register_ac(ac)
        
        assert registry.get_domain_for_ac("AC-AR-006-01") == "tdd"
        assert registry.get_domain_for_ac("AC-NONEXISTENT-01") is None
    
    def test_get_acs_for_domain(self):
        """Test getting all ACs for a domain."""
        registry = ACDomainRegistry()
        
        ac1 = ACMetadata(ac_id="AC-AR-001-01", title="AC1", description="Desc1", domain="planning")
        ac2 = ACMetadata(ac_id="AC-AR-001-02", title="AC2", description="Desc2", domain="planning")
        ac3 = ACMetadata(ac_id="AC-AR-006-01", title="AC3", description="Desc3", domain="tdd")
        
        registry.register_ac(ac1)
        registry.register_ac(ac2)
        registry.register_ac(ac3)
        
        planning_acs = registry.get_acs_for_domain("planning")
        assert len(planning_acs) == 2
        assert planning_acs[0].ac_id == "AC-AR-001-01"
        assert planning_acs[1].ac_id == "AC-AR-001-02"
    
    def test_get_orchestrator_for_ac(self):
        """Test getting orchestrator for an AC."""
        registry = ACDomainRegistry()
        
        domain = DomainMetadata(
            domain_id="tdd",
            domain_name="TDD",
            orchestrator="TDDOrchestrator",
            tier_access=[0, 1, 2],
            ac_count=1,
        )
        registry.register_domain(domain)
        
        ac = ACMetadata(ac_id="AC-AR-006-01", title="AC", description="Desc", domain="tdd")
        registry.register_ac(ac)
        
        assert registry.get_orchestrator_for_ac("AC-AR-006-01") == "TDDOrchestrator"
    
    def test_get_acs_for_orchestrator(self):
        """Test getting all ACs for an orchestrator."""
        registry = ACDomainRegistry()
        
        domain = DomainMetadata(
            domain_id="tdd",
            domain_name="TDD",
            orchestrator="TDDOrchestrator",
            tier_access=[0, 1, 2],
            ac_count=2,
        )
        registry.register_domain(domain)
        
        ac1 = ACMetadata(ac_id="AC-AR-006-01", title="AC1", description="Desc1", domain="tdd")
        ac2 = ACMetadata(ac_id="AC-AR-006-02", title="AC2", description="Desc2", domain="tdd")
        registry.register_ac(ac1)
        registry.register_ac(ac2)
        
        orch_acs = registry.get_acs_for_orchestrator("TDDOrchestrator")
        assert len(orch_acs) == 2
    
    def test_get_acs_for_category(self):
        """Test getting all ACs in a category."""
        registry = ACDomainRegistry()
        
        ac1 = ACMetadata(
            ac_id="AC-AR-006-01",
            title="AC1",
            description="Desc1",
            domain="tdd",
            categories=["test_execution", "code_coverage"],
        )
        ac2 = ACMetadata(
            ac_id="AC-AR-006-02",
            title="AC2",
            description="Desc2",
            domain="tdd",
            categories=["test_execution"],
        )
        ac3 = ACMetadata(
            ac_id="AC-AR-001-01",
            title="AC3",
            description="Desc3",
            domain="planning",
            categories=["phase_management"],
        )
        
        registry.register_ac(ac1)
        registry.register_ac(ac2)
        registry.register_ac(ac3)
        
        test_exec_acs = registry.get_acs_for_category("test_execution")
        assert len(test_exec_acs) == 2
        
        coverage_acs = registry.get_acs_for_category("code_coverage")
        assert len(coverage_acs) == 1
    
    def test_count_acs_for_domain(self):
        """Test counting ACs in a domain."""
        registry = ACDomainRegistry()
        
        for i in range(1, 4):
            ac = ACMetadata(
                ac_id=f"AC-AR-001-0{i}",
                title=f"AC{i}",
                description=f"Desc{i}",
                domain="planning",
            )
            registry.register_ac(ac)
        
        assert registry.count_acs_for_domain("planning") == 3
        assert registry.count_acs_for_domain("tdd") == 0
    
    def test_get_all_domains(self):
        """Test getting list of all domains."""
        registry = ACDomainRegistry()
        
        for domain_id in ["tdd", "planning", "ado", "interaction"]:
            domain = DomainMetadata(
                domain_id=domain_id,
                domain_name=domain_id.upper(),
                orchestrator=f"{domain_id.capitalize()}Orchestrator",
                tier_access=[0, 1],
                ac_count=10,
            )
            registry.register_domain(domain)
        
        domains = registry.get_all_domains()
        assert len(domains) == 4
        assert "tdd" in domains
        assert "planning" in domains
    
    def test_get_all_orchestrators(self):
        """Test getting list of all orchestrators."""
        registry = ACDomainRegistry()
        
        for domain_id in ["tdd", "planning"]:
            domain = DomainMetadata(
                domain_id=domain_id,
                domain_name=domain_id.upper(),
                orchestrator=f"{domain_id.capitalize()}Orchestrator",
                tier_access=[0, 1],
                ac_count=10,
            )
            registry.register_domain(domain)
        
        orchestrators = registry.get_all_orchestrators()
        assert len(orchestrators) == 2
        assert "TddOrchestrator" in orchestrators or "tdd" in str(orchestrators)
    
    def test_get_all_categories(self):
        """Test getting list of all categories."""
        registry = ACDomainRegistry()
        
        ac1 = ACMetadata(ac_id="AC1", title="T1", description="D1", domain="tdd", categories=["cat_a", "cat_b"])
        ac2 = ACMetadata(ac_id="AC2", title="T2", description="D2", domain="planning", categories=["cat_b", "cat_c"])
        
        registry.register_ac(ac1)
        registry.register_ac(ac2)
        
        categories = registry.get_all_categories()
        assert len(categories) == 3
        assert "cat_a" in categories
        assert "cat_b" in categories
        assert "cat_c" in categories
    
    def test_get_domain_summary(self):
        """Test getting domain summary."""
        registry = ACDomainRegistry()
        
        domain = DomainMetadata(
            domain_id="tdd",
            domain_name="TDD",
            orchestrator="TDDOrchestrator",
            tier_access=[0, 1, 2],
            ac_count=3,
        )
        registry.register_domain(domain)
        
        ac1 = ACMetadata(
            ac_id="AC1",
            title="T1",
            description="D1",
            domain="tdd",
            categories=["test_execution"],
        )
        ac2 = ACMetadata(
            ac_id="AC2",
            title="T2",
            description="D2",
            domain="tdd",
            categories=["code_coverage"],
        )
        
        registry.register_ac(ac1)
        registry.register_ac(ac2)
        
        summary = registry.get_domain_summary("tdd")
        assert summary['domain'] == "tdd"
        assert summary['ac_count'] == 2
        assert summary['orchestrator'] == "TDDOrchestrator"
        assert "test_execution" in summary['categories']
    
    def test_get_statistics(self):
        """Test getting comprehensive statistics."""
        registry = ACDomainRegistry()
        
        for domain_id in ["tdd", "planning"]:
            domain = DomainMetadata(
                domain_id=domain_id,
                domain_name=domain_id.upper(),
                orchestrator=f"{domain_id.capitalize()}Orchestrator",
                tier_access=[0, 1],
                ac_count=10,
            )
            registry.register_domain(domain)
        
        ac1 = ACMetadata(ac_id="AC1", title="T1", description="D1", domain="tdd", categories=["cat_a"])
        ac2 = ACMetadata(ac_id="AC2", title="T2", description="D2", domain="planning", categories=["cat_b"])
        
        registry.register_ac(ac1)
        registry.register_ac(ac2)
        
        stats = registry.get_statistics()
        assert stats['total_acs'] == 2
        assert stats['total_domains'] == 2
        assert stats['total_categories'] == 2


# =============================================================================
# ACDomainLoader Tests
# =============================================================================

class TestACDomainLoader:
    """Test loading AC-to-domain mappings from YAML."""
    
    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """Reset registry singleton before each test."""
        ACDomainRegistry._instance = None
        yield
        ACDomainRegistry._instance = None
    
    def test_loader_creation(self):
        """Test creating loader instance."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        loader = ACDomainLoader(tier1_path)
        
        assert loader.tier1_path == tier1_path
        assert loader.mappings_file.name == "ac-domain-mappings.yaml"
    
    def test_load_mappings(self):
        """Test loading mappings from actual YAML file."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        loader = ACDomainLoader(tier1_path)
        
        registry = loader.load_mappings()
        
        # Verify registry is populated
        assert registry is not None
        assert len(registry.ac_metadata) > 0
        assert len(registry.domain_metadata) == 4  # 4 domains
    
    def test_load_mappings_file_not_found(self):
        """Test handling missing mappings file."""
        tier1_path = Path("/nonexistent/path")
        loader = ACDomainLoader(tier1_path)
        
        with pytest.raises(FileNotFoundError):
            loader.load_mappings()


# =============================================================================
# ACDomainPopulator Tests
# =============================================================================

class TestACDomainPopulator:
    """Test the high-level populator interface."""
    
    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """Reset registry singleton before each test."""
        ACDomainRegistry._instance = None
        yield
        ACDomainRegistry._instance = None
    
    def test_populator_creation(self):
        """Test creating populator instance."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        assert populator.tier1_path == tier1_path
    
    def test_populate(self):
        """Test populating AC-to-domain mappings."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        registry = populator.populate()
        assert registry is not None
        assert len(registry.ac_metadata) == 87  # All ACs from cortex-master
    
    def test_get_registry(self):
        """Test getting registry after population."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        registry = populator.get_registry()
        
        assert registry is not None
        assert len(registry.ac_metadata) > 0
    
    def test_get_registry_before_populate(self):
        """Test error when getting registry before population."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        with pytest.raises(RuntimeError):
            populator.get_registry()
    
    def test_get_populated_domains(self):
        """Test getting list of populated domains."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        domains = populator.get_populated_domains()
        
        assert len(domains) == 4
        assert "tdd" in domains
        assert "planning" in domains
        assert "ado" in domains
        assert "interaction" in domains
    
    def test_get_mappings_summary(self):
        """Test getting summary of mappings."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        summary = populator.get_mappings_summary()
        
        assert summary['total_acs'] == 87
        assert summary['total_domains'] == 4
    
    def test_query_domain_for_ac(self):
        """Test querying domain for specific AC."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        domain = populator.query_domain_for_ac("AC-AR-001-01")
        
        assert domain == "planning"
    
    def test_query_orchestrator_for_ac(self):
        """Test querying orchestrator for specific AC."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        orchestrator = populator.query_orchestrator_for_ac("AC-AR-006-01")
        
        assert orchestrator == "TDDOrchestrator"
    
    def test_query_acs_for_domain(self):
        """Test querying all ACs for a domain."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        tdd_acs = populator.query_acs_for_domain("tdd")
        
        assert len(tdd_acs) == 22
    
    def test_query_acs_for_orchestrator(self):
        """Test querying all ACs for an orchestrator."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        orch_acs = populator.query_acs_for_orchestrator("ADOOrchestrator")
        
        assert len(orch_acs) == 23


# =============================================================================
# Integration Tests
# =============================================================================

class TestACDomainMappingIntegration:
    """Integration tests for AC-to-domain mapping functionality."""
    
    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """Reset registry singleton before each test."""
        ACDomainRegistry._instance = None
        yield
        ACDomainRegistry._instance = None
    
    def test_full_ac_domain_population(self):
        """Test full population and query cycle."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        # Populate
        registry = populator.populate()
        
        # Verify all ACs are present
        assert len(registry.ac_metadata) == 87
        
        # Verify domain distribution (actual counts from YAML)
        assert registry.count_acs_for_domain("tdd") == 22
        assert registry.count_acs_for_domain("planning") == 26
        assert registry.count_acs_for_domain("ado") == 23
        assert registry.count_acs_for_domain("interaction") == 16
    
    def test_ac_domain_consistency(self):
        """Test that AC-to-domain index is consistent with domain-to-AC."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        registry = populator.get_registry()
        
        # For each domain, verify that all ACs in that domain
        # have the domain set in their ac_to_domain mapping
        for domain_id in registry.get_all_domains():
            domain_acs = registry.get_acs_for_domain(domain_id)
            for ac in domain_acs:
                assert registry.get_domain_for_ac(ac.ac_id) == domain_id
    
    def test_orchestrator_ac_mappings(self):
        """Test orchestrator-to-AC mappings are correct."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        registry = populator.get_registry()
        
        # Verify each orchestrator has correct AC counts (actual from YAML)
        tdd_acs = registry.get_acs_for_orchestrator("TDDOrchestrator")
        assert len(tdd_acs) == 22
        
        planning_acs = registry.get_acs_for_orchestrator("PlanningOrchestrator")
        assert len(planning_acs) == 26
        
        ado_acs = registry.get_acs_for_orchestrator("ADOOrchestrator")
        assert len(ado_acs) == 23
        
        interaction_acs = registry.get_acs_for_orchestrator("InteractionOrchestrator")
        assert len(interaction_acs) == 16
    
    def test_specific_ac_mappings(self):
        """Test specific AC mappings are correct."""
        tier1_path = resolve_path("cortex_brain", "tier1")
        populator = ACDomainPopulator(tier1_path)
        
        populator.populate()
        registry = populator.get_registry()
        
        # Test specific mappings from ac-domain-mappings.yaml
        test_cases = [
            ("AC-AR-001-01", "planning"),
            ("AC-AR-006-01", "tdd"),
            ("AC-AR-008-01", "ado"),
            ("AC-AR-008-03", "interaction"),
            ("AC-FR-001-01", "tdd"),
            ("AC-FR-003-01", "ado"),
            ("AC-FR-005-01", "interaction"),
            ("AC-NFR-001-01", "tdd"),
            ("AC-NFR-002-01", "ado"),
            ("AC-NFR-003-01", "interaction"),
        ]
        
        for ac_id, expected_domain in test_cases:
            actual_domain = registry.get_domain_for_ac(ac_id)
            assert actual_domain == expected_domain, f"{ac_id} should map to {expected_domain}, got {actual_domain}"
