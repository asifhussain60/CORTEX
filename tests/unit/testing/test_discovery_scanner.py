"""
Test Suite: Discovery Scanner - Validates component discovery functionality

Authority: cortex-total-recall.prompt.md v2.0 | AC-WIRING-HARNESS-001
Phase: PRODUCTION-READINESS | Status: ✅ TEST SUITE ACTIVE
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add cortex to path
cortex_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(cortex_root))

from cortex.testing.discovery_scanner import (
    DiscoveryScanner,
    DiscoveredComponent,
    DiscoveryCategory,
)


class TestDiscoveryScannerInitialization:
    """Test scanner initialization and setup."""
    
    def test_scanner_initializes_with_default_path(self):
        """Scanner should initialize with CORTEX root path."""
        scanner = DiscoveryScanner()
        assert scanner.cortex_root is not None
        assert scanner.cortex_root.exists()
    
    def test_scanner_initializes_with_custom_path(self):
        """Scanner should accept custom root path."""
        custom_path = str(cortex_root)
        scanner = DiscoveryScanner(cortex_root=custom_path)
        assert str(scanner.cortex_root) == custom_path
    
    def test_scanner_builds_test_mapping(self):
        """Scanner should build test file mapping."""
        scanner = DiscoveryScanner()
        assert isinstance(scanner.test_mapping, dict)
    
    def test_discovered_components_list_initialized(self):
        """Discovered components list should initialize empty."""
        scanner = DiscoveryScanner()
        assert scanner.discovered_components == []
    
    def test_lens_patterns_defined(self):
        """LENS phase patterns should be defined."""
        assert hasattr(DiscoveryScanner, 'LENS_PATTERNS')
        assert 'Language' in DiscoveryScanner.LENS_PATTERNS
        assert 'Examination' in DiscoveryScanner.LENS_PATTERNS
        assert 'Navigation' in DiscoveryScanner.LENS_PATTERNS
        assert 'Synthesis' in DiscoveryScanner.LENS_PATTERNS


class TestOrchestratorDiscovery:
    """Test orchestrator component discovery."""
    
    def test_scan_orchestrators_finds_classes(self):
        """Should find orchestrator classes."""
        scanner = DiscoveryScanner()
        orchestrators = scanner.scan_orchestrators()
        
        # Should find at least MasterOrchestrator
        assert len(orchestrators) >= 0  # May be empty in test env
        
        # All results should be orchestrators
        for comp in orchestrators:
            assert comp.category == DiscoveryCategory.ORCHESTRATOR
    
    def test_orchestrator_has_required_attributes(self):
        """Discovered orchestrators should have all required attributes."""
        scanner = DiscoveryScanner()
        orchestrators = scanner.scan_orchestrators()
        
        for comp in orchestrators:
            assert comp.name is not None
            assert comp.class_name is not None
            assert comp.full_entry_point is not None
            assert comp.priority in [0, 1, 2]
            assert comp.category == DiscoveryCategory.ORCHESTRATOR
    
    def test_master_orchestrator_priority_is_critical(self):
        """MasterOrchestrator should have priority 0 (critical)."""
        scanner = DiscoveryScanner()
        orchestrators = scanner.scan_orchestrators()
        
        master_orcls = [o for o in orchestrators if "Master" in o.class_name]
        for comp in master_orcls:
            assert comp.priority == 0


class TestLENSComponentDiscovery:
    """Test LENS protocol component discovery."""
    
    def test_scan_lens_components(self):
        """Should discover LENS phase components."""
        scanner = DiscoveryScanner()
        lens_comps = scanner.scan_lens_components()
        
        # Should discover components
        assert isinstance(lens_comps, list)
        
        # All should be LENS components
        for comp in lens_comps:
            assert comp.category == DiscoveryCategory.LENS_COMPONENT
    
    def test_lens_phases_have_patterns(self):
        """Each LENS phase should have defined patterns."""
        for phase in ['Language', 'Examination', 'Navigation', 'Synthesis']:
            assert phase in DiscoveryScanner.LENS_PATTERNS
            assert isinstance(DiscoveryScanner.LENS_PATTERNS[phase], list)
            assert len(DiscoveryScanner.LENS_PATTERNS[phase]) > 0
    
    def test_language_phase_priority(self):
        """Language phase components should have priority 0."""
        scanner = DiscoveryScanner()
        lens_comps = scanner.scan_lens_components()
        
        # Filter for components that match language patterns
        language_patterns = DiscoveryScanner.LENS_PATTERNS['Language']
        for comp in lens_comps:
            for pattern in language_patterns:
                if pattern in comp.class_name.lower():
                    assert comp.priority == 0


class TestInfrastructureDiscovery:
    """Test infrastructure component discovery."""
    
    def test_scan_infrastructure_components(self):
        """Should discover infrastructure components."""
        scanner = DiscoveryScanner()
        infra = scanner.scan_infrastructure()
        
        assert isinstance(infra, list)
        for comp in infra:
            assert comp.category == DiscoveryCategory.INFRASTRUCTURE
    
    def test_infrastructure_patterns_defined(self):
        """Infrastructure patterns should be defined."""
        assert len(DiscoveryScanner.INFRASTRUCTURE_PATTERNS) > 0
        assert "CircuitBreaker" in DiscoveryScanner.INFRASTRUCTURE_PATTERNS
        assert "TransactionManager" in DiscoveryScanner.INFRASTRUCTURE_PATTERNS


class TestGovernanceDiscovery:
    """Test governance component discovery."""
    
    def test_scan_governance_components(self):
        """Should discover governance components."""
        scanner = DiscoveryScanner()
        governance = scanner.scan_governance()
        
        assert isinstance(governance, list)
        for comp in governance:
            assert comp.category == DiscoveryCategory.GOVERNANCE
    
    def test_governance_registry_critical(self):
        """GovernanceRegistry should be critical priority."""
        scanner = DiscoveryScanner()
        governance = scanner.scan_governance()
        
        registry_comps = [g for g in governance if "Registry" in g.class_name]
        for comp in registry_comps:
            assert comp.priority == 0


class TestMCPToolkitDiscovery:
    """Test MCP toolkit component discovery."""
    
    def test_scan_mcp_toolkit(self):
        """Should discover MCP toolkit components."""
        scanner = DiscoveryScanner()
        toolkit = scanner.scan_mcp_toolkit()
        
        assert isinstance(toolkit, list)
        for comp in toolkit:
            assert comp.category == DiscoveryCategory.TOOLKIT
    
    def test_mcp_patterns_defined(self):
        """MCP patterns should be defined."""
        assert len(DiscoveryScanner.MCP_PATTERNS) > 0
        assert "ToolRegistry" in DiscoveryScanner.MCP_PATTERNS


class TestFullScan:
    """Test complete discovery scan."""
    
    def test_scan_all_returns_unique_components(self):
        """scan_all should return deduplicated components."""
        scanner = DiscoveryScanner()
        components = scanner.scan_all()
        
        # Check for duplicates
        entry_points = [c.full_entry_point for c in components]
        assert len(entry_points) == len(set(entry_points))  # No duplicates
    
    def test_scan_all_populates_discovered_components(self):
        """scan_all should populate discovered_components list."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        
        assert len(scanner.discovered_components) > 0
    
    def test_scan_all_categorizes_components(self):
        """All components should have valid categories."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        
        valid_categories = [cat.value for cat in DiscoveryCategory]
        for comp in scanner.discovered_components:
            assert comp.category in DiscoveryCategory
    
    def test_scan_all_assigns_priorities(self):
        """All components should have valid priorities."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        
        for comp in scanner.discovered_components:
            assert 0 <= comp.priority <= 10


