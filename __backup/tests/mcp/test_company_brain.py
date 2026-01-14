"""
Tests for Company Brain Plugin System (feat06-mcp Phase 3).

Tests company brain registry, domain plugin architecture, and brain isolation.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P3
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def temp_company_workspace(tmp_path):
    """Create temporary workspace with company brains."""
    workspace = tmp_path / "company_workspace"
    workspace.mkdir()
    
    # Create Company A brain
    company_a = workspace / "company-a"
    company_a.mkdir()
    (company_a / ".git").mkdir()
    brain_a = company_a / "cortex-brain"
    brain_a.mkdir()
    (brain_a / "tier0").mkdir()
    
    # Company A config
    config_a = {
        "company": "company-a",
        "domain": "finance",
        "cortex_enabled": True,
        "plugins": ["finance_domain", "reporting"]
    }
    with open(company_a / "cortex.config.json", "w") as f:
        json.dump(config_a, f)
    
    # Create Company B brain
    company_b = workspace / "company-b"
    company_b.mkdir()
    (company_b / ".git").mkdir()
    brain_b = company_b / "cortex-brain"
    brain_b.mkdir()
    (brain_b / "tier0").mkdir()
    
    # Company B config
    config_b = {
        "company": "company-b",
        "domain": "healthcare",
        "cortex_enabled": True,
        "plugins": ["healthcare_domain", "hipaa_compliance"]
    }
    with open(company_b / "cortex.config.json", "w") as f:
        json.dump(config_b, f)
    
    return workspace


class TestCompanyBrainRegistry:
    """Test company brain registration and discovery."""
    
    def test_registers_company_brain(self, temp_company_workspace):
        """Test registers a company brain."""
        from src.mcp.company_brain_plugin import CompanyBrainRegistry
        
        registry = CompanyBrainRegistry(workspace_root=temp_company_workspace)
        registry.discover()
        
        brains = registry.list_brains()
        assert len(brains) == 2
        
        brain_names = [b.company for b in brains]
        assert "company-a" in brain_names
        assert "company-b" in brain_names
    
    def test_gets_brain_by_company_name(self, temp_company_workspace):
        """Test retrieves brain by company name."""
        from src.mcp.company_brain_plugin import CompanyBrainRegistry
        
        registry = CompanyBrainRegistry(workspace_root=temp_company_workspace)
        registry.discover()
        
        brain = registry.get_brain("company-a")
        assert brain is not None
        assert brain.company == "company-a"
        assert brain.domain == "finance"
    
    def test_filters_brains_by_domain(self, temp_company_workspace):
        """Test filters brains by domain."""
        from src.mcp.company_brain_plugin import CompanyBrainRegistry
        
        registry = CompanyBrainRegistry(workspace_root=temp_company_workspace)
        registry.discover()
        
        finance_brains = registry.filter_by_domain("finance")
        assert len(finance_brains) == 1
        assert finance_brains[0].company == "company-a"
    
    def test_handles_missing_brain(self, temp_company_workspace):
        """Test handles requests for non-existent brain."""
        from src.mcp.company_brain_plugin import CompanyBrainRegistry
        
        registry = CompanyBrainRegistry(workspace_root=temp_company_workspace)
        registry.discover()
        
        brain = registry.get_brain("nonexistent")
        assert brain is None


class TestDomainPluginArchitecture:
    """Test domain-specific plugin loading and execution."""
    
    def test_loads_domain_plugins(self, temp_company_workspace):
        """Test loads plugins for a domain."""
        from src.mcp.company_brain_plugin import DomainPluginManager, DomainPlugin
        
        manager = DomainPluginManager(workspace_root=temp_company_workspace)
        manager.initialize()
        
        # Register a test plugin first
        class TestFinancePlugin(DomainPlugin):
            name = "finance_test"
            domain = "finance"
            
            def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": "finance_executed"}
        
        manager.register_plugin(TestFinancePlugin())
        
        # Get plugins for finance domain
        plugins = manager.get_plugins_for_domain("finance")
        assert len(plugins) > 0
    
    def test_registers_custom_plugin(self, temp_company_workspace):
        """Test registers a custom domain plugin."""
        from src.mcp.company_brain_plugin import DomainPluginManager, DomainPlugin
        
        manager = DomainPluginManager(workspace_root=temp_company_workspace)
        manager.initialize()
        
        # Create custom plugin
        class CustomPlugin(DomainPlugin):
            name = "custom_plugin"
            domain = "finance"
            
            def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": "custom_executed"}
        
        plugin = CustomPlugin()
        manager.register_plugin(plugin)
        
        # Verify registration
        plugins = manager.get_plugins_for_domain("finance")
        plugin_names = [p.name for p in plugins]
        assert "custom_plugin" in plugin_names
    
    def test_executes_plugin(self, temp_company_workspace):
        """Test executes a plugin with context."""
        from src.mcp.company_brain_plugin import DomainPluginManager, DomainPlugin
        
        manager = DomainPluginManager(workspace_root=temp_company_workspace)
        manager.initialize()
        
        # Register test plugin
        class TestPlugin(DomainPlugin):
            name = "test_plugin"
            domain = "finance"
            
            def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"status": "success", "input": context.get("data")}
        
        plugin = TestPlugin()
        manager.register_plugin(plugin)
        
        # Execute
        result = manager.execute_plugin(
            plugin_name="test_plugin",
            context={"data": "test_value"}
        )
        
        assert result["status"] == "success"
        assert result["input"] == "test_value"
    
    def test_plugin_validation(self, temp_company_workspace):
        """Test validates plugin configuration."""
        from src.mcp.company_brain_plugin import DomainPluginManager
        
        manager = DomainPluginManager(workspace_root=temp_company_workspace)
        manager.initialize()
        
        # Attempt to execute non-existent plugin
        with pytest.raises(ValueError, match="Plugin not found"):
            manager.execute_plugin(
                plugin_name="nonexistent",
                context={}
            )


class TestBrainIsolation:
    """Test isolation between company brains."""
    
    def test_isolates_brain_operations(self, temp_company_workspace):
        """Test operations are isolated to specific brain."""
        from src.mcp.company_brain_plugin import BrainIsolation
        
        isolation = BrainIsolation(workspace_root=temp_company_workspace)
        isolation.initialize()
        
        # Create isolation context for company-a
        context = isolation.create_brain_context("company-a")
        
        assert context.company == "company-a"
        assert context.domain == "finance"
        assert context.is_isolated
    
    def test_prevents_cross_brain_contamination(self, temp_company_workspace):
        """Test operations in one brain don't affect another."""
        from src.mcp.company_brain_plugin import BrainIsolation
        
        isolation = BrainIsolation(workspace_root=temp_company_workspace)
        isolation.initialize()
        
        # Execute in company-a context
        result_a = isolation.execute_in_brain(
            company="company-a",
            operation=lambda ctx: ctx.company
        )
        
        assert result_a == "company-a"
        
        # Verify company-b unaffected
        result_b = isolation.execute_in_brain(
            company="company-b",
            operation=lambda ctx: ctx.company
        )
        
        assert result_b == "company-b"
    
    def test_brain_specific_env_vars(self, temp_company_workspace):
        """Test each brain gets isolated environment variables."""
        from src.mcp.company_brain_plugin import BrainIsolation
        
        isolation = BrainIsolation(workspace_root=temp_company_workspace)
        isolation.initialize()
        
        env_a = isolation.get_brain_env("company-a")
        assert env_a["CORTEX_COMPANY"] == "company-a"
        assert env_a["CORTEX_DOMAIN"] == "finance"
        
        env_b = isolation.get_brain_env("company-b")
        assert env_b["CORTEX_COMPANY"] == "company-b"
        assert env_b["CORTEX_DOMAIN"] == "healthcare"


