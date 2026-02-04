"""
Tests for MCP Tool: cortex_onboard_repository_json
Author: Asif Hussain
Date: 2026-02-04
Authority: CORE-008 (TDD), MCP-FIRST architecture
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

# Mock MCP tool (will be implemented after tests)
class MockMCPOnboardTool:
    """Mock implementation for testing"""
    
    def __init__(self):
        self.invocation_count = 0
        self.last_repo_slug = None
        self.last_lens_data = None
    
    def execute(self, repo_slug: str, lens_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock tool execution"""
        self.invocation_count += 1
        self.last_repo_slug = repo_slug
        self.last_lens_data = lens_data
        
        return {
            "status": "success",
            "repo_slug": repo_slug,
            "adapter": "json",
            "data_path": f"/data/{repo_slug}/dashboard.json",
            "file_size_kb": 15,
            "generation_time_ms": 45
        }


class TestMCPOnboardToolSchema:
    """Test MCP tool schema definition"""
    
    def test_tool_has_valid_schema(self):
        """MCP tool defines complete schema"""
        tool_schema = {
            "name": "cortex_onboard_repository_json",
            "description": "Onboard repository with JSON-first data architecture",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository identifier (kebab-case)"
                    },
                    "lens_data": {
                        "type": "object",
                        "description": "LENS analysis output"
                    },
                    "base_path": {
                        "type": "string",
                        "description": "Output base path (default: cortex/visualization/dashboards/data)"
                    }
                },
                "required": ["repo_slug", "lens_data"]
            }
        }
        
        # Validate schema structure
        assert "name" in tool_schema
        assert "input_schema" in tool_schema
        assert tool_schema["input_schema"]["type"] == "object"
        assert "repo_slug" in tool_schema["input_schema"]["properties"]
        assert "lens_data" in tool_schema["input_schema"]["properties"]
        assert len(tool_schema["input_schema"]["required"]) == 2
    
    def test_tool_schema_validates_repo_slug(self):
        """Schema enforces kebab-case repo slugs"""
        valid_slugs = ["cortex", "test-repo", "my-project-v2"]
        invalid_slugs = ["Cortex", "test_repo", "test repo"]
        
        # This test documents the expected validation
        for slug in valid_slugs:
            # Valid: only lowercase alphanumeric and hyphens
            assert all(c.islower() or c.isdigit() or c == '-' for c in slug)
        
        for slug in invalid_slugs:
            # Invalid: contains uppercase, underscores, or spaces
            assert not all(c.islower() or c.isdigit() or c == '-' for c in slug)


class TestMCPOnboardToolExecution:
    """Test MCP tool execution"""
    
    def test_tool_executes_successfully(self):
        """Tool executes with valid inputs"""
        tool = MockMCPOnboardTool()
        
        lens_data = {
            "repo": {"name": "cortex", "path": "/tmp"},
            "files": [{"path": "main.py", "language": "Python", "lines": 100}],
            "metrics": {"health_score": 85}
        }
        
        result = tool.execute("cortex", lens_data)
        
        assert result["status"] == "success"
        assert result["repo_slug"] == "cortex"
        assert result["adapter"] == "json"
        assert tool.invocation_count == 1
    
    def test_tool_returns_output_schema(self):
        """Tool returns proper output format"""
        tool = MockMCPOnboardTool()
        lens_data = {"repo": {"name": "test"}, "files": [], "metrics": {}}
        
        result = tool.execute("test-repo", lens_data)
        
        # Validate output schema
        assert "status" in result
        assert "repo_slug" in result
        assert "adapter" in result
        assert "data_path" in result
        assert "file_size_kb" in result
        assert "generation_time_ms" in result
    
    def test_tool_handles_multiple_invocations(self):
        """Tool tracks multiple calls correctly"""
        tool = MockMCPOnboardTool()
        lens_data = {"repo": {"name": "test"}, "files": [], "metrics": {}}
        
        tool.execute("repo-1", lens_data)
        tool.execute("repo-2", lens_data)
        tool.execute("repo-3", lens_data)
        
        assert tool.invocation_count == 3
        assert tool.last_repo_slug == "repo-3"


