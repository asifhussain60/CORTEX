"""
Phase 8 Integration Tests

Validates that Solution Structure Collector and Tech Stack Risk Scorer
work together seamlessly to produce complete dashboard data.
"""

import pytest
from unittest.mock import patch, Mock
from src.dashboard.data.solution_structure_collector import SolutionStructureCollector
from src.dashboard.data.tech_stack_risk_scorer import TechStackRiskScorer


class TestPhase8Integration:
    """Test integration between Phase 8.1 and 8.2 components."""

    def test_solution_collector_and_risk_scorer_integration(self):
        """Solution hierarchy and risk scores should work together."""
        # Solution data
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
        
        # Tech stack data
        tech_stack = {
            "backend": [
                {"name": ".NET", "version": "8", "cve_count": 2}
            ]
        }
        
        # Collect solution structure
        solution_collector = SolutionStructureCollector()
        solution_data = solution_collector.collect(solutions)
        
        # Enrich tech stack with risk scores
        risk_scorer = TechStackRiskScorer()
        enriched_stack = risk_scorer.enrich_tech_stack(tech_stack)
        
        # Verify both components produce valid data
        assert "hierarchy" in solution_data
        assert solution_data["metadata"]["total_solutions"] == 1
        assert enriched_stack["backend"][0]["name"] == ".NET"
        assert "risk_score" in enriched_stack["backend"][0]

    @patch('requests.get')
    def test_end_to_end_dashboard_data_generation(self, mock_get):
        """Complete dashboard data generation pipeline."""
        # Mock EOL API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "cycle": "8",
                "releaseDate": "2023-11-14",
                "eol": "2026-11-10"
            }
        ]
        mock_get.return_value = mock_response
        
        # Complete dashboard data
        dashboard_data = {
            "solutions": [
                {
                    "name": "Main.sln",
                    "projects": [
                        {
                            "name": "Main.Api",
                            "loc": 8000,
                            "file_count": 80,
                            "dependencies": []
                        }
                    ]
                }
            ],
            "tech_stack": {
                "backend": [
                    {"name": ".NET", "version": "8", "cve_count": 2}
                ],
                "frontend": [],
                "database": []
            }
        }
        
        # Process pipeline
        solution_collector = SolutionStructureCollector()
        risk_scorer = TechStackRiskScorer()
        
        # Generate complete output
        output = {
            "solution_structure": solution_collector.collect(dashboard_data["solutions"]),
            "tech_stack": risk_scorer.enrich_tech_stack(dashboard_data["tech_stack"])
        }
        
        # Validate output structure
        assert "solution_structure" in output
        assert "tech_stack" in output
        
        # Solution structure
        assert output["solution_structure"]["hierarchy"]["name"] == "Repository"
        assert len(output["solution_structure"]["hierarchy"]["children"]) == 1
        assert output["solution_structure"]["metadata"]["total_loc"] == 8000
        
        # Tech stack with risk
        assert output["tech_stack"]["backend"][0]["risk_score"] >= 0
        assert output["tech_stack"]["backend"][0]["eol_date"] == "2026-11-10"

    def test_hierarchy_preserves_project_metadata_for_risk_correlation(self):
        """Project metadata should be preserved for frontend correlation."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {
                        "name": "App.Web",
                        "type": "ASP.NET Core Web Application",
                        "loc": 5000,
                        "file_count": 50,
                        "responsibilities": ["API", "UI"]
                    }
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        project_node = result["hierarchy"]["children"][0]["children"][0]
        assert project_node["type"] == "ASP.NET Core Web Application"
        assert "responsibilities" in project_node

    @patch('requests.get')
    def test_risk_scorer_handles_multiple_technologies(self, mock_get):
        """Risk scorer should handle mixed tech stacks."""
        # Mock different API responses
        def mock_api_response(url, timeout):
            if "dotnet.json" in url:
                response = Mock()
                response.status_code = 200
                response.json.return_value = [
                    {"cycle": "8", "releaseDate": "2023-11-14", "eol": "2026-11-10"}
                ]
                return response
            elif "nodejs.json" in url:
                response = Mock()
                response.status_code = 200
                response.json.return_value = [
                    {"cycle": "20", "releaseDate": "2023-04-18", "eol": "2026-04-30"}
                ]
                return response
            else:
                response = Mock()
                response.status_code = 404
                return response
        
        mock_get.side_effect = mock_api_response
        
        tech_stack = {
            "backend": [
                {"name": ".NET", "version": "8", "cve_count": 2}
            ],
            "frontend": [
                {"name": "Node.js", "version": "20", "cve_count": 0}
            ]
        }
        
        scorer = TechStackRiskScorer()
        enriched = scorer.enrich_tech_stack(tech_stack)
        
        # Both technologies enriched
        assert enriched["backend"][0]["eol_date"] == "2026-11-10"
        assert enriched["frontend"][0]["eol_date"] == "2026-04-30"
        assert enriched["backend"][0]["risk_score"] > 0
        assert enriched["frontend"][0]["risk_score"] >= 0

    def test_empty_data_handling_across_components(self):
        """All components should handle empty data gracefully."""
        solution_collector = SolutionStructureCollector()
        risk_scorer = TechStackRiskScorer()
        
        # Empty solutions
        solution_data = solution_collector.collect([])
        assert solution_data["hierarchy"]["children"] == []
        assert solution_data["metadata"]["total_solutions"] == 0
        
        # Empty tech stack
        enriched_stack = risk_scorer.enrich_tech_stack({
            "backend": [],
            "frontend": []
        })
        assert enriched_stack["backend"] == []
        assert enriched_stack["frontend"] == []

    def test_dependency_graph_with_risk_annotations(self):
        """Dependency graph should be compatible with risk data."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {
                        "name": "App.Web",
                        "loc": 5000,
                        "dependencies": ["App.Core", "App.Data"]
                    },
                    {
                        "name": "App.Core",
                        "loc": 3000,
                        "dependencies": ["App.Data"]
                    },
                    {
                        "name": "App.Data",
                        "loc": 2000,
                        "dependencies": []
                    }
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        # Verify dependency graph structure
        assert len(result["dependencies"]) == 3
        
        # Dependencies can be annotated with risk data in frontend
        for edge in result["dependencies"]:
            assert "source" in edge
            assert "target" in edge


