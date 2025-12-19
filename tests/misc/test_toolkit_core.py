"""
Unit Tests for CORTEX Toolkit Core Tools

Tests the toolkit registry, tool discovery, and execution mechanisms.
"""
import sys
from pathlib import Path
import unittest

# Add toolkit to path
TOOLKIT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLKIT_ROOT))

from shared.toolkit_registry import ToolkitRegistry
from shared.config import get_config


class TestToolkitRegistry(unittest.TestCase):
    """Test toolkit registry functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = ToolkitRegistry()
    
    def test_registry_initialization(self):
        """Test registry initializes correctly."""
        self.assertIsNotNone(self.registry)
        self.assertIsNotNone(self.registry.manifest)
    
    def test_manifest_loading(self):
        """Test manifest loads with expected structure."""
        manifest = self.registry.manifest
        self.assertIn('toolkit', manifest)
        self.assertIn('categories', manifest)
        self.assertIn('tools', manifest)
        self.assertEqual(manifest['toolkit']['version'], '1.0.0')
    
    def test_list_tools(self):
        """Test listing all tools."""
        tools = self.registry.list_tools()
        self.assertIsInstance(tools, dict)
        self.assertGreater(len(tools), 0)
        
        # Check for known categories
        expected_categories = ['brain_operations', 'operations', 'planning']
        for category in expected_categories:
            self.assertIn(category, tools)
    
    def test_list_tools_by_category(self):
        """Test listing tools by specific category."""
        brain_tools = self.registry.list_tools(category='brain_operations')
        self.assertIsInstance(brain_tools, dict)
        self.assertIn('brain_operations', brain_tools)
        
        # Check for known brain operations
        brain_tool_names = [tool['name'] for tool in brain_tools['brain_operations']]
        self.assertIn('align', brain_tool_names)
        self.assertIn('healthcheck', brain_tool_names)
    
    def test_get_tool_metadata(self):
        """Test retrieving tool metadata."""
        tool_info = self.registry.get_tool('align')
        self.assertIsNotNone(tool_info)
        self.assertEqual(tool_info['name'], 'align')
        self.assertEqual(tool_info['command'], 'cortex-align')
        self.assertIn('script', tool_info)
        self.assertIn('wrapper', tool_info)
    
    def test_get_nonexistent_tool(self):
        """Test getting tool that doesn't exist."""
        tool_info = self.registry.get_tool('nonexistent_tool')
        self.assertIsNone(tool_info)
    
    def test_platform_support(self):
        """Test platform support checking."""
        tool_info = self.registry.get_tool('align')
        is_supported = self.registry.is_platform_supported(tool_info)
        self.assertIsInstance(is_supported, bool)
        # Most tools support all platforms
        self.assertTrue(is_supported)
    
    def test_tool_structure(self):
        """Test tool metadata has required fields."""
        tool_info = self.registry.get_tool('align')
        required_fields = ['name', 'command', 'description', 'script', 
                          'wrapper', 'platforms', 'execution_method']
        for field in required_fields:
            self.assertIn(field, tool_info, f"Missing required field: {field}")
    
    def test_tool_paths_exist(self):
        """Test that tool script paths exist."""
        tools = self.registry.list_tools()
        for category, tool_list in tools.items():
            for tool in tool_list:
                script_path = TOOLKIT_ROOT / tool['script']
                self.assertTrue(script_path.exists(), 
                              f"Script not found: {script_path}")
                
                if tool.get('wrapper'):
                    wrapper_path = TOOLKIT_ROOT / tool['wrapper']
                    self.assertTrue(wrapper_path.exists(), 
                                  f"Wrapper not found: {wrapper_path}")


class TestToolkitConfig(unittest.TestCase):
    """Test toolkit configuration system."""
    
    def test_config_loading(self):
        """Test configuration loads successfully."""
        config = get_config()
        self.assertIsNotNone(config)
    
    def test_toolkit_root(self):
        """Test toolkit root path is set."""
        config = get_config()
        toolkit_root = config.get_toolkit_root()
        self.assertIsNotNone(toolkit_root)
        self.assertTrue(Path(toolkit_root).exists())
    
    def test_workspace_roots(self):
        """Test workspace roots are configured."""
        config = get_config()
        workspace_roots = config.get_workspace_roots()
        self.assertIsInstance(workspace_roots, dict)
        # Should have at least CORTEX
        self.assertIn('cortex', workspace_roots)


class TestBrainOperations(unittest.TestCase):
    """Test brain operations tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = ToolkitRegistry()
    
    def test_align_tool_exists(self):
        """Test align tool is registered."""
        tool = self.registry.get_tool('align')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'align')
    
    def test_healthcheck_tool_exists(self):
        """Test healthcheck tool is registered."""
        tool = self.registry.get_tool('healthcheck')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'healthcheck')
    
    def test_optimize_tool_exists(self):
        """Test optimize tool is registered."""
        tool = self.registry.get_tool('optimize')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'optimize')
    
    def test_cleanup_tool_exists(self):
        """Test cleanup tool is registered."""
        tool = self.registry.get_tool('cleanup')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'cleanup')


class TestSystemOperations(unittest.TestCase):
    """Test system operations tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = ToolkitRegistry()
    
    def test_review_tool_exists(self):
        """Test review tool is registered."""
        tool = self.registry.get_tool('review')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'review')
    
    def test_deploy_tool_exists(self):
        """Test deploy tool is registered."""
        tool = self.registry.get_tool('deploy')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'deploy')
    
    def test_sanitize_tool_exists(self):
        """Test sanitize tool is registered."""
        tool = self.registry.get_tool('sanitize')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'sanitize')


class TestPlanningTools(unittest.TestCase):
    """Test planning tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = ToolkitRegistry()
    
    def test_plan_tool_exists(self):
        """Test plan tool is registered."""
        tool = self.registry.get_tool('plan')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'plan')
    
    def test_ado_tool_exists(self):
        """Test ado tool is registered."""
        tool = self.registry.get_tool('ado')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'ado')


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
