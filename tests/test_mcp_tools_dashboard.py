# AC_START: AC-PHASE59-S4-001
# Tests for MCP Tools & Dashboard (Phase 59, Stage 4)
# Purpose: Validate MCP tool exposure and dashboard functionality

import pytest
import json
from typing import Dict, Any
from cortex.lens.ml_patterns.mcp_tools import (
    PatternSimilarityTool,
    RepositoryClusteringTool,
)


class TestPatternSimilarityTool:
    """Test suite for pattern similarity MCP tool."""
    
    def test_initialize_tool(self):
        """T1: Initialize pattern similarity tool."""
        tool = PatternSimilarityTool()
        
        assert tool is not None
        assert tool.name == "cortex_pattern_similarity"
    
    def test_get_tool_schema(self):
        """T2: Retrieve tool schema for MCP registration."""
        tool = PatternSimilarityTool()
        schema = tool.get_schema()
        
        assert "name" in schema
        assert "description" in schema
        assert "inputSchema" in schema
        assert schema["name"] == "cortex_pattern_similarity"
    
    def test_analyze_patterns(self):
        """T3: Analyze similarity between two patterns."""
        tool = PatternSimilarityTool()
        
        pattern1 = {
            "pattern_type": "architecture",
            "lines_of_code": 1500,
            "cyclomatic_complexity": 8.5,
            "modularity_score": 0.78,
            "coupling_score": 0.45,
            "cohesion_score": 0.82,
        }
        
        pattern2 = {
            "pattern_type": "architecture",
            "lines_of_code": 1510,
            "cyclomatic_complexity": 8.6,
            "modularity_score": 0.77,
            "coupling_score": 0.46,
            "cohesion_score": 0.81,
        }
        
        result = tool.analyze_patterns(pattern1, pattern2)
        
        assert "similarity" in result
        assert 0 <= result["similarity"] <= 1
        assert result["similarity"] > 0.8
    
    def test_batch_similarity_analysis(self):
        """T4: Analyze similarities for batch of patterns."""
        tool = PatternSimilarityTool()
        
        patterns = [
            {
                "id": "p1",
                "pattern_type": "architecture",
                "lines_of_code": 1500,
                "cyclomatic_complexity": 8.5,
                "modularity_score": 0.78,
                "coupling_score": 0.45,
                "cohesion_score": 0.82,
            },
            {
                "id": "p2",
                "pattern_type": "design",
                "lines_of_code": 2000,
                "cyclomatic_complexity": 10.0,
                "modularity_score": 0.80,
                "coupling_score": 0.40,
                "cohesion_score": 0.85,
            },
        ]
        
        result = tool.batch_analyze(patterns)
        
        assert "results" in result
        assert len(result["results"]) > 0
    
    def test_tool_execution_result(self):
        """T5: Verify tool returns properly formatted result."""
        tool = PatternSimilarityTool()
        
        pattern1 = {
            "pattern_type": "architecture",
            "lines_of_code": 1500,
            "cyclomatic_complexity": 8.5,
            "modularity_score": 0.78,
            "coupling_score": 0.45,
            "cohesion_score": 0.82,
        }
        
        pattern2 = {
            "pattern_type": "architecture",
            "lines_of_code": 1600,
            "cyclomatic_complexity": 9.0,
            "modularity_score": 0.75,
            "coupling_score": 0.50,
            "cohesion_score": 0.80,
        }
        
        result = tool.analyze_patterns(pattern1, pattern2)
        
        assert isinstance(result, dict)
        assert "similarity" in result
        assert "embedding1_dim" in result or "details" in result


class TestRepositoryClusteringTool:
    """Test suite for repository clustering MCP tool."""
    
    def test_initialize_clustering_tool(self):
        """T6: Initialize repository clustering tool."""
        tool = RepositoryClusteringTool()
        
        assert tool is not None
        assert tool.name == "cortex_repository_clustering"
    
    def test_cluster_repositories(self):
        """T7: Cluster repositories based on fingerprints."""
        tool = RepositoryClusteringTool()
        
        repositories = {
            "repo1": {
                "components": ["api", "core"],
                "avg_complexity": 0.65,
                "total_size": 3500,
                "avg_modularity": 0.82,
            },
            "repo2": {
                "components": ["api", "core"],
                "avg_complexity": 0.66,
                "total_size": 3600,
                "avg_modularity": 0.81,
            },
            "repo3": {
                "components": ["monolith"],
                "avg_complexity": 0.85,
                "total_size": 50000,
                "avg_modularity": 0.30,
            },
        }
        
        result = tool.cluster_repositories(repositories, n_clusters=2)
        
        assert "clusters" in result
        assert len(result["clusters"]) == 2
        assert "metadata" in result
    
    def test_clustering_tool_schema(self):
        """T8: Retrieve clustering tool schema."""
        tool = RepositoryClusteringTool()
        schema = tool.get_schema()
        
        assert "name" in schema
        assert schema["name"] == "cortex_repository_clustering"
        assert "description" in schema
        assert "inputSchema" in schema


class TestDashboardIntegration:
    """Test suite for dashboard data export."""
    
    def test_generate_dashboard_data(self):
        """T9: Generate data for visualization dashboard."""
        from cortex.lens.ml_patterns.dashboard_generator import DashboardGenerator
        
        generator = DashboardGenerator()
        
        fingerprints = {
            "repo1": {
                "repository_id": "repo1",
                "total_complexity": 0.65,
                "total_modularity": 0.82,
                "component_count": 2,
            },
            "repo2": {
                "repository_id": "repo2",
                "total_complexity": 0.70,
                "total_modularity": 0.78,
                "component_count": 3,
            },
        }
        
        clusters = {
            "0": ["repo1"],
            "1": ["repo2"],
        }
        
        dashboard_data = generator.generate(fingerprints, clusters)
        
        assert "repos" in dashboard_data
        assert "clusters" in dashboard_data
        assert len(dashboard_data["repos"]) == 2
    
    def test_export_as_json(self):
        """T10: Export dashboard data as JSON."""
        from cortex.lens.ml_patterns.dashboard_generator import DashboardGenerator
        
        generator = DashboardGenerator()
        
        dashboard_data = {
            "repos": [
                {"id": "repo1", "complexity": 0.65, "modularity": 0.82},
            ],
            "clusters": [0],
        }
        
        json_str = generator.to_json(dashboard_data)
        
        assert isinstance(json_str, str)
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert "repos" in parsed
        assert "clusters" in parsed


# AC_COMPLETE: AC-PHASE59-S4-001 ✅ 10/10 tests
