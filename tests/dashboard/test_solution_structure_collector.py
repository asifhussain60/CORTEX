"""
Phase 8.1: Solution Structure Collector Tests (Backend)

RED phase: TDD for backend data collector that extracts solution hierarchy
from engineering-onboarding.json and prepares D3.js-compatible data structure.
"""

import pytest
from src.dashboard.data.solution_structure_collector import SolutionStructureCollector


class TestSolutionDataExtraction:
    """Test extracting solution data from engineering-onboarding.json."""

    def test_extract_from_engineering_onboarding(self):
        """Should extract solutions from engineering-onboarding.json."""
        # Sample structure from engineering-onboarding.json
        onboarding_data = {
            "sections": [
                {
                    "title": "Solution Structure",
                    "content": {
                        "solutions": [
                            {
                                "name": "TimeTracking.sln",
                                "path": "Source/TimeTracking.sln",
                                "project_count": 4,
                                "vs_version": "17",
                                "description": "Main application solution",
                                "projects": [
                                    {
                                        "name": "TimeTracking.Web",
                                        "loc": 52840,
                                        "file_count": 347,
                                        "dependencies": ["TimeTracking.Core"]
                                    },
                                    {
                                        "name": "TimeTracking.Core",
                                        "loc": 78125,
                                        "file_count": 523,
                                        "dependencies": []
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        
        collector = SolutionStructureCollector()
        solutions = collector.extract_solutions_from_onboarding(onboarding_data)
        
        assert len(solutions) == 1
        assert solutions[0]["name"] == "TimeTracking.sln"
        assert solutions[0]["project_count"] == 4
        assert len(solutions[0]["projects"]) == 2

    def test_extract_handles_missing_solution_structure_section(self):
        """Should return empty list when section is missing."""
        onboarding_data = {
            "sections": [
                {
                    "title": "Architecture",
                    "content": {}
                }
            ]
        }
        
        collector = SolutionStructureCollector()
        solutions = collector.extract_solutions_from_onboarding(onboarding_data)
        
        assert solutions == []

    def test_extract_handles_empty_sections(self):
        """Should handle empty sections list."""
        collector = SolutionStructureCollector()
        solutions = collector.extract_solutions_from_onboarding({"sections": []})
        
        assert solutions == []


class TestHierarchyBuilding:
    """Test building hierarchical tree from solution data."""

    def test_build_single_solution_hierarchy(self):
        """Should create Repository → Solution → Projects hierarchy."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {"name": "App.Web", "loc": 5000, "file_count": 50},
                    {"name": "App.Core", "loc": 3000, "file_count": 30}
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        hierarchy = collector.build_hierarchy(solutions)
        
        assert hierarchy["name"] == "Repository"
        assert hierarchy["type"] == "root"
        assert len(hierarchy["children"]) == 1
        
        solution_node = hierarchy["children"][0]
        assert solution_node["name"] == "App.sln"
        assert solution_node["type"] == "solution"
        assert len(solution_node["children"]) == 2

    def test_build_multiple_solutions_hierarchy(self):
        """Should handle multiple solutions at root level."""
        solutions = [
            {
                "name": "Main.sln",
                "projects": [{"name": "Main.Api", "loc": 8000}]
            },
            {
                "name": "Tests.sln",
                "projects": [{"name": "Tests.Unit", "loc": 4000}]
            }
        ]
        
        collector = SolutionStructureCollector()
        hierarchy = collector.build_hierarchy(solutions)
        
        assert len(hierarchy["children"]) == 2
        assert hierarchy["children"][0]["name"] == "Main.sln"
        assert hierarchy["children"][1]["name"] == "Tests.sln"

    def test_project_nodes_have_correct_structure(self):
        """Project nodes should have name, type, value (LOC), file_count."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {"name": "App.Web", "loc": 12000, "file_count": 100}
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        hierarchy = collector.build_hierarchy(solutions)
        
        project_node = hierarchy["children"][0]["children"][0]
        assert project_node["name"] == "App.Web"
        assert project_node["type"] == "project"
        assert project_node["value"] == 12000  # LOC for D3.js sizing
        assert project_node["file_count"] == 100

    def test_solution_nodes_aggregate_child_metrics(self):
        """Solution nodes should sum LOC and file_count from projects."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {"name": "App.Web", "loc": 5000, "file_count": 50},
                    {"name": "App.Core", "loc": 3000, "file_count": 30},
                    {"name": "App.Data", "loc": 2000, "file_count": 20}
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        hierarchy = collector.build_hierarchy(solutions)
        
        solution_node = hierarchy["children"][0]
        assert solution_node["value"] == 10000  # 5000 + 3000 + 2000
        assert solution_node["file_count"] == 100  # 50 + 30 + 20
        assert solution_node["project_count"] == 3

    def test_root_node_aggregates_all_solutions(self):
        """Root should sum all metrics across solutions."""
        solutions = [
            {
                "name": "Main.sln",
                "projects": [{"name": "Main.Api", "loc": 8000, "file_count": 80}]
            },
            {
                "name": "Tests.sln",
                "projects": [{"name": "Tests.Unit", "loc": 4000, "file_count": 40}]
            }
        ]
        
        collector = SolutionStructureCollector()
        hierarchy = collector.build_hierarchy(solutions)
        
        assert hierarchy["value"] == 12000  # 8000 + 4000
        assert hierarchy["file_count"] == 120  # 80 + 40


class TestDependencyExtraction:
    """Test extracting dependency edges between projects."""

    def test_extract_simple_dependencies(self):
        """Should create source→target edges from project dependencies."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {
                        "name": "App.Web",
                        "loc": 5000,
                        "dependencies": ["App.Core", "App.Infrastructure"]
                    },
                    {"name": "App.Core", "loc": 3000, "dependencies": []},
                    {
                        "name": "App.Infrastructure",
                        "loc": 2000,
                        "dependencies": ["App.Core"]
                    }
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        edges = collector.extract_dependencies(solutions)
        
        assert len(edges) == 3
        assert {"source": "App.Web", "target": "App.Core"} in edges
        assert {"source": "App.Web", "target": "App.Infrastructure"} in edges
        assert {"source": "App.Infrastructure", "target": "App.Core"} in edges

    def test_extract_dependencies_handles_missing_field(self):
        """Should handle projects without dependencies field."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {"name": "App.Web", "loc": 5000}  # No dependencies field
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        edges = collector.extract_dependencies(solutions)
        
        assert edges == []

    def test_extract_cross_solution_dependencies(self):
        """Should detect dependencies across solutions."""
        solutions = [
            {
                "name": "Main.sln",
                "projects": [
                    {
                        "name": "Main.Api",
                        "loc": 8000,
                        "dependencies": ["Shared.Models"]
                    }
                ]
            },
            {
                "name": "Shared.sln",
                "projects": [
                    {"name": "Shared.Models", "loc": 2000, "dependencies": []}
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        edges = collector.extract_dependencies(solutions)
        
        assert len(edges) == 1
        assert {"source": "Main.Api", "target": "Shared.Models"} in edges


class TestMetadataCalculation:
    """Test calculating aggregate metadata for dashboard summary."""

    def test_calculate_metadata_single_solution(self):
        """Should calculate totals for single solution."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {"name": "App.Web", "loc": 5000, "file_count": 50},
                    {"name": "App.Core", "loc": 3000, "file_count": 30}
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        metadata = collector.calculate_metadata(solutions)
        
        assert metadata["total_solutions"] == 1
        assert metadata["total_projects"] == 2
        assert metadata["total_loc"] == 8000
        assert metadata["total_files"] == 80

    def test_calculate_metadata_multiple_solutions(self):
        """Should aggregate across all solutions."""
        solutions = [
            {
                "name": "Main.sln",
                "projects": [
                    {"name": "Main.Api", "loc": 8000, "file_count": 80}
                ]
            },
            {
                "name": "Tests.sln",
                "projects": [
                    {"name": "Tests.Unit", "loc": 4000, "file_count": 40},
                    {"name": "Tests.Integration", "loc": 2000, "file_count": 20}
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        metadata = collector.calculate_metadata(solutions)
        
        assert metadata["total_solutions"] == 2
        assert metadata["total_projects"] == 3
        assert metadata["total_loc"] == 14000  # 8000 + 4000 + 2000
        assert metadata["total_files"] == 140  # 80 + 40 + 20

    def test_calculate_metadata_empty_solutions(self):
        """Should return zero totals for empty input."""
        collector = SolutionStructureCollector()
        metadata = collector.calculate_metadata([])
        
        assert metadata["total_solutions"] == 0
        assert metadata["total_projects"] == 0
        assert metadata["total_loc"] == 0
        assert metadata["total_files"] == 0


class TestCollectMethod:
    """Test main collect() entry point."""

    def test_collect_returns_complete_package(self):
        """Should return hierarchy + dependencies + metadata."""
        solutions = [
            {
                "name": "TimeTracking.sln",
                "projects": [
                    {
                        "name": "TimeTracking.Web",
                        "loc": 52840,
                        "file_count": 347,
                        "dependencies": ["TimeTracking.Core"]
                    },
                    {
                        "name": "TimeTracking.Core",
                        "loc": 78125,
                        "file_count": 523,
                        "dependencies": []
                    }
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        # Verify structure
        assert "hierarchy" in result
        assert "dependencies" in result
        assert "metadata" in result
        
        # Hierarchy
        assert result["hierarchy"]["name"] == "Repository"
        assert len(result["hierarchy"]["children"]) == 1
        
        # Dependencies
        assert len(result["dependencies"]) == 1
        assert result["dependencies"][0]["source"] == "TimeTracking.Web"
        assert result["dependencies"][0]["target"] == "TimeTracking.Core"
        
        # Metadata
        assert result["metadata"]["total_solutions"] == 1
        assert result["metadata"]["total_projects"] == 2
        assert result["metadata"]["total_loc"] == 130965
        assert result["metadata"]["total_files"] == 870

    def test_collect_preserves_solution_metadata_fields(self):
        """Should preserve original solution metadata in hierarchy."""
        solutions = [
            {
                "name": "App.sln",
                "path": "Source/App.sln",
                "vs_version": "17",
                "description": "Main application",
                "project_count": 1,
                "projects": [
                    {"name": "App.Web", "loc": 5000, "file_count": 50}
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        solution_node = result["hierarchy"]["children"][0]
        assert solution_node["path"] == "Source/App.sln"
        assert solution_node["vs_version"] == "17"
        assert solution_node["description"] == "Main application"
        assert solution_node["project_count"] == 1

    def test_collect_handles_empty_input(self):
        """Should handle empty solutions gracefully."""
        collector = SolutionStructureCollector()
        result = collector.collect([])
        
        assert result["hierarchy"]["name"] == "Repository"
        assert result["hierarchy"]["children"] == []
        assert result["dependencies"] == []
        assert result["metadata"]["total_solutions"] == 0

    def test_collect_handles_none_input(self):
        """Should handle None input gracefully."""
        collector = SolutionStructureCollector()
        result = collector.collect(None)
        
        assert result["hierarchy"]["name"] == "Repository"
        assert result["hierarchy"]["children"] == []


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_solution_without_name(self):
        """Should skip solutions missing required 'name' field."""
        solutions = [
            {
                "projects": [{"name": "App.Web", "loc": 5000}]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        # Should skip malformed solution
        assert len(result["hierarchy"]["children"]) == 0

    def test_handles_project_without_name(self):
        """Should skip projects missing required 'name' field."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {"loc": 5000, "file_count": 50}  # No name
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        solution_node = result["hierarchy"]["children"][0]
        # Should skip malformed project
        assert len(solution_node["children"]) == 0

    def test_handles_missing_loc_field(self):
        """Should default LOC to 0 when missing."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {"name": "App.Web", "file_count": 50}  # No LOC
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        project_node = result["hierarchy"]["children"][0]["children"][0]
        assert project_node["value"] == 0

    def test_handles_missing_file_count_field(self):
        """Should default file_count to 0 when missing."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {"name": "App.Web", "loc": 5000}  # No file_count
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        project_node = result["hierarchy"]["children"][0]["children"][0]
        assert project_node["file_count"] == 0

    def test_large_solution_with_many_projects(self):
        """Should handle large solutions efficiently."""
        projects = [
            {"name": f"Project{i}", "loc": 1000 * i, "file_count": 10 * i}
            for i in range(1, 101)  # 100 projects
        ]
        
        solutions = [{"name": "LargeSolution.sln", "projects": projects}]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        solution_node = result["hierarchy"]["children"][0]
        assert len(solution_node["children"]) == 100
        # Sum = 1000 * (1+2+...+100) = 1000 * 5050 = 5,050,000
        assert result["metadata"]["total_loc"] == 5050000
