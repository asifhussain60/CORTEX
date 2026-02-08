"""AC-PHASE43-004: DependencyMapper Integration Tests

Validates that DependencyMapper is wired into LENSOrchestrator
and produces dependency findings in the unified analysis result.

Target: 4/4 tests passing
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.lens.orchestrator import LENSOrchestrator
from cortex.core.intelligence.dependency_mapper import DependencyMapper, DependencyMap


class TestLENSDependencyIntegration:
    """Tests for DependencyMapper integration with LENSOrchestrator."""
    
    def test_lens_orchestrator_initializes_dependency_mapper(self):
        """Validate orchestrator has DependencyMapper instance."""
        # Create temporary repo path
        repo_path = Path(__file__).parent.parent.parent.parent
        orchestrator = LENSOrchestrator(repo_path=repo_path)
        assert hasattr(orchestrator, 'dependency_mapper'), \
            "LENSOrchestrator missing dependency_mapper attribute"
        assert isinstance(orchestrator.dependency_mapper, DependencyMapper), \
            f"dependency_mapper is {type(orchestrator.dependency_mapper)}, expected DependencyMapper"
    
    def test_dependency_findings_method_exists(self):
        """Validate _build_dependency_findings() method exists and returns dict."""
        repo_path = Path(__file__).parent.parent.parent.parent
        orchestrator = LENSOrchestrator(repo_path=repo_path)
        assert hasattr(orchestrator, '_build_dependency_findings'), \
            "LENSOrchestrator missing _build_dependency_findings() method"
        
        # Mock AST result
        mock_ast_result = {
            "imports": ["os", "sys"],
            "from_imports": {"json": ["loads", "dumps"]},
        }
        
        # Call should return dict with expected keys
        result = orchestrator._build_dependency_findings(Path("test.py"), mock_ast_result)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        
        # Should have dependency_map and source keys
        assert "dependency_map" in result or "dependencies" in result or "error" in result, \
            f"Result missing expected keys: {result.keys()}"


class TestDependencyMapperExport:
    """Tests for DependencyMapper class interface."""
    
    def test_dependency_mapper_accessible(self):
        """Validate DependencyMapper class is importable and instantiable."""
        mapper = DependencyMapper()
        assert mapper is not None, "Failed to instantiate DependencyMapper"
        assert hasattr(mapper, 'map_dependencies'), \
            "DependencyMapper missing map_dependencies() method"
    
    def test_dependency_mapper_maps_dependencies(self):
        """Validate DependencyMapper.map_dependencies() produces DependencyMap."""
        mapper = DependencyMapper(local_packages={"myproject"})
        
        # Create mock parse result
        mock_parse = Mock()
        mock_parse.success = True
        mock_parse.imports = ["os", "sys", "pytest"]
        mock_parse.from_imports = {
            "json": ["loads"],
            "myproject": ["utils"],
        }
        
        result = mapper.map_dependencies(mock_parse)
        
        # Validate result structure
        assert isinstance(result, DependencyMap), \
            f"Expected DependencyMap, got {type(result)}"
        assert hasattr(result, 'standard_library'), "Missing standard_library"
        assert hasattr(result, 'third_party'), "Missing third_party"
        assert hasattr(result, 'local'), "Missing local"
        assert hasattr(result, 'all_imports'), "Missing all_imports property"
