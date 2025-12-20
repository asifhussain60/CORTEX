"""
Component Discovery Scanner Tests

Tests for discovering unwired SOLID components in CORTEX codebase.

RED PHASE: Tests written FIRST to define expected behavior.
"""

import pytest
from pathlib import Path
from dataclasses import dataclass
from typing import List

# Import will fail initially (RED phase)
from src.operations.modules.realignment.component_discovery_scanner import (
    ComponentDiscoveryScanner,
    DiscoveredComponent
)


class TestComponentDiscoveryScanner:
    """Test component discovery and wiring detection."""
    
    @pytest.fixture
    def scanner(self):
        """Create scanner instance."""
        return ComponentDiscoveryScanner()
    
    @pytest.fixture
    def cortex_root(self):
        """Get CORTEX root directory."""
        return Path(__file__).parent.parent
    
    def test_discovers_solid_principle_enforcer(self, scanner, cortex_root):
        """Test: Discovers SOLIDPrincipleEnforcer with full SOLID capabilities."""
        # RED: This test MUST fail initially
        components = scanner.discover_components(cortex_root)
        
        # Find SOLIDPrincipleEnforcer
        enforcer = next(
            (c for c in components if c.name == "SOLIDPrincipleEnforcer"),
            None
        )
        
        assert enforcer is not None, "SOLIDPrincipleEnforcer not discovered"
        assert "solid_principle_enforcer.py" in str(enforcer.file_path)
        assert "SRP" in enforcer.capabilities
        assert "OCP" in enforcer.capabilities
        assert "LSP" in enforcer.capabilities
        assert "ISP" in enforcer.capabilities
        assert "DIP" in enforcer.capabilities
    
    def test_discovers_solid_analyzer(self, scanner, cortex_root):
        """Test: Discovers SOLIDAnalyzer with SRP/DIP capabilities."""
        # RED: This test MUST fail initially
        components = scanner.discover_components(cortex_root)
        
        # Find SOLIDAnalyzer
        analyzer = next(
            (c for c in components if c.name == "SOLIDAnalyzer"),
            None
        )
        
        assert analyzer is not None, "SOLIDAnalyzer not discovered"
        assert "code_review_plugin.py" in str(analyzer.file_path)
        assert "SRP" in analyzer.capabilities
        assert "DIP" in analyzer.capabilities
    
    def test_discovers_dependency_graph(self, scanner, cortex_root):
        """Test: Discovers DependencyGraph with coupling capabilities."""
        # RED: This test MUST fail initially
        components = scanner.discover_components(cortex_root)
        
        # Find DependencyGraph
        dep_graph = next(
            (c for c in components if c.name == "DependencyGraph"),
            None
        )
        
        assert dep_graph is not None, "DependencyGraph not discovered"
        assert "dependency_crawler.py" in str(dep_graph.file_path)
        assert "COUPLING" in dep_graph.capabilities
        assert "CIRCULAR_DEPS" in dep_graph.capabilities
    
    def test_detects_unwired_status(self, scanner, cortex_root):
        """Test: Detects unwired status (no imports found)."""
        # RED: This test MUST fail initially
        components = scanner.discover_components(cortex_root)
        
        # All 3 components should be unwired initially
        unwired = [c for c in components if not c.is_wired]
        
        assert len(unwired) >= 1, "Should detect unwired components"
        
        # At minimum, SOLIDPrincipleEnforcer should be unwired
        enforcer_unwired = any(
            c.name == "SOLIDPrincipleEnforcer" for c in unwired
        )
        assert enforcer_unwired, "SOLIDPrincipleEnforcer should be unwired"
    
    def test_suggests_correct_wiring_targets(self, scanner, cortex_root):
        """Test: Suggests correct wiring targets (RefactoringIntelligence)."""
        # RED: This test MUST fail initially
        components = scanner.discover_components(cortex_root)
        
        # Find unwired SOLID components
        solid_components = [
            c for c in components 
            if "SOLID" in c.name or "Dependency" in c.name
        ]
        
        for component in solid_components:
            assert len(component.potential_uses) > 0, \
                f"{component.name} should have suggested wiring targets"
            
            # Should suggest RefactoringIntelligence
            assert any(
                "RefactoringIntelligence" in target 
                for target in component.potential_uses
            ), f"{component.name} should suggest RefactoringIntelligence"
    
    def test_extracts_capabilities_from_methods(self, scanner):
        """Test: Extracts capabilities from class methods via AST."""
        # RED: This test MUST fail initially
        
        # Create test file with SOLID methods
        test_code = """
class TestAnalyzer:
    def check_srp_violation(self):
        pass
    
    def check_ocp_violation(self):
        pass
    
    def detect_coupling(self):
        pass
"""
        
        capabilities = scanner._extract_capabilities_from_code(test_code)
        
        assert "SRP" in capabilities
        assert "OCP" in capabilities
        assert "COUPLING" in capabilities
    
    def test_determines_wiring_status_from_imports(self, scanner, cortex_root):
        """Test: Determines if component is imported anywhere in codebase."""
        # RED: This test MUST fail initially
        
        # Check if scanner can detect imports
        is_wired = scanner._check_if_wired(
            cortex_root,
            "SOLIDPrincipleEnforcer",
            Path("src/cortex_agents/test_generator/solid_principle_enforcer.py")
        )
        
        # Initially should be False (unwired)
        assert isinstance(is_wired, bool)


class TestComponentDiscoveryPatterns:
    """Test pattern matching for component discovery."""
    
    def test_matches_enforcer_pattern(self):
        """Test: Matches *_enforcer.py pattern."""
        scanner = ComponentDiscoveryScanner()
        
        test_path = Path("src/cortex_agents/test_generator/solid_principle_enforcer.py")
        assert scanner._matches_pattern(test_path)
    
    def test_matches_analyzer_pattern(self):
        """Test: Matches *_analyzer.py pattern."""
        scanner = ComponentDiscoveryScanner()
        
        test_path = Path("src/plugins/code_review_plugin.py")
        # Should match plugin files containing analyzers
        assert scanner._matches_pattern(test_path) or scanner._should_scan_file(test_path)
    
    def test_ignores_test_files(self):
        """Test: Ignores test files."""
        scanner = ComponentDiscoveryScanner()
        
        test_path = Path("tests/test_component_discovery_scanner.py")
        assert not scanner._should_scan_file(test_path)
    
    def test_ignores_brain_files(self):
        """Test: Ignores cortex-brain files."""
        scanner = ComponentDiscoveryScanner()
        
        test_path = Path("cortex-brain/some_analyzer.py")
        assert not scanner._should_scan_file(test_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