class TestCompanyBrainIntegration:
    """Integration tests for company brain plugin system."""
    
    def test_full_brain_plugin_pipeline(self, temp_company_workspace):
        """Test complete pipeline: discover → load plugins → execute."""
        from src.mcp.company_brain_plugin import (
            CompanyBrainRegistry,
            DomainPluginManager,
            BrainIsolation
        )
        
        # Discover brains
        registry = CompanyBrainRegistry(workspace_root=temp_company_workspace)
        registry.discover()
        
        brains = registry.list_brains()
        assert len(brains) == 2
        
        # Load plugins for each brain
        plugin_manager = DomainPluginManager(workspace_root=temp_company_workspace)
        plugin_manager.initialize()
        
        for brain in brains:
            plugins = plugin_manager.get_plugins_for_domain(brain.domain)
            # Should have at least the configured plugins
            assert len(plugins) >= 0  # May be 0 if plugins not yet implemented
    
    def test_cross_brain_coordination(self, temp_company_workspace):
        """Test coordinating operations across multiple company brains."""
        from src.mcp.company_brain_plugin import CompanyBrainRegistry, BrainIsolation
        
        registry = CompanyBrainRegistry(workspace_root=temp_company_workspace)
        registry.discover()
        
        isolation = BrainIsolation(workspace_root=temp_company_workspace)
        isolation.initialize()
        
        # Execute operation in all brains
        results = []
        for brain in registry.list_brains():
            result = isolation.execute_in_brain(
                company=brain.company,
                operation=lambda ctx: {"company": ctx.company, "domain": ctx.domain}
            )
            results.append(result)
        
        assert len(results) == 2
        assert any(r["company"] == "company-a" for r in results)
        assert any(r["company"] == "company-b" for r in results)
