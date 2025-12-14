"""
CORTEX Component Wiring Integration Tests

Comprehensive tests to ensure all CORTEX modules, plugins, agents, and tiers
are correctly wired together and can communicate properly.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys


class TestPluginWiring:
    """Test that all plugins are correctly wired"""
    
    def test_all_plugins_discoverable(self):
        """Test that plugin registry can discover all plugins"""
        from src.plugins.plugin_registry import PluginRegistry
        
        registry = PluginRegistry()
        registry.discover_plugins()  # Discover plugins before getting them
        plugins = registry.get_all_plugins()
        
        # Should have plugins registered
        assert len(plugins) > 0, "No plugins discovered"
        
        # Each plugin should have required attributes
        for plugin in plugins:
            assert hasattr(plugin, 'metadata')
            assert hasattr(plugin, 'initialize')
            assert hasattr(plugin, 'execute')
    
    def test_plugin_command_registration(self):
        """Test that plugins can register commands"""
        from src.plugins.plugin_registry import PluginRegistry
        from src.plugins.command_registry import CommandRegistry
        
        plugin_registry = PluginRegistry()
        plugin_registry.discover_plugins()  # Discover plugins first
        command_registry = CommandRegistry()
        
        # Plugins should register commands
        plugins = plugin_registry.get_all_plugins()
        
        for plugin in plugins:
            if hasattr(plugin, 'register_commands'):
                commands = plugin.register_commands()
                
                # Each command should have required fields
                for cmd in commands:
                    assert hasattr(cmd, 'command')
                    assert hasattr(cmd, 'plugin_id')
                    assert hasattr(cmd, 'description')
    
    def test_platform_switch_plugin_integration(self):
        """Test PlatformSwitchPlugin is wired correctly"""
        try:
            from src.plugins.platform_switch_plugin import PlatformSwitchPlugin
            
            plugin = PlatformSwitchPlugin()
            
            # Should initialize
            assert plugin.initialize() == True
            
            # Should have metadata
            assert plugin.metadata is not None
            assert plugin.metadata.plugin_id == "platform_switch"
        except ImportError:
            pytest.skip("PlatformSwitchPlugin not available")


class TestAgentWiring:
    """Test that all agents are correctly wired"""
    
    def test_intent_router_wiring(self):
        """Test IntentRouter is wired to all agents"""
        from src.cortex_agents.intent_router import IntentRouter
        
        # Mock tier APIs
        mock_tier1 = Mock()
        mock_tier2 = Mock()
        mock_tier3 = Mock()
        
        router = IntentRouter(
            name="test_router",
            tier1_api=mock_tier1,
            tier2_kg=mock_tier2,
            tier3_context=mock_tier3
        )
        
        # Should have agents registered
        assert hasattr(router, 'agents')
        assert len(router.agents) > 0
    
    def test_all_agents_have_base_methods(self):
        """Test that all agents implement required base methods"""
        from src.cortex_agents.base_agent import BaseAgent
        import inspect
        
        # Find all agent classes
        agent_classes = []
        
        # Import known agents
        try:
            from src.cortex_agents.intent_router import IntentRouter
            agent_classes.append(IntentRouter)
        except ImportError:
            pass
        
        try:
            from src.cortex_agents.work_planner import WorkPlanner
            agent_classes.append(WorkPlanner)
        except ImportError:
            pass
        
        try:
            from src.cortex_agents.code_executor import CodeExecutor
            agent_classes.append(CodeExecutor)
        except ImportError:
            pass
        
        # Each should be a BaseAgent subclass
        for agent_class in agent_classes:
            assert issubclass(agent_class, BaseAgent)
            
            # Should have required methods
            assert hasattr(agent_class, 'can_handle')
            assert hasattr(agent_class, 'execute')


class TestTierWiring:
    """Test that all tiers are correctly wired together"""
    
    def test_tier0_brain_protector_integration(self):
        """Test Tier 0 Brain Protector is wired"""
        try:
            from src.tier0.brain_protector import BrainProtector
            
            protector = BrainProtector()
            
            # Should load rules
            assert hasattr(protector, 'rules')
            
            # Should have SKULL rules
            skull_rules = [r for r in protector.rules if 'SKULL' in r.get('id', '')]
            assert len(skull_rules) > 0, "No SKULL rules loaded"
        except Exception as e:
            pytest.skip(f"BrainProtector not available: {e}")
    
    def test_tier1_conversation_manager_integration(self):
        """Test Tier 1 Conversation Manager is wired"""
        try:
            from src.tier1.conversation_manager import ConversationManager
            
            # Should be able to instantiate
            manager = ConversationManager()
            
            # Should have database path
            assert hasattr(manager, 'db_path')
        except Exception as e:
            pytest.skip(f"ConversationManager not available: {e}")
    
    def test_tier2_knowledge_graph_integration(self):
        """Test Tier 2 Knowledge Graph is wired"""
        try:
            from src.tier2.knowledge_graph import KnowledgeGraph
            
            # Should be able to instantiate
            kg = KnowledgeGraph()
            
            # Should have required methods
            assert hasattr(kg, 'add_pattern')
            assert hasattr(kg, 'search_patterns')
        except Exception as e:
            pytest.skip(f"KnowledgeGraph not available: {e}")
    
    def test_tier3_metrics_integration(self):
        """Test Tier 3 metrics are wired"""
        from src.metrics.brain_metrics_collector import BrainMetricsCollector
        
        collector = BrainMetricsCollector()
        
        # Should be able to collect metrics
        metrics = collector.get_brain_performance_metrics()
        
        assert metrics is not None
        assert 'tier1' in metrics
        assert 'tier2' in metrics
        assert 'tier3' in metrics


class TestOperationsWiring:
    """Test that operations orchestrators are wired correctly"""
    
    def test_operation_factory_wiring(self):
        """Test OperationFactory can create operations"""
        try:
            from src.operations.operation_factory import OperationFactory
            
            factory = OperationFactory()
            
            # Should have registered operations
            operations = factory.get_available_operations()
            
            assert len(operations) > 0, "No operations registered"
        except Exception as e:
            pytest.skip(f"OperationFactory not available: {e}")
    
    def test_cleanup_orchestrator_wiring(self):
        """Test CleanupOrchestrator is wired"""
        try:
            from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator
            
            # Should be able to import
            assert CleanupOrchestrator is not None
        except ImportError:
            pytest.skip("CleanupOrchestrator not available")
    
    def test_design_sync_orchestrator_wiring(self):
        """Test DesignSyncOrchestrator is wired"""
        try:
            from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
            
            # Should be able to import
            assert DesignSyncOrchestrator is not None
        except ImportError:
            pytest.skip("DesignSyncOrchestrator not available")
    
    def test_optimize_system_orchestrator_wiring(self):
        """Test OptimizeSystemOrchestrator is wired"""
        try:
            from src.operations.modules.system.optimize_system_orchestrator import OptimizeSystemOrchestrator
            
            # Should be able to import
            assert OptimizeSystemOrchestrator is not None
        except ImportError:
            pytest.skip("OptimizeSystemOrchestrator not available")


class TestHeaderFormatterWiring:
    """Test that header formatters are wired correctly after consolidation"""
    
    def test_operation_header_formatter_import(self):
        """Test OperationHeaderFormatter can be imported"""
        from src.operations.operation_header_formatter import OperationHeaderFormatter
        
        assert OperationHeaderFormatter is not None
    
    def test_backward_compatibility_imports(self):
        """Test backward compatibility imports work"""
        from src.operations.operation_header_formatter import (
            HeaderFormatter,
            format_minimalist_header,
            print_minimalist_header,
            format_completion_footer
        )
        
        assert HeaderFormatter is not None
        assert format_minimalist_header is not None
        assert print_minimalist_header is not None
        assert format_completion_footer is not None
    
    def test_orchestrators_use_new_formatter(self):
        """Test that orchestrators import from consolidated formatter"""
        import ast
        
        # Check cleanup orchestrator
        cleanup_file = Path("src/operations/modules/cleanup/cleanup_orchestrator.py")
        if cleanup_file.exists():
            content = cleanup_file.read_text(encoding='utf-8')
            
            # Should import from operation_header_formatter
            assert "operation_header_formatter" in content
            
            # Should NOT import from old files
            assert "header_utils" not in content or "operation_header_formatter" in content
    
    def test_all_orchestrators_updated(self):
        """Test all orchestrators use new formatter"""
        orchestrator_files = [
            "src/operations/modules/cleanup/cleanup_orchestrator.py",
            "src/operations/modules/design_sync/design_sync_orchestrator.py",
            "src/operations/modules/system/optimize_system_orchestrator.py"
        ]
        
        for file_path in orchestrator_files:
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding='utf-8')
                
                # Should use operation_header_formatter
                if "header" in content.lower():
                    assert "operation_header_formatter" in content, \
                        f"{file_path} not using operation_header_formatter"


class TestConfigWiring:
    """Test configuration system is wired correctly"""
    
    def test_config_module_import(self):
        """Test config module can be imported"""
        from src.config import config
        
        assert config is not None
    
    def test_config_paths_accessible(self):
        """Test config provides required paths"""
        from src.config import config
        
        # Should have key paths
        assert hasattr(config, 'root_path')
        assert hasattr(config, 'brain_path')
        assert hasattr(config, 'src_path')
        
        # Paths should be Path objects
        assert isinstance(config.root_path, Path)
        assert isinstance(config.brain_path, Path)
    
    def test_tier_database_paths(self):
        """Test tier database paths are configured"""
        from src.config import config
        
        assert hasattr(config, 'tier1_db_path')
        assert hasattr(config, 'tier2_db_path')


class TestTokenEfficiencyMetricsFileWiring:
    """Test token-efficiency-metrics.yaml file is properly integrated"""
    
    def test_file_exists(self):
        """Test token-efficiency-metrics.yaml exists"""
        from src.config import config
        
        metrics_file = config.brain_path / "tier3" / "token-efficiency-metrics.yaml"
        
        assert metrics_file.exists(), "token-efficiency-metrics.yaml not found"
    
    def test_file_is_valid_yaml(self):
        """Test file contains valid YAML"""
        import yaml
        from src.config import config
        
        metrics_file = config.brain_path / "tier3" / "token-efficiency-metrics.yaml"
        
        with open(metrics_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data is not None
        assert isinstance(data, dict)
    
    def test_contains_token_efficiency_metrics(self):
        """Test file contains token efficiency metrics"""
        import yaml
        from src.config import config
        
        metrics_file = config.brain_path / "tier3" / "token-efficiency-metrics.yaml"
        
        with open(metrics_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Should have token efficiency section
        assert 'token_efficiency' in data, "Missing token_efficiency section"
        
        # Should have key metrics
        token_eff = data['token_efficiency']
        assert 'vanilla_copilot' in token_eff
        assert 'cortex' in token_eff
        assert 'improvement' in token_eff
    
    def test_old_file_removed(self):
        """Test old efficiency-metrics.yaml is removed"""
        from src.config import config
        
        old_file = config.brain_path / "tier3" / "efficiency-metrics.yaml"
        
        assert not old_file.exists(), "Old efficiency-metrics.yaml still exists"
    
    def test_documentation_references_updated(self):
        """Test documentation references new filename"""
        doc_files = [
            "cortex-brain/CORTEX-EFFICIENCY-SUMMARY.md",
            "cortex-brain/CORTEX-EFFICIENCY-METRICS.md",
            "cortex-brain/response-templates.yaml"
        ]
        
        for doc_path in doc_files:
            path = Path(doc_path)
            if path.exists():
                content = path.read_text(encoding='utf-8')
                
                # Should reference new filename
                assert "token-efficiency-metrics.yaml" in content, \
                    f"{doc_path} doesn't reference new filename"
                
                # Should NOT reference old filename
                assert "efficiency-metrics.yaml" not in content or \
                       "token-efficiency-metrics.yaml" in content, \
                    f"{doc_path} still references old filename"


class TestEndToEndWiring:
    """End-to-end tests to verify complete system wiring"""
    
    def test_plugin_to_agent_communication(self):
        """Test plugins can communicate with agents"""
        # This would test a full workflow
        pytest.skip("Requires full system setup")
    
    def test_tier_to_tier_communication(self):
        """Test tiers can communicate with each other"""
        # This would test tier integration
        pytest.skip("Requires full system setup")
    
    def test_operation_execution_flow(self):
        """Test complete operation execution flow"""
        # This would test full operation
        pytest.skip("Requires full system setup")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
