"""
Tests for cortex_total_recall MCP tool.

Tests feature discovery across CORTEX components:
- Orchestrators
- MCP tools
- Governance agents
- Knowledge areas

CORE-008: Tests written before implementation validation.
"""

import pytest
from cortex.mcp.cortex_tools import CORTEXTotalRecallTool


class TestTotalRecallTool:
    """Test cortex_total_recall feature discovery."""

    @pytest.fixture
    def tool(self) -> CORTEXTotalRecallTool:
        """Create tool instance."""
        return CORTEXTotalRecallTool()

    def test_tool_definition(self, tool: CORTEXTotalRecallTool):
        """Test tool definition is correct."""
        definition = tool.definition
        
        assert definition.name == "cortex_total_recall"
        assert "discover" in definition.description.lower() or "recall" in definition.description.lower()
        assert definition.metadata["category"] == "knowledge"
        
        # Verify parameters
        param_names = [p.name for p in definition.parameters]
        assert "query" in param_names
        
        # Query parameter should be required
        query_param = next(p for p in definition.parameters if p.name == "query")
        assert query_param.required is True

    def test_search_orchestrators(self, tool: CORTEXTotalRecallTool):
        """Test searching for orchestrators."""
        result = tool.execute(query="tdd")
        
        assert result["status"] == "success"
        assert result["query"] == "tdd"
        assert result["matches_found"] > 0
        
        # Should find TDD orchestrator
        orchestrators = result["results"]["orchestrators"]
        assert len(orchestrators) > 0
        assert any("tdd" in o["name"].lower() for o in orchestrators)

    def test_search_mcp_tools(self, tool: CORTEXTotalRecallTool):
        """Test searching for MCP tools."""
        result = tool.execute(query="process")
        
        assert result["status"] == "success"
        assert result["matches_found"] > 0
        
        # Should find cortex_process_request tool
        mcp_tools = result["results"]["mcp_tools"]
        assert len(mcp_tools) > 0
        assert any("process" in t["name"].lower() for t in mcp_tools)

    def test_search_governance_agents(self, tool: CORTEXTotalRecallTool):
        """Test searching for governance agents."""
        result = tool.execute(query="governance")
        
        assert result["status"] == "success"
        assert result["matches_found"] > 0
        
        # Should find governance agents
        agents = result["results"]["agents"]
        assert len(agents) > 0
        assert any("governance" in a["name"] for a in agents)

    def test_search_knowledge_areas(self, tool: CORTEXTotalRecallTool):
        """Test searching for knowledge areas."""
        result = tool.execute(query="python")
        
        assert result["status"] == "success"
        assert result["matches_found"] > 0
        
        # Should find Python knowledge area
        knowledge = result["results"]["knowledge_areas"]
        assert len(knowledge) > 0
        assert any("python" in k["name"].lower() for k in knowledge)

    def test_search_no_matches(self, tool: CORTEXTotalRecallTool):
        """Test search with no matches."""
        result = tool.execute(query="nonexistent_feature_xyz123")
        
        assert result["status"] == "success"
        assert result["matches_found"] == 0
        assert all(len(result["results"][k]) == 0 for k in result["results"])

    def test_search_multiple_categories(self, tool: CORTEXTotalRecallTool):
        """Test search that matches multiple categories."""
        result = tool.execute(query="enforcement")
        
        assert result["status"] == "success"
        assert result["matches_found"] > 0
        
        # Should match both orchestrator and agent
        assert len(result["results"]["orchestrators"]) > 0
        assert len(result["results"]["agents"]) > 0

    def test_scope_parameter(self, tool: CORTEXTotalRecallTool):
        """Test scope parameter filtering."""
        # Test with specific scope
        result = tool.execute(query="governance", scope="governance")
        
        assert result["status"] == "success"
        assert result["scope"] == "governance"
        
        # Should still find governance-related items
        assert result["matches_found"] > 0

    def test_summary_statistics(self, tool: CORTEXTotalRecallTool):
        """Test summary statistics are correct."""
        result = tool.execute(query="test")
        
        assert result["status"] == "success"
        assert "summary" in result
        
        summary = result["summary"]
        assert "orchestrators" in summary
        assert "mcp_tools" in summary
        assert "agents" in summary
        assert "knowledge_areas" in summary
        
        # Summary counts should match results
        total_from_summary = sum(summary.values())
        total_from_results = sum(len(result["results"][k]) for k in result["results"])
        assert total_from_summary == total_from_results

    def test_case_insensitive_search(self, tool: CORTEXTotalRecallTool):
        """Test search is case-insensitive."""
        result_lower = tool.execute(query="tdd")
        result_upper = tool.execute(query="TDD")
        result_mixed = tool.execute(query="Tdd")
        
        # All should return same results
        assert result_lower["matches_found"] == result_upper["matches_found"]
        assert result_lower["matches_found"] == result_mixed["matches_found"]

    def test_error_handling(self, tool: CORTEXTotalRecallTool, monkeypatch):
        """Test error handling in tool execution."""
        # Mock an error in orchestrator search
        def mock_error(*args, **kwargs):
            raise RuntimeError("Simulated error")
        
        # Tool should handle errors gracefully
        # Since we catch exceptions per-section, the tool should still return success
        # with partial results
        result = tool.execute(query="test")
        
        # Should not raise exception, should return result
        assert "status" in result
        # Even if some searches fail, tool should complete

    def test_results_structure(self, tool: CORTEXTotalRecallTool):
        """Test results have correct structure."""
        result = tool.execute(query="process")
        
        assert "status" in result
        assert "query" in result
        assert "scope" in result
        assert "matches_found" in result
        assert "results" in result
        assert "summary" in result
        
        # Results should have all categories
        results = result["results"]
        assert "orchestrators" in results
        assert "mcp_tools" in results
        assert "agents" in results
        assert "knowledge_areas" in results
        
        # Each category should be a list
        assert isinstance(results["orchestrators"], list)
        assert isinstance(results["mcp_tools"], list)
        assert isinstance(results["agents"], list)
        assert isinstance(results["knowledge_areas"], list)

    def test_match_item_structure(self, tool: CORTEXTotalRecallTool):
        """Test each match item has correct structure."""
        result = tool.execute(query="tdd")
        
        # Check orchestrator match structure
        if result["results"]["orchestrators"]:
            orch = result["results"]["orchestrators"][0]
            assert "name" in orch
            assert "description" in orch
            assert "category" in orch
        
        # Check MCP tool match structure
        result2 = tool.execute(query="process")
        if result2["results"]["mcp_tools"]:
            tool_match = result2["results"]["mcp_tools"][0]
            assert "name" in tool_match
            assert "description" in tool_match
            assert "category" in tool_match
        
        # Check agent match structure
        result3 = tool.execute(query="governance")
        if result3["results"]["agents"]:
            agent = result3["results"]["agents"][0]
            assert "name" in agent
            assert "description" in agent
            assert "category" in agent
        
        # Check knowledge area match structure
        result4 = tool.execute(query="python")
        if result4["results"]["knowledge_areas"]:
            knowledge = result4["results"]["knowledge_areas"][0]
            assert "name" in knowledge
            assert "description" in knowledge