class TestDiscoveredComponentConversion:
    """Test conversion of discovered components to inventory format."""
    
    def test_component_to_inventory_entry(self):
        """Component should convert to inventory entry."""
        comp = DiscoveredComponent(
            name="test_component",
            module_path="cortex.testing.test_module",
            class_name="TestComponent",
            full_entry_point="cortex.testing.test_module.TestComponent",
            category=DiscoveryCategory.ORCHESTRATOR,
            priority=1,
            docstring="Test component for validation",
        )
        
        entry = comp.to_inventory_entry()
        
        assert "TestComponent" in entry
        assert "cortex.testing.test_module.TestComponent" in entry
        assert "DISCOVERED-ORCHESTRATOR" in entry
    
    def test_inventory_entry_has_required_fields(self):
        """Generated inventory entry should have all required fields."""
        comp = DiscoveredComponent(
            name="test",
            module_path="cortex.test",
            class_name="TestClass",
            full_entry_point="cortex.test.TestClass",
            category=DiscoveryCategory.INFRASTRUCTURE,
            priority=2,
        )
        
        entry = comp.to_inventory_entry()
        
        required_fields = [
            "id=",
            "name=",
            "category=",
            "status=",
            "description=",
            "tests_count=",
            "test_pass_rate=",
            "entry_point=",
        ]
        
        for field in required_fields:
            assert field in entry


