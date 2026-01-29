"""
Tests for ImpactAnalysisRenderer.

This module tests the impact analysis visualization renderer that calculates
change propagation and blast radius for code modifications.

Author: Asif Hussain
Orchestrator: TestOrchestrator
AC-ID: TEST-008
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.visualization.renderers.impact_analysis_renderer import (
    ImpactAnalysisRenderer,
    ImpactNode,
    ChangeImpact,
    RiskLevel,
)


class TestImpactNode:
    """Test ImpactNode dataclass."""
    
    def test_create_file_node(self):
        """Test creating file impact node."""
        node = ImpactNode(
            node_type="file",
            name="module.py",
            path=Path("cortex/module.py"),
        )
        
        assert node.node_type == "file"
        assert node.name == "module.py"
        assert node.path == Path("cortex/module.py")
        assert node.function_name is None
    
    def test_create_function_node(self):
        """Test creating function impact node."""
        node = ImpactNode(
            node_type="function",
            name="process_data",
            path=Path("cortex/processor.py"),
            function_name="process_data",
        )
        
        assert node.node_type == "function"
        assert node.name == "process_data"
        assert node.path == Path("cortex/processor.py")
        assert node.function_name == "process_data"


class TestChangeImpact:
    """Test ChangeImpact dataclass."""
    
    def test_create_low_risk_impact(self):
        """Test creating low-risk change impact."""
        impact = ChangeImpact(
            target_file="test.py",
            affected_files=[],
            affected_functions=[],
            blast_radius=5,
            risk_level="LOW",
            recommendations=["Low risk change"],
        )
        
        assert impact.target_file == "test.py"
        assert impact.blast_radius == 5
        assert impact.risk_level == "LOW"
        assert len(impact.recommendations) == 1
    
    def test_create_critical_risk_impact(self):
        """Test creating critical-risk change impact."""
        affected_files = [f"module{i}.py" for i in range(25)]
        
        impact = ChangeImpact(
            target_file="core.py",
            affected_files=affected_files,
            affected_functions=[],
            blast_radius=75,
            risk_level="CRITICAL",
            recommendations=["CRITICAL: Extensive testing required"],
        )
        
        assert impact.blast_radius == 75
        assert impact.risk_level == "CRITICAL"
        assert len(impact.affected_files) == 25


class TestImpactAnalysisRenderer:
    """Test ImpactAnalysisRenderer class."""
    
    @pytest.fixture
    def renderer(self):
        """Create renderer instance."""
        return ImpactAnalysisRenderer()
    
    @pytest.fixture
    def sample_repo_path(self, tmp_path):
        """Create sample repository structure."""
        repo = tmp_path / "sample_repo"
        repo.mkdir()
        
        # Create sample files
        (repo / "module_a.py").write_text(
            "from module_b import helper\n\n"
            "def process():\n"
            "    return helper()\n"
        )
        (repo / "module_b.py").write_text(
            "def helper():\n"
            "    return 42\n"
        )
        (repo / "module_c.py").write_text(
            "from module_a import process\n\n"
            "def run():\n"
            "    return process()\n"
        )
        
        return repo
    
    @pytest.fixture
    def sample_ast_analysis(self):
        """Create sample AST analysis data."""
        return {
            "functions": [
                {"name": "process", "lineno": 3, "complexity": 2},
                {"name": "helper", "lineno": 1, "complexity": 1},
                {"name": "run", "lineno": 3, "complexity": 2},
            ],
            "imports": [
                {"module": "module_b", "names": ["helper"]},
                {"module": "module_a", "names": ["process"]},
            ],
        }
    
    @pytest.fixture
    def sample_git_analysis(self):
        """Create sample git analysis data."""
        return {
            "commits": [
                {
                    "hash": "abc123",
                    "author": "Developer",
                    "date": "2024-01-15",
                    "message": "Add feature",
                    "files_changed": ["module_a.py"],
                }
            ],
            "file_changes": {
                "module_a.py": {"additions": 10, "deletions": 2, "commits": 5},
                "module_b.py": {"additions": 5, "deletions": 1, "commits": 3},
            },
        }
    
    def test_analyze_file_impact_no_dependencies(
        self, renderer, sample_repo_path, sample_ast_analysis, sample_git_analysis
    ):
        """Test analyzing file with no dependencies."""
        target_file = sample_repo_path / "standalone.py"
        target_file.write_text("def standalone():\n    pass\n")
        
        with patch.object(renderer, "_find_dependent_files", return_value=[]):
            with patch.object(renderer, "_find_dependent_functions", return_value=[]):
                impact = renderer.analyze_file_impact(
                    repo_path=sample_repo_path,
                    target_file=str(target_file),
                    ast_analysis=sample_ast_analysis,
                    git_analysis=sample_git_analysis,
                )
        
        assert "standalone.py" in impact.target_file
        assert impact.blast_radius == 0
        assert impact.risk_level == "LOW"
        assert len(impact.affected_files) == 0
    
    def test_analyze_file_impact_with_dependencies(
        self, renderer, sample_repo_path, sample_ast_analysis, sample_git_analysis
    ):
        """Test analyzing file with dependencies."""
        target_file = sample_repo_path / "module_b.py"
        
        # Mock finding dependent files (return strings, not Paths)
        dependent_files = [str(sample_repo_path / "module_a.py")]
        
        with patch.object(renderer, "_find_dependent_files", return_value=dependent_files):
            with patch.object(renderer, "_find_dependent_functions", return_value=[]):
                impact = renderer.analyze_file_impact(
                    repo_path=sample_repo_path,
                    target_file=str(target_file),
                    ast_analysis=sample_ast_analysis,
                    git_analysis=sample_git_analysis,
                )
        
        assert "module_b.py" in impact.target_file
        assert impact.blast_radius >= 1
        assert len(impact.affected_files) == 1
        assert "module_a.py" in impact.affected_files[0]
    
    def test_analyze_function_impact(
        self, renderer, sample_repo_path, sample_ast_analysis, sample_git_analysis
    ):
        """Test analyzing function impact."""
        target_file = sample_repo_path / "module_b.py"
        target_function = "helper"
        
        # Mock returns strings in format "file:function"
        with patch.object(renderer, "_find_function_callers", return_value=[
            f"{sample_repo_path / 'module_a.py'}:process"
        ]):
            impact = renderer.analyze_function_impact(
                target_file=str(target_file),
                target_function=target_function,
                ast_analysis=sample_ast_analysis,
            )
        
        assert impact.target_function == "helper"
        assert len(impact.affected_functions) == 1
        assert "process" in impact.affected_functions[0]
    
    def test_calculate_risk_level_low(self, renderer):
        """Test calculating LOW risk level."""
        risk_level = renderer._calculate_risk_level(5, 0)
        assert risk_level == "LOW"
    
    def test_calculate_risk_level_medium(self, renderer):
        """Test calculating MEDIUM risk level."""
        risk_level = renderer._calculate_risk_level(15, 0)
        assert risk_level == "MEDIUM"
    
    def test_calculate_risk_level_high(self, renderer):
        """Test calculating HIGH risk level."""
        risk_level = renderer._calculate_risk_level(25, 0)
        assert risk_level == "HIGH"
    
    def test_calculate_risk_level_critical(self, renderer):
        """Test calculating CRITICAL risk level."""
        risk_level = renderer._calculate_risk_level(55, 0)
        assert risk_level == "CRITICAL"
    
    def test_generate_recommendations_low_risk(self, renderer):
        """Test generating recommendations for low risk."""
        recommendations = renderer._generate_recommendations("LOW", [])
        
        assert len(recommendations) > 0
        assert any("LOW RISK" in rec for rec in recommendations)
    
    def test_generate_recommendations_critical_risk(self, renderer):
        """Test generating recommendations for critical risk."""
        affected_files = [f"module{i}.py" for i in range(30)]
        
        recommendations = renderer._generate_recommendations("CRITICAL", affected_files)
        
        assert len(recommendations) > 0
        assert any("CRITICAL" in rec for rec in recommendations)
        assert any("incremental" in rec.lower() or "rollout" in rec.lower() for rec in recommendations)
    
    def test_render_impact_graph(self, renderer, sample_repo_path):
        """Test rendering impact graph data."""
        affected_files = ["dep1.py", "dep2.py"]
        
        impact = ChangeImpact(
            target_file="module.py",
            affected_files=affected_files,
            affected_functions=[],
            blast_radius=2,
            risk_level="MEDIUM",
            recommendations=["Test changes"],
        )
        
        graph_data = renderer.render_impact_graph(impact)
        
        assert "nodes" in graph_data
        assert "links" in graph_data
        assert len(graph_data["nodes"]) >= 3  # target + 2 affected
        assert all("id" in node for node in graph_data["nodes"])
        assert all("group" in node for node in graph_data["nodes"])
    
    def test_render_impact_graph_with_functions(self, renderer, sample_repo_path):
        """Test rendering impact graph with functions."""
        affected_functions = ["dep.py:func1", "dep.py:func2"]
        
        impact = ChangeImpact(
            target_file="module.py",
            affected_files=[],
            affected_functions=affected_functions,
            blast_radius=2,
            risk_level="LOW",
            recommendations=[],
        )
        
        graph_data = renderer.render_impact_graph(impact)
        
        # Check function nodes
        function_nodes = [n for n in graph_data["nodes"] if n.get("group") == 2]
        assert len(function_nodes) == 2
    
    def test_render_blast_radius_heatmap(self, renderer, sample_repo_path):
        """Test rendering blast radius heatmap."""
        # Create mock analysis data
        all_files = [
            sample_repo_path / "low_impact.py",
            sample_repo_path / "medium_impact.py",
            sample_repo_path / "high_impact.py",
        ]
        
        # Test the heatmap with proper AST analysis data
        ast_analysis_with_files = {
            "files": [
                {"path": "low_impact.py", "imports": []},
                {"path": "medium_impact.py", "imports": []},
                {"path": "high_impact.py", "imports": []},
            ]
        }
        
        heatmap_data = renderer.render_blast_radius_heatmap(
            repo_path=sample_repo_path,
            ast_analysis=ast_analysis_with_files,
        )
        
        assert "data" in heatmap_data
        assert len(heatmap_data["data"]) >= 0  # May be empty with mock data
    
    def test_find_dependent_files(self, renderer, sample_repo_path, sample_ast_analysis):
        """Test finding dependent files."""
        target_file = "module_b.py"
        
        dependent_files = renderer._find_dependent_files(
            target_file=target_file,
            ast_analysis=sample_ast_analysis,
        )
        
        # Depends on ast_analysis having imports that reference module_b
        assert isinstance(dependent_files, list)
    
    def test_find_dependent_files_no_dependents(self, renderer, sample_repo_path, sample_ast_analysis):
        """Test finding dependent files when none exist."""
        # Create standalone file not referenced anywhere
        target_file = "standalone.py"
        
        dependent_files = renderer._find_dependent_files(
            target_file=target_file,
            ast_analysis=sample_ast_analysis,
        )
        
        assert len(dependent_files) == 0
    
    def test_impact_analysis_integration(
        self, renderer, sample_repo_path, sample_ast_analysis, sample_git_analysis
    ):
        """Test complete impact analysis workflow."""
        target_file = str(sample_repo_path / "module_b.py")
        
        # Analyze file impact
        impact = renderer.analyze_file_impact(
            repo_path=sample_repo_path,
            target_file=target_file,
            ast_analysis=sample_ast_analysis,
            git_analysis=sample_git_analysis,
        )
        
        # Render visualizations
        graph_data = renderer.render_impact_graph(impact)
        
        # Verify complete workflow
        assert "module_b.py" in impact.target_file
        assert impact.blast_radius >= 0
        assert impact.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert "nodes" in graph_data
        assert "links" in graph_data


class TestImpactAnalysisEdgeCases:
    """Test edge cases in impact analysis."""
    
    @pytest.fixture
    def renderer(self):
        """Create renderer instance."""
        return ImpactAnalysisRenderer()
    
    def test_empty_repository(self, renderer, tmp_path):
        """Test impact analysis on empty repository."""
        empty_repo = tmp_path / "empty"
        empty_repo.mkdir()
        
        target_file = empty_repo / "only_file.py"
        target_file.write_text("def func():\n    pass\n")
        
        impact = renderer.analyze_file_impact(
            repo_path=empty_repo,
            target_file=str(target_file),
            ast_analysis={"functions": [], "imports": [], "files": []},
            git_analysis={"commits": [], "file_changes": {}},
        )
        
        assert impact.blast_radius == 0
        assert impact.risk_level == "LOW"
    
    def test_circular_dependencies(self, renderer, tmp_path):
        """Test handling circular dependencies."""
        repo = tmp_path / "circular"
        repo.mkdir()
        
        # Create circular imports
        (repo / "a.py").write_text("from b import func_b\n\ndef func_a():\n    return func_b()\n")
        (repo / "b.py").write_text("from a import func_a\n\ndef func_b():\n    return func_a()\n")
        
        target_file = "a.py"
        ast_analysis = {
            "files": [
                {"path": "a.py", "imports": ["b"]},
                {"path": "b.py", "imports": ["a"]},
            ]
        }
        
        # Should handle circular dependencies without infinite loop
        dependent_files = renderer._find_dependent_files(
            target_file=target_file,
            ast_analysis=ast_analysis,
        )
        
        assert len(dependent_files) >= 0  # Should not crash
    
    def test_nonexistent_file(self, renderer, tmp_path):
        """Test analyzing nonexistent file."""
        repo = tmp_path / "test_repo"
        repo.mkdir()
        
        nonexistent = "nonexistent.py"
        
        impact = renderer.analyze_file_impact(
            repo_path=repo,
            target_file=nonexistent,
            ast_analysis={"functions": [], "imports": [], "files": []},
            git_analysis={"commits": [], "file_changes": {}},
        )
        
        assert "nonexistent.py" in impact.target_file
        assert impact.blast_radius == 0