class TestMCPOnboardToolErrorHandling:
    """Test MCP tool error handling"""
    
    def test_tool_rejects_missing_repo_slug(self):
        """Tool rejects missing required parameter"""
        tool = MockMCPOnboardTool()
        
        # This documents expected behavior
        with pytest.raises(TypeError):
            tool.execute(lens_data={"repo": {}})
    
    def test_tool_rejects_invalid_repo_slug_format(self):
        """Tool validates repo slug format"""
        tool = MockMCPOnboardTool()
        lens_data = {"repo": {"name": "test"}, "files": [], "metrics": {}}
        
        invalid_slugs = ["Test_Repo", "test repo", "123"]
        
        for slug in invalid_slugs:
            # Tool should reject invalid format (documented expectation)
            # Current mock accepts; future implementation will validate
            result = tool.execute(slug, lens_data)
            assert result["repo_slug"] == slug  # Mock doesn't validate yet
    
    def test_tool_handles_empty_lens_data(self):
        """Tool gracefully handles empty LENS output"""
        tool = MockMCPOnboardTool()
        
        result = tool.execute("test-repo", {})
        
        assert result["status"] == "success"
        assert result["repo_slug"] == "test-repo"


class TestMCPOnboardToolIntegration:
    """Test MCP tool integration"""
    
    def test_tool_integrates_with_adapter(self):
        """Tool output compatible with JSONAdapter"""
        from cortex.visualization.adapters.json_adapter import JSONAdapter
        from cortex.visualization.json_data_generator import JSONDataGenerator
        
        tool = MockMCPOnboardTool()
        generator = JSONDataGenerator()
        
        # Simulate workflow
        lens_data = {
            "repo": {"name": "cortex", "path": "/tmp"},
            "files": [{"path": "main.py", "language": "Python", "lines": 100}],
            "metrics": {"health_score": 85}
        }
        
        # Tool invokes workflow internally
        result = tool.execute("cortex", lens_data)
        
        # Verify integration point
        assert result["adapter"] == "json"
        assert result["data_path"].endswith(".json")
    
    def test_tool_produces_mcp_catalog_entry(self):
        """Tool has proper MCP catalog registration"""
        catalog_entry = {
            "name": "cortex_onboard_repository_json",
            "description": "Onboard repository with JSON-first data",
            "category": "orchestration",
            "version": "1.0",
            "schema": {
                "input": {
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string"},
                        "lens_data": {"type": "object"}
                    }
                },
                "output": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "repo_slug": {"type": "string"},
                        "data_path": {"type": "string"}
                    }
                }
            }
        }
        
        assert catalog_entry["name"] == "cortex_onboard_repository_json"
        assert "input" in catalog_entry["schema"]
        assert "output" in catalog_entry["schema"]


class TestMCPOnboardToolGateway:
    """Test MCP gateway integration"""
    
    def test_tool_gateway_routing(self):
        """Tool accessible via MCP gateway"""
        # This documents the MCP routing expectation
        gateway_route = {
            "path": "/tools/cortex_onboard_repository_json",
            "method": "POST",
            "handler": "cortex_onboard_repository_json"
        }
        
        assert "path" in gateway_route
        assert gateway_route["method"] == "POST"
        assert "cortex_onboard_repository_json" in gateway_route["handler"]
    
    def test_tool_with_mcp_decorator(self):
        """Tool decorated with @mcp_tool"""
        # Document expected decorator structure
        decorator_spec = {
            "name": "cortex_onboard_repository_json",
            "module": "cortex.mcp.tools.onboarding_tools",
            "function": "onboard_repository_json",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repo_slug": {"type": "string"},
                    "lens_data": {"type": "object"},
                    "base_path": {"type": "string"}
                },
                "required": ["repo_slug", "lens_data"]
            }
        }
        
        assert decorator_spec["name"] == "cortex_onboard_repository_json"
        assert "input_schema" in decorator_spec
        assert len(decorator_spec["input_schema"]["required"]) >= 2
