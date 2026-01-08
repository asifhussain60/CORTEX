"""
Integration tests for complete MCP system (feat06-mcp Phase 4).

Tests MCP protocol compliance and multi-repo integration.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P4
"""

import pytest
import json
from pathlib import Path


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance across the stack."""
    
    def test_mcp_server_initialization(self):
        """Test MCP server initializes correctly."""
        from src.mcp.mcp_server import MCPServer
        
        server = MCPServer()
        assert server is not None
        assert server.capability_registry is not None
    
    def test_tools_list_returns_valid_format(self):
        """Test tools/list returns valid MCP format."""
        from src.mcp.mcp_server import MCPServer
        
        server = MCPServer()
        result = server.handle_tools_list(None)
        
        assert "tools" in result
        assert isinstance(result["tools"], list)
    
    def test_jsonrpc_message_formats(self):
        """Test JSON-RPC message format compliance."""
        from src.mcp.jsonrpc_server import JSONRPCRequest, JSONRPCResponse, JSONRPCError
        
        # Test request format
        request = JSONRPCRequest(method="test", params={}, id=1)
        req_dict = request.to_dict()
        assert req_dict["jsonrpc"] == "2.0"
        assert req_dict["method"] == "test"
        assert "id" in req_dict
        
        # Test response format
        response = JSONRPCResponse(result={"status": "ok"}, id=1)
        resp_dict = response.to_dict()
        assert resp_dict["jsonrpc"] == "2.0"
        assert "result" in resp_dict
        
        # Test error format
        error = JSONRPCError(code=-32601, message="Not found")
        error_response = JSONRPCResponse(error=error, id=1)
        error_dict = error_response.to_dict()
        assert error_dict["jsonrpc"] == "2.0"
        assert "error" in error_dict
        assert error_dict["error"]["code"] == -32601


class TestMultiRepoIntegration:
    """Test multi-repo operations integration."""
    
    def test_discover_multiple_repos(self, tmp_path):
        """Test discovering multiple repositories."""
        from src.mcp.multi_repo_manager import MultiRepoManager
        
        # Create test repos
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        for i in range(3):
            repo = workspace / f"repo{i}"
            repo.mkdir()
            (repo / ".git").mkdir()
            if i < 2:  # Make 2 CORTEX-enabled
                (repo / "cortex-brain").mkdir()
        
        # Test discovery
        manager = MultiRepoManager(workspace_root=workspace)
        manager.initialize()
        
        all_repos = manager.list_repos()
        assert len(all_repos) == 3
        
        cortex_repos = manager.list_repos(cortex_enabled_only=True)
        assert len(cortex_repos) == 2
    
    def test_cross_repo_operations(self, tmp_path):
        """Test executing operations across repositories."""
        from src.mcp.multi_repo_manager import MultiRepoManager
        
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        for i in range(2):
            repo = workspace / f"repo{i}"
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / "cortex-brain").mkdir()
        
        manager = MultiRepoManager(workspace_root=workspace)
        manager.initialize()
        
        # Execute status check across repos
        results = manager.execute_across_repos(
            operation="status_check",
            cortex_enabled_only=True
        )
        
        assert len(results) == 2
        for result in results:
            assert "repo" in result
            assert result["status"] in ["success", "error"]


class TestCompanyBrainIntegration:
    """Test company brain system integration."""
    
    def test_discover_company_brains(self, tmp_path):
        """Test discovering company brains."""
        from src.mcp.company_brain_plugin import CompanyBrainRegistry
        
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        # Create company repos
        for company in ["acme-corp", "widget-co"]:
            repo = workspace / company
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / "cortex-brain").mkdir()
            
            config = {
                "company": company,
                "domain": "manufacturing",
                "cortex_enabled": True
            }
            with open(repo / "cortex.config.json", "w") as f:
                json.dump(config, f)
        
        registry = CompanyBrainRegistry(workspace_root=workspace)
        registry.discover()
        
        brains = registry.list_brains()
        assert len(brains) == 2
        
        brain_names = [b.company for b in brains]
        assert "acme-corp" in brain_names
        assert "widget-co" in brain_names
    
    def test_domain_plugin_execution(self):
        """Test executing domain plugins."""
        from src.mcp.company_brain_plugin import DomainPluginManager, DomainPlugin
        from typing import Dict, Any
        
        manager = DomainPluginManager()
        manager.initialize()
        
        # Register test plugin
        class TestDomainPlugin(DomainPlugin):
            name = "test_plugin"
            domain = "testing"
            
            def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "status": "executed",
                    "input": context.get("data")
                }
        
        plugin = TestDomainPlugin()
        manager.register_plugin(plugin)
        
        # Execute
        result = manager.execute_plugin(
            plugin_name="test_plugin",
            context={"data": "test_value"}
        )
        
        assert result["status"] == "executed"
        assert result["input"] == "test_value"
    
    def test_brain_isolation(self, tmp_path):
        """Test brain isolation between companies."""
        from src.mcp.company_brain_plugin import BrainIsolation, CompanyBrainRegistry
        
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        # Create 2 company brains
        for company in ["company-a", "company-b"]:
            repo = workspace / company
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / "cortex-brain").mkdir()
            
            config = {
                "company": company,
                "domain": "test",
                "cortex_enabled": True
            }
            with open(repo / "cortex.config.json", "w") as f:
                json.dump(config, f)
        
        isolation = BrainIsolation(workspace_root=workspace)
        isolation.initialize()
        
        # Execute in isolated contexts
        result_a = isolation.execute_in_brain(
            company="company-a",
            operation=lambda ctx: ctx.company
        )
        
        result_b = isolation.execute_in_brain(
            company="company-b",
            operation=lambda ctx: ctx.company
        )
        
        assert result_a == "company-a"
        assert result_b == "company-b"


class TestEndToEndScenarios:
    """End-to-end scenario tests."""
    
    def test_full_mcp_stack(self):
        """Test complete MCP stack from server to backend."""
        from src.mcp.mcp_server import MCPServer
        from src.mcp.jsonrpc_server import JSONRPCServer
        
        # Create server
        mcp_server = MCPServer()
        jsonrpc_server = JSONRPCServer()
        
        # Register MCP methods
        jsonrpc_server.register_method("tools/list", mcp_server.handle_tools_list)
        jsonrpc_server.register_method("tools/call", mcp_server.handle_tools_call)
        
        # Verify registration
        assert "tools/list" in jsonrpc_server.methods
        assert "tools/call" in jsonrpc_server.methods
    
    def test_multi_layer_coordination(self, tmp_path):
        """Test coordination across all layers."""
        from src.mcp.multi_repo_manager import MultiRepoManager
        from src.mcp.company_brain_plugin import CompanyBrainRegistry, BrainIsolation
        
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        # Create multi-layer structure
        company = workspace / "test-company"
        company.mkdir()
        (company / ".git").mkdir()
        (company / "cortex-brain").mkdir()
        
        config = {
            "company": "test-company",
            "domain": "testing",
            "cortex_enabled": True
        }
        with open(company / "cortex.config.json", "w") as f:
            json.dump(config, f)
        
        # Layer 1: Multi-repo discovery
        repo_manager = MultiRepoManager(workspace_root=workspace)
        repo_manager.initialize()
        assert len(repo_manager.list_repos()) == 1
        
        # Layer 2: Company brain discovery
        brain_registry = CompanyBrainRegistry(workspace_root=workspace)
        brain_registry.discover()
        assert len(brain_registry.list_brains()) == 1
        
        # Layer 3: Isolated execution
        isolation = BrainIsolation(workspace_root=workspace)
        isolation.initialize()
        result = isolation.execute_in_brain(
            company="test-company",
            operation=lambda ctx: {"company": ctx.company, "domain": ctx.domain}
        )
        assert result["company"] == "test-company"
        assert result["domain"] == "testing"


class TestPerformanceAndScaling:
    """Test performance and scaling characteristics."""
    
    def test_handles_multiple_repos_efficiently(self, tmp_path):
        """Test efficient handling of multiple repositories."""
        from src.mcp.multi_repo_manager import MultiRepoManager
        
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        # Create 10 repos
        for i in range(10):
            repo = workspace / f"repo{i}"
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / "cortex-brain").mkdir()
        
        manager = MultiRepoManager(workspace_root=workspace)
        manager.initialize()
        
        repos = manager.list_repos()
        assert len(repos) == 10
    
    def test_capability_registry_search_performance(self):
        """Test capability registry list performance."""
        from src.mcp.capability_registry import CapabilityRegistry
        
        registry = CapabilityRegistry()
        
        # Registry should handle list operations efficiently
        results = registry.list_all()
        assert isinstance(results, list)
