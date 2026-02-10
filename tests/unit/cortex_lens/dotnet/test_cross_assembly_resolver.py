"""
Tests for CrossAssemblyResolver

AC_START: AC-PHASE67-S1-CROSS-ASSEMBLY-TEST-001
"""

import pytest
from cortex_lens.dotnet.cross_assembly_resolver import CrossAssemblyResolver


@pytest.fixture
def sample_solution():
    """Create sample solution with multiple projects."""
    return {
        "solution_name": "TestSolution",
        "projects": [
            {
                "name": "Core",
                "semantic_model": {
                    "Types": [
                        {
                            "Name": "IEntity",
                            "Namespace": "Core.Entities",
                            "BaseType": None,
                            "Interfaces": [],
                            "Methods": [],
                            "Properties": []
                        }
                    ]
                }
            },
            {
                "name": "Infrastructure",
                "semantic_model": {
                    "Types": [
                        {
                            "Name": "Repository",
                            "Namespace": "Infrastructure.Data",
                            "BaseType": "object",
                            "Interfaces": ["Core.Entities.IEntity"],  # References Core
                            "Methods": [],
                            "Properties": []
                        }
                    ]
                }
            },
            {
                "name": "Api",
                "semantic_model": {
                    "Types": [
                        {
                            "Name": "UserController",
                            "Namespace": "Api.Controllers",
                            "BaseType": "object",
                            "Interfaces": [],
                            "Methods": [
                                {
                                    "Name": "GetEntity",
                                    "ReturnType": "Core.Entities.IEntity",  # References Core
                                    "Parameters": []
                                }
                            ],
                            "Properties": []
                        }
                    ]
                }
            }
        ]
    }


class TestCrossAssemblyResolver:
    """Test suite for CrossAssemblyResolver."""
    
    def test_init(self, sample_solution):
        """Test resolver initialization."""
        resolver = CrossAssemblyResolver(sample_solution)
        
        assert resolver is not None
        assert len(resolver.projects) == 3
    
    def test_build_assembly_graph(self, sample_solution):
        """
        Test building assembly dependency graph.
        
        AC: Infrastructure → Core, Api → Core
        """
        resolver = CrossAssemblyResolver(sample_solution)
        
        graph = resolver.build_assembly_graph()
        
        assert "Core" in graph
        assert "Infrastructure" in graph
        assert "Api" in graph
        
        # Infrastructure depends on Core (via IEntity interface)
        assert "Core" in graph["Infrastructure"]
        
        # Api depends on Core (via IEntity return type)
        assert "Core" in graph["Api"]
    
    def test_detect_circular_references(self, sample_solution):
        """
        Test circular dependency detection.
        
        AC: No circular dependencies in sample solution
        """
        resolver = CrossAssemblyResolver(sample_solution)
        
        cycles = resolver.detect_circular_references()
        
        # Sample solution has no circular dependencies
        assert len(cycles) == 0
    
    def test_get_dependency_order(self, sample_solution):
        """
        Test topological sort of projects.
        
        AC: Core must come before Infrastructure and Api
        """
        resolver = CrossAssemblyResolver(sample_solution)
        
        order = resolver.get_dependency_order()
        
        assert len(order) == 3
        
        # Core should come first (no dependencies)
        assert order[0] == "Core"
        
        # Infrastructure and Api should come after Core
        core_index = order.index("Core")
        infra_index = order.index("Infrastructure")
        api_index = order.index("Api")
        
        assert infra_index > core_index
        assert api_index > core_index
    
    def test_get_project_dependencies(self, sample_solution):
        """Test getting direct dependencies of a project."""
        resolver = CrossAssemblyResolver(sample_solution)
        
        core_deps = resolver.get_project_dependencies("Core")
        infra_deps = resolver.get_project_dependencies("Infrastructure")
        
        # Core has no dependencies
        assert len(core_deps) == 0
        
        # Infrastructure depends on Core
        assert "Core" in infra_deps
    
    def test_get_project_dependents(self, sample_solution):
        """Test getting projects that depend on a project."""
        resolver = CrossAssemblyResolver(sample_solution)
        
        core_dependents = resolver.get_project_dependents("Core")
        
        # Both Infrastructure and Api depend on Core
        assert "Infrastructure" in core_dependents
        assert "Api" in core_dependents


# AC_COMPLETE: AC-PHASE67-S1-CROSS-ASSEMBLY-TEST-001 ✅ 6 tests defined
