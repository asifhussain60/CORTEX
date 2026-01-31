"""
TDD Tests for LENS Visualization Orchestrator.

Tests main coordinator integrating LENS analyzers with visualization system:
- Repository analysis via GitHistoryAnalyzer, ASTAnalyzer, CommentExtractor
- Dashboard data generation for all tabs
- Output routing to appropriate location
- Context-aware tab configuration

Authority: CORE-008 (TDD First)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-001
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.orchestrators.support.lens_visualization_orchestrator import (
    LENSVisualizationOrchestrator,
    DashboardData,
)


class TestLENSVisualizationOrchestrator:
    """Test LENS Visualization Orchestrator main coordinator."""
    
    def test_instantiate_orchestrator(self, tmp_path):
        """Test creating LENSVisualizationOrchestrator instance."""
        orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
        
        assert orchestrator.repo_path == tmp_path
        assert hasattr(orchestrator, "git_analyzer")
        assert hasattr(orchestrator, "ast_analyzer")
        assert hasattr(orchestrator, "comment_extractor")
    
    def test_generate_dashboard_creates_output_directory(self, tmp_path):
        """Test dashboard generation creates output directory."""
        orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
        
        # Mock LENS analyzers
        with patch.object(orchestrator, "_run_analysis"):
            dashboard_data = orchestrator.generate_dashboard()
        
        # Output directory should be created
        assert isinstance(dashboard_data, DashboardData)
        assert dashboard_data.output_path.exists()
    
    def test_generate_dashboard_uses_custom_output_path(self, tmp_path):
        """Test dashboard generation respects custom output path."""
        orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
        custom_output = tmp_path / "custom/dashboard"
        
        with patch.object(orchestrator, "_run_analysis"):
            dashboard_data = orchestrator.generate_dashboard(output_path=custom_output)
        
        assert dashboard_data.output_path == custom_output
    
    def test_generate_repository_overview(self, tmp_path):
        """Test generating Repository Overview tab data."""
        orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
        
        # Mock AST analysis
        mock_ast = {
            "functions": [{"name": "create_user"}, {"name": "send_email"}],
            "classes": [{"name": "UserController"}],
            "imports": ["flask", "sqlalchemy"],
        }
        
        with patch.object(orchestrator, "ast_analyzer") as mock_analyzer:
            mock_analyzer.analyze.return_value = mock_ast
            
            overview_data = orchestrator.generate_repository_overview()
        
        assert "summary" in overview_data
        assert "capabilities" in overview_data
        assert "tech_stack" in overview_data
        assert "architecture_pattern" in overview_data
    
    def test_generate_dependency_graph_call_graph(self, tmp_path):
        """Test generating call graph data."""
        orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
        
        # Mock AST with function calls
        mock_ast = {
            "functions": [
                {"name": "main", "calls": ["process_data", "save_results"]},
                {"name": "process_data", "calls": ["validate_input"]},
            ],
        }
        
        with patch.object(orchestrator, "ast_analyzer") as mock_analyzer:
            mock_analyzer.analyze.return_value = mock_ast
            
            graph_data = orchestrator.generate_dependency_graph(visualization_type="call_graph")
        
        assert "nodes" in graph_data
        assert "edges" in graph_data
        assert len(graph_data["nodes"]) > 0
    
    def test_generate_dependency_graph_import_graph(self, tmp_path):
        """Test generating import graph data."""
        orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
        
        # Mock AST with imports
        mock_ast = {
            "modules": [
                {"name": "module_a", "imports": ["module_b", "module_c"]},
                {"name": "module_b", "imports": ["module_c"]},
            ],
        }
        
        with patch.object(orchestrator, "ast_analyzer") as mock_analyzer:
            mock_analyzer.analyze.return_value = mock_ast
            
            graph_data = orchestrator.generate_dependency_graph(visualization_type="import_graph")
        
        assert "nodes" in graph_data
        assert "edges" in graph_data
    
    def test_generate_class_diagram_uml(self, tmp_path):
        """Test generating UML class diagram data."""
        orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
        
        # Mock AST with classes
        mock_ast = {
            "classes": [
                {
                    "name": "User",
                    "methods": ["__init__", "login", "logout"],
                    "attributes": ["id", "name", "email"],
                },
                {
                    "name": "Admin",
                    "bases": ["User"],
                    "methods": ["grant_permission"],
                },
            ],
        }
        
        with patch.object(orchestrator, "ast_analyzer") as mock_analyzer:
            mock_analyzer.analyze.return_value = mock_ast
            
            diagram_data = orchestrator.generate_class_diagram(diagram_type="uml")
        
        assert "classes" in diagram_data
        assert len(diagram_data["classes"]) == 2
        assert any(c["name"] == "User" for c in diagram_data["classes"])
    
    def test_generate_temporal_analysis(self, tmp_path):
        """Test generating temporal analysis (git timeline)."""
        orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
        
        # Mock Git history
        mock_commits = [
            {"sha": "abc123", "author": "Alice", "date": "2024-01-15", "message": "Add feature"},
            {"sha": "def456", "author": "Bob", "date": "2024-01-16", "message": "Fix bug"},
        ]
        
        with patch.object(orchestrator, "git_analyzer") as mock_analyzer:
            mock_analyzer.get_commits.return_value = mock_commits
            
            temporal_data = orchestrator.generate_temporal_analysis()
        
        assert "timeline" in temporal_data
        assert "commits" in temporal_data
        assert len(temporal_data["commits"]) == 2
    
    def test_generate_impact_analysis(self, tmp_path):
        """Test generating impact analysis for a file."""
        orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
        target_file = tmp_path / "module.py"
        
        # Mock AST with dependencies
        mock_dependencies = {
            "imported_by": ["tests/test_module.py", "app/main.py"],
            "imports": ["utils/helpers.py"],
        }
        
        with patch.object(orchestrator, "ast_analyzer") as mock_analyzer:
            mock_analyzer.get_dependencies.return_value = mock_dependencies
            
            impact_data = orchestrator.generate_impact_analysis(target_file)
        
        assert "target" in impact_data
        assert "affected_files" in impact_data
        assert len(impact_data["affected_files"]) > 0
    
    def test_context_aware_tabs_external_repo(self, tmp_path):
        """Test dashboard shows 5 tabs for external repository."""
        # Mock is_cortex_repository at the module level WHERE IT'S IMPORTED
        with patch("cortex.visualization.dashboard_configuration.is_cortex_repository", return_value=False):
            orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
            tabs = orchestrator.get_dashboard_tabs()
        
        assert len(tabs) == 5  # Universal tabs only
        assert all(tab.is_universal for tab in tabs)
    
    def test_context_aware_tabs_cortex_repo(self, tmp_path):
        """Test dashboard shows 8 tabs for CORTEX repository."""
        # Mock is_cortex_repository at the module level WHERE IT'S IMPORTED
        with patch("cortex.visualization.dashboard_configuration.is_cortex_repository", return_value=True):
            orchestrator = LENSVisualizationOrchestrator(repo_path=tmp_path)
            tabs = orchestrator.get_dashboard_tabs()
        
        assert len(tabs) == 8  # Universal + CORTEX tabs
        # First 5 should be universal
        assert all(tabs[i].is_universal for i in range(5))
        # Last 3 should be CORTEX-specific
        assert all(tabs[i].requires_cortex for i in range(5, 8))


class TestDashboardData:
    """Test DashboardData dataclass."""
    
    def test_create_dashboard_data(self, tmp_path):
        """Test creating DashboardData instance."""
        output_path = tmp_path / ".cortex/lens-dashboard"
        
        dashboard_data = DashboardData(
            output_path=output_path,
            tabs=[],
            repository_overview={},
            dependency_graph={},
            class_diagrams={},
            temporal_analysis={},
            impact_analysis={},
        )
        
        assert dashboard_data.output_path == output_path
        assert isinstance(dashboard_data.tabs, list)
        assert isinstance(dashboard_data.repository_overview, dict)