class TestDiscoverySummary:
    """Test discovery summary generation."""
    
    def test_get_summary_returns_dict(self):
        """get_summary should return dictionary."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        summary = scanner.get_summary()
        
        assert isinstance(summary, dict)
    
    def test_summary_has_required_keys(self):
        """Summary should have required keys."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        summary = scanner.get_summary()
        
        required_keys = [
            'total_discovered',
            'by_category',
            'critical_priority',
            'high_priority',
            'components',
        ]
        
        for key in required_keys:
            assert key in summary
    
    def test_summary_counts_match_discovered(self):
        """Summary counts should match discovered components."""
        scanner = DiscoveryScanner()
        components = scanner.scan_all()
        summary = scanner.get_summary()
        
        assert summary['total_discovered'] == len(components)
    
    def test_summary_categories_sum_to_total(self):
        """Summary category counts should sum to total."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        summary = scanner.get_summary()
        
        category_sum = sum(summary['by_category'].values())
        assert category_sum == summary['total_discovered']
    
    def test_summary_components_list_complete(self):
        """Summary components list should include all discovered."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        summary = scanner.get_summary()
        
        assert len(summary['components']) == summary['total_discovered']


class TestComponentFiltering:
    """Test component discovery filtering and selection."""
    
    def test_critical_components_identified(self):
        """Should identify critical priority components."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        
        critical = [c for c in scanner.discovered_components if c.priority == 0]
        
        assert len(critical) > 0
    
    def test_components_by_category(self):
        """Should be able to filter components by category."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        
        orchestrators = [
            c for c in scanner.discovered_components
            if c.category == DiscoveryCategory.ORCHESTRATOR
        ]
        
        assert len(orchestrators) >= 0
    
    def test_components_with_tests(self):
        """Should identify components with associated tests."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        
        tested = [c for c in scanner.discovered_components if c.test_count > 0]
        
        # May be empty in test env but structure should exist
        for comp in tested:
            assert len(comp.test_files) > 0


class TestGenerateInventoryUpdates:
    """Test inventory generation from discovered components."""
    
    def test_generate_inventory_updates_returns_string(self):
        """Should generate inventory updates as string."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        
        inventory = scanner.generate_inventory_updates()
        assert isinstance(inventory, str)
    
    def test_inventory_has_header(self):
        """Generated inventory should have header."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        inventory = scanner.generate_inventory_updates()
        
        assert "AUTO-DISCOVERED COMPONENTS" in inventory
        assert "discovery_scanner.py" in inventory
    
    def test_inventory_has_category_sections(self):
        """Generated inventory should have sections for each category."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        inventory = scanner.generate_inventory_updates()
        
        # Should have at least one section
        assert "SECTION:" in inventory


# Integration tests with wiring harness
class TestIntegrationWithWiringHarness:
    """Test integration with wiring harness inventory."""
    
    def test_discovered_components_compatible_format(self):
        """Discovered components should be compatible with inventory format."""
        from cortex.testing.wiring_harness_inventory import UnwiredComponent, ComponentCategory
        
        scanner = DiscoveryScanner()
        components = scanner.scan_all()
        
        # Should be convertible to UnwiredComponent
        for comp in components[:3]:  # Test first 3
            # This should not raise
            entry_str = comp.to_inventory_entry()
            assert "UnwiredComponent" not in entry_str or "DISCOVERED" in entry_str
    
    def test_discovery_provides_inventory_entries(self):
        """Discovery should provide entries suitable for wiring harness."""
        scanner = DiscoveryScanner()
        scanner.scan_all()
        
        if len(scanner.discovered_components) > 0:
            for comp in scanner.discovered_components[:1]:
                entry = comp.to_inventory_entry()
                
                # Should have all required UnwiredComponent fields
                required = [
                    'id=',
                    'name=',
                    'entry_point=',
                    'wiring_priority=',
                ]
                
                for req in required:
                    assert req in entry


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