class TestPhase8DataFormats:
    """Test D3.js data format compatibility."""

    def test_hierarchy_format_compatible_with_d3_tree(self):
        """Hierarchy should match D3.js tree layout format."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {"name": "App.Web", "loc": 5000, "file_count": 50}
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        hierarchy = result["hierarchy"]
        
        # D3.js requires: name, children (optional), value (optional)
        def validate_d3_node(node):
            assert "name" in node
            if "children" in node and node["children"]:
                for child in node["children"]:
                    validate_d3_node(child)
        
        validate_d3_node(hierarchy)

    def test_dependency_edges_format_compatible_with_d3_force(self):
        """Dependency edges should match D3.js force-directed graph format."""
        solutions = [
            {
                "name": "App.sln",
                "projects": [
                    {
                        "name": "App.Web",
                        "loc": 5000,
                        "dependencies": ["App.Core"]
                    },
                    {"name": "App.Core", "loc": 3000, "dependencies": []}
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        edges = result["dependencies"]
        
        # D3.js force layout requires: source, target
        for edge in edges:
            assert "source" in edge
            assert "target" in edge
            assert isinstance(edge["source"], str)
            assert isinstance(edge["target"], str)


class TestPhase8ErrorHandling:
    """Test error handling across Phase 8 components."""

    @patch('requests.get')
    def test_graceful_degradation_when_api_fails(self, mock_get):
        """Should continue with partial data when API fails."""
        mock_get.side_effect = Exception("Network error")
        
        tech_stack = {
            "backend": [
                {"name": ".NET", "version": "8", "cve_count": 2}
            ]
        }
        
        scorer = TechStackRiskScorer()
        enriched = scorer.enrich_tech_stack(tech_stack)
        
        # Should still have risk score (based on CVE only)
        assert "risk_score" in enriched["backend"][0]
        assert enriched["backend"][0]["eol_date"] is None

    def test_malformed_solution_data_handling(self):
        """Should skip malformed solutions gracefully."""
        solutions = [
            {
                "name": "Valid.sln",
                "projects": [
                    {"name": "Valid.Project", "loc": 5000}
                ]
            },
            {
                # Missing name
                "projects": [
                    {"name": "Orphaned.Project", "loc": 3000}
                ]
            },
            {
                "name": "Empty.sln",
                "projects": [
                    {"loc": 2000}  # Missing name
                ]
            }
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        # Should only process valid solution
        assert len(result["hierarchy"]["children"]) == 2  # Valid + Empty (with 0 children)
        assert result["hierarchy"]["children"][0]["name"] == "Valid.sln"


class TestPhase8Performance:
    """Test performance characteristics."""

    @patch('requests.get')
    def test_caching_reduces_api_calls(self, mock_get):
        """Caching should prevent duplicate API calls."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"cycle": "8", "releaseDate": "2023-11-14", "eol": "2026-11-10"}
        ]
        mock_get.return_value = mock_response
        
        tech_stack = {
            "backend": [
                {"name": ".NET", "version": "8", "cve_count": 2},
                {"name": ".NET", "version": "8", "cve_count": 3},  # Same tech
                {"name": ".NET", "version": "8", "cve_count": 0}   # Same tech
            ]
        }
        
        scorer = TechStackRiskScorer()
        enriched = scorer.enrich_tech_stack(tech_stack)
        
        # Should call API only once due to caching
        assert mock_get.call_count == 1
        
        # All three entries enriched
        assert all("eol_date" in tech for tech in enriched["backend"])

    def test_large_solution_hierarchy_performance(self):
        """Should handle large solution hierarchies efficiently."""
        # Create 10 solutions with 20 projects each
        solutions = [
            {
                "name": f"Solution{i}.sln",
                "projects": [
                    {
                        "name": f"Project{i}_{j}",
                        "loc": 1000 * j,
                        "file_count": 10 * j,
                        "dependencies": []
                    }
                    for j in range(1, 21)
                ]
            }
            for i in range(1, 11)
        ]
        
        collector = SolutionStructureCollector()
        result = collector.collect(solutions)
        
        # Verify structure
        assert len(result["hierarchy"]["children"]) == 10
        assert result["metadata"]["total_solutions"] == 10
        assert result["metadata"]["total_projects"] == 200
